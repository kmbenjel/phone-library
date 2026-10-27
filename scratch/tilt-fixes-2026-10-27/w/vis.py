"""vis.py BOOK PAGE TURN OUT.jpg [Y0:Y1] — the text block as scanned (left) and as turned by TURN (right), 1,000 px, with a
level red line through each line the tracker reads (at its middle) and its own fitted line in blue; the angle written"""
import sys, os, json, glob, math
sys.path.insert(0, os.path.expanduser("~/.local/share/phone-library-tools/site"))
import numpy as np, pymupdf
from PIL import Image, ImageDraw
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, D + '/code')
import bc_w as bc
C = '/home/k/.cache/phone-library/crop-regress/'
h, g, d, out = sys.argv[1], int(sys.argv[2]), float(sys.argv[3]), sys.argv[4]
yr = tuple(map(float, sys.argv[5].split(':'))) if len(sys.argv) > 5 else None
doc = pymupdf.open(C + h + '.pdf'); tiles = []
for turn in (0.0, d):
    tu = bc.Turner(doc, g - 1); page = tu.page(turn, 0, 0); a, z = bc.gray(page, 1000); a = a.copy(); pw = page.rect.width; tu.close()
    mk = bc.marks(a, z, pw); tb = mk.get('text')
    T = bc.line_tracks(a, mk['paper'], tb, z)
    im = Image.fromarray(a).convert('RGB'); dr = ImageDraw.Draw(im)
    for y, an, sh, rms, n in T:
        ok = rms <= 0.6 and n >= 6 and sh >= 0.3
        x0, x1 = tb[0] * z, tb[2] * z; yc = y * z; xc = (x0 + x1) / 2; s = math.tan(math.radians(an))
        dr.line([(x0, yc), (x1, yc)], fill=(255, 0, 0) if ok else (255, 170, 170), width=1)
        dr.line([(x0, yc + (x0 - xc) * s), (x1, yc + (x1 - xc) * s)], fill=(0, 0, 255) if ok else (170, 170, 255), width=1)
        dr.text((x1 + 3, yc - 6), f'{an:+.2f}' + ('' if ok else '?'), fill=(200, 0, 0) if ok else (160, 160, 160))
    y0, y1 = (yr[0] * z, yr[1] * z) if yr else (tb[1] * z - 10, tb[3] * z + 10)
    tiles.append(im.crop((int(tb[0] * z - 10), int(y0), int(tb[2] * z + 50), int(y1))))
    tiles.append(Image.new('RGB', (12, tiles[-1].size[1]), (90, 140, 200) if turn else (220, 200, 160)))
W = sum(t.size[0] for t in tiles); H = max(t.size[1] for t in tiles); o = Image.new('RGB', (W, H), 'white'); x = 0
for t in tiles: o.paste(t, (x, 0)); x += t.size[0]
o.save(out, quality=88); print(out, o.size)
