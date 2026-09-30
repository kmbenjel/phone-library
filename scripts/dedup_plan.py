"""Plan moving verified duplicate copies to the quarantine folder (Books-مكررات/<original path>).
Keeps the best copy per content group. Scope flag: --safe = only same-folder and same-category groups."""
import csv, re, sys, os, json
from collections import defaultdict, Counter
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUAR = 'Books-مكررات'
index, out = sys.argv[1], sys.argv[2]
safe = '--safe' in sys.argv
count = Counter(p.rsplit('/', 1)[0] for p, s in csv.reader(open(index), delimiter='\t'))
prov = {}
pp = os.path.join(ROOT, 'data/phone/provenance.tsv')
if os.path.exists(pp):
    for r in csv.DictReader(open(pp), delimiter='\t'): prov[r['path']] = r
# folder identity = majority Waqfeya book of its files
ident = defaultdict(Counter)
for path, r in prov.items():
    if r.get('waqfeya_id'): ident[path.rsplit('/', 1)[0]][r['waqfeya_id']] += 1
wcat = {}
mp = {}
for l in open(os.path.join(ROOT, 'data/mappings/waqfeya-to-phone.tsv')):
    if l.startswith('#') or not l.strip(): continue
    k, _, v = l.rstrip('\n').partition('\t'); mp[k.strip()] = v.strip()
for fn in ('data/waqfeya/books.jsonl',):
    for l in open(os.path.join(ROOT, fn)):
        b = json.loads(l); c = re.sub(r'^[\d.]+\s+', '', ((b.get('category') or {}).get('name') or '').strip()); wcat[b['_id']] = mp.get(c, '')
g = defaultdict(list)
for s, h, p in csv.reader(open(os.path.join(ROOT, 'data/phone/dup-fingerprints.tsv')), delimiter='\t'): g[(s, h)].append(p)
def score(p):
    folder, fname = p.rsplit('/', 1); cat = folder.split('/')[0]; name = folder.split('/', 1)[1]
    s = 0
    r = prov.get(p, {}); wid = r.get('waqfeya_id')
    if wid:
        top = ident[folder].most_common(1)
        if top and top[0][0] == wid: s += 40                      # the folder is this book's own folder
        if len(ident[folder]) > 2: s -= 40                         # mixed (bucket) folder
        if wcat.get(wid) == cat: s += 15                            # category agrees with Waqfeya's
    if re.search(r'نسخة (ثانية|أخرى)|\(\d\)\.pdf$', fname): s -= 50
    if '_alt' in p: s -= 50
    if '...' in name: s -= 20
    if '...' in fname: s -= 5
    if re.search(r'-\s*\S{1,2}$', name): s -= 10           # cut mid-word, e.g. "... -ا"
    s += min(count[folder], 60) * 2                           # the more complete set wins
    s += min(len(name), 120) / 10                              # fuller descriptive name
    return s
rows = []; skipped = Counter()
for (size, h), ps in g.items():
    if len(ps) < 2: continue
    cats = {p.split('/')[0] for p in ps}; folders = {p.rsplit('/', 1)[0] for p in ps}
    if safe and len(cats) > 1: skipped['cross-category'] += 1; continue
    keep = max(ps, key=score)
    for p in ps:
        if p != keep: rows.append((p, keep, int(size)))
with open(out, 'w') as w:
    for p, keep, size in sorted(rows):
        w.write(f'Books/{p}\t{QUAR}/{p}\tduplicate of: {keep}\n')
print('moves', len(rows), 'GB', round(sum(r[2] for r in rows) / 2**30, 2), dict(skipped))
