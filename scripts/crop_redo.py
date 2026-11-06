"""Redo the crop of books cropped by an earlier version of scripts/book_crop.py (owner 2026-10-15, after his review of
crop-review-002/004: «you should be mature enough now to handle all this … Go ahead»). Per book (a phone path under Books/):
  1. the original bytes: the latest logged crop of the book (under any of its earlier names) gives the original size and
     MD5; the phone file must still be the cropped file that crop wrote (its logged MD5) — else the book is left alone; the
     laptop's copy when its MD5 is the original's, else the phone file truncated to the original size (a crop is an
     appended revision), checked against the original MD5;
  2. the method as it is now (crop_batch.analyse: book_crop.plan + apply, sample sheets for the review page);
  3. the new file = the original + the new revision, or the original alone when the method now leaves the book as it is
     (logged «crop undone»); uploaded beside the old one as «<name>.redo», checked on the phone (size + MD5), the old file
     deleted and the new one renamed into its place, checked again — a dropped connection never leaves a damaged book;
     each attempt reads first where the last one stopped (put_in_place), and a phone away — out of the house, its FTP
     app stopped — pauses the run until it answers again (wait_phone, 2026-10-29: a connection lost mid-upload marked
     the book failed for good and could leave «<name>.redo» in Books/; a phone away made the run walk the whole list);
  4. logged in data/changes/changes.tsv (action «crop», reason «redo …»), the recipe kept, index-now.tsv size updated,
     data/crop/redo-done.tsv (resumable). The earlier sample sheets are kept in crop-sheets-v1/.
  --remote (owner 2026-11-04 «optimize for speed … more powerful CPU/memory (cloud)»): step 2 runs on the cloud VM
     (VM_NAME in VM_ZONE, scripts/crop_remote.py there), N books at once (default 14 — its 16 processors); the laptop
     stages, uploads each original to it (paced, one bulk transfer at a time with the phone's: §7.9), gets back the new
     revision's bytes and the review sheets, and does steps 3–4 as before. The VM away (a spot VM stopped by Google) pauses
     the run and starts it again (wait_vm).
Usage: python3 scripts/crop_redo.py --list-all OUT.tsv          (every book cropped and not undone, current paths)
       python3 scripts/crop_redo.py LIST.tsv BATCH [--workers N] [--dry] [--remote]   (--dry: everything but the phone write)"""
import csv, hashlib, io, itertools, json, os, shlex, shutil, subprocess, sys, tarfile, threading, time, ftplib
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
import crop_batch as cb
J = lambda *p: os.path.join(ROOT, *p)
DONE = J('data', 'crop', 'redo-done.tsv')
LOCAL_MAP = os.path.expanduser('~/.cache/phone-library/local-map.tsv')

def crops():
    """{phone path at crop time: (original size, original md5, cropped md5)} — the latest crop row of each path; a path
    whose latest row is an undo maps to None"""
    out = {}
    for r in csv.reader(open(cb.LOG, encoding='utf-8'), delimiter='\t'):
        if len(r) > 4 and r[1] == 'crop':
            p = r[2].removeprefix('Books/'); why = r[4]
            if why.startswith('crop undone'): out[p] = None; continue
            if 'original ' not in why: continue
            try:
                n0 = int(why.split('original ')[1].split(' B')[0]); m0 = why.split('md5 ')[1].split(';')[0].strip()
                m1 = why.rsplit('→ md5 ', 1)[1].split()[0].strip() if '→ md5 ' in why else None
            except (IndexError, ValueError): continue
            out[p] = (n0, m0, m1)
    return out

def logged(path, table, back):
    for name in cb.names_of(path, back):
        if name in table: return table[name]
    return None

def list_all(out_tsv):
    table = crops(); fwd, back = cb.moves()
    idx = {l.split('\t')[0] for l in open(J('data', 'phone', 'index-now.tsv'), encoding='utf-8') if l.strip()}
    rows = []
    def follow(p):                                    # the logged moves, read once
        seen = set()
        while p in fwd and p not in seen: seen.add(p); p = fwd[p]
        return p
    for p, v in table.items():
        if not v: continue
        now = p if p in idx else follow(p)            # follow the moves only while the path is missing (an older file of the
        if now in idx: rows.append(now)               # same name may have moved away long before this book got it)
    rows = sorted(set(rows))
    open(out_tsv, 'w', encoding='utf-8').write('\n'.join(rows) + '\n'); print(len(rows), 'books cropped and not undone')

