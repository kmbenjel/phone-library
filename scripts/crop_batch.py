"""Apply scripts/book_crop.py to phone books, batch by batch (owner 2026-10-09: sample 4 approved, «aren't we done with sample
judging» — the method now runs on the library; the regression test must pass first: scripts/crop_regress.py → 0 failures).

Per file (a PDF on the phone, path relative to Books/):
  1. the bytes: the laptop's copy (~/Books, via ~/.cache/phone-library/local-map.tsv) when its MD5 equals the phone file's
     (server-side XMD5), else the file is fetched from the phone (shared lock /tmp/phone-ftp.lock);
  2. book_crop.plan() → skip unless decision == 'crop' and no page keeps a tilt (residual_tilt empty);
  3. book_crop.apply() → an INCREMENTAL save: the original bytes unchanged + an appended update (CropBox, turn/move
     streams); checked: the output starts with the exact original bytes; same pages; every image byte-identical;
  4. on the phone: XMD5 must still equal the original's; only the appended part is sent (FTP APPE); then the phone file's
     size and XMD5 must equal the output's — else the original is put back at once (STOR) and checked;
  5. logged in data/changes/changes.tsv (action «crop»: original size + MD5, appended bytes, gain, pages turned/whole),
     the recipe kept in data/crop/recipes/<original md5>.json (undo = truncate the phone file to the original size:
     scripts/crop_batch.py --undo <path>), data/phone/index-now.tsv size updated, data/crop/done.tsv (resumable).
Usage: python3 scripts/crop_batch.py LIST.tsv BATCH_NAME [--workers N]   (LIST: one phone path per line, under Books/)
       python3 scripts/crop_batch.py --undo PATH                         (restore one file to its original bytes)"""
import csv, hashlib, io, json, os, subprocess, sys, tempfile, time, ftplib, fcntl
from concurrent.futures import ProcessPoolExecutor, as_completed
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
J = lambda *p: os.path.join(ROOT, *p)
STAGE = J('downloads', 'crop-batch'); os.makedirs(STAGE, exist_ok=True)
RECIPES = J('data', 'crop', 'recipes'); os.makedirs(RECIPES, exist_ok=True)
DONE = J('data', 'crop', 'done.tsv')
LOG = J('data', 'changes', 'changes.tsv')
LOCAL_MAP = os.path.expanduser('~/.cache/phone-library/local-map.tsv')
LOCK = '/tmp/phone-ftp.lock'

def md5_file(p):
    h = hashlib.md5()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''): h.update(b)
    return h.hexdigest()

class Phone:
    """one FTP connection under the shared lock, for the few operations of one file"""
    def __enter__(self):
        from phone_host import HOST, PORT
        self.lk = open(LOCK, 'w'); fcntl.flock(self.lk, fcntl.LOCK_EX)
        self.f = ftplib.FTP(); self.f.connect(HOST, PORT, timeout=120); self.f.login(); self.f.encoding = 'utf-8'
        return self
    def __exit__(self, *a):
        try: self.f.quit()
        except Exception: pass
        fcntl.flock(self.lk, fcntl.LOCK_UN); self.lk.close()
    def md5(self, path):
        r = self.f.sendcmd('XMD5 Books/' + path)            # 251 "path" HEX
        return r.rsplit(' ', 1)[-1].strip().lower()
    def size(self, path): return self.f.size('Books/' + path)
    def get(self, path, dst):
        with open(dst, 'wb') as o: self.f.retrbinary('RETR Books/' + path, o.write, blocksize=1 << 16)
    def append(self, path, data): self.f.storbinary('APPE Books/' + path, io.BytesIO(data), blocksize=1 << 16)
    def put(self, path, src):
        with open(src, 'rb') as i: self.f.storbinary('STOR Books/' + path, i, blocksize=1 << 16)

def analyse(path, src):
    """CPU part, in a worker process: plan + apply to a copy; returns what the phone step needs"""
    import book_crop as bc
    rec = bc.plan(src)
    out = {'path': path, 'src': src, 'decision': rec.get('decision'), 'gain': rec.get('gain'),
           'turned': sum(1 for p in rec['pages'] if p.get('skew')), 'whole': len(rec.get('whole') or []),
           'residual': rec.get('residual_tilt') or [], 'untreated': rec.get('untreated_tilt') or [],
           'clean': rec.get('clean_margins'), 'enlarged': len(rec.get('enlarged') or [])}
    if rec.get('decision') != 'crop' or out['residual']:
        return out
    dst = src[:-4] + '.cropped.pdf'
    info = bc.apply(src, rec, dst)
    n = os.path.getsize(src)
    with open(src, 'rb') as a, open(dst, 'rb') as b:
        if a.read() != b.read(n): raise RuntimeError('the output does not start with the original bytes')
    out.update(dst=dst, info=info, recipe={'pages': [{k: p.get(k) for k in ('crop', 'skew', 'move', 'enlarged', 'curved') if p.get(k)}
                                                    for p in rec['pages']], 'size': rec.get('size'), 'gain': rec.get('gain'),
                                          'clean_margins': rec.get('clean_margins'), 'parity_offsets': rec.get('parity_offsets')})
    return out

def log_change(path, why, batch):
    with open(LOG, 'a', newline='', encoding='utf-8') as f:
        csv.writer(f, delimiter='\t').writerow([time.strftime('%F %T'), 'crop', 'Books/' + path, 'Books/' + path, why, batch])

def set_index_size(path, size):
    p = J('data', 'phone', 'index-now.tsv'); rows = open(p, encoding='utf-8').read().split('\n')
    for k, l in enumerate(rows):
        if l.split('\t', 1)[0] == path: rows[k] = f'{path}\t{size}'
    open(p, 'w', encoding='utf-8').write('\n'.join(rows))

