#!/usr/bin/env python3
"""Download missing core reference books from Waqfeya / Archive.org and upload to phone.
Logs progress and retries with exponential backoff when Archive.org returns 503 or times out."""
import csv, json, os, re, subprocess, sys, time, urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from report_recommend import CORE, on_phone, best_waqfeya
from rename_plan import canonical_folder, vol_from_orig, clean, fit, short_title, author_short
from label_numbering_plan import parse

J = lambda p: os.path.join(ROOT, p)
PLAN = '046-core-books'
LOG = J('data/changes/changes.tsv')
DOWNLOADS_DIR = J('downloads')
os.makedirs(DOWNLOADS_DIR, exist_ok=True)

books = {}
for fn in ('data/waqfeya/books.jsonl', 'data/waqfeya/details.jsonl', 'data/waqfeya/details2.jsonl'):
    if os.path.exists(J(fn)):
        for l in open(J(fn)):
            d = json.loads(l)
            books[d['_id']] = {**books.get(d['_id'], {}), **d}

missing = []
for d, t, h in CORE:
    b = on_phone(t, h)
    if not b:
        w = best_waqfeya(t, h)
        if w: missing.append((d, t, h, w))

print(f"[{time.strftime('%T')}] Books to fetch ({len(missing)}):", flush=True)
for d, t, h, w in missing:
    print(f" - {d}: {w['name']}", flush=True)

jobs = []
for d, t, h, w in missing:
    b = books[w['waqfeya_id']]
    canon, title, a = canonical_folder(b)
    cat = w['phone_category']
    dest = f"{cat}/{canon}"
    short = clean(short_title(title, a))
    
    links = [lk for lk in b.get('links', []) if lk.get('url', '').strip().lower().endswith('.pdf')]
    main_count = sum(1 for lk in links if (vol_from_orig(lk['url'].rsplit('/', 1)[-1]) or (1, 'vol'))[1] == 'vol')
    
    for lk in links:
        url = lk.get('url', '').strip()
        fname = urllib.parse.unquote(url.rsplit('/', 1)[-1])
        m = re.search(r'archive\.org/download/([^/]+)/(.+?)\s*$', url)
        if not m: continue
        item_id = m.group(1)
        
        pr = parse(lk.get('title', ''))
        v = vol_from_orig(fname)
        
        if main_count <= 1:
            name = fit(title, 180) + (' (الواجهة)' if v and v[1] == 'front' else '') + '.pdf'
        elif pr:
            text = pr[2] or ('الواجهة' if pr[1] == 'front' and not pr[0] else 'المقدمة' if pr[1] == 'front' else '')
            name = f'{pr[0]:02d} - {short}' + (f' ({fit(text, 90)})' if text else '') + '.pdf'
        elif v:
            name = f'{v[0]:02d} - {short}' + (' (الواجهة)' if v == (0, 'front') else ' (المقدمة)' if v[1] == 'front' else '') + '.pdf'
        else:
            name = f'{short} ({clean(re.sub(r"\.pdf$", "", fname, flags=re.I))}).pdf'
            
        target = f'Books/{dest}/{name}'
        local = os.path.join(DOWNLOADS_DIR, f"{item_id}__{re.sub(r'[^A-Za-z0-9._-]', '_', fname)}")
        jobs.append({
            'url': url,
            'local': local,
            'target': target,
            'bname': b.get('name', ''),
            'book_title': title
        })

print(f"[{time.strftime('%T')}] Total files: {len(jobs)}", flush=True)

def download_file(url, local):
    if os.path.exists(local) and os.path.getsize(local) > 1000:
        with open(local, 'rb') as f:
            if f.read(5) == b'%PDF-':
                return True
    
    for attempt in range(1, 15):
        res = subprocess.run([
            'curl', '-sL', '--fail', '--retry', '2', '--max-time', '600',
            '-A', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            '-o', local, url
        ], capture_output=True)
        if res.returncode == 0 and os.path.exists(local) and os.path.getsize(local) > 1000:
            with open(local, 'rb') as f:
                if f.read(5) == b'%PDF-':
                    return True
        wait_s = min(30 * attempt, 180)
        print(f"[{time.strftime('%T')}] Waiting {wait_s}s for archive.org (attempt {attempt}/15)...", flush=True)
        time.sleep(wait_s)
    return False

def upload_file(local, target, bname, url):
    chk = subprocess.run(['rclone', 'lsjson', f'phone:{target}'], capture_output=True, text=True)
    if chk.returncode == 0 and chk.stdout.strip() not in ('', '[]'):
        return True
        
    res = subprocess.run([
        'rclone', 'copyto', local, f'phone:{target}',
        '--inplace', '--ftp-concurrency', '1', '-q'
    ], capture_output=True, text=True)
    
    if res.returncode == 0:
        with open(LOG, 'a', newline='') as f:
            w = csv.writer(f, delimiter='\t')
            w.writerow([time.strftime('%F %T'), 'add', '', target, f'CORE book from Waqfeya «{bname}»: {url}', PLAN])
        print(f"[{time.strftime('%T')}] Uploaded: {target}", flush=True)
        return True
    else:
        print(f"[{time.strftime('%T')}] Upload failed for {target}: {res.stderr[:200]}", flush=True)
        return False

completed = 0
for idx, job in enumerate(jobs, 1):
    print(f"[{time.strftime('%T')}] ({idx}/{len(jobs)}) Fetching: {job['target'].split('/')[-1]}", flush=True)
    if download_file(job['url'], job['local']):
        if upload_file(job['local'], job['target'], job['bname'], job['url']):
            completed += 1
    else:
        print(f"[{time.strftime('%T')}] Skipping after repeated failures: {job['url']}", flush=True)

print(f"[{time.strftime('%T')}] Finished. Uploaded {completed} of {len(jobs)} files.", flush=True)
