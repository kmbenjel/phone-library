"""redo_upload_test.py — crop_redo.put_in_place and stage() against a FAKE phone (no FTP, no data file touched): the
connection dropped at every single step of an upload in turn, then random runs of several drops and «phone away» spells;
each time the book must end as the new file, checked, with no «.redo» left beside it — or, where the phone file changed
meanwhile or the upload came out wrong, the old file untouched (2026-10-29)."""
import ftplib, hashlib, os, random, sys, tempfile
sys.path.insert(0, '/home/k/projects/phone-library/scripts')
import crop_batch as cb, crop_redo as R

md5 = lambda b: hashlib.md5(b).hexdigest()
S = {'ops': 0, 'fail': set(), 'away': 0, 'waits': 0, 'corrupt': False, 'short': False}
FS = {}

def tick(op):
    S['ops'] += 1
    if S['ops'] in S['fail']: raise ConnectionResetError(f'injected drop at op {S["ops"]} ({op})')

class FakeFTP:
    def delete(self, p): tick('delete'); del FS[p]
    def rename(self, a, b):
        tick('rename')
        if a not in FS: raise ftplib.error_perm('550 no such file')
        FS[b] = FS.pop(a)

class FakePhone:
    def __enter__(self):
        if S['away'] > 0: S['away'] -= 1; raise OSError(113, 'No route to host')
        tick('connect'); self.f = FakeFTP(); return self
    def __exit__(self, *a): pass
    def md5(self, path):
        tick('md5')
        if 'Books/' + path not in FS: raise ftplib.error_perm('550 not found')
        return md5(FS['Books/' + path])
    def size(self, path): tick('size'); return len(FS['Books/' + path])
    def get(self, path, dst):
        b = FS['Books/' + path]; tick('get')
        open(dst, 'wb').write(b[:len(b) // 3] if S['short'] else b)
    def put(self, path, src):
        b = open(src, 'rb').read()
        if S['ops'] + 1 in S['fail']: FS['Books/' + path] = b[:len(b) // 2]   # (a drop mid-transfer leaves half a file)
        tick('put')
        FS['Books/' + path] = (b[:-1] + b'X') if S['corrupt'] else b

def fake_wait(why): S['waits'] += 1; return 'fake'
cb.Phone = FakePhone; R.wait_phone = fake_wait

tmp = tempfile.mkdtemp(prefix='redo-test-')
orig = os.urandom(5000); old = orig + b'OLD-REVISION' * 40; new = orig + b'NEW-REVISION' * 55
src = os.path.join(tmp, 'new.pdf'); open(src, 'wb').write(new)
P = 'الأدب/كتاب للتجربة.pdf'; K = 'Books/' + P; T = K + '.redo'

def reset(**kw):
    FS.clear(); FS[K] = old; S.update(ops=0, fail=set(), away=0, waits=0, corrupt=False, short=False); S.update(kw)

def run():
    try: R.put_in_place(P, src, len(new), md5(new), md5(old)); return 'ok'
    except RuntimeError as e: return f'error: {e}'

bad = 0
reset(); assert run() == 'ok' and FS == {K: new}; clean_ops = S['ops']
print(f'clean upload: {clean_ops} phone operations')
for n in range(1, clean_ops + 1):                    # one drop at each step
    reset(fail={n}); res = run()
    ok = res == 'ok' and FS == {K: new}
    bad += not ok; print(f'  drop at op {n:2}: {res:6} waits {S["waits"]} files {sorted(k[-12:] for k in FS)} {"" if ok else "  <-- WRONG"}')
random.seed(7)
for trial in range(300):                             # several drops and phone-away spells (≤ 4 lost attempts: 5 tries)
    reset(fail=set(random.sample(range(1, 40), random.randint(0, 3))), away=random.randint(0, 1))
    res = run()
    ok = (res == 'ok' and FS == {K: new}) or (res.startswith('error: the upload did not finish') and FS.get(K) in (old, new))
    if not ok: bad += 1; print('  WRONG', trial, res, S, sorted(FS))
reset(); FS[K] = b'someone else changed it'
res = run(); ok = res.startswith('error: the phone file changed') and FS == {K: b'someone else changed it'}
bad += not ok; print('phone file changed meanwhile:', res, '' if ok else '<-- WRONG')
reset(corrupt=True); res = run(); ok = res.startswith('error: upload not verified') and FS == {K: old}
bad += not ok; print('upload came out wrong:', res, '| files', sorted(k[-12:] for k in FS), '' if ok else '<-- WRONG')
reset(); FS.pop(K); FS[T] = new; res = run(); ok = res == 'ok' and FS == {K: new}   # an earlier run stopped after the delete
bad += not ok; print('only «.redo» left by an earlier run:', res, '' if ok else '<-- WRONG')
reset(); FS.pop(K); FS[T] = new[:100]; res = run(); ok = res.startswith('error: the book is gone') and FS == {T: new[:100]}
bad += not ok; print('book gone, «.redo» unchecked:', res, '' if ok else '<-- WRONG')

# stage(): the original bytes from the cropped phone file, a short download is a lost connection (retried), never a skip
cb.STAGE = tmp; R.LOCAL_MAP = os.path.join(tmp, 'none.tsv')
reset(); w, now = R.stage(P, len(orig), md5(orig), md5(old)); ok = open(w, 'rb').read() == orig and now == md5(old)
bad += not ok; print('stage:', 'original recovered' if ok else 'WRONG')
reset(short=True)
try: R.stage(P, len(orig), md5(orig), md5(old)); ok = False
except R.LOST as e: ok = True; print('stage, download cut short:', type(e).__name__, e)
bad += not ok
reset(); FS[K] = b'x' * 9000
try: R.stage(P, len(orig), md5(orig), md5(old)); ok = False
except RuntimeError as e: ok = 'not the one the crop wrote' in str(e); print('stage, phone file not the crop\'s:', e)
bad += not ok
print('ALL RIGHT' if not bad else f'{bad} WRONG')