def main(list_tsv, batch, workers=4):
    paths = [l.strip().removeprefix('Books/') for l in open(list_tsv, encoding='utf-8') if l.strip() and not l.startswith('#')]
    done = {l.split('\t')[0] for l in open(DONE, encoding='utf-8')} if os.path.exists(DONE) else set()
    todo = [p for p in paths if p not in done]
    local = dict(l.rstrip('\n').split('\t')[:2] for l in open(LOCAL_MAP, encoding='utf-8')) if os.path.exists(LOCAL_MAP) else {}
    print(f'{len(todo)} files to do ({len(paths) - len(todo)} done before)', flush=True)
    def stage(path):                                  # the original bytes, checked against the phone's own MD5
        with Phone() as ph: want = ph.md5(path)
        lp = local.get(path)
        if lp and os.path.exists(lp) and md5_file(lp) == want: return lp, want, False
        dst = os.path.join(STAGE, hashlib.md5(path.encode()).hexdigest()[:12] + '.pdf')
        with Phone() as ph: ph.get(path, dst)
        if md5_file(dst) != want: raise RuntimeError('download differs from the phone file')
        return dst, want, True
    with ProcessPoolExecutor(workers) as ex:
        futs = {}
        for path in todo:
            try:
                src, m0, staged = stage(path)
            except Exception as e:
                print('STAGE FAIL', path, e, flush=True); continue
            work = os.path.join(STAGE, hashlib.md5(path.encode()).hexdigest()[:12] + '.work.pdf')
            if src != work: subprocess.run(['cp', src, work], check=True)
            if staged: os.remove(src)
            futs[ex.submit(analyse, path, work)] = (path, m0)
            while len(futs) >= workers * 2:           # keep the pool fed, the staging small
                for fu in as_completed(list(futs)): finish(fu, futs.pop(fu), batch); break
        for fu in as_completed(list(futs)): finish(fu, futs.pop(fu), batch)

def finish(fu, meta, batch):
    path, m0 = meta
    try: r = fu.result()
    except Exception as e:
        print('ANALYSE FAIL', path, repr(e)[:200], flush=True); return
    src = r['src']
    def mark(result):
        with open(DONE, 'a', encoding='utf-8') as f: f.write(f'{path}\t{m0}\t{result}\n')
    try:
        if not r.get('dst'):
            mark(f'skip: {r["decision"]}' + (f'; residual tilt {r["residual"][:5]}' if r.get('residual') else ''))
            print('skip', path[:80], '|', r['decision'][:60], flush=True); return
        dst = r['dst']; n0 = os.path.getsize(src); n1 = os.path.getsize(dst); m1 = md5_file(dst)
        tail = open(dst, 'rb').read()[n0:]
        with Phone() as ph:
            if ph.md5(path) != m0: raise RuntimeError('the phone file changed meanwhile')
            try:
                ph.append(path, tail)
                ok = ph.size(path) == n1 and ph.md5(path) == m1
            except Exception as e:
                ok = False; print('APPEND ERROR', path, e, flush=True)
            if not ok:                                # put the original back, at once, and prove it
                ph.put(path, src)
                back = ph.md5(path) == m0
                raise RuntimeError('append not verified; original restored' + ('' if back else ' — RESTORE NOT VERIFIED'))
        json.dump(r['recipe'], open(os.path.join(RECIPES, m0 + '.json'), 'w'), ensure_ascii=False)
        log_change(path, f'book_crop (lossless): gain {r["gain"]}, pages turned {r["turned"]}, whole {r["whole"]}, enlarged {r["enlarged"]}, '
                         f'clean margins {r["clean"]}; original {n0} B md5 {m0}; appended {n1 - n0} B → md5 {m1}', batch)
        set_index_size(path, n1)
        mark(f'cropped {n0}->{n1}')
        print('CROPPED', path[:80], '| gain', r['gain'], '| turned', r['turned'], '| whole', r['whole'], flush=True)
    except Exception as e:
        mark(f'FAIL {e}'); print('FAIL', path, e, flush=True)
    finally:
        for p in (src, r.get('dst')):
            if p and os.path.exists(p): os.remove(p)

def undo(path):
    """truncate the phone file back to its original bytes (the size and MD5 logged by the crop)"""
    path = path.removeprefix('Books/')
    rows = [r for r in csv.reader(open(LOG, encoding='utf-8'), delimiter='\t') if len(r) > 4 and r[1] == 'crop' and r[2] == 'Books/' + path]
    if not rows: sys.exit('no crop logged for ' + path)
    why = rows[-1][4]; n0 = int(why.split('original ')[1].split(' B')[0]); m0 = why.split('md5 ')[1].split(';')[0]
    tmp = os.path.join(STAGE, 'undo.pdf')
    with Phone() as ph:
        ph.get(path, tmp)
        with open(tmp, 'r+b') as f: f.truncate(n0)
        if md5_file(tmp) != m0: sys.exit('the truncated file is not the original — nothing changed on the phone')
        ph.put(path, tmp)
        assert ph.md5(path) == m0
    os.remove(tmp); set_index_size(path, n0)
    log_change(path, f'crop undone: back to the original ({n0} B md5 {m0})', 'crop-undo')
    print('restored', path)

if __name__ == '__main__':
    if sys.argv[1] == '--undo': undo(sys.argv[2])
    else:
        w = int(sys.argv[sys.argv.index('--workers') + 1]) if '--workers' in sys.argv else 4
        main(sys.argv[1], sys.argv[2], w)
