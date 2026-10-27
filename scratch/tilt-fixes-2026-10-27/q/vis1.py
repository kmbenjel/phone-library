"""vis.py BOOK PAGE OUT.jpg TURN [TURN …] — three long text lines of a page (top, middle, bottom of the text block) at
1,400 px, turned by each TURN, stretched ×3 upright, with level guide lines; the baselines' reading of each view in its label"""
import glob, json, os, sys
sys.path.insert(0, '/home/k/projects/phone-library/scripts'); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import book_crop as bc, numpy as np, pymupdf
from basefit import base_angles, line_bands
from PIL import Image, ImageDraw, ImageFont
C = os.path.expanduser('~/.cache/phone-library/crop-regress/')
h, pg, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]; turns = [float(t) for t in sys.argv[4:]]
R = json.load(open(sorted(glob.glob(C + h + '.b32a237bbf*.json'))[-1])); p = R['pages'][pg - 1]
tb = p.get('text') or p.get('core'); paper = p.get('paper') or 255
doc = pymupdf.open(C + h + '.pdf'); tu = bc.Turner(doc, pg - 1)
F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 18)
views = []
for d in turns:
    a, z = bc.gray(tu.page(d), 1400); a = np.array(a); L = base_angles(a.copy(), paper, tb, z)
    m = float(np.median([v[1] for v in L])) if L else float('nan'); views.append((d, a, z, m, len(L)))
tu.close(); doc.close()
d0, a0, z, _, _ = views[0]; H, W = a0.shape
x0, x1 = max(0, int(tb[0] * z - 0.02 * W)), min(W, int(tb[2] * z + 0.02 * W))
ink = np.clip((paper - a0[:, x0:x1].astype(float)) / paper, 0, 1)
bandsl = [(r0, r1) for r0, r1 in line_bands(ink[int(tb[1] * z):int(tb[3] * z)], W)]
bandsl = [(r0 + int(tb[1] * z), r1 + int(tb[1] * z)) for r0, r1 in bandsl if r1 - r0 >= 0.009 * W]
wide = [(r0, r1) for r0, r1 in bandsl if (ink[r0:r1].sum(0) > 0.5).sum() >= 0.6 * (x1 - x0)] or bandsl
pick = [wide[0], wide[len(wide) // 2], wide[-1]] if len(wide) >= 3 else wide
tiles = []
for r0, r1 in pick:
    ph = int(0.15 * (r1 - r0))
    for d, a, z_, m, n in views:
        b = Image.fromarray(a[max(0, r0 - ph):r1 + ph, x0:x1]).convert('RGB')
        b = b.resize((b.size[0], b.size[1] * 4), Image.BICUBIC); dr = ImageDraw.Draw(b)
        for f in np.arange(0.1, 0.95, 0.08): dr.line([(0, int(f * b.size[1])), (b.size[0], int(f * b.size[1]))], fill=(220, 40, 40), width=1)
        lab = Image.new('RGB', (b.size[0], 24), (120, 160, 210)); ImageDraw.Draw(lab).text((6, 2), f'turn {d:+.3f}   baselines then read {m:+.3f} ({n} lines)', fill=(0, 0, 0), font=F)
        tiles += [lab, b]
    sh = Image.new('RGB', (x1 - x0, sum(t.size[1] for t in tiles)), (255, 255, 255)); y = 0
    for t in tiles: sh.paste(t, (0, y)); y += t.size[1]
    o = out.replace('.jpg', f'-{r0}.jpg'); sh.save(o, quality=90); print(o, sh.size); tiles = []
print([(v[0], round(v[3], 3), v[4]) for v in views])
