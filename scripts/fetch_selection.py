"""Download what the owner ticked on the selection page (Hindawi VSI, OpenStax, Hesperian, Siyavula) and add it.

Input: the page's `selections/current` document saved as JSON (ArtifactData get → file). Catalogues:
selection/catalog.json (titles, OpenStax PDF urls) and data/sources/hesperian-books.json (chapter parts in reading
order). Downloads run in parallel (Hindawi one at a time with a pause: its CDN challenges bursts); every file is
checked (%PDF + page count), Hesperian chapters are joined with pdfunite, and one uploader thread sends everything
over a single FTP connection, logging each file (action 'add', PLAN). Re-runnable: added targets are skipped.
Usage: PLAN=042-selection python3 scripts/fetch_selection.py selection/selection.json"""
import csv, json, os, queue, re, subprocess, sys, threading, time, urllib.request, xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J = lambda p: os.path.join(ROOT, p)
PLAN = os.environ.get('PLAN', '042-selection')
SCI, MED = 'العلوم والرياضيات (Science and Mathematics)', 'الطب والصحة'
HUM, HIS, PSY = 'العلوم الإنسانية والاجتماعية (Humanities and Social Sciences)', 'التاريخ والوقائع العامة', 'علم النفس وتطوير الذات'
SERIES = 'المجلات والدوريات والسلاسل الكبرى/سلسلة مقدمات قصيرة جدا (مؤسسة هنداوي)'
safe = lambda s: re.sub(r'\s+', ' ', s.replace(':', ' -').replace('/', '-').replace('?', '؟')).strip()

def openstax_target(t):
    m = re.match(r'^(Calculus|University Physics) Volume (\d)$', t)
    if m: return f'{SCI}/{m.group(1)} - OpenStax/{int(m.group(2)):02d} - {m.group(1)} (Volume {m.group(2)}).pdf'
    m = re.match(r'^World History, Volume (\d): (.+)$', t)
    if m: return f'{HIS}/World History - OpenStax/{int(m.group(1)):02d} - World History (Volume {m.group(1)} - {m.group(2)}).pdf'
    sec = PSY if t.startswith('Psychology') else HUM if t.startswith(('Principles of Economics', 'Introduction to Philosophy')) else SCI
    return f'{sec}/{safe(t)} - OpenStax/{safe(t)}.pdf'

def jobs(sel):
    cat = json.load(open(J('selection/catalog.json')))
    by = {k: {x['id']: x for x in v} for k, v in cat.items()}
    hb = json.load(open(J('data/sources/hesperian-books.json')))
    out = []
    for i in sel.get('hindawi', []):
        x = by['hindawi'][i]
        out.append(('hindawi', f'Books/{SERIES}/{safe(x["t"])} - {safe(x["a"])}.pdf', [f'https://downloads.hindawi.org/books/{i}.pdf']))
    for i in sel.get('openstax', []):
        x = by['openstax'][i]
        out.append(('openstax', 'Books/' + openstax_target(x['t']), [x['u']]))
    for k in sel.get('hesperian', []):
        b = hb[k]
        out.append(('hesperian', f'Books/{MED}/{safe(b["title"])} - Hesperian/{safe(b["title"])}.pdf', b['parts']))
    for i in sel.get('siyavula', []):
        g = re.search(r'grade(\d+)', i).group(1)
        out.append(('archive:' + i, f'Books/{SCI}/Everything Maths - Siyavula/{g} - Everything Maths (Grade {g}).pdf', []))
    return out

def archive_pdf(ident):
    x = urllib.request.urlopen(urllib.request.Request(f'https://archive.org/download/{ident}/{ident}_files.xml', headers={'User-Agent': 'personal-library/1.0'}), timeout=120).read()
    fs = [(f.get('name'), int(f.findtext('size') or 0)) for f in ET.fromstring(x).findall('file') if f.get('name', '').lower().endswith('.pdf') and not f.get('name').lower().endswith('_text.pdf')]
    n = max(fs, key=lambda f: f[1])[0]
    return f'https://archive.org/download/{ident}/{urllib.parse.quote(n)}'

def pages(p):
    out = subprocess.run(['pdfinfo', p], capture_output=True, text=True).stdout
    return next((int(l.split()[-1]) for l in out.splitlines() if l.startswith('Pages:')), 0)

import urllib.parse
DL = J('downloads/selection'); os.makedirs(DL, exist_ok=True)
done = {r[3] for r in csv.reader(open(J('data/changes/changes.tsv')), delimiter='\t') if r and r[1] == 'add'}
hind_lock, print_lock = threading.Lock(), threading.Lock()
up = queue.Queue(); stats = {'ok': 0, 'bad': 0}
say = lambda *a: (print_lock.acquire(), print(*a, flush=True), print_lock.release())

def fetch(job):
    src, target, urls = job
    if target in done: return
    key = re.sub(r'[^A-Za-z0-9]+', '_', target.encode('ascii', 'ignore').decode())[-60:] + '_' + str(abs(hash(target)) % 10**8)
    if src.startswith('archive:'): urls = [archive_pdf(src.split(':', 1)[1])]
    parts = []
    for k, u in enumerate(urls):
        p = os.path.join(DL, f'{key}_{k:03d}.pdf')
        if not (os.path.exists(p) and os.path.getsize(p) > 1000 and open(p, 'rb').read(5) == b'%PDF-'):
            if src == 'hindawi': hind_lock.acquire()
            try:
                for attempt in range(3):
                    subprocess.run(['curl', '-sL', '--fail', '--retry', '3', '--max-time', '3600', '-A', 'Mozilla/5.0', '-o', p, u])
                    if os.path.exists(p) and open(p, 'rb').read(5) == b'%PDF-': break
                    time.sleep(20 * (attempt + 1))
                if src == 'hindawi': time.sleep(2)
            finally:
                if src == 'hindawi': hind_lock.release()
        if not os.path.exists(p) or open(p, 'rb').read(5) != b'%PDF-':
            say('FAIL', target.split('/', 2)[2][:90], u); stats['bad'] += 1; return
        parts.append(p)
    out = parts[0] if len(parts) == 1 else os.path.join(DL, f'{key}_book.pdf')
    if len(parts) > 1: subprocess.run(['pdfunite'] + parts + [out], check=True)
    n = pages(out)
    if n < 2: say('BAD PDF', target); stats['bad'] += 1; return
    up.put((target, out, n, urls, len(parts)))

def uploader():
    while True:
        item = up.get()
        if item is None: return
        target, out, n, urls, np_ = item
        r = subprocess.run(['rclone', 'copyto', out, f'phone:{target}', '--inplace', '--ftp-concurrency', '1', '-q'], capture_output=True, text=True)
        if r.returncode: say('UPLOAD FAIL', target, r.stderr[-200:]); stats['bad'] += 1; continue
        with open(J('data/changes/changes.tsv'), 'a', newline='') as f:
            csv.writer(f, delimiter='\t').writerow([time.strftime('%F %T'), 'add', '', target,
                f'owner-selected ({n} pages{", %d parts joined" % np_ if np_ > 1 else ""}): {urls[0]}', PLAN])
        stats['ok'] += 1; say(f'added ({n} p, {os.path.getsize(out) / 2**20:.1f} MB)', target.split('/', 1)[1][:120])

sel = json.load(open(sys.argv[1]))
JOBS = jobs(sel)
say('jobs:', len(JOBS))
t = threading.Thread(target=uploader); t.start()
with ThreadPoolExecutor(4) as ex: list(ex.map(fetch, JOBS))
up.put(None); t.join()
say('added:', stats['ok'], '| problems:', stats['bad'])
