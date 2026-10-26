"""Apply scripts/book_crop.py to phone books, batch by batch (owner 2026-10-09: sample 4 approved, «aren't we done with sample
judging» — the method now runs on the library; the regression test must pass first: scripts/crop_regress.py → 0 failures).

Per file (a PDF on the phone, path relative to Books/):
  1. the bytes: the laptop's copy (~/Books, via ~/.cache/phone-library/local-map.tsv) when its MD5 equals the phone file's
     (server-side XMD5), else the file is fetched from the phone (shared lock /tmp/phone-ftp.lock);
  2. book_crop.plan() → skip unless decision == 'crop' and no page keeps a tilt (residual_tilt empty);
  3. book_crop.apply() → an INCREMENTAL save: the original bytes unchanged + an appended update (CropBox, turn/move/scale
     streams); checked: the output starts with the exact original bytes; same pages; every image byte-identical; every
     page exactly the book's size (owner 2026-10-09: «اتحاد العرض… يجب اطّراده في جميع الكتب») — else nothing is sent;
  4. on the phone: XMD5 must still equal the original's; only the appended part is sent (FTP APPE); then the phone file's
     size and XMD5 must equal the output's — else the original is put back at once (STOR) and checked;
  5. logged in data/changes/changes.tsv (action «crop»: original size + MD5, appended bytes, gain, pages turned/whole),
     the recipe kept in data/crop/recipes/<original md5>.json (undo = truncate the phone file to the original size:
     scripts/crop_batch.py --undo <path>), data/phone/index-now.tsv size updated, data/crop/done.tsv (resumable).
Usage: python3 scripts/crop_batch.py LIST.tsv BATCH_NAME [--workers N] [--jobs J]   (LIST: one phone path per line, under
       Books/; --workers 1 --jobs 8: one book at a time, its pages shared among 8 processes)
       python3 scripts/crop_batch.py --undo PATH                         (restore one file to its original bytes)"""
import csv, hashlib, io, json, os, subprocess, sys, tempfile, time, ftplib, fcntl, unicodedata
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
SHEETS = os.path.expanduser('~/.cache/phone-library/crop-sheets')

def moves():
    """(forward, back): logged moves from → to and to → from (paths under Books/), read fresh — the names change while a
    batch runs (rename passes on the same night, owner 2026-10-10)"""
    fwd, back = {}, {}
    for r in csv.reader(open(LOG, encoding='utf-8'), delimiter='\t'):
        if len(r) > 3 and r[1] == 'move' and r[2] and r[3]:
            a, b = r[2].removeprefix('Books/'), r[3].removeprefix('Books/'); fwd[a] = b; back[b] = a
    return fwd, back

def follow(path):
    """where a file that is no longer at `path` went: the chain of logged moves from it"""
    fwd, _ = moves(); seen = set()
    while path in fwd and path not in seen: seen.add(path); path = fwd[path]
    return path

OWNER_TURNS = J('data', 'crop', 'owner-turns.tsv')
OWNER_PAGES = J('data', 'crop', 'owner-pages.tsv')

def listed(table, path):
    """the rows of a list of pages (path, page, …) that are about this book: the list's paths and `path` are each followed
    to the name the file has now (logged moves, only while the name is not on the phone — the log also holds the crop's
    own swaps), Unicode-normalised"""
    if not os.path.exists(table): return []
    N = lambda x: unicodedata.normalize('NFC', x.removeprefix('Books/'))
    rows = [l.rstrip('\n').split('\t') for l in open(table, encoding='utf-8') if l.strip() and not l.startswith('#')]
    if not rows: return []
    fwd = {N(a): N(b) for a, b in moves()[0].items()}
    idx = {N(l.split('\t')[0]) for l in open(J('data', 'phone', 'index-now.tsv'), encoding='utf-8') if l.strip()}
    def now(x):
        x, seen = N(x), set()
        while x not in idx and x in fwd and x not in seen: seen.add(x); x = fwd[x]
        return x
    me = now(path)
    return [r for r in rows if now(r[0]) == me]

def owner_turns(path):
    """the pages of this book the owner ruled «turn» (data/crop/owner-turns.tsv: path, page, measured tilt, verdict — his
    verdicts on site/crop-tilt-001.html, 2026-10-25) → {page (1-based, as in the recipe): |tilt|}, for book_crop.plan"""
    return {int(r[1]): float(r[2]) for r in listed(OWNER_TURNS, path)}

