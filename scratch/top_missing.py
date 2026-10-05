"""One-off (2026-10-05, owner: «a selection of the top of the missing titles from all over waqfeya of all times»):
Waqfeya records the phone lacks as works (no title of the same work on the phone — the matching principle of AGENTS §3),
ranked by visits, without audio/video/software/mushafs/children's books, archive.org items checked live.
→ data/expansion/top-missing.json (the first N live ones) for reading and choosing by hand."""
import json, csv, re, os, sys, urllib.request, collections
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from textnorm import title_key
N = int(sys.argv[1]) if len(sys.argv) > 1 else 400
SKIP_CAT = r'صوتيات|مرئيات|برامج|المصاحف|الطفل المسلم|مجلات|الموسوعات العامة'
SKIP_NAME = r'مصحف|برنامج|أطلس|للأطفال|ملون|\[DVD|نص للوورد|الموسوعة العربية العالمية|العربية بين يديك'
idx = [title_key(p) for p, s in csv.reader(open(os.path.join(ROOT, 'data/phone/index-now.tsv'), encoding='utf-8'), delimiter='\t')]
def present(name):
    k = title_key(re.split(r'\s+-\s+(?:ط|ت)[\s.:]|\s+=\s+', name)[0]).split()
    key = ' '.join(k[:3])
    return bool(key) and any(key in n for n in idx)
det = {}
for fn in ('data/waqfeya/details.jsonl', 'data/waqfeya/details2.jsonl'):
    for l in open(os.path.join(ROOT, fn), encoding='utf-8'):
        d = json.loads(l); det[d['_id']] = d
rows = [r for r in csv.DictReader(open(os.path.join(ROOT, 'data/compare/waqfeya-matches.tsv'), encoding='utf-8'), delimiter='\t')
        if r['status'] == 'missing' and not re.search(SKIP_CAT, r['waqfeya_category']) and not re.search(SKIP_NAME, r['name'])]
rows.sort(key=lambda r: -int(r['visits'] or 0))
out, seen = [], set()
for r in rows:
    if len(out) >= N: break
    if present(r['name']): continue
    k = ' '.join(title_key(r['name']).split()[:3])
    if k in seen: continue                       # another record of a work already chosen (a second edition)
    d = det.get(r['waqfeya_id']) or {}
    links = [x['url'].strip() for x in d.get('links') or [] if 'archive.org/download/' in x.get('url', '')]
    if not links: continue
    items, sizes = {}, {}
    for it in collections.Counter(u.split('/download/')[1].split('/')[0] for u in links):
        try:
            m = json.load(urllib.request.urlopen(f'https://archive.org/metadata/{it}', timeout=40))
            items[it] = bool(m.get('files')) and not m.get('is_dark')
            for f in m.get('files') or []: sizes[f'{it}/{f["name"]}'] = int(f.get('size') or 0)
        except Exception: items[it] = False
    if not items or not all(items.values()): continue
    files = [urllib.request.unquote(u.split('/download/')[1]) for u in links]
    seen.add(k)
    out.append({'id': r['waqfeya_id'], 'name': r['name'], 'author': r['author'], 'cat': r['waqfeya_category'], 'century': r['century'],
                'visits': int(r['visits'] or 0), 'volumes': r['volumes'], 'publisher': str(d.get('publisher') or ''),
                'links': links, 'mb': round(sum(sizes.get(f, 0) for f in files) / 1e6, 1), 'url': r['url']})
    if len(out) % 25 == 0: print(len(out), flush=True)
json.dump(out, open(os.path.join(ROOT, 'data/expansion/top-missing.json'), 'w'), ensure_ascii=False, indent=1)
print(len(out), 'live, absent works', round(sum(x['mb'] for x in out) / 1e3, 1), 'GB')
