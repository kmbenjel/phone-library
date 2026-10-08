"""Apply a rename/move plan on the phone over FTP (server-side RNFR/RNTO: nothing is re-uploaded).
Plan: TSV with columns  from<TAB>to<TAB>reason   (paths relative to the FTP root, e.g. Books/...)
- never overwrites: an item whose destination exists is skipped and reported
- creates missing parent folders; removes source folders left empty (logged as rmdir)
- every change is appended to data/changes/changes.tsv (time, action, from, to, reason, plan)
Undo:  python3 scripts/apply_plan.py --undo <plan-name>   (replays that plan's moves in reverse)
Usage: python3 scripts/apply_plan.py plan.tsv [--dry-run]"""
import ftplib, csv, os, sys, time, posixpath
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG = os.path.join(ROOT, 'data/changes/changes.tsv')
from phone_host import HOST, PORT
# Folders holding the library's own indexes/reports (AGENTS.md §4b): never moved out of, emptied or removed.
from special_dirs import NOT_BOOKS
PROTECTED = tuple('Books/' + d for d in NOT_BOOKS)

def protected(p):
    if os.environ.get('ALLOW_PROTECTED') == '1': return False      # deliberate step only (substituting improved copies)
    return any(p == d or p.startswith(d + '/') for d in PROTECTED)

def connect(tries=8):
    """the phone's FTP app sometimes accepts the TCP connection but sends no greeting for a few minutes (stale sessions
    after timeouts, 2026-10-06): wait and retry instead of failing the plan"""
    import time
    for i in range(tries):
        try:
            f = ftplib.FTP(); f.encoding = 'utf-8'; f.connect(HOST, PORT, timeout=60); f.login(); return f
        except (OSError, EOFError, ftplib.Error) as e:
            if i == tries - 1: raise
            print(f'phone FTP not answering ({type(e).__name__}); retry {i + 1}/{tries - 1} in 30 s', flush=True); time.sleep(30)

CACHE = {}   # folder -> set of entry names (loaded once per folder, updated on every change)

def listing(f, d):
    if d not in CACHE:
        if d == '' or d == '.' or d == '/':
            try: CACHE[d] = {posixpath.basename(n) for n in f.nlst(d)} - {'.', '..'}
            except ftplib.error_perm: CACHE[d] = None
        else:
            parent, name = posixpath.split(d)
            parent_l = listing(f, parent)
            if parent_l is not None and name in parent_l:
                try: CACHE[d] = {posixpath.basename(n) for n in f.nlst(d)} - {'.', '..'}
                except ftplib.error_perm: CACHE[d] = None
            else:
                CACHE[d] = None          # folder does not exist
    return CACHE[d]

def exists(f, path):
    parent, name = posixpath.split(path)
    l = listing(f, parent)
    return l is not None and name in l

def note_add(path):
    parent, name = posixpath.split(path)
    if CACHE.get(parent) is not None: CACHE[parent].add(name)
    elif parent in CACHE: CACHE[parent] = {name}

def note_del(path):
    parent, name = posixpath.split(path)
    if CACHE.get(parent) is not None: CACHE[parent].discard(name)

def mkdirs(f, path, made):
    parts = path.split('/'); cur = ''
    for p in parts:
        cur = posixpath.join(cur, p) if cur else p
        if cur in made: continue
        if not exists(f, cur):
            f.mkd(cur); note_add(cur); CACHE[cur] = set()
        made.add(cur)

def is_empty(f, d):
    l = listing(f, d)
    return l is not None and len(l) == 0

def log(w, action, a, b, reason, plan):
    w.writerow([time.strftime('%F %T'), action, a, b, reason, plan])

_KNOWN = None
def known_paths():
    """paths of data/phone/index-now.tsv (relative to Books/), for the dry run"""
    global _KNOWN
    if _KNOWN is None:
        p = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data/phone/index-now.tsv')
        _KNOWN = {l.split('\t', 1)[0] for l in open(p, encoding='utf-8')} if os.path.exists(p) else set()
    return _KNOWN

def run(rows, plan, dry):
    f = None if dry else connect(); made = set(); ok = skipped = 0
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    with open(LOG, 'a', newline='') as lf:
        w = csv.writer(lf, delimiter='\t')
        for a, b, reason in rows:
            if a == b: continue
            if protected(a): print('REFUSED (index folder)', a); skipped += 1; continue
            if dry:                                    # check against index-now.tsv (2026-10-08: plans written without
                known = known_paths()                  # «Books/» passed a dry run and failed on the phone with 553)
                if known and a[6:] not in known and not any(k.startswith(a[6:] + '/') for k in known):
                    print('NOT IN INDEX (path wrong or «Books/» missing?)', a); skipped += 1; continue
                if known and b[6:] in known: print('TARGET EXISTS', b); skipped += 1; continue
                print('MOVE', a, '->', b); ok += 1; continue
            for attempt in range(3):
                try:
                    if exists(f, b): print('SKIP (exists)', b); skipped += 1; break
                    mkdirs(f, posixpath.dirname(b), made)
                    f.rename(a, b); note_del(a); note_add(b); log(w, 'move', a, b, reason, plan); ok += 1
                    src_dir = posixpath.dirname(a)
                    while src_dir.count('/') >= 2 and is_empty(f, src_dir):   # keep Books/<category>
                        f.rmd(src_dir); note_del(src_dir); CACHE.pop(src_dir, None); log(w, 'rmdir', src_dir, '', 'empty after move', plan)
                        src_dir = posixpath.dirname(src_dir)
                    break
                except (ftplib.error_temp, OSError, EOFError) as e:
                    print('retry', a, e); time.sleep(3); f = connect(); CACHE.clear()
                except ftplib.error_perm as e:
                    print('FAIL', a, '->', b, e); skipped += 1; break
            lf.flush()
    print(f'{"planned" if dry else "moved"}: {ok}  skipped: {skipped}')

if __name__ == '__main__':
    args = [x for x in sys.argv[1:] if not x.startswith('--')]
    if '--undo' in sys.argv:
        plan = args[0]
        moves = [r for r in csv.reader(open(LOG), delimiter='\t') if r[5] == plan and r[1] == 'move']
        run([(r[3], r[2], 'undo ' + plan) for r in reversed(moves)], 'undo-' + plan, '--dry-run' in sys.argv)
    else:
        path = args[0]
        rows = [r[:3] for r in csv.reader(open(path), delimiter='\t') if r and not r[0].startswith('#')]
        run(rows, os.path.basename(path).rsplit('.', 1)[0], '--dry-run' in sys.argv)
