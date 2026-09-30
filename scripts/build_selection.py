"""Build the owner's selection page (published as a claude.ai artifact with a db): selection/catalog.json + the page.

Sources: the curated catalogues already in selection/catalog.json (hindawi, openstax, hesperian, siyavula) plus,
rebuilt on every run from the comparisons, every Waqfeya book in the library's sections that is missing or
incomplete on the phone (data/compare/waqfeya-matches.tsv) and every Shamela book missing on the phone
(data/compare/shamela-matches.tsv), marked when Waqfeya has a PDF with the same title.
Output: selection/catalog.json and selection/اختيار-كتب-المؤسسات.html (publish that file with the Artifact tool to
https://claude.ai/artifact/65hgeqWwbTengz9NTxJ1CP; the owner's ticks are read with ArtifactData get selections/current).
Usage: python3 scripts/build_selection.py"""
import csv, json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from textnorm import title_key
J = lambda p: os.path.join(ROOT, p)

cat = json.load(open(J('selection/catalog.json')))
W = list(csv.DictReader(open(J('data/compare/waqfeya-matches.tsv')), delimiter='\t'))
waq = []
for r in W:
    if not r['phone_category'] or r['status'] not in ('missing', 'partial'): continue
    x = {'id': r['waqfeya_id'], 't': r['name'], 'a': r['author'].split('؛')[0].strip(), 'g': r['phone_category'],
         'v': int(r['visits'] or 0), 'n': int(r['volumes'] or 0), 'mb': round(float(r['size_mb'] or 0)), 'c': r['century'].replace('القرن ', '').replace(' هـ', '')}
    if r['status'] == 'partial':
        x['p'] = f"{r['volumes_on_phone']}/{r['volumes']}"; x['mb'] = round(float(r['missing_mb'] or 0))
    waq.append(x)
waq.sort(key=lambda x: (x['g'], 'p' not in x, -x['v']))          # incomplete books first in each section, then by popularity
best = {}
for r in W:
    k = title_key(r['name'])
    if k and (k not in best or int(r['visits'] or 0) > int(best[k]['visits'] or 0)): best[k] = r
sham = []
for r in csv.DictReader(open(J('data/compare/shamela-matches.tsv')), delimiter='\t'):
    if r['phone_book_ids']: continue
    d = int(r['death']) if r['death'].isdigit() else 0
    x = {'id': r['shamela_id'], 't': r['title'], 'a': r['author'], 'g': r['category'], 'd': d if 0 < d < 1500 else 0}
    w = best.get(title_key(r['title']))
    if w: x['w'] = w['waqfeya_id']
    sham.append(x)
sham.sort(key=lambda x: (x['g'], x['d'] or 9999))
cat['waqfeya'], cat['shamela'] = waq, sham
json.dump(cat, open(J('selection/catalog.json'), 'w'), ensure_ascii=False)
page = open(J('selection/page.template.html')).read().replace('/*DATA*/', json.dumps(cat, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/'))
open(J('selection/اختيار-كتب-المؤسسات.html'), 'w').write(page)
print({k: len(v) for k, v in cat.items()}, f'page {len(page.encode()) / 2**20:.1f} MB')
