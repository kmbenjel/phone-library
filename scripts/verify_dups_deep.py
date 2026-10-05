"""Stronger duplicate proof: besides size + first/last 64 KB (dup_check.py), compare 64 KB at 25%, 50%, 75% of both files.
Input: a dedup plan (from, to, 'duplicate of: <kept path>'). Output: data/phone/dup-deep.tsv (aside, kept, same|different|error)"""
import csv, hashlib, os, subprocess, sys, urllib.parse
from concurrent.futures import ThreadPoolExecutor
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
from phone_host import FTP
size = {p: int(s) for p, s in csv.reader(open(sys.argv[2]), delimiter='\t')}
def chunks(path):
    n = size[path]; out = []
    for frac in (0.25, 0.5, 0.75):
        a = int(n * frac); rng = f'{a}-{min(n - 1, a + 65535)}'
        for _ in range(3):
            r = subprocess.run(['curl', '-s', '--max-time', '90', '-r', rng, FTP + urllib.parse.quote(path)], capture_output=True)
            if r.returncode == 0 and r.stdout: out.append(hashlib.sha1(r.stdout).hexdigest()); break
        else: return None
    return out
def check(row):
    aside, kept = row[0][6:], row[2].split('duplicate of: ', 1)[1]
    a, b = chunks(aside), chunks(kept)
    return [aside, kept, 'error' if a is None or b is None else ('same' if a == b else 'different')]
rows = list(csv.reader(open(sys.argv[1]), delimiter='\t'))
with ThreadPoolExecutor(4) as ex: res = list(ex.map(check, rows))
csv.writer(open(os.path.join(ROOT, 'data/phone/dup-deep.tsv'), 'w'), delimiter='\t').writerows(res)
from collections import Counter; print(Counter(r[2] for r in res))
