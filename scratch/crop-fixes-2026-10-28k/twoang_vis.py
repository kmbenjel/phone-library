"""twoang_vis.py BOOK PAGE TURN OUT.jpg — every line guard W reads on a page (line_tracks at 1,000 px, as scanned), drawn
over the page at its own angle across the text block, labelled «before → after the turn»; red: made worse beyond 0.35°
(fix T), orange: beyond 0.5° (the old bar too), green: takes the turn. To judge a refusal by eye: are these real lines, and
do they lie at two angles?"""
import sys, os, json, math
S = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, S + '/code'); sys.path.insert(1, '/home/k/projects/phone-library/scripts')
import bc_j as bc, pymupdf
from PIL import Image, ImageDraw, ImageFont
h, pg, d, out = sys.argv[1], int(sys.argv[2]), float(sys.argv[3]), sys.argv[4]
C = os.path.expanduser('~/.cache/phone-library/crop-regress'); doc = pymupdf.open(f'{C}/{h}.pdf'); tu = bc.Turner(doc, pg - 1)
def view(t):
    page = tu.page(t, 0, 0); a, z = bc.gray(page, 1000); mk = bc.marks(a, z, page.rect.width)
    return a, z, mk, bc.line_tracks(a, mk['paper'], mk.get('text'), z)
a0, z, mk, t0 = view(0); _, _, _, t1 = view(d)
L = bc.lines_read(t0, t1, d) or []
img = Image.fromarray(a0).convert('RGB'); dr = ImageDraw.Draw(img)
F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 14)
tb = mk['text']; x0, x1 = tb[0] * z, tb[2] * z; xc = (x0 + x1) / 2
for y, b, af in L:
    worse35 = abs(af) > 0.35 + 1e-6 and abs(af) >= abs(b) + 0.25 - 1e-6; worse50 = abs(af) >= max(0.5, abs(b) + 0.25) - 1e-6
    col = (230, 120, 0) if worse50 else (220, 0, 0) if worse35 else (0, 160, 0)
    k = math.tan(math.radians(b)); yc = y * z
    dr.line([(x0, yc + k * (x0 - xc)), (x1, yc + k * (x1 - xc))], fill=col, width=2)   # (line_tracks fits rows on columns, y down)
    dr.text((x1 + 6, yc - 8), f'{b:+.2f}→{af:+.2f}', fill=col, font=F)
dr.text((10, 10), f'{h} p.{pg} turn {d}: {len(L)} lines read', fill=(0, 0, 200), font=F)
W = img.width; img = img.resize((W * 900 // W, img.height * 900 // W)); img.save(out, quality=85)
print(out, len(L), 'lines')
