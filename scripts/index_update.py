"""Bring data/phone/index-now.tsv up to date from data/changes/changes.tsv without listing the phone (useful while
long jobs hold both FTP connections). Applies the logged deletes and moves (file or folder prefix) of the given plans.
Additions need their sizes: pass them as extra TSV files (path<TAB>size, paths relative to Books/).
Usage: python3 scripts/index_update.py PLAN [PLAN...] [--add added.tsv]"""
import csv, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IDX = os.path.join(ROOT, 'data/phone/index-now.tsv')
args = sys.argv[1:]
adds = [args[i + 1] for i, a in enumerate(args) if a == '--add']
plans = {a for i, a in enumerate(args) if a != '--add' and (i == 0 or args[i - 1] != '--add')}
idx = {p: s for p, s in csv.reader(open(IDX, encoding='utf-8'), delimiter='\t')}
strip = lambda p: p[6:] if p.startswith('Books/') else p
n = 0
for r in csv.reader(open(os.path.join(ROOT, 'data/changes/changes.tsv'), encoding='utf-8'), delimiter='\t'):
    if len(r) < 6 or r[5] not in plans: continue
    act, a, b = r[1], strip(r[2]), strip(r[3])
    if act == 'delete' and a in idx:
        del idx[a]; n += 1
    elif act == 'move':
        if a in idx: idx[b] = idx.pop(a); n += 1
        else:
            for p in [p for p in idx if p.startswith(a + '/')]:
                idx[b + p[len(a):]] = idx.pop(p); n += 1
for f in adds:
    for p, s in csv.reader(open(f, encoding='utf-8'), delimiter='\t'):
        idx[strip(p)] = s; n += 1
with open(IDX, 'w', encoding='utf-8', newline='') as o:
    w = csv.writer(o, delimiter='\t', lineterminator='\n')
    for p in sorted(idx): w.writerow([p, idx[p]])
print('applied', n, 'changes;', len(idx), 'files in index-now.tsv')
