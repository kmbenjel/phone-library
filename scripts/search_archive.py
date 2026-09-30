"""Search archive.org for books (title + author) and list candidate items with PDF count/size and downloads.
Usage: python3 scripts/search_archive.py  (edit WANTED)  -> data/compare/archive-candidates.json"""
import json, os, re, sys, time, urllib.parse, urllib.request
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from textnorm import norm
WANTED = [
 ('شرح القصائد التسع المشهورات', 'النحاس'), ('منتهى الطلب من أشعار العرب', 'ميمون'), ('مختارات شعراء العرب', 'الشجري'),
 ('الحماسة', 'البحتري'), ('الحماسة الشجرية', 'الشجري'), ('الأشباه والنظائر من أشعار المتقدمين', 'الخالدي'),
 ('معجم الشعراء', 'المرزباني'), ('تتمة اليتيمة', 'الثعالبي'), ('دمية القصر', 'الباخرزي'), ('خريدة القصر', 'الأصفهاني'),
 ('قلائد العقيان', 'خاقان'), ('ريحانة الألبا', 'الخفاجي'), ('سلافة العصر', 'معصوم'), ('نفحة الريحانة', 'المحبي'),
 ('روضة الآس', 'المقري'), ('زاد المسافر', 'إدريس'), ('مختارات البارودي', 'البارودي'), ('مجاني الأدب', 'شيخو'),
 ('شعراء النصرانية', 'شيخو'), ('مختار الأغاني', 'منظور'),
]
def get(url):
    for a in range(4):
        try: return json.load(urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'personal-library/1.0'}), timeout=90))
        except Exception: time.sleep(3 * (a + 1))
    return {}
out = {}
for title, author in WANTED:
    q = f'title:({title}) AND mediatype:texts'
    url = 'https://archive.org/advancedsearch.php?' + urllib.parse.urlencode([('q', q), ('rows', '40'), ('output', 'json')] + [('fl[]', f) for f in ('identifier', 'title', 'creator', 'downloads', 'item_size')])
    docs = get(url).get('response', {}).get('docs', [])
    tw = set(norm(title).split()); ah = norm(author).removeprefix('ال')
    cands = []
    for d in docs:
        t = ' '.join(d['title']) if isinstance(d.get('title'), list) else str(d.get('title', ''))
        c = ' '.join(d['creator']) if isinstance(d.get('creator'), list) else str(d.get('creator', ''))
        if not tw <= set(norm(t).split()): continue
        if 'الحماسة' == title and 'بحتر' not in norm(t + ' ' + c): continue
        cands.append({'id': d['identifier'], 'title': t, 'creator': c, 'downloads': d.get('downloads', 0), 'size': d.get('item_size', 0), 'author_match': ah in norm(t + ' ' + c)})
    cands.sort(key=lambda x: (not x['author_match'], -int(x['downloads'] or 0)))
    out[title] = cands[:8]
    print(f'## {title} ({author}) — {len(cands)} candidates')
    for c in cands[:6]: print(f"   {'✓' if c['author_match'] else ' '} {c['id'][:34]:36s} dl={c['downloads']:<6} {int(c['size'] or 0)/2**20:7.0f}MB  {c['title'][:70]}")
    time.sleep(1)
json.dump(out, open(os.path.join(ROOT, 'data/compare/archive-candidates.json'), 'w'), ensure_ascii=False, indent=1)
