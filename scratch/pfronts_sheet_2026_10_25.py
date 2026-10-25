"""One-off: the 33 «…p.pdf» front parts (scratch/missing_p_fronts_2026_10_20.py → argv[1]/list.json) beside the first pages
of the volume each belongs to (stored page images, found through the change log; the volume path re-found by its folder when
the provenance path is stale) → argv[1]/targets.json + contact sheets argv[1]/sheet*.png for the eye check."""
import csv, glob, hashlib, json, os, re, subprocess, sys, unicodedata
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(ROOT)
from PIL import Image, ImageDraw, ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True; Image.MAX_IMAGE_PIXELS = None
S = sys.argv[1]; N = lambda s: unicodedata.normalize('NFC', s)
o = json.load(open(f'{S}/list.json'))
idx = {N(l.split('\t')[0]): (l.split('\t')[0], l.rstrip('\n').split('\t')[1]) for l in open('data/phone/index-now.tsv', encoding='utf-8')}
mv, rev = {}, {}
for r in csv.reader(open('data/changes/changes.tsv', encoding='utf-8'), delimiter='\t'):
    if len(r) > 3 and r[1] == 'move':
        a, b = N(r[2].removeprefix('Books/')), N(r[3].removeprefix('Books/')); mv[a] = b; rev.setdefault(b, []).append(a)
def cur(p):
    p = N(p); s = 0
    while p in mv and s < 60: p = mv[p]; s += 1
    return p
keys = {}
for l in open('data/inspect/files.jsonl'):
    try: d = json.loads(l)
    except ValueError: continue
    if d.get('key'): keys.setdefault(N(d['path']), []).append(d['key'])
def imgs(p, n=2):
    raw, size = idx[p]; ks = [hashlib.md5(f'{raw}\t{size}'.encode()).hexdigest()[:16]]
    todo, seen = [p], {p}
    while todo:
        x = todo.pop(); ks += keys.get(x, [])
        for a in rev.get(x, []):
            if a not in seen: seen.add(a); todo.append(a)
    for k in ks:
        fs = sorted(glob.glob(f'data/inspect/pages/{k}-*.jpg'), key=lambda f: int(re.search(r'-(\d+)\.jpg$', f).group(1)))
        if fs: return fs[:n]
    return []
FOLDERS = {'المغرب في حلى المغرب': 'التاريخ/المغرب في حلى المغرب - قسم الأندلس - ابن سعيد المغربي (ت شوقي ضيف - دار المعارف)',
           'درء تعارض': 'العقيدة/درء تعارض العقل والنقل - ابن تيمية (ت رشاد سالم - جامعة الإمام)',
           'رؤوس المسائل': 'الفقه الحنبلي/رؤوس المسائل الخلافية بين جمهور الفقهاء - العكبري',
           'شرح القصائد السبع': 'الأدب/شرح القصائد السبع الطوال الجاهليات - ابن الأنباري (ت عبد السلام هارون - دار المعارف)',
           'سير أعلام': 'التراجم والطبقات/سير أعلام النبلاء - الحافظ الذهبي (ت الأرناؤوط - الرسالة)',
           'صحيح ابن خزيمة': 'كتب السنة/صحيح ابن خزيمة - ابن خزيمة النيسابوري (ت الأعظمي - المكتب الإسلامي)'}
out = []
for i, x in enumerate(o, 1):
    v = cur(x['volume'])
    if v not in idx:
        fol = next((N(f) for k, f in FOLDERS.items() if k in x['volume']), None)
        m = re.search(r'/(\d+) - ', x['volume'])
        cand = sorted(p for p in idx if fol and m and p.startswith(fol + '/') and p.split('/')[-1].startswith(m.group(1) + ' - ')
                      and not re.search(r'المقدمة|الواجهة|الغلاف', p.split('/')[-1])) if fol else []
        v = cand[0] if cand else None
    if 'تاريخ الأمم والملوك' in (x['volume'] or ''): v = None          # the set was a duplicate (plan 370)
    out.append({'i': i, 'file': x['file'], 'pages': x['pages'], 'local': x['local'], 'volume': v,
                'vol_imgs': imgs(v) if v else []})
json.dump(out, open(f'{S}/targets.json', 'w'), ensure_ascii=False, indent=1)
os.makedirs(f'{S}/img', exist_ok=True)
W, H = 120, 170
def th(f):
    try: im = Image.open(f); im.draft('L', (W * 2, H * 2)); im = im.convert('L'); im.thumbnail((W, H))
    except Exception: im = Image.new('L', (W, H), 200)
    bg = Image.new('L', (W, H), 255); bg.paste(im, ((W - im.width) // 2, (H - im.height) // 2)); return bg
rows = [x for x in out if x['volume']]
for s in range(0, len(rows), 8):
    sheet = Image.new('L', (40 + 7 * (W + 4), 8 * (H + 6)), 255); d = ImageDraw.Draw(sheet)
    for r, x in enumerate(rows[s:s + 8]):
        n = x['pages'] or 1
        pp = sorted(set([1, 2, 3, n]))
        pi = []
        for p in pp:
            pre = f"{S}/img/p{x['i']}_{p}"
            subprocess.run(['pdftoppm', '-png', '-r', '25', '-f', str(p), '-l', str(p), '-singlefile', x['local'], pre], capture_output=True)
            pi.append(pre + '.png')
        d.text((2, r * (H + 6) + H // 2), str(x['i']), fill=0)
        for c, f in enumerate(pi[:4] + [None] + x['vol_imgs'][:2]):
            if f: sheet.paste(th(f), (40 + c * (W + 4), r * (H + 6)))
    sheet.save(f'{S}/sheet{s // 8 + 1}.png')
print(len(out), 'parts;', len(rows), 'with a volume;', sum(1 for x in rows if not x['vol_imgs']), 'volumes without stored images')
