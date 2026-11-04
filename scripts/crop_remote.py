"""The cloud VM's side of `crop_redo.py --remote` (owner 2026-11-04: «optimize for speed … I would let you pause the process
… more powerful CPU/memory (cloud)»). Only the CPU part runs there — crop_batch.analyse, the same code at the same version
(the laptop syncs scripts/ and the data analyse reads, and checks book_crop's MD5); the laptop keeps the phone, the change
log, redo-done.tsv and the recipes, and gets back only the new revision's bytes (a crop is an appended revision) and the
review sheets.
Each book has a folder of its own on the VM, DIR = redo/<hash of its path>-<original md5>-<book_crop md5>, holding
src.pdf (the original). A run of the laptop started again finds a book analysed or being analysed meanwhile.
Usage (on the VM, from the repo copy; PATHHEX = the phone path's UTF-8 bytes in hex, safe in any shell):
  python3 -I scripts/crop_remote.py start DIR PATHHEX MD5   → «nosrc» (src.pdf missing or not MD5), «done», «error»,
                                                               «running», or «started» (analysis launched, detached)
  python3 -I scripts/crop_remote.py wait DIR [SECONDS]       → the state after waiting up to SECONDS (default 600) for the end
  python3 -I scripts/crop_remote.py clean DIR PATHHEX        → DIR and the book's review sheets removed
  (run DIR PATHHEX MD5: the analysis itself, launched by start)
out.json = analyse's dict + n1/m1 (the new file's size and MD5) + the run's printed lines; error.txt on a failure."""
import hashlib, json, os, shutil, subprocess, sys, time, traceback
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHEETS = os.path.expanduser('~/.cache/phone-library/crop-sheets')

def md5_file(p):
    h = hashlib.md5()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''): h.update(b)
    return h.hexdigest()

def alive(d):
    try: pid = int(open(os.path.join(d, 'pid')).read())
    except (OSError, ValueError): return False
    try: os.kill(pid, 0); return True
    except OSError: return False

def state(d):
    if os.path.exists(os.path.join(d, 'out.json')): return 'done'
    if os.path.exists(os.path.join(d, 'error.txt')): return 'error'
    return 'running' if alive(d) else 'none'

def start(d, pathhex, m0):
    s = state(d)
    if s in ('done', 'error', 'running'): return s
    src = os.path.join(d, 'src.pdf')
    if not os.path.exists(src) or md5_file(src) != m0: return 'nosrc'
    for f in ('log', 'out.json.tmp'):                 # (an analysis killed with its VM: begun again from the original)
        try: os.remove(os.path.join(d, f))
        except OSError: pass
    try: os.remove(src[:-4] + '.cropped.pdf')
    except OSError: pass
    # (the book's earlier review sheets on the VM out first: the laptop copies back the whole folder)
    shutil.rmtree(os.path.join(SHEETS, hashlib.md5(bytes.fromhex(pathhex)).hexdigest()[:12]), ignore_errors=True)
    p = subprocess.Popen([sys.executable, '-I', os.path.abspath(__file__), 'run', d, pathhex, m0], cwd=ROOT,
                         stdin=subprocess.DEVNULL, stdout=open(os.path.join(d, 'log'), 'w'), stderr=subprocess.STDOUT,
                         start_new_session=True)       # (detached: a dropped ssh connection does not stop it)
    open(os.path.join(d, 'pid'), 'w').write(str(p.pid))
    return 'started'

def run(d, pathhex, m0):
    sys.path.insert(0, os.path.join(ROOT, 'scripts')); os.chdir(ROOT)
    path = bytes.fromhex(pathhex).decode('utf-8'); src = os.path.join(d, 'src.pdf')
    try:
        import crop_batch as cb
        out = cb.analyse(path, src, 1)
        new = out.get('dst') or src
        out.update(n1=os.path.getsize(new), m1=md5_file(new), n0=os.path.getsize(src))
        sys.stdout.flush()
        out['log'] = open(os.path.join(d, 'log'), encoding='utf-8', errors='replace').read()[-4000:]
        json.dump(out, open(os.path.join(d, 'out.json.tmp'), 'w'), ensure_ascii=False,
                  default=lambda o: o.item() if hasattr(o, 'item') else str(o))   # (numpy scalars as numbers)
        os.replace(os.path.join(d, 'out.json.tmp'), os.path.join(d, 'out.json'))
    except BaseException:
        open(os.path.join(d, 'error.txt'), 'w').write(traceback.format_exc()[-3000:])
        raise

def wait(d, secs=600):
    t = time.time()
    while state(d) == 'running' and time.time() - t < secs: time.sleep(5)
    return state(d)

def clean(d, pathhex):
    shutil.rmtree(d, ignore_errors=True)
    shutil.rmtree(os.path.join(SHEETS, hashlib.md5(bytes.fromhex(pathhex)).hexdigest()[:12]), ignore_errors=True)

if __name__ == '__main__':
    a = sys.argv[1:]
    d = os.path.join(os.path.expanduser('~'), a[1]) if len(a) > 1 else None
    if a[0] == 'start': print(start(d, a[2], a[3]))
    elif a[0] == 'wait': print(wait(d, int(a[2]) if len(a) > 2 else 600))
    elif a[0] == 'clean': clean(d, a[2]); print('cleaned')
    elif a[0] == 'run': run(d, a[2], a[3])
    else: sys.exit(__doc__)