LOST = (OSError, EOFError, ftplib.error_temp)       # a connection lost or refused for now: the phone away, not the book

def wait_phone(why):
    """until the phone's FTP answers again: its known addresses every minute, the whole network every ten (phone_host);
    said once every half hour. A phone away — out of the house, its FTP app stopped — pauses the run where it is"""
    import phone_host
    for t in itertools.count():
        hosts = dict.fromkeys(h for h in (cb._HOST, phone_host.HOST, *phone_host.CANDIDATES) if h)
        h = next((x for x in hosts if phone_host._answers(x)), None) or (phone_host.find() if t % 10 == 9 else None)
        if h: cb._HOST = h; return h
        if t % 30 == 0: print(time.strftime('%F %T'), f'phone away ({why}): waiting for it', flush=True)
        time.sleep(60)

# ---- the cloud VM (--remote) ----
VM_NAME, VM_ZONE, VM_USER = (os.environ.get('CROP_VM', 'crop-vm'), os.environ.get('CROP_VM_ZONE', 'europe-southwest1-b'),
                             os.environ.get('CROP_VM_USER', 'k'))
VM_PROJ = [f'--project={os.environ["CROP_VM_PROJECT"]}'] if os.environ.get('CROP_VM_PROJECT') else []   # (a VM in another
VM_KEY = os.path.expanduser('~/.ssh/google_compute_engine')                                                  # gcloud project, 2026-11-06)
VM_REPO = 'phone-library'                             # the repo copy in the VM user's home
VM_DATA = ['data/crop/owner-turns.tsv', 'data/crop/owner-pages.tsv', 'data/changes/changes.tsv', 'data/phone/index-now.tsv']
VM = None                                             # «user@address» once --remote has found it
class _Net:
    """bulk transfers, the phone's and the VM's: one at a time (AGENTS.md §7.9), but NET_HOTSPOT (3) at once on the phone's
    own hotspot, where no one else's network can lag and one ssh stream over 4G leaves most of the link idle (owner
    2026-11-05 «yes»). The phone's own transfers stay one at a time anyway: cb.Phone holds /tmp/phone-ftp.lock throughout.
    The network is looked at on every acquire (the pacer re-checks it every 30 s): back home it is one again."""
    def __init__(self): self.c = threading.Condition(); self.n = 0
    def limit(self):
        p = cb.pacer(); return NET_HOTSPOT if getattr(p, 'hotspot', False) and not getattr(p, 'on', True) else 1
    def __enter__(self):
        with self.c:
            while self.n >= self.limit(): self.c.wait(5)
            self.n += 1
    def __exit__(self, *a):
        with self.c: self.n -= 1; self.c.notify_all()
NET_HOTSPOT = int(os.environ.get('NET_HOTSPOT', '3'))
NET = _Net()
STAGE_GB = float(os.environ.get('STAGE_GB', '6'))     # (§7.5: the staged originals waiting for the VM, at most this much)
BC = None                                             # book_crop.py's MD5: the VM must run the same

def vm_address():
    r = subprocess.run(['gcloud', 'compute', 'instances', 'describe', VM_NAME, f'--zone={VM_ZONE}', *VM_PROJ,
                        '--format=value(status,networkInterfaces[0].accessConfigs[0].natIP)'], capture_output=True, text=True, timeout=120)
    if r.returncode: raise RuntimeError(f'gcloud: {r.stderr.strip()[:200]}')
    st, ip = (r.stdout.split() + ['', ''])[:2]
    return st, ip

def ssh_args():
    return ['ssh', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=20', '-o', 'ServerAliveInterval=30', '-o', 'ServerAliveCountMax=4',
            '-o', 'StrictHostKeyChecking=accept-new', '-i', VM_KEY, VM]

def ssh(cmd, data=None, timeout=900):
    """one command on the VM → its output (bytes); ConnectionError when ssh itself fails (exit 255: the VM away)"""
    try: r = subprocess.run(ssh_args() + [cmd], input=data, capture_output=True, timeout=timeout)
    except subprocess.TimeoutExpired: raise ConnectionError(f'ssh timed out after {timeout} s: {cmd[:80]}')
    if r.returncode == 255: raise ConnectionError(f'ssh: {r.stderr.decode(errors="replace").strip()[:200]}')
    if r.returncode: raise RuntimeError(f'on the VM: {cmd[:100]} → exit {r.returncode}: {r.stderr.decode(errors="replace").strip()[-300:]}')
    return r.stdout

