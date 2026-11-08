"""Build a folder-level duplicate analysis from dup-fingerprints.tsv + the phone index."""
import csv, json, sys
from collections import defaultdict
idx = sys.argv[1]
files = defaultdict(list)
for p, s in csv.reader(open(idx), delimiter='\t'): files[p.rsplit('/', 1)[0]].append(p)
g = defaultdict(list)
for s, h, p in csv.reader(open('data/phone/dup-fingerprints.tsv'), delimiter='\t'): g[(s, h)].append(p)
groups = [v for v in g.values() if len(v) > 1]
copy_of = {}  # file -> set(folders holding a copy)
pairs = defaultdict(set)
for v in groups:
    for p in v:
        for q in v:
            if p != q: pairs[(p.rsplit('/',1)[0], q.rsplit('/',1)[0])].add(p)
out = []
for (a, b), shared in pairs.items():
    if a >= b and a != b: continue
    out.append({'a': a, 'b': b, 'na': len(files[a]), 'nb': len(files[b]),
                'a_dup': len(shared), 'b_dup': len(pairs[(b, a)]) if a != b else len(shared)})
json.dump(out, open('data/phone/dup-pairs.json', 'w'), ensure_ascii=False, indent=0)
kinds = defaultdict(int)
for r in out:
    if r['a'] == r['b']: k = 'same-folder'
    elif r['a_dup'] == r['na'] and r['b_dup'] == r['nb']: k = 'identical-folders'
    elif r['a_dup'] == r['na'] or r['b_dup'] == r['nb']: k = 'one-contains-other'
    else: k = 'partial-overlap'
    r['kind'] = k; kinds[k] += 1
    r['cross_cat'] = r['a'].split('/')[0] != r['b'].split('/')[0]
json.dump(out, open('data/phone/dup-pairs.json', 'w'), ensure_ascii=False, indent=0)
print(dict(kinds), 'cross-category:', sum(r['cross_cat'] for r in out))
