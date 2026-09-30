"""Verify same-size duplicate candidates by comparing head+tail 64KB fingerprints over FTP.
Input: data/phone/index-*.tsv (path<TAB>size).  Output: data/phone/dup-fingerprints.tsv"""
import csv, hashlib, subprocess, sys, os, urllib.parse
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FTP = os.environ.get('PHONE_FTP', 'ftp://192.168.11.100:2221/Books/')
index = sys.argv[1]
by_size = defaultdict(list)
for path, size in csv.reader(open(index), delimiter='\t'):
    if int(size) > 0: by_size[int(size)].append(path)
cands = [(s, p) for s, ps in by_size.items() if len(ps) > 1 for p in ps]
def chunk(path, rng):
    url = FTP + urllib.parse.quote(path)
    for _ in range(3):
        r = subprocess.run(['curl', '-s', '--max-time', '60', '-r', rng, url], capture_output=True)
        if r.returncode == 0 and r.stdout: return r.stdout
    return b''
def fp(item):
    size, path = item
    h = hashlib.sha1(chunk(path, '0-65535') + b'|' + chunk(path, '-65536')).hexdigest()
    return size, path, h
out = os.path.join(ROOT, 'data/phone/dup-fingerprints.tsv')
with ThreadPoolExecutor(4) as ex, open(out, 'w') as w:
    for i, (size, path, h) in enumerate(ex.map(fp, cands), 1):
        w.write(f'{size}\t{h}\t{path}\n')
        if i % 200 == 0: print(i, '/', len(cands), flush=True)
print('done', len(cands))
