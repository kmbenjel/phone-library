"""Download replacement PDFs from archive.org (via their Waqfeya records) and upload them to the phone.
Input: data/phone/downloads.json (from the replacement planning step). Each file: download -> check exact size + %PDF -> upload.
Every added file is logged in data/changes/changes.tsv (action 'add', with the source URL)."""
import csv, json, os, re, subprocess, sys, time, urllib.parse
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from rename_plan import canonical_folder, vol_from_orig, clean, fit, short_title, author_short
from label_numbering_plan import parse
J = lambda p: os.path.join(ROOT, p)
books = {}
for fn in ('data/waqfeya/books.jsonl', 'data/waqfeya/details.jsonl', 'data/waqfeya/details2.jsonl'):
    for l in open(J(fn)):
        d = json.loads(l); books[d['_id']] = {**books.get(d['_id'], {}), **d}
link = {}
for b in books.values():
    for x in b.get('links') or []:
        m = re.search(r'archive\.org/download/([^/]+)/(.+?)\s*$', x.get('url', ''))
        if m: link[(m.group(1), urllib.parse.unquote(m.group(2)))] = x['title']
todo = json.load(open(J('data/phone/downloads.json')))
os.makedirs(J('downloads'), exist_ok=True)
done = {r[3] for r in csv.reader(open(J('data/changes/changes.tsv')), delimiter='\t') if r and r[1] == 'add' and r[5] == '021-replacements'}
jobs = []; seen = set()
for t in todo:                                   # 1. decide every file's destination name up front
    wid = t['waqfeya_id']
    if wid in seen: continue
    seen.add(wid); b = books[wid]
    sec = t['folder'].split('/')[0]
    canon, title, a = canonical_folder(b)
    dest = t['folder'] if t['mode'] == 'missing volumes' else f'{sec}/{canon}'
    short = clean(short_title(title, a))
    files = sorted(t['download'], key=lambda f: f['name'])
    main_count = sum(1 for f in files if (vol_from_orig(f['name']) or (1, 'vol'))[1] == 'vol')
    for f in files:
        lab = link.get((f['item'], f['name']), '')
        pr = parse(lab) if lab else None
        v = vol_from_orig(f['name'])
        if main_count <= 1 and t['mode'] == 'whole book':
            name = fit(title, 180) + (' (الواجهة)' if v and v[1] == 'front' else '') + '.pdf'
        elif pr:
            text = pr[2] or ('الواجهة' if pr[1] == 'front' and not pr[0] else 'المقدمة' if pr[1] == 'front' else '')
            name = f'{pr[0]:02d} - {short}' + (f' ({fit(text, 90)})' if text else '') + '.pdf'
        elif v:
            name = f'{v[0]:02d} - {short}' + (' (الواجهة)' if v == (0, 'front') else ' (المقدمة)' if v[1] == 'front' else '') + '.pdf'
        else:
            name = f'{short} ({clean(re.sub(r"\.pdf$", "", f["name"], flags=re.I))}).pdf'
        target = f'Books/{dest}/{name}'
        if target in done: continue
        url = f'https://archive.org/download/{urllib.parse.quote(f["item"])}/{urllib.parse.quote(f["name"])}'
        local = J(f'downloads/{f["item"]}__{re.sub(r"[^A-Za-z0-9._-]", "_", f["name"])}')
        jobs.append((url, local, f['size'], target, b['name']))
print('files to do:', len(jobs), '| already added:', len(done), flush=True)

import threading
from concurrent.futures import ThreadPoolExecutor
lock = threading.Lock(); stats = {'ok': 0, 'bad': 0}
log = csv.writer(open(J('data/changes/changes.tsv'), 'a', newline=''), delimiter='\t')
uploader = ThreadPoolExecutor(2)                   # the phone's FTP server limits simultaneous logins
def upload(job):
    url, local, size, target, bname = job
    r = subprocess.run(['rclone', 'lsjson', f'phone:{target}'], capture_output=True, text=True)
    if r.returncode == 0 and r.stdout.strip() not in ('', '[]'):
        cur = json.loads(r.stdout)[0].get('Size')
        if cur == size:
            with lock: log.writerow([time.strftime('%F %T'), 'add', '', target, f'replacement from Waqfeya «{bname}»: {url}', '021-replacements']); stats['ok'] += 1
            return
        subprocess.run(['rclone', 'deletefile', f'phone:{target}'], capture_output=True)   # our own cut-off upload
    r = subprocess.run(['rclone', 'copyto', local, f'phone:{target}', '--inplace', '--ftp-concurrency', '1', '-q'], capture_output=True, text=True)
    with lock:
        if r.returncode: print('UPLOAD FAIL', target, r.stderr[-200:], flush=True); stats['bad'] += 1; return
        log.writerow([time.strftime('%F %T'), 'add', '', target, f'replacement from Waqfeya «{bname}»: {url}', '021-replacements']); stats['ok'] += 1
        print('added', target.split('/', 2)[2][:90], flush=True)
def download(job):
    url, local, size, target, bname = job
    if not (os.path.exists(local) and os.path.getsize(local) == size):
        subprocess.run(['curl', '-sL', '--fail', '--retry', '3', '--max-time', '3600', '-A', 'personal-library/1.0', '-o', local, url])
    if os.path.exists(local) and os.path.getsize(local) == size and open(local, 'rb').read(5) == b'%PDF-':
        return uploader.submit(upload, job)
    with lock: print('BAD download', url, flush=True); stats['bad'] += 1
with ThreadPoolExecutor(6) as dl:                  # 2. six parallel downloads from archive.org
    futs = [dl.submit(download, j) for j in jobs]
    ups = [f.result() for f in futs]
for u in ups:
    if u: u.result()
uploader.shutdown(wait=True)
print('uploaded:', stats['ok'], '| failed:', stats['bad'], flush=True)
