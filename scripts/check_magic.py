"""Read the first 8 bytes of every file on the phone: is it really a PDF? -> data/phone/file-types.tsv (path, size, type)"""
import csv, os, subprocess, sys, urllib.parse
from concurrent.futures import ThreadPoolExecutor
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
from phone_host import FTP
rows = [(p, int(s)) for p, s in csv.reader(open(sys.argv[1]), delimiter='\t') if not p.startswith('فهارس الويب/')]
def kind(row):
    p, s = row
    for _ in range(3):
        r = subprocess.run(['curl', '-s', '--max-time', '60', '-r', '0-15', FTP + urllib.parse.quote(p)], capture_output=True)
        if r.returncode == 0: break
    b = r.stdout
    t = ('pdf' if b.startswith(b'%PDF') else 'html' if b.lstrip()[:15].lower().startswith((b'<!doctype', b'<html')) else
         'zip' if b.startswith(b'PK') else 'empty' if s == 0 else 'error' if not b else 'other:' + b[:8].hex())
    return p, s, t
with ThreadPoolExecutor(3) as ex, open(os.path.join(ROOT, 'data/phone/file-types.tsv'), 'w') as w:
    for i, (p, s, t) in enumerate(ex.map(kind, rows), 1):
        w.write(f'{p}\t{s}\t{t}\n')
print('done', len(rows))
