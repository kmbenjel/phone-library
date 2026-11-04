"""Verify same-size duplicate candidates by comparing head+tail 64KB fingerprints over FTP.
Input: data/phone/index-*.tsv (path<TAB>size).  Output: data/phone/dup-fingerprints.tsv"""
import csv, hashlib, subprocess, sys, os, urllib.parse
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import phone_host
index = sys.argv[1]
by_size = defaultdict(list)
for path, size in csv.reader(open(index), delimiter='\t'):
    if int(size) > 0: by_size[int(size)].append(path)
cands = [(s, p) for s, ps in by_size.items() if len(ps) > 1 for p in ps]
def fp(item):
    """an unreadable file gets «error-<path>», never a shared fingerprint (before 2026-11-04 two failed reads gave every
    same-size file sha1(b'|') — one fingerprint, «duplicates» — when the phone refused curl's anonymous login)"""
    size, path = item
    a, b = phone_host.read_range(path, 0, 65536, 60), phone_host.read_range(path, max(0, size - 65536), 65536, 60)
    if not a or not b: return size, path, 'error-' + hashlib.sha1(path.encode()).hexdigest()
    return size, path, hashlib.sha1(a + b'|' + b).hexdigest()
out = os.path.join(ROOT, 'data/phone/dup-fingerprints.tsv')
with ThreadPoolExecutor(4) as ex, open(out, 'w') as w:
    for i, (size, path, h) in enumerate(ex.map(fp, cands), 1):
        w.write(f'{size}\t{h}\t{path}\n')
        if i % 200 == 0: print(i, '/', len(cands), flush=True)
print('done', len(cands))