VM_WAIT = threading.Lock()

def wait_vm(why):
    """until the VM answers again; a spot VM stopped by Google is started again (its address may change). One thread
    waits, the others behind it find the VM back at once"""
    with VM_WAIT: _wait_vm(why)

def _wait_vm(why):
    global VM
    for t in itertools.count():
        try: ssh('true', timeout=60); return
        except (ConnectionError, RuntimeError): pass
        if t % 5 == 0:
            try:
                st, ip = vm_address()
                if ip: VM = f'{VM_USER}@{ip}'
                if st in ('TERMINATED', 'STOPPED'):
                    print(time.strftime('%F %T'), f'VM {VM_NAME} {st} ({why}): starting it again', flush=True)
                    subprocess.run(['gcloud', 'compute', 'instances', 'start', VM_NAME, f'--zone={VM_ZONE}', *VM_PROJ], capture_output=True, timeout=600)
                    continue
            except Exception as e: print(time.strftime('%F %T'), 'gcloud:', repr(e)[:160], flush=True)
        if t % 30 == 0: print(time.strftime('%F %T'), f'VM away ({why}): waiting for it', flush=True)
        time.sleep(60)

def sync_vm():
    """the scripts and the data analyse reads, to the VM's repo copy; the same book_crop.py or nothing runs"""
    global VM, BC
    st, ip = vm_address()
    if st in ('TERMINATED', 'STOPPED'):              # (stopped when idle, or by Google: started for the run)
        print(time.strftime('%F %T'), f'VM {VM_NAME} {st}: starting it', flush=True)
        subprocess.run(['gcloud', 'compute', 'instances', 'start', VM_NAME, f'--zone={VM_ZONE}', *VM_PROJ], capture_output=True, timeout=600)
        for _ in range(20):
            st, ip = vm_address()
            if st == 'RUNNING' and ip:
                VM = f'{VM_USER}@{ip}'
                try: ssh('true', timeout=60); break
                except (ConnectionError, RuntimeError): pass
            time.sleep(15)
    if st != 'RUNNING' or not ip: raise SystemExit(f'VM {VM_NAME} is {st}: start it first (gcloud compute instances start {VM_NAME} --zone={VM_ZONE})')
    VM = f'{VM_USER}@{ip}'
    rsh = ' '.join(shlex.quote(x) for x in ssh_args()[:-1])
    for src, dst, extra in ((J('scripts') + '/', f'{VM}:{VM_REPO}/scripts/', ['--delete', '--exclude=__pycache__']),
                            (None, f'{VM}:{VM_REPO}/', ['--relative'])):
        cmd = ['rsync', '-a', '-e', rsh, *extra] + ([src] if src else [f'./{p}' for p in VM_DATA]) + [dst]
        r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=1800)
        if r.returncode: raise SystemExit(f'rsync to the VM failed: {r.stderr.strip()[:300]}')
    BC = cb.md5_file(J('scripts', 'book_crop.py'))
    there = ssh(f'md5sum {VM_REPO}/scripts/book_crop.py').decode().split()[0]
    if there != BC: raise SystemExit(f'book_crop.py on the VM ({there}) is not the laptop\'s ({BC})')
    print(f'VM {VM_NAME} at {ip}: scripts and data synced, book_crop {BC[:10]}', flush=True)
    cb.pacer()                                        # (one pacer for every thread: made here, before them)

