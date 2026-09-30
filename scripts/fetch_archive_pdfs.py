"""Download chosen archive.org items (or files) as PDFs and add them to the library, with explicit names.

LIST=lists/NNN.tsv rows: section<TAB>folder<TAB>file name<TAB>archive.org id[<TAB>file inside the item]
(section may be FR/EN/DE/ES/TR, see fetch_gutenberg.py). Without an explicit file, the item's largest original PDF
(not *_text.pdf) is taken. Parallel downloads (4), exact-size + %PDF + page-count check, one FTP connection for
uploads, every file logged (action 'add', PLAN). UPLOAD=0 only downloads and prints page counts and the first/last
text lines, to check the content before anything goes to the phone.
Usage: PLAN=NNN-name LIST=lists/NNN.tsv [UPLOAD=0] python3 scripts/fetch_archive_pdfs.py"""
import csv, os, subprocess, sys, threading, time, urllib.parse, urllib.request, xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J = lambda p: os.path.join(ROOT, p)
SEC = {'FR': 'أدب عالمي - فرنسي (Littérature française)', 'EN': 'أدب عالمي - إنجليزي (English Literature)',
       'DE': 'أدب عالمي - ألماني (Deutsche Literatur)', 'ES': 'أدب عالمي - إسباني (Literatura en español)', 'TR': 'أدب عالمي - مترجم'}
PLAN, UPLOAD = os.environ.get('PLAN', 'archive-pdfs'), os.environ.get('UPLOAD', '1') != '0'
ROWS = [r for r in csv.reader(open(os.environ['LIST']), delimiter='\t') if r and not r[0].startswith('#')]
DL = J('downloads/archive'); os.makedirs(DL, exist_ok=True)
done = {r[3] for r in csv.reader(open(J('data/changes/changes.tsv')), delimiter='\t') if r and r[1] == 'add'}
lock = threading.Lock()

def files_of(i):
    x = urllib.request.urlopen(urllib.request.Request(f'https://archive.org/download/{i}/{i}_files.xml', headers={'User-Agent': 'personal-library/1.0'}), timeout=120).read()
    return [(f.get('name'), int(f.findtext('size') or 0), f.get('source')) for f in ET.fromstring(x).findall('file')]

def text(p, first, last):
    return ' '.join(subprocess.run(['pdftotext', '-f', str(first), '-l', str(last), p, '-'], capture_output=True, text=True).stdout.split())

def pages(p):
    out = subprocess.run(['pdfinfo', p], capture_output=True, text=True).stdout
    return next((int(l.split()[-1]) for l in out.splitlines() if l.startswith('Pages:')), 0)

def one(r):
    sec, folder, name, ident = SEC.get(r[0], r[0]), r[1], r[2], r[3]
    target = f'Books/{sec}/{folder}/{name}'
    if target in done: return None
    fs = files_of(ident)
    pdfs = [(n, s) for n, s, src in fs if n.lower().endswith('.pdf') and not n.lower().endswith('_text.pdf')]
    if len(r) > 4: pdfs = [(n, s) for n, s in pdfs if n == r[4]]
    if not pdfs: return (target, 'NO PDF in ' + ident)
    n, s = max(pdfs, key=lambda x: x[1])
    local = os.path.join(DL, f'{ident}__{os.path.basename(n)}')
    if not (os.path.exists(local) and os.path.getsize(local) == s):
        subprocess.run(['curl', '-sL', '--fail', '--retry', '3', '--max-time', '3600', '-A', 'personal-library/1.0', '-o', local,
                        f'https://archive.org/download/{urllib.parse.quote(ident)}/{urllib.parse.quote(n)}'])
    if not os.path.exists(local) or os.path.getsize(local) != s or open(local, 'rb').read(5) != b'%PDF-':
        return (target, f'download failed or not a PDF ({ident}/{n})')
    pg = pages(local)
    info = f'{pg} p, {s / 2**20:.1f} MB | start: {text(local, 1, min(pg, 12))[:160]} | end: {text(local, max(1, pg - 6), pg)[-200:]}'
    if not UPLOAD: return (target, info)
    with lock:
        u = subprocess.run(['rclone', 'copyto', local, f'phone:{target}', '--inplace', '--ftp-concurrency', '1', '-q'], capture_output=True, text=True)
        if u.returncode: return (target, 'UPLOAD FAIL ' + u.stderr[-200:])
        with open(J('data/changes/changes.tsv'), 'a', newline='') as f:
            csv.writer(f, delimiter='\t').writerow([time.strftime('%F %T'), 'add', '', target,
                f'archive.org {ident}/{n} ({pg} pages): https://archive.org/details/{ident}', PLAN])
    return (target, f'added ({pg} p, {s / 2**20:.1f} MB)')

with ThreadPoolExecutor(4) as ex:
    for res in ex.map(one, ROWS):
        if res: print(res[0].split('/', 2)[-1][:110], '\n    ', res[1], flush=True)
