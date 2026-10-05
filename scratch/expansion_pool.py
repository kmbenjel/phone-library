"""One-off (2026-10-05, owner): candidate pool from Waqfeya records the phone lacks (conceptually: no title of the
same work by the same author on the phone), in three groups: careful printers (العامرة/بولاق/الأميرية، الحلبي، الخانجي،
دار المعارف، حجرية فاس، دائرة المعارف العثمانية، السلفية/المنيرية/السعادة…، المستشرقون), the most read heritage titles,
and poetry dawawin. Each record's archive.org items are checked live. → data/expansion/pool.json"""
import json, csv, re, os, sys, urllib.request, collections
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from textnorm import title_key, norm, author_tokens
os.makedirs(os.path.join(ROOT, 'data/expansion'), exist_ok=True)
st = {r['waqfeya_id']: r for r in csv.DictReader(open(os.path.join(ROOT, 'data/compare/waqfeya-matches.tsv'), encoding='utf-8'), delimiter='\t')}
idx = [p for p, s in csv.reader(open(os.path.join(ROOT, 'data/phone/index-now.tsv'), encoding='utf-8'), delimiter='\t')]
nidx = [title_key(p) for p in idx]
PRINTERS = r'العامرة|بولاق|الأميرية|الآستانة|استانبول|إستانبول|الجوائب|الحلبي|الخانجي|دار المعارف|حجرية|الحجرية|فاس|دائرة المعارف|السلفية|المنيرية|السعادة|التقدم|الميمنية|الخيرية|الوهبية|الجمالية|الشرفية|بريل|ليدن|ليبسك|برلين|المستشرقين|مطبعة'
MODERN = r'موسوعة العربية العالمية|أطلس|برنامج|مصحف|العربية بين يديك|للأطفال|قصص|روايات|مجلة|تفسير الشعراوي|تنمية|رواية'
def present(name, author):
    k = title_key(re.split(r'\s+-\s+(?:ط|ت)[\s.:]', name)[0]).split()
    key = ' '.join(k[:3]) if len(k) >= 3 else ' '.join(k)
    return bool(key) and any(key in n for n in nidx)
def live(links):
    items = collections.Counter(u.split('/download/')[1].split('/')[0] for u in links if '/download/' in u)
    out = {}
    for it in items:
        try:
            m = json.load(urllib.request.urlopen(f'https://archive.org/metadata/{it}', timeout=40))
            out[it] = bool(m.get('files')) and not m.get('is_dark')
        except Exception: out[it] = False
    return out
pool = []
for fn in ('data/waqfeya/details.jsonl', 'data/waqfeya/details2.jsonl'):
    for l in open(os.path.join(ROOT, fn), encoding='utf-8'):
        d = json.loads(l); r = st.get(d['_id'])
        if not r or r['status'] != 'missing': continue
        name = d['name']; pub = str(d.get('publisher') or ''); au = (d.get('author') or {}).get('name', '') if isinstance(d.get('author'), dict) else ''
        if re.search(MODERN, name): continue
        groups = []
        if re.search(PRINTERS, pub + ' ' + name): groups.append('printer')
        if re.search(r'ديوان|شعر ', name): groups.append('diwan')
        cent = re.search(r'(\d+)', str(d.get('century') or '')); cent = int(cent.group(1)) if cent else None
        if (d.get('visitCounts') or 0) > 60000 and (cent is None or cent <= 13): groups.append('popular')
        if not groups or present(name, au): continue
        links = [x['url'].strip() for x in d.get('links') or [] if 'archive.org/download/' in x.get('url', '')]
        if not links: continue
        pool.append({'id': d['_id'], 'name': name, 'author': au, 'publisher': pub, 'century': cent, 'visits': d.get('visitCounts'),
                     'volumes': d.get('numberOfVolumes'), 'groups': groups, 'links': links, 'cat': (d.get('category') or {}).get('name', '') if isinstance(d.get('category'), dict) else ''})
print(len(pool), 'candidates before the live check', collections.Counter(g for p in pool for g in p['groups']))
for i, p in enumerate(pool):
    lv = live(p['links']); p['live'] = all(lv.values()) and bool(lv); p['items'] = lv
    if i % 50 == 0: print(i, flush=True)
json.dump(pool, open(os.path.join(ROOT, 'data/expansion/pool.json'), 'w'), ensure_ascii=False, indent=1)
print('live', sum(p['live'] for p in pool), 'of', len(pool))
