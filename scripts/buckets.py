"""Detect 'bucket' folders: one folder holding several different books, files named 'NN - <folder> (<real title>).pdf'."""
import csv, re, sys
from collections import defaultdict, Counter
def buckets(index):
    files = defaultdict(list)
    for p, s in csv.reader(open(index), delimiter='\t'):
        f, n = p.rsplit('/', 1); files[f].append(n)
    out = {}
    for f, ns in files.items():
        if len(ns) < 2: continue
        name = f.split('/', 1)[1]
        nums = Counter(m.group(1) for n in ns for m in [re.match(r'^(\d+) - ', n)] if m)
        paren = [m.group(1) for n in ns for m in [re.match(r'^\d+ - .*?\((.+)\)\.pdf$', n)] if m]
        same_num = max(nums.values()) if nums else 0
        titles = {re.sub(r'\s+', ' ', t)[:25] for t in paren}
        if same_num >= 2 and len(titles) >= 2: out[f] = len(ns)
    return out
if __name__ == '__main__':
    b = buckets(sys.argv[1])
    print(len(b), 'bucket folders,', sum(b.values()), 'files')
    for f, n in sorted(b.items(), key=lambda x: -x[1]): print(f'{n}\t{f}')
