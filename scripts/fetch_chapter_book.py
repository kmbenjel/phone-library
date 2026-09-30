"""Add a book that its publisher only offers as separate chapter PDFs (Hesperian, some UNESCO titles):
download every part in the given order, check each is a PDF, join them with pdfunite into one file, check the page
count, upload with one FTP connection and log it (action 'add').
Usage: python3 scripts/fetch_chapter_book.py "<phone path under Books/>" PLAN url1 url2 ...   (parts in reading order)"""
import csv, os, subprocess, sys, time, hashlib
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J = lambda p: os.path.join(ROOT, p)
target, plan, urls = 'Books/' + sys.argv[1], sys.argv[2], sys.argv[3:]
if target in {r[3] for r in csv.reader(open(J('data/changes/changes.tsv')), delimiter='\t') if r and r[1] == 'add'}:
    sys.exit('already added: ' + target)
D = J('downloads/chapters/' + hashlib.md5(target.encode()).hexdigest()[:10]); os.makedirs(D, exist_ok=True)
parts = []
for k, u in enumerate(urls):
    p = os.path.join(D, f'{k:03d}.pdf')
    if not (os.path.exists(p) and os.path.getsize(p) > 1000):
        subprocess.run(['curl', '-sL', '--fail', '--retry', '3', '-A', 'Mozilla/5.0', '-o', p, u])
    if not os.path.exists(p) or open(p, 'rb').read(5) != b'%PDF-': sys.exit(f'part {k} failed: {u}')
    parts.append(p)
out = os.path.join(D, 'book.pdf')
subprocess.run(['pdfunite'] + parts + [out], check=True) if len(parts) > 1 else subprocess.run(['cp', parts[0], out], check=True)
pages = next(int(l.split()[-1]) for l in subprocess.run(['pdfinfo', out], capture_output=True, text=True).stdout.splitlines() if l.startswith('Pages:'))
r = subprocess.run(['rclone', 'copyto', out, f'phone:{target}', '--inplace', '--ftp-concurrency', '1', '-q'], capture_output=True, text=True)
if r.returncode: sys.exit('UPLOAD FAIL ' + r.stderr[-200:])
with open(J('data/changes/changes.tsv'), 'a', newline='') as f:
    csv.writer(f, delimiter='\t').writerow([time.strftime('%F %T'), 'add', '', target,
        f'{len(parts)} publisher chapter PDFs joined ({pages} pages): {urls[0].rsplit("/", 1)[0]}/', plan])
print(f'added ({pages} p, {os.path.getsize(out) / 2**20:.1f} MB, {len(parts)} parts)', target)
