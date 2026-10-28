"""tzoom.py BOOK PAGE V1,V2,… OUT.png [x0,y0,x1,y1] [DPI] — the page turned and moved as the LAST variant's recipe has it (the
reader's view before the crop), each variant's crop drawn on it (V1 red, V2 green, V3 blue, V4 orange; the last variant's text
block thin magenta, its box thin cyan), clipped to the region (pt, turned view) — to judge what each frame takes in or cuts.
Variants: out/<book>.<v>.json (this folder; r27l = 27l's cached recipe). A variant turned otherwise is named on the sheet."""
import sys, os, json
sys.path.insert(0, '/home/k/projects/phone-library/scripts')
import book_crop as bc
from PIL import Image, ImageDraw, ImageFont
S = os.path.dirname(os.path.abspath(__file__))
h, pg, vs, out = sys.argv[1], int(sys.argv[2]), sys.argv[3].split(','), sys.argv[4]
reg = [float(v) for v in sys.argv[5].split(',')] if len(sys.argv) > 5 and sys.argv[5] != '-' else None
dpi = int(sys.argv[6]) if len(sys.argv) > 6 else 150
P = [json.load(open(f'{S}/out/{h}.{v}.json'))['pages'][pg - 1] for v in vs]
q = P[-1]; mv = q.get('move') or [0, 0]
doc = bc.pymupdf.open(os.path.expanduser(f'~/.cache/phone-library/crop-regress/{h}.pdf'))
tu = bc.Turner(doc, pg - 1); page = tu.page(q.get('skew') or 0, mv[0], mv[1])
r = bc.pymupdf.Rect(reg) if reg else page.rect
pix = page.get_pixmap(dpi=dpi, clip=r, alpha=False); im = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
tu.close(); doc.close()
s = dpi / 72; d = ImageDraw.Draw(im)
R = lambda b: [(b[0] - r.x0) * s, (b[1] - r.y0) * s, (b[2] - r.x0) * s, (b[3] - r.y0) * s]
cols = [(220, 0, 0), (0, 160, 0), (0, 70, 230), (255, 140, 0)]
if q.get('text'): d.rectangle(R(q['text']), outline=(220, 0, 220), width=1)
if q.get('box'): d.rectangle(R(q['box']), outline=(0, 200, 220), width=1)
font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 12)
for k, (v, p) in enumerate(zip(vs, P)):
    c = p.get('show') or p.get('crop')
    if c: d.rectangle(R(c), outline=cols[k % 4], width=2)
    turn = '' if (p.get('skew'), p.get('move')) == (q.get('skew'), q.get('move')) else f' (turned {p.get("skew")} move {p.get("move")})'
    d.text((4, 4 + 14 * k), f'{v}: {c}{turn}', fill=cols[k % 4], font=font)
im.save(out); print(out, im.size, 'skew', q.get('skew'), 'move', mv)