def owner_pages(path):
    """the pages of this book the owner pointed at in an earlier crop review (data/crop/owner-pages.tsv: path, page, his
    words, where; and the pages he ruled «turn», owner-turns.tsv) → {page (1-based): «his words» (where)}: drawn on the
    review page of every new crop of the book, doubted by the method or not, so that he sees each remark answered (the
    pilot redo of 2026-10-26 holds five of the books he marked on 10-14)"""
    out = {}
    for r in listed(OWNER_TURNS, path): out.setdefault(int(r[1]), []).append('أجزتَ تدويرها (crop-tilt-001، 2026-10-25)')
    for r in listed(OWNER_PAGES, path): out.setdefault(int(r[1]), []).append(f'«{r[2]}»' + (f' ({r[3]})' if len(r) > 3 and r[3] else ''))
    return {k: ' / '.join(v) for k, v in out.items()}

def names_of(path, back):
    """the file's earlier names (its logged moves, followed backwards)"""
    out, seen = [path], set()
    while path in back and path not in seen: seen.add(path); path = back[path]; out.append(path)
    return out

def md5_file(p):
    h = hashlib.md5()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''): h.update(b)
    return h.hexdigest()

_PACER = None
def pacer():
    global _PACER
    if _PACER is None:
        from netpace import Pacer
        _PACER = Pacer()
    return _PACER

_HOST = None

class Phone:
    """one FTP connection under the shared lock, for the few operations of one file"""
    def __enter__(self):
        import phone_host
        global _HOST
        self.lk = open(LOCK, 'w'); fcntl.flock(self.lk, fcntl.LOCK_EX)
        self.f = ftplib.FTP()
        try: self.f.connect(_HOST or phone_host.HOST, phone_host.PORT, timeout=120)
        except OSError:                                  # the phone moved (it switched .100 ↔ .102 on 2026-10-11)
            _HOST = phone_host.find()
            if not _HOST: raise
            self.f = ftplib.FTP(); self.f.connect(_HOST, phone_host.PORT, timeout=120)
        phone_host.login(self.f); self.f.encoding = 'utf-8'
        return self
    def __exit__(self, *a):
        try: self.f.quit()
        except Exception: pass
        fcntl.flock(self.lk, fcntl.LOCK_UN); self.lk.close()
    def md5(self, path):
        r = self.f.sendcmd('XMD5 Books/' + path)            # 251 "path" HEX
        return r.rsplit(' ', 1)[-1].strip().lower()
    def size(self, path): return self.f.size('Books/' + path)
    def get(self, path, dst):                       # paced: the home Wi-Fi stays free for games and calls (AGENTS.md §7.9)
        pc = pacer()
        with open(dst, 'wb') as o:
            def w(chunk): o.write(chunk); pc.wait(len(chunk))
            self.f.retrbinary('RETR Books/' + path, w, blocksize=1 << 16)
    def append(self, path, data): self.f.storbinary('APPE Books/' + path, io.BytesIO(data), blocksize=1 << 16)
    def put(self, path, src):
        with open(src, 'rb') as i: self.f.storbinary('STOR Books/' + path, i, blocksize=1 << 16)

