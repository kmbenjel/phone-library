"""For files that start with %PDF: read the last 2 KB and check for the %%EOF end marker (a truncated download lacks it).
-> data/phone/pdf-tail.tsv (path, size, ok|no-eof|error)"""
import csv, os, subprocess, urllib.parse
from concurrent.futures import ThreadPoolExecutor
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
from phone_host import FTP
rows = [(p, int(s)) for p, s, t in csv.reader(open(os.path.join(ROOT, 'data/phone/file-types.tsv')), delimiter='\t') if t == 'pdf']
def tail(row):
    p, s = row
    for _ in range(3):
        r = subprocess.run(['curl', '-s', '--max-time', '60', '-r', f'{max(0, s - 2048)}-{s - 1}', FTP + urllib.parse.quote(p)], capture_output=True)
        if r.returncode == 0 and r.stdout: return p, s, ('ok' if b'%%EOF' in r.stdout else 'no-eof')
    return p, s, 'error'
with ThreadPoolExecutor(3) as ex, open(os.path.join(ROOT, 'data/phone/pdf-tail.tsv'), 'w') as w:
    for p, s, t in ex.map(tail, rows): w.write(f'{p}\t{s}\t{t}\n')
