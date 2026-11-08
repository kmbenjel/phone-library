"""For files that start with %PDF: read the last 2 KB and check for the %%EOF end marker (a truncated download lacks it).
-> data/phone/pdf-tail.tsv (path, size, ok|no-eof|error)"""
import csv, os, subprocess, urllib.parse
from concurrent.futures import ThreadPoolExecutor
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import phone_host
rows = [(p, int(s)) for p, s, t in csv.reader(open(os.path.join(ROOT, 'data/phone/file-types.tsv')), delimiter='\t') if t == 'pdf']
def tail(row):
    p, s = row
    b = phone_host.read_range(p, max(0, s - 2048), min(s, 2048), 60)
    return p, s, ('error' if not b else 'ok' if b'%%EOF' in b else 'no-eof')
with ThreadPoolExecutor(3) as ex, open(os.path.join(ROOT, 'data/phone/pdf-tail.tsv'), 'w') as w:
    for p, s, t in ex.map(tail, rows): w.write(f'{p}\t{s}\t{t}\n')