def analyse(path, src, jobs=1):
    """CPU part, in a worker process: plan + apply to a copy; returns what the phone step needs (jobs > 1: the book's pages
    shared out among that many processes — one urgent book with all processors)"""
    import book_crop as bc
    rec = bc.plan(src, jobs, owner_turns=owner_turns(path))
    out = {'path': path, 'src': src, 'decision': rec.get('decision'), 'gain': rec.get('gain'),
           'turned': sum(1 for p in rec['pages'] if p.get('skew')), 'whole': len(rec.get('whole') or []),
           'residual': rec.get('residual_tilt') or [], 'untreated': rec.get('untreated_tilt') or [],
           'clean': rec.get('clean_margins'), 'enlarged': len(rec.get('enlarged') or []), 'scaled': len(rec.get('scaled') or []),
           'bands': len(rec.get('bands') or []), 'notes': sum(1 for p in rec['pages'] if p.get('notes'))}
    if rec.get('decision') not in ('crop', 'level') or out['residual']:
        return out
    dst = src[:-4] + '.cropped.pdf'
    info = bc.apply(src, rec, dst)
    n = os.path.getsize(src)
    with open(src, 'rb') as a, open(dst, 'rb') as b:
        if a.read() != b.read(n): raise RuntimeError('the output does not start with the original bytes')
    # THE DOUBTFUL PAGES for the owner's review (owner 2026-10-18: «show me what would be better reviewed manually»; the review
    # page shows only them — «hope my remarks will be rare»): every page the method itself is unsure of, in every book —
    # a tilt measured differently by its measures or left untreated, a stain kept inside to keep the margins balanced, a
    # page left whole or shown larger, a stamp covered, a page on the scanner bed filled beyond its edge. Up to 6 a book
    try:
        P = rec['pages']; untreated = {k - 1 for k in rec.get('untreated_tilt') or []}; whole = {k - 1 for k in rec.get('whole') or []}
        flags = []
        for i, p in enumerate(P):
            why = ('tilt' if p.get('unsure_tilt') or p.get('tilt_disputed') or i in untreated else
                   'whole' if i in whole or (p['kind'] == 'text' and not p.get('crop') and rec.get('decision') == 'crop') else
                   'stain' if p.get('stain_kept') else
                   'stamp' if p.get('stamp') else
                   'sheet' if p.get('sheet_fill') and p.get('crop') else
                   'larger' if (p.get('enlarged') or 1) >= 1.05 else
                   # (the second look's own corrections, 2026-10-26: a mark the moved box would have cut, taken in; a page
                   # number read as a stain, put back — shown so that he sees them work)
                   'cut' if p.get('verify_cut') else
                   'folio' if p.get('folio_blot') else None)
            if why: flags.append((i, why))
        order = {'tilt': 0, 'whole': 1, 'stain': 2, 'stamp': 3, 'larger': 4, 'sheet': 5, 'cut': 6, 'folio': 7}
        seen, sp = set(), []
        for i, why in sorted(flags, key=lambda x: (order[x[1]], x[0])):   # each kind of doubt first, then more of them
            if why in seen: continue
            seen.add(why); sp.append((i, why))
        for i, why in sorted(flags, key=lambda x: (order[x[1]], x[0])):
            if len(sp) >= 6: break
            if (i, why) not in sp: sp.append((i, why))
        # (and every page the owner pointed at before, his words beside it: «owner», with the method's own doubt if any)
        own = {pg - 1: w for pg, w in owner_pages(path).items() if 0 < pg <= len(P)}
        pick = dict(sorted(sp)[:6])
        for i in own: pick[i] = 'owner' + ('+' + pick[i] if i in pick else '')
        shown = sorted(pick.items())
        d = os.path.join(SHEETS, hashlib.md5(path.encode()).hexdigest()[:12])
        if shown:
            bc.sheet(src, rec, d, shown)
        json.dump({'path': path, 'decision': rec.get('decision'), 'reasons': rec.get('reasons'), 'gain': rec.get('gain'),
                   'doubts': {w: sum(1 for _, x in flags if x == w) for w in order}, 'shown': shown,
                   'owner': {str(i + 1): w for i, w in own.items()}},
                  open(os.path.join(d, 'book.json'), 'w') if os.makedirs(d, exist_ok=True) is None else None, ensure_ascii=False)
    except Exception as e: print('SHEET FAIL', path[:60], repr(e)[:120], flush=True)
    out.update(dst=dst, info=info, recipe={'pages': [{k: p.get(k) for k in ('crop', 'show', 'scale', 'bands', 'fit_whole', 'skew', 'move', 'enlarged',
                                                               'curved', 'notes', 'anchored_x', 'anchored_y',
                                                               'verify_moved', 'verify_cut', 'folio_blot', 'owner_turn') if p.get(k)}
                                                    for p in rec['pages']], 'size': rec.get('size'), 'gain': rec.get('gain'),
                                          'margin_pt': rec.get('margin_pt'), 'clean_margins': rec.get('clean_margins'),
                                          'decision': rec.get('decision'), 'reasons': rec.get('reasons'), 'level_trim': rec.get('level_trim'),
                                          'parity_offsets': rec.get('parity_offsets')})
    return out

