"""Stronger duplicate proof: besides size + first/last 64 KB (dup_check.py), compare 64 KB at 25%, 50%, 75% of both files.
Input: a dedup plan (from, to, 'duplicate of: <kept path>'). Output: data/phone/dup-deep.tsv (aside, kept, same|different|error)"""
import csv, hashlib, os, subprocess, sys, urllib.parse
from concurrent.futures import ThreadPoolExecutor
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import phone_host
size = {p: int(s) for p, s in csv.reader(open(sys.argv[2]), delimiter='\t')}
def chunks(path):
    n = size[path]; out = []
    for frac in (0.25, 0.5, 0.75):
        b = phone_host.read_range(path, int(n * frac), 65536, 90)
        if not b: return None
        out.append(hashlib.sha1(b).hexdigest())
    return out
def check(row):
    aside, kept = row[0][6:], row[2].split('duplicate of: ', 1)[1]
    a, b = chunks(aside), chunks(kept)
    return [aside, kept, 'error' if a is None or b is None else ('same' if a == b else 'different')]
rows = list(csv.reader(open(sys.argv[1]), delimiter='\t'))
with ThreadPoolExecutor(4) as ex: res = list(ex.map(check, rows))
csv.writer(open(os.path.join(ROOT, 'data/phone/dup-deep.tsv'), 'w'), delimiter='\t').writerows(res)
from collections import Counter; print(Counter(r[2] for r in res))