def vm_put(local, remote):
    """the file to the VM (written as «.part», renamed when whole), paced like the phone's transfers and alone on the network"""
    q = shlex.quote(remote)
    with NET:
        p = subprocess.Popen(ssh_args() + [f'mkdir -p "$(dirname {q})" && cat > {q}.part && mv {q}.part {q}'], stdin=subprocess.PIPE,
                             stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        pc = cb.pacer()
        try:
            with open(local, 'rb') as f:
                for b in iter(lambda: f.read(1 << 16), b''): p.stdin.write(b); pc.wait(len(b))
            p.stdin.close()
        except BrokenPipeError: pass
        rc = p.wait(); err = p.stderr.read().decode(errors='replace').strip()
    if rc: raise ConnectionError(f'upload to the VM failed (exit {rc}): {err[:200]}')

def remote_analyse(path, work, m0):
    """crop_batch.analyse on the VM → its dict with the laptop's paths: the new file = the original + the revision's bytes
    fetched back (checked against the VM's MD5), the review sheets copied into the laptop's crop-sheets folder"""
    hx = path.encode('utf-8').hex(); h = hashlib.md5(path.encode()).hexdigest()[:12]
    d = f'redo/{h}-{m0[:10]}-{BC[:10]}'; tool = f'python3 -I {VM_REPO}/scripts/crop_remote.py'
    n0 = os.path.getsize(work); uploaded = False; again = 0
    while True:
        try:
            s = ssh(f'mkdir -p {d} && {tool} start {d} {hx} {m0}').decode().strip()
            if s == 'nosrc':
                if uploaded: raise RuntimeError('the original on the VM is not the staged one after its upload')
                vm_put(work, f'{d}/src.pdf'); uploaded = True; continue
            while s in ('started', 'running'):
                s = ssh(f'{tool} wait {d} 600', timeout=900).decode().strip()
            if s == 'none':                           # (the VM was stopped mid-analysis: started again — three times at
                again += 1                            # most: an analysis killed with no word, e.g. out of memory)
                if again > 3: ssh(f'{tool} clean {d} {hx}'); raise RuntimeError('the analysis on the VM ended 4 times with no result')
                continue
            if s == 'error':
                err = ssh(f'cat {d}/error.txt; {tool} clean {d} {hx} >/dev/null').decode(errors='replace')
                raise RuntimeError('on the VM: ' + err.strip().splitlines()[-1][:300] if err.strip() else 'on the VM: failed')
            out = json.loads(ssh(f'cat {d}/out.json'))
            for l in (out.pop('log', '') or '').splitlines():
                if l.strip(): print('  VM |', l[:200], flush=True)
            if out.get('n0') != n0: raise RuntimeError(f'the VM analysed {out.get("n0")} B, not the staged {n0} B')
            new = work
            if out.get('dst'):
                with NET: tail = ssh(f'tail -c +{n0 + 1} {d}/src.cropped.pdf', timeout=3600)
                new = work[:-4] + '.cropped.pdf'
                shutil.copyfile(work, new)
                with open(new, 'ab') as f: f.write(tail)
            if os.path.getsize(new) != out['n1'] or cb.md5_file(new) != out['m1']:
                raise RuntimeError(f'the new file rebuilt here is not the VM\'s (size {os.path.getsize(new)} vs {out["n1"]})')
            sheets = ssh(f'cd .cache/phone-library/crop-sheets 2>/dev/null && [ -d {h} ] && tar -cf - {h} || true')
            if sheets:
                shutil.rmtree(os.path.join(cb.SHEETS, h), ignore_errors=True)
                with tarfile.open(fileobj=io.BytesIO(sheets)) as t: t.extractall(cb.SHEETS, filter='data')
            ssh(f'{tool} clean {d} {hx}')
            out.update(src=work, dst=new if out.get('dst') else None)
            return out
        except ConnectionError as e:
            print('VM LOST', path[:80], repr(e)[:160], flush=True); wait_vm('analysis')

def staged_gb():
    try: return sum(e.stat().st_size for e in os.scandir(cb.STAGE) if e.is_file()) / 2 ** 30
    except OSError: return 0.0

def md5_of(ph, path):
    """the phone file's MD5, or None when there is no such file"""
    try: return ph.md5(path)
    except ftplib.error_perm as e:
        if str(e).startswith('550'): return None
        raise

def put_in_place(path, new, n1, m1, m_old, tries=5):
    """the new file (n1 bytes, md5 m1) into the place of the phone file m_old, safe against a connection lost at any step:
    uploaded beside it as «<name>.redo», checked (size + MD5), the old file deleted, the new one renamed into its place and
    checked again. Each attempt reads first where the last one stopped — the new file in place already (renamed), only at
    «.redo» (the old one deleted: renamed now), or the old file still there (uploaded again) — and a lost connection waits
    for the phone before the next. Raises on anything else (the phone file changed meanwhile, an upload not verified)"""
    tmp = path + '.redo'
    for attempt in range(1, tries + 1):
        try:
            with cb.Phone() as ph:
                now = md5_of(ph, path)
                if now == m1: pass                     # (an earlier attempt got as far as the rename)
                elif now is None:
                    if md5_of(ph, tmp) != m1: raise RuntimeError('the book is gone from the phone and no checked «.redo» copy is there')
                    ph.f.rename('Books/' + tmp, 'Books/' + path)
                elif now != m_old: raise RuntimeError('the phone file changed meanwhile')
                else:
                    with NET: ph.put(tmp, new)
                    if ph.size(tmp) != n1 or ph.md5(tmp) != m1:
                        ph.f.delete('Books/' + tmp); raise RuntimeError('upload not verified (the old file is untouched)')
                    ph.f.delete('Books/' + path)
                    ph.f.rename('Books/' + tmp, 'Books/' + path)
                if md5_of(ph, path) != m1: raise RuntimeError('RENAMED FILE NOT VERIFIED — check ' + path)
                return
        except LOST as e:
            print(f'PHONE LOST during the upload (attempt {attempt})', path[:80], repr(e)[:120], flush=True)
            if attempt < tries: wait_phone('upload')
    raise RuntimeError(f'the upload did not finish in {tries} attempts (each after the phone came back)')

def stage(path, n0, m0, m1):
    """the original bytes in the staging folder (a copy: the worker writes beside it)"""
    work = os.path.join(cb.STAGE, hashlib.md5(path.encode()).hexdigest()[:12] + '.work.pdf')
    local = dict(l.rstrip('\n').split('\t')[:2] for l in open(LOCAL_MAP, encoding='utf-8')) if os.path.exists(LOCAL_MAP) else {}
    with cb.Phone() as ph: now = ph.md5(path)
    if m1 and now != m1: raise RuntimeError(f'the phone file is not the one the crop wrote (md5 {now} ≠ {m1})')
    lp = local.get(path)
    if lp and os.path.exists(lp) and os.path.getsize(lp) == n0 and cb.md5_file(lp) == m0:
        shutil.copyfile(lp, work); return work, now
    with cb.Phone() as ph, NET: ph.get(path, work)
    if os.path.getsize(work) < n0: raise ConnectionError(f'the download stopped short ({os.path.getsize(work)} of ≥ {n0} B)')
    with open(work, 'r+b') as f: f.truncate(n0)
    if cb.md5_file(work) != m0: os.remove(work); raise RuntimeError('the truncated phone file is not the original')
    return work, now

DRY = False

def finish(fu, meta, batch):
    path, n0, m0, m_old = meta
    try: r = fu.result()
    except Exception as e: print('ANALYSE FAIL', path, repr(e)[:200], flush=True); return
    src = r['src']; new = r.get('dst') or src
    def mark(result):
        with open(DONE, 'a', encoding='utf-8') as f: f.write(f'{path}\t{m0}\t{result}\n')
    try:
        n1 = os.path.getsize(new); m1 = cb.md5_file(new)
        with open(new, 'rb') as f:
            if f.read(n0) != open(src, 'rb').read(n0): raise RuntimeError('the new file does not start with the original bytes')
        if m1 == m_old: mark('same as before'); print('SAME', path[:80], flush=True); return
        if DRY:
            print('DRY', r['decision'][:60], path[:70], '| would upload', n1, 'B (was', os.path.getsize(src), '+ old revision)', flush=True); return
        put_in_place(path, new, n1, m1, m_old)
        if r.get('dst'):
            import json
            json.dump(r['recipe'], open(os.path.join(cb.RECIPES, m0 + '.json'), 'w'), ensure_ascii=False)
            cb.log_change(path, f'book_crop {r["decision"]} (lossless), redo with the corrected method: gain {r["gain"]}, pages turned {r["turned"]}, '
                                f'shrunk to the book size {r["scaled"]}; original {n0} B md5 {m0}; appended {n1 - n0} B → md5 {m1}', batch)
            mark(f'redone {n0}->{n1}'); print('REDONE', path[:80], '| gain', r['gain'], '| turned', r['turned'], flush=True)
        else:
            cb.log_change(path, f'crop undone: back to the original ({n0} B md5 {m0}) — the corrected method leaves it as it is: {r["decision"][:120]}', batch)
            mark('original restored'); print('RESTORED', path[:80], '|', r['decision'][:80], flush=True)
        cb.set_index_size(path, n1)
    except Exception as e:                            # (a refused login: not marked, the book is done in a later run)
        if str(e).startswith('530'): print('RETRY LATER (login refused — AGENTS.md §2)', path, e, flush=True); return 'later'
        mark(f'FAIL {e}'); print('FAIL', path, e, flush=True)
    finally:
        for p in {src, r.get('dst')}:
            if p and os.path.exists(p): os.remove(p)

def main(list_tsv, batch, workers=3, remote=False):
    if remote: sync_vm()
    table = crops(); fwd, back = cb.moves()
    idx = {l.split('\t')[0] for l in open(J('data', 'phone', 'index-now.tsv'), encoding='utf-8') if l.strip()}
    def follow(p):                                    # ONLY a path no longer on the phone is followed, to the first path
        seen = set()                                  # of its chain that is (the log also holds the crop's own swaps:
        while p not in idx and p in fwd and p not in seen: seen.add(p); p = fwd[p]   # original → «نسخ مستبعدة/__المستبدل»
        return p                                      # — followed blindly, 739 books led to their set-aside originals)
    done = {l.split('\t')[0] for l in open(DONE, encoding='utf-8')} if os.path.exists(DONE) else set()
    # (each book at its CURRENT path — a rename or a move since the list was made, e.g. the naming pass, is followed
    # through the change log; else the phone has no such file and the book would be skipped for good)
    paths = [follow(l.strip()) for l in open(list_tsv, encoding='utf-8') if l.strip() and not l.startswith('#')]
    paths = [p for p in paths if not any(n in done for n in cb.names_of(p, back))]   # (done under any of its names)
    print(f'{len(paths)} books to redo', flush=True)
    v1 = cb.SHEETS + '-v1'; os.makedirs(v1, exist_ok=True); later = []
    with (ThreadPoolExecutor(workers) if remote else ProcessPoolExecutor(workers)) as ex:
        futs = {}
        def fin(fu):
            meta = futs.pop(fu)
            if finish(fu, meta, batch) == 'later': later.append(meta[0])
        for path in paths:
            if not cb.os.path.exists(cb.STAGE): os.makedirs(cb.STAGE, exist_ok=True)
            lg = logged(path, table, back)
            if not lg: print('NOT CROPPED', path, flush=True); continue
            n0, m0, m1 = lg
            work = err = None; lost = 0
            while work is None and err is None:       # (the phone away: the run waits here for it, then stages this book
                try: work, now = stage(path, n0, m0, m1)   # again — it used to walk the rest of the list, a network scan
                except ftplib.error_perm as e:        # for each book, and start over two minutes later)
                    if str(e).startswith('530'): raise SystemExit(f'FTP login refused ({e}) — the login is not set (AGENTS.md §2); nothing marked, rerun later')
                    err = e
                except LOST as e:
                    lost += 1; print('PHONE AWAY while staging', path[:80], repr(e)[:120], flush=True)
                    if lost >= 5: print('RETRY LATER (lost 5 times while staging)', path, flush=True); later.append(path); break
                    wait_phone('staging')
                except Exception as e: err = e
            if err is not None:
                with open(DONE, 'a', encoding='utf-8') as f: f.write(f'{path}\t{m0}\tSKIP {err}\n')
                print('SKIP', path, err, flush=True)
            if work is None: continue
            sh = os.path.join(cb.SHEETS, hashlib.md5(path.encode()).hexdigest()[:12])
            if os.path.isdir(sh) and not os.path.exists(os.path.join(v1, os.path.basename(sh))): shutil.move(sh, v1)
            if remote: futs[ex.submit(remote_analyse, path, work, m0)] = (path, n0, m0, now)
            else: futs[ex.submit(cb.analyse, path, work, 1)] = (path, n0, m0, now)
            while futs and ((len(futs) >= workers + 1 or staged_gb() > STAGE_GB) if remote else   # (the VM: N at once, one staged
                            (len(futs) >= min(workers, cb.governed(workers)) + 1 or not cb.room())):   # ahead) the governor's number,
                                                                   # one staged ahead; a new book only with ≥ 3 GB free
                for fu in as_completed(list(futs)): fin(fu); break
        for fu in as_completed(list(futs)): fin(fu)
    if later:                                         # (books not done and not marked — the run ends «not finished», so
        print(f'{len(later)} books left for later', flush=True)   # run_resumable.sh runs it again for them)
        sys.exit(3)

if __name__ == '__main__':
    a = sys.argv[1:]
    if '--dry' in a: DRY = True; a.remove('--dry'); DONE = DONE + '.dry'
    remote = '--remote' in a
    if remote: a.remove('--remote')
    if a and a[0] == '--list-all': list_all(a[1])
    else: main(a[0], a[1], int(a[a.index('--workers') + 1]) if '--workers' in a else (14 if remote else 3), remote)