def log_change(path, why, batch):
    with open(LOG, 'a', newline='', encoding='utf-8') as f:
        csv.writer(f, delimiter='\t').writerow([time.strftime('%F %T'), 'crop', 'Books/' + path, 'Books/' + path, why, batch])

def set_index_size(path, size):
    p = J('data', 'phone', 'index-now.tsv'); rows = open(p, encoding='utf-8').read().split('\n')
    for k, l in enumerate(rows):
        if l.split('\t', 1)[0] == path: rows[k] = f'{path}\t{size}'
    open(p, 'w', encoding='utf-8').write('\n'.join(rows))

class Inline:
    """a one-at-a-time executor in this process (a single book whose pages use the processors themselves)"""
    def __init__(self, n=1): pass
    def __enter__(self): return self
    def __exit__(self, *a): return False
    def submit(self, fn, *a):
        from concurrent.futures import Future
        f = Future()
        try: f.set_result(fn(*a))
        except Exception as e: f.set_exception(e)
        return f

WORKERS_FILE = J('data', 'crop', 'workers')

def governed(default):
    """the number of books analysed at once, as scripts/mem_governor.py sets it (data/crop/workers; owner 2026-10-18: more
    workers, fewer when memory runs short) — read before each new book; without the file, the number given"""
    try: return max(1, int(open(WORKERS_FILE).read().strip()))
    except (OSError, ValueError): return default

def free_gb():
    for l in open('/proc/meminfo'):
        if l.startswith('MemAvailable:'): return int(l.split()[1]) / 1048576
    return 99.0

def own_bytes():
    """this process's resident memory (VmRSS), in bytes"""
    for l in open('/proc/self/status'):
        if l.startswith('VmRSS:'): return int(l.split()[1]) * 1024
    return 0

def room(need=3.0, own=0):
    """a new book starts only with ≥ 3 GB free, whatever the worker count (2026-10-18 03:05: the owner's session was closed
    by systemd-oomd while a bench ran 3 analyses beside his browsers — free memory had fallen to 0.8 GB).
    own: bytes the caller holds that the new book will reuse — a book analysed in the caller's own process (one worker:
    crop_regress, crop_minitest) runs in the memory it kept from the last one. Counted as taken, it blocked the regression
    for good (2026-10-26 08:18, 26e: 0.83 GB of its own): the governor's pen is free + what it holds − 2.5 GB, so «what it
    holds ≤ pen − 2.2 GB» meant free ≥ 4.7 GB whatever the job held"""
    if free_gb() < need: return False
    try:                                              # and room in the pen (crop.slice, sized by scripts/mem_governor.py)
        cg = f'/sys/fs/cgroup/user.slice/user-{os.getuid()}.slice/user@{os.getuid()}.service/crop.slice'
        hi = open(cg + '/memory.high').read().strip()
        # (a book ≈ 1.5 GB: one process analysing a whole book peaked at 0.97–1.29 GB on the 31 regression books, 26f, 2026-10-26
        # — the 2.2 GB of 10-18 predates the stamps fix of 10-25; with the pen at its 2 GB floor no book could start at all)
        if hi != 'max' and int(open(cg + '/memory.current').read()) - own > int(hi) - 1.5 * 2 ** 30: return False
    except (OSError, ValueError): pass
    return True

