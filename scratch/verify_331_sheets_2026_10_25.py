"""One-off (owner 2026-10-20, doubts-001 row 28: «ألم تمرّ على الجميع قارئا للصفحات الدالة؟؟»): every file plan 331 named from
a Waqfeya label, as it is now, with its first stored pages (data/inspect/pages, found through the change log; rendered by
front_pages.py when missing) for reading the volume number on its title page → argv[1]/v331.json + sheets argv[1]/v331_N.png."""
import csv, glob, hashlib, json, os, re, sys, unicodedata, subprocess
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(ROOT)
from PIL import Image, ImageDraw, ImageFont, ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True; Image.MAX_IMAGE_PIXELS = None
S = sys.argv[1]; os.makedirs(S, exist_ok=True); N = lambda s: unicodedata.normalize('NFC', s)
idx = {N(l.split('\t')[0]): (l.split('\t')[0], l.rstrip('\n').split('\t')[1]) for l in open('data/phone/index-now.tsv', encoding='utf-8')}
mv, rev = {}, {}
for r in csv.reader(open('data/changes/changes.tsv', encoding='utf-8'), delimiter='\t'):
    if len(r) > 3 and r[1] == 'move':
        a, b = N(r[2].removeprefix('Books/')), N(r[3].removeprefix('Books/')); mv[a] = b; rev.setdefault(b, []).append(a)
def cur(p):
    p = N(p); s = 0
    while p in mv and s < 60: p = mv[p]; s += 1
    return p
keys, meta = {}, {}
for l in open('data/inspect/files.jsonl'):
    try: d = json.loads(l)
    except ValueError: continue
    if d.get('key'): keys.setdefault(N(d['path']), []).append(d['key']); meta[d['key']] = (d.get('meta') or {}).get('title')
def hist(p):
    out, todo = [p], [p]
    while todo:
        x = todo.pop()
        for a in rev.get(x, []):
            if a not in out: out.append(a); todo.append(a)
    return out
def pages(p):
    raw, size = idx[p]; ks = [hashlib.md5(f'{raw}\t{size}'.encode()).hexdigest()[:16]] + [k for h in hist(p) for k in keys.get(h, [])]
    for k in ks:
        fs = sorted(glob.glob(f'data/inspect/pages/{k}-*.jpg'), key=lambda f: int(re.search(r'-(\d+)\.jpg$', f).group(1)))
        if fs: return fs[:3], meta.get(k)
    return [], next((meta.get(k) for k in ks if meta.get(k)), None)
rows = []
for l in open('plans/331-raw-archive-names.tsv', encoding='utf-8'):
    a, b, why = l.rstrip('\n').split('\t')[:3]
    c = cur(b.removeprefix('Books/'))
    if c not in idx or c.startswith('نسخ'): continue
    fs, t = pages(c)
    rows.append({'path': c, 'raw': idx[c][0], 'label': why, 'pdf_title': t, 'imgs': fs, 'orig': a.split('/')[-1]})
need = [r['raw'] for r in rows if not r['imgs']]
if need:
    open(f'{S}/need.txt', 'w', encoding='utf-8').write('\n'.join(need) + '\n')
    subprocess.run(['python3', 'scripts/front_pages.py', f'{S}/need.txt', '3'])
    for r in rows:
        if not r['imgs']: r['imgs'], _ = pages(r['path'])
json.dump(rows, open(f'{S}/v331.json', 'w'), ensure_ascii=False, indent=1)
W, H = 170, 240
font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 14) if os.path.exists('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf') else None
for s in range(0, len(rows), 16):
    sheet = Image.new('L', (4 * (3 * (W + 2) + 16), 4 * (H + 22)), 255); d = ImageDraw.Draw(sheet)
    for j, r in enumerate(rows[s:s + 16]):
        X = (j % 4) * (3 * (W + 2) + 16); Y = (j // 4) * (H + 22)
        nn = re.match(r'(\d+)', r['path'].split('/')[-1]); d.text((X + 2, Y + 2), f"{s + j + 1}  NN={nn.group(1) if nn else '-'}", fill=0, font=font)
        for c, f in enumerate(r['imgs'][:3]):
            try: im = Image.open(f); im.draft('L', (W * 2, H * 2)); im = im.convert('L'); im.thumbnail((W, H)); sheet.paste(im, (X + c * (W + 2), Y + 20))
            except Exception: pass
    sheet.save(f'{S}/v331_{s // 16 + 1}.png')
print(len(rows), 'files;', sum(1 for r in rows if not r['imgs']), 'without pages')
