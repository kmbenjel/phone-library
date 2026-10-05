"""One-off (2026-10-05): the careful-printer titles chosen by hand from data/expansion/pool.json (indices of the listing
sorted by group, publisher, -visits), re-checked for presence with a looser key (2 title words) and sized from
archive.org → data/expansion/printers-pick.json"""
import json, csv, re, os, sys, urllib.request, collections
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from textnorm import title_key, author_tokens
PICK = [5,7,8,16,34,35,39,41,*range(42,62),72,73,74,75,79,80,81,83,84,86,87,88,90,92,93,95,99,103,104,107,108,109,112,114,115,116,
        122,125,126,128,138,140,141,144,145,148,149,150,151,154,155,157,160,166,167,168,172,175,178,179,180,181,182,189,193,195,196,
        197,198,200,201,204,205,207,208,209,210,216,218,220,225,227,230,239,240,243,250,256,258,259,260,261,272,273,279,281,287,288,
        290,291,292,293,294,297,298,301,302,303,304,305,308,310,311,312,313,314,315,320]
p = [x for x in json.load(open(os.path.join(ROOT, 'data/expansion/pool.json'))) if x.get('live')]
p.sort(key=lambda x: (x['groups'][0], x.get('publisher') or '', -x.get('visits', 0)))
idx = [title_key(q) for q, s in csv.reader(open(os.path.join(ROOT, 'data/phone/index-now.tsv'), encoding='utf-8'), delimiter='\t')]
out = []
for i in PICK:
    x = p[i]
    k = title_key(re.split(r'\s+-\s+(?:ط|ت)[\s.:]|\s+=\s+', x['name'])[0]).split()
    au = author_tokens(re.split(r'[؛،]', x['author'])[0])
    k2 = ' '.join(k[:2])
    maybe = [q for q in idx if k2 and k2 in q and (not au or any(a in q for a in au))][:3]
    sizes = {}
    for it in collections.Counter(u.split('/download/')[1].split('/')[0] for u in x['links']):
        try:
            m = json.load(urllib.request.urlopen(f'https://archive.org/metadata/{it}', timeout=40))
            for f in m.get('files') or []: sizes[f'{it}/{f["name"]}'] = int(f.get('size') or 0)
        except Exception: pass
    files = [urllib.request.unquote(u.split('/download/')[1]) for u in x['links']]
    x['files'] = [(f, sizes.get(f, 0)) for f in files]; x['mb'] = round(sum(s for _, s in x['files']) / 1e6, 1); x['maybe_present'] = maybe
    out.append(x)
    print(i, x['name'][:60], x['mb'], 'MB', 'MAYBE:' + ' | '.join(maybe)[:150] if maybe else '', flush=True)
json.dump(out, open(os.path.join(ROOT, 'data/expansion/printers-pick.json'), 'w'), ensure_ascii=False, indent=1)
print(len(out), round(sum(x['mb'] for x in out) / 1e3, 2), 'GB')