def main(list_tsv, batch, workers=4, jobs=1):
    paths = [l.strip().removeprefix('Books/') for l in open(list_tsv, encoding='utf-8') if l.strip() and not l.startswith('#')]
    done = {l.split('\t')[0] for l in open(DONE, encoding='utf-8')} if os.path.exists(DONE) else set()
    crop_rows = {r[2].removeprefix('Books/') for r in csv.reader(open(LOG, encoding='utf-8'), delimiter='\t') if len(r) > 2 and r[1] == 'crop'}
    _, back = moves()
    todo = [p for p in paths if not any(n in done or n in crop_rows for n in names_of(p, back))]
    local = dict(l.rstrip('\n').split('\t')[:2] for l in open(LOCAL_MAP, encoding='utf-8')) if os.path.exists(LOCAL_MAP) else {}
    print(f'{len(todo)} files to do ({len(paths) - len(todo)} done before)', flush=True)
    def stage(path):                                  # the original bytes, checked against the phone's own MD5
        with Phone() as ph: want = ph.md5(path)       # (path: where the file is now — see the loop below)
        lp = local.get(path)
        if lp and os.path.exists(lp) and md5_file(lp) == want: return lp, want, False
        dst = os.path.join(STAGE, hashlib.md5(path.encode()).hexdigest()[:12] + '.pdf')
        with Phone() as ph: ph.get(path, dst)
        if md5_file(dst) != want: raise RuntimeError('download differs from the phone file')
        return dst, want, True
    with (ProcessPoolExecutor(workers) if workers > 1 else Inline()) as ex:
        futs = {}
        for path in todo:
            try:
                with Phone() as ph:
                    try: ph.size(path)
                    except ftplib.error_perm:         # renamed since the list was made: follow its logged moves
                        new = follow(path)
                        if new == path: raise RuntimeError('not on the phone')
                        print('MOVED', path[:60], '→', new[:60], flush=True); path = new
                src, m0, staged = stage(path)
            except ftplib.error_perm as e:
                if str(e).startswith('530'): raise SystemExit(f'FTP login refused ({e}) — the login is not set (AGENTS.md §2); stopped, nothing marked')
                print('STAGE FAIL', path, e, flush=True); continue
            except Exception as e:
                print('STAGE FAIL', path, e, flush=True); continue
            work = os.path.join(STAGE, hashlib.md5(path.encode()).hexdigest()[:12] + '.work.pdf')
            if src != work: subprocess.run(['cp', src, work], check=True)
            if staged: os.remove(src)
            futs[ex.submit(analyse, path, work, jobs)] = (path, m0)
            while futs and (len(futs) >= min(workers, governed(workers)) + (1 if workers > 1 else 0) or not room()):
                                                                   # (books in flight: the governed number and one staged
                                                                   # ahead — and a new one only with ≥ 3 GB free)
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
    touched = False                                   # nothing written to the phone yet
    try:
        if not r.get('dst'):
            mark(f'skip: {r["decision"]}' + (f'; residual tilt {r["residual"][:5]}' if r.get('residual') else ''))
            print('skip', path[:80], '|', r['decision'][:60], flush=True); return
        dst = r['dst']; n0 = os.path.getsize(src); n1 = os.path.getsize(dst); m1 = md5_file(dst)
        tail = open(dst, 'rb').read()[n0:]
        with Phone() as ph:
            try: now = ph.md5(path)
            except ftplib.error_perm:                 # renamed during the analysis: its new name, same bytes
                new = follow(path)
                if new == path: raise
                now = ph.md5(new); print('MOVED', path[:60], '→', new[:60], flush=True); path = new
            if now != m0: raise RuntimeError('the phone file changed meanwhile')
            try:
                touched = True
                ph.append(path, tail)
                ok = ph.size(path) == n1 and ph.md5(path) == m1
            except Exception as e:
                ok = False; print('APPEND ERROR', path, e, flush=True)
            if not ok:                                # put the original back, at once, and prove it
                ph.put(path, src)
                back = ph.md5(path) == m0
                raise RuntimeError('append not verified; original restored' + ('' if back else ' — RESTORE NOT VERIFIED'))
        json.dump(r['recipe'], open(os.path.join(RECIPES, m0 + '.json'), 'w'), ensure_ascii=False)
        log_change(path, f'book_crop {r["decision"]} (lossless): gain {r["gain"]}, pages turned {r["turned"]}, shrunk to the book size {r["scaled"]}, '
                         f'on blank paper {r["bands"]}, marginal notes kept {r["notes"]}, clean margins {r["clean"]}; '
                         f'original {n0} B md5 {m0}; appended {n1 - n0} B → md5 {m1}', batch)
        set_index_size(path, n1)
        mark(f'cropped {n0}->{n1}')
        print('CROPPED', path[:80], '| gain', r['gain'], '| turned', r['turned'], '| shrunk to fit', r['scaled'], flush=True)
    except Exception as e:
        if not touched and isinstance(e, OSError):    # the phone was away before anything was written: not done, retried
            print('RETRY LATER (phone away)', path, e, flush=True)   # in a later batch (2026-10-11: «No route to host»)
        else:
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
        j = int(sys.argv[sys.argv.index('--jobs') + 1]) if '--jobs' in sys.argv else 1
        main(sys.argv[1], sys.argv[2], w, j)
