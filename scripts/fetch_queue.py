#!/usr/bin/env python3
"""Unified, resumable download → verify → upload pipeline (AGENTS.md §7).

Input: a TSV queue  `url<TAB>size<TAB>target<TAB>reason`  (size 0 = unknown; url `file:///abs/path` = a file already
  downloaded and checked: verified, uploaded, then deleted).
  target `Books/...`        → uploaded to the phone (phone:Books/...), staged copy deleted after upload
  target `local:<path>`     → saved under ~/Books/<path> (no phone involved)
  url `phone:Books/...`     → copied FROM the phone (target must be local:)

Stages run concurrently:
  * downloads: DL_JOBS files at once (default 12), each with aria2c -x8 -s8 (resume with --continue)
  * verify: %PDF magic, exact size, %%EOF tail, pdfinfo opens it
  * phone I/O: ONE thread, serialized across ALL processes by an flock on /tmp/phone-ftp.lock
    (the phone FTP server takes one connection: --checkers=1 --transfers=1)
Staged bytes are capped (STAGE_GB, default 6) because the laptop disk is small.
State: data/queue/<queue name>.done (one target per line) → rerun to resume.
Usage: python3 scripts/fetch_queue.py QUEUE.tsv PLAN_NAME
"""
import csv, fcntl, hashlib, os, queue, subprocess, sys, threading, time
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J = lambda p: os.path.join(ROOT, p)
QFILE, PLAN = sys.argv[1], sys.argv[2]
DL_JOBS = int(os.environ.get('DL_JOBS', 12))
CONN = os.environ.get('CONN', '8')
STAGE_MAX = float(os.environ.get('STAGE_GB', 6)) * 1e9
NET_MB = float(os.environ.get('NET_MB', 3))          # total internet download cap in MB/s (0 = none); see AGENTS §7.8
PHONE_BW = os.environ.get('PHONE_BW', '6M')          # rclone --bwlimit for phone uploads (Wi-Fi shared)
LOCAL_BOOKS = os.path.expanduser('~/Books')
STAGE = J('downloads/queue'); os.makedirs(STAGE, exist_ok=True); os.makedirs(J('data/queue'), exist_ok=True)
DONE_F = J('data/queue/' + os.path.basename(QFILE).rsplit('.', 1)[0] + '.done')
done = set(open(DONE_F).read().split('\n')) if os.path.exists(DONE_F) else set()
lock = threading.Lock(); staged = [0]; stats = {'ok': 0, 'bad': 0, 'skip': 0}
stage_cv = threading.Condition()
upq = queue.Queue()
log = open(J('data/changes/changes.tsv'), 'a', newline=''); logw = csv.writer(log, delimiter='\t')
bad = open(J('data/queue/' + os.path.basename(QFILE).rsplit('.', 1)[0] + '.failed'), 'a')

class PhoneLock:
    def __enter__(self):
        self.f = open('/tmp/phone-ftp.lock', 'w'); fcntl.flock(self.f, fcntl.LOCK_EX)
    def __exit__(self, *a):
        fcntl.flock(self.f, fcntl.LOCK_UN); self.f.close()

RC = ['--checkers=1', '--transfers=1', '--ftp-concurrency', '1', '--inplace', '-q', '--retries', '5', '--bwlimit', PHONE_BW]

def ok_pdf(p, size):
    try:
        n = os.path.getsize(p)
        if size and n != size: return f'size {n}≠{size}'
        with open(p, 'rb') as f:
            if f.read(4) != b'%PDF': return 'not %PDF'
            f.seek(max(0, n - 2048)); 
            if b'%%EOF' not in f.read(): return 'no %%EOF'
        if subprocess.run(['pdfinfo', p], capture_output=True).returncode: return 'pdfinfo fails'
    except OSError as e: return str(e)
    return None

def done_mark(target, reason, url):
    with lock:
        done.add(target); open(DONE_F, 'a').write(target + '\n')
        logw.writerow([time.strftime('%F %T'), 'add', url, target, reason, PLAN]); log.flush()
        stats['ok'] += 1
        print(f"[{stats['ok']} ok/{stats['bad']} bad] {target[-110:]}", flush=True)

def fail(target, why):
    with lock:
        stats['bad'] += 1; bad.write(f'{target}\t{why}\n'); bad.flush(); print('FAIL', why, target[-90:], flush=True)

def phone_worker():
    while True:
        item = upq.get()
        if item is None: return
        kind, src, dst, size, reason, url = item
        with PhoneLock():
            if kind == 'up':
                parent_dir = os.path.dirname('phone:' + dst)
                subprocess.run(['rclone', 'mkdir', parent_dir] + RC, capture_output=True)
                r = subprocess.run(['rclone', 'copyto', src, 'phone:' + dst] + RC, capture_output=True, text=True)
            else:
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                r = subprocess.run(['rclone', 'copyto', src, dst + '.part'] + RC, capture_output=True, text=True)
        if r.returncode:
            fail(dst, 'rclone ' + r.stderr[-150:])
            if os.path.exists(dst + '.part'):
                try: os.remove(dst + '.part')
                except OSError: pass
        elif kind == 'up':
            done_mark(dst, reason, url); 
        else:
            why = ok_pdf(dst + '.part', size)
            if why:
                fail(dst, why)
                if os.path.exists(dst + '.part'):
                    try: os.remove(dst + '.part')
                    except OSError: pass
            else:
                try:
                    os.rename(dst + '.part', dst)
                    done_mark('local:' + os.path.relpath(dst, LOCAL_BOOKS), reason, url)
                except OSError as e:
                    fail(dst, f'rename fail: {e}')
        if kind == 'up':
            if os.path.exists(src):
                try: os.remove(src)
                except OSError: pass
            with stage_cv: staged[0] -= size or 0; stage_cv.notify_all()
        upq.task_done()

