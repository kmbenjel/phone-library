"""Compare the phone library with the whole Waqfeya catalog.
status per Waqfeya book: complete | partial (some volumes) | other-copy (same title, different files/edition) | missing
Output: data/compare/waqfeya-matches.tsv"""
import csv, json, os, re, sys
from collections import defaultdict
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from textnorm import title_key, author_tokens
from rename_plan import vol_from_orig
J = lambda p: os.path.join(ROOT, p)
def is_volume(f):
    n = f['name'].lower()
    return n.endswith('.pdf') and not n.endswith('_text.pdf') and f.get('format') != 'Text PDF' and f['size'] > 0
items = {}
for fn in ['data/archive/items.jsonl'] + sorted(os.path.relpath(p, ROOT) for p in __import__('glob').glob(os.path.join(ROOT, 'data/archive/files*.jsonl'))):
    for l in open(J(fn)):
        d = json.loads(l)
        if not d.get('error'): items[d['id']] = [f for f in d.get('files', []) if is_volume(f)]
books = {}
for fn in ('data/waqfeya/books.jsonl', 'data/waqfeya/details.jsonl', 'data/waqfeya/details2.jsonl'):
    for l in open(J(fn)):
        d = json.loads(l); books[d['_id']] = {**books.get(d['_id'], {}), **d}
wmap = {}
for l in open(J('data/mappings/waqfeya-to-phone.tsv')):
    if l.startswith('#') or not l.strip(): continue
    k, _, v = l.rstrip('\n').partition('\t'); wmap[k.strip()] = v.strip()
def phone_cat(c):
    c = re.sub(r'^[\d.]+\s+', '', (c or '').strip()); return c, wmap.get(c)
# phone side
prov = defaultdict(set)          # waqfeya id -> set of (archive id, orig name) present on phone
prov_books = defaultdict(set)    # waqfeya id -> phone folders
for r in csv.DictReader(open(J('data/phone/provenance.tsv')), delimiter='\t'):
    if r['waqfeya_id']:
        prov[r['waqfeya_id']].add((r['archive_id'], r['orig_name'])); prov_books[r['waqfeya_id']].add(r['path'].rsplit('/', 1)[0])
cat = json.load(open(J('data/catalog.json')))
keys = defaultdict(set); pauth = {}
for b in cat['books']:
    for t in {b['title']} | {w['name'] for w in b.get('waqfeya', [])}:
        k = title_key(t)
        if k: keys[k].add(b['cat'] + '/' + b['folder'])
    pauth[b['cat'] + '/' + b['folder']] = author_tokens(b.get('author', ''))
rows = []
for wid, b in books.items():
    ids = set(re.findall(r'archive\.org/(?:details|download)/([^/"?#\s]+)', json.dumps([b.get('thumbnail'), b.get('links'), b.get('archiveLink')], ensure_ascii=False)))
    allv = {(i, f['name']) for i in ids for f in items.get(i, [])}
    vols = {x for x in allv if (vol_from_orig(x[1]) or (1, 'vol'))[1] == 'vol'}      # main volumes only (no cover/preface files)
    have = prov.get(wid, set()) & (vols or allv) or prov.get(wid, set())
    wcat, pcat = phone_cat((b.get('category') or {}).get('name'))
    if have:
        status = 'complete' if not vols or have >= vols else 'partial'
        where = sorted(prov_books[wid])
    else:
        k = title_key(b['name']); at = author_tokens((b.get('author') or {}).get('name', ''))
        cand = keys.get(k, set())
        if cand and len(k.split()) <= 2 and at: cand = {c for c in cand if not pauth[c] or pauth[c] & at}
        status, where = ('other-copy', sorted(cand)) if cand else ('missing', [])
    size_mb = sum(f['size'] for i in ids for f in items.get(i, []) if is_volume(f)) / 2**20
    missing_mb = sum(f['size'] for i in ids for f in items.get(i, []) if is_volume(f) and (i, f['name']) in vols - have) / 2**20 if status == 'partial' else (size_mb if status == 'missing' else 0)
    rows.append([wid, b['name'], (b.get('author') or {}).get('name', ''), wcat, pcat or '', (b.get('century') or {}).get('name', ''),
                 b.get('visitCounts', 0), len(vols), len(have), round(size_mb, 1), round(missing_mb, 1), status, ' | '.join(where),
                 'https://waqfeya.net/books/' + b.get('permalink', ''), ' '.join(sorted(ids)), 'known' if ids and all(i in items for i in ids) else 'unknown-files'])
with open(J('data/compare/waqfeya-matches.tsv'), 'w') as f:
    w = csv.writer(f, delimiter='\t')
    w.writerow(['waqfeya_id', 'name', 'author', 'waqfeya_category', 'phone_category', 'century', 'visits', 'volumes', 'volumes_on_phone', 'size_mb', 'missing_mb', 'status', 'phone_folders', 'url', 'archive_ids', 'files_known'])
    w.writerows(rows)
from collections import Counter
print(Counter(r[11] for r in rows))
