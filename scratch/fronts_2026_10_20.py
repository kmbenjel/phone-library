"""One-off survey (owner 2026-10-20, doubts-001 row 30: «أظن أن الوقفية تفرد الواجهة أو الواجهات … عن الأجزاء كلها مع
واجهاتها، وإن كان كذلك فلا حاجة لتلك الواجهات في مكتبتي»): every separate front file of a set — its page count, and
whether the set's first volume opens with a title page (its first page rendered in data/inspect/pages: little ink in
few lines). Writes scratch output to the path given."""
import csv, glob, hashlib, json, os, re, sys, unicodedata
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(ROOT)
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
import numpy as np
N = lambda s: unicodedata.normalize('NFC', s)
idx = {N(l.split('\t')[0]): (l.split('\t')[0], l.rstrip('\n').split('\t')[1]) for l in open('data/phone/index-now.tsv', encoding='utf-8')}
rev = {}
for r in csv.reader(open('data/changes/changes.tsv', encoding='utf-8'), delimiter='\t'):
    if len(r) > 3 and r[1] == 'move': rev.setdefault(N(r[3].removeprefix('Books/')), []).append(N(r[2].removeprefix('Books/')))
rec = {}
for l in open('data/inspect/files.jsonl'):
    try: d = json.loads(l)
    except ValueError: continue
    if d.get('key'): rec.setdefault(N(d['path']), []).append(d)
def history(p):
    out, todo = [p], [p]
    while todo:
        x = todo.pop()
        for a in rev.get(x, []):
            if a not in out: out.append(a); todo.append(a)
    return out
def info(p):
    raw, size = idx[p]; keys = [hashlib.md5(f'{raw}\t{size}'.encode()).hexdigest()[:16]]; pages = None
    for h in history(p):
        for d in rec.get(h, []):
            keys.append(d['key']); pages = pages or d.get('pages')
    img = next((f for k in keys for f in [f'data/inspect/pages/{k}-1.jpg'] if os.path.exists(f)), None)
    return pages, img
def titleness(img):
    im = Image.open(img); im.draft("L", (600, 840)); a = np.asarray(im.convert("L").resize((300, 420)), dtype=float)
    core = a[30:390, 25:275] < 128
    rows = core.mean(1) > 0.01
    lines = int((rows[1:] & ~rows[:-1]).sum())
    return round(float(core.mean()), 4), lines
out = []
fronts = [p for p in idx if re.search(r'الواجهة|الغلاف', p.split('/')[-1]) and p.count('/') >= 2
          and not p.startswith(('نسخ مستبعدة', 'نسخ محسنة', 'فهارس الويب'))]
for f in sorted(fronts):
    folder = f.rsplit('/', 1)[0]
    sibs = sorted(p for p in idx if p.startswith(folder + '/') and p.count('/') == f.count('/') and p != f
                  and not re.search(r'الواجهة|الغلاف|المقدمة|مقدمة', p.split('/')[-1]))
    fp, _ = info(f)
    v1 = sibs[0] if sibs else ''
    vp, vimg = info(v1) if v1 else (None, None)
    ink, lines = titleness(vimg) if vimg else (None, None)
    out.append({'front': f, 'front_pages': fp, 'front_bytes': int(idx[f][1]), 'vol1': v1, 'vol1_img': vimg, 'ink': ink, 'lines': lines})
json.dump(out, open(sys.argv[1], 'w'), ensure_ascii=False, indent=0)
import collections
print(len(out), 'fronts')
print('front pages:', collections.Counter('?' if o['front_pages'] is None else o['front_pages'] if o['front_pages'] <= 3 else '>3' for o in out))
print('vol1 image:', sum(1 for o in out if o['vol1_img']), 'of', len(out))