def archive_mirrors(url):
    """https://archive.org/download/<item>/<file> → the same file on each of the item's storage servers
    (https://<server><dir>/<file>); archive.org's own redirect sometimes lands on a node that answers HTTP 500."""
    import json, urllib.parse, urllib.request
    item, _, f = url.split('/download/', 1)[1].partition('/')
    try:
        m = json.load(urllib.request.urlopen(f'https://archive.org/metadata/{item}', timeout=60))
    except Exception:
        return []
    return [f'https://{s}{m["dir"]}/{f}' for s in (m.get('workable_servers') or [m.get('d1'), m.get('d2')]) if s and m.get('dir')]

def download(row):
    url, size, target, reason = row[0], int(row[1] or 0), row[2], row[3] if len(row) > 3 else ''
    if 'سلسلة عالم المعرفة (المجلس الوطني للثقافة - الكويت)' in target and 'الأعداد ' not in target:
        import re
        fname = posixpath.basename(target)
        m = re.match(r'^(\d+)', fname)
        if m:
            num = int(m.group(1))
            start = ((num - 1) // 100) * 100 + 1
            bucket = f'الأعداد {start:03d} - {start+99:03d}'
            dname = posixpath.dirname(target)
            target = posixpath.join(dname, bucket, fname)
    if target in done: stats['skip'] += 1; return
    if url.startswith('phone:'):
        upq.put(('down', url, os.path.join(LOCAL_BOOKS, target[6:]), size, reason, url)); return
    if url.startswith('file://'):         # already downloaded and read (staged for checking): verify, upload, then removed
        src = url[7:]; why = ok_pdf(src, size)
        if why: fail(target, why); return
        with stage_cv: staged[0] += size
        upq.put(('up', src, target, size, reason, url)); return
    to_local = target.startswith('local:')
    out = os.path.join(LOCAL_BOOKS, target[6:]) if to_local else os.path.join(STAGE, hashlib.md5(target.encode()).hexdigest() + '.pdf')
    if to_local and os.path.exists(out) and not ok_pdf(out, size): done_mark(target, reason, url); return
    with stage_cv:
        while not to_local and staged[0] + size > STAGE_MAX and staged[0] > 0: stage_cv.wait()
        if not to_local: staged[0] += size
    os.makedirs(os.path.dirname(out), exist_ok=True)
    lim = [f'--max-download-limit={int(NET_MB * 1e6 / DL_JOBS)}'] if NET_MB else []      # shared home internet (AGENTS §7.8)
    r = subprocess.run(['aria2c', '-q', *lim, '--continue=true', f'-x{CONN}', f'-s{CONN}', '-k1M', '--max-tries=5', '--retry-wait=10',
                        '--allow-overwrite=true', '--auto-file-renaming=false', '-U', 'personal-library/1.0',
                        '-d', os.path.dirname(out), '-o', os.path.basename(out), url], capture_output=True, text=True)
    if r.returncode:                      # some archive.org data nodes refuse parallel ranges (HTTP 500): one plain stream
        if os.path.exists(out): os.remove(out)
        lim_c = ['--limit-rate', str(int(NET_MB * 1e6 / DL_JOBS))] if NET_MB else []
        r = subprocess.run(['curl', '-sfL', '--retry', '5', '--retry-delay', '10', *lim_c, '-A', 'personal-library/1.0', '-o', out, url], capture_output=True, text=True)
        why = f'curl exit {r.returncode}' if r.returncode else ok_pdf(out, size)
        if why and '://archive.org/download/' in url:   # the redirect picked a failing node: try the item's own servers
            for alt in archive_mirrors(url):
                if os.path.exists(out): os.remove(out)
                r = subprocess.run(['curl', '-sfL', '--retry', '3', *lim_c, '-A', 'personal-library/1.0', '-o', out, alt], capture_output=True, text=True)
                why = f'curl exit {r.returncode} (mirrors)' if r.returncode else ok_pdf(out, size)
                if not why: break
    else:
        why = ok_pdf(out, size)
    if why:
        fail(target, why)
        if os.path.exists(out): os.remove(out)
        if not to_local:
            with stage_cv: staged[0] -= size; stage_cv.notify_all()
        return
    if to_local: done_mark(target, reason, url)
    else: upq.put(('up', out, target, size, reason, url))

rows = [r for r in csv.reader(open(QFILE), delimiter='\t') if r and not r[0].startswith('#')]
print(f'{len(rows)} items, {len([r for r in rows if r[2] in done])} already done; {DL_JOBS} downloads × {CONN} connections, 1 phone connection', flush=True)
pw = threading.Thread(target=phone_worker, daemon=True); pw.start()
with ThreadPoolExecutor(DL_JOBS) as ex: list(ex.map(download, rows))
upq.put(None); pw.join()
print('DONE', stats, flush=True)
