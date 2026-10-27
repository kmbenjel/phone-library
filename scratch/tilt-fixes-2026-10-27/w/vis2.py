"""vis2.py BOOK PAGE OUT.jpg — tracker v2 chains on the page as scanned: each reliable chain's points and fit, angle labelled"""
import sys, os, math
sys.path.insert(0, os.path.expanduser("~/.local/share/phone-library-tools/site"))
import numpy as np, pymupdf
from PIL import Image, ImageDraw
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, D + '/code'); sys.path.insert(0, D)
import bc_w as bc, track2
C = '/home/k/.cache/phone-library/crop-regress/'
h, g, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
doc = pymupdf.open(C + h + '.pdf'); page = doc[g - 1]; a, z = bc.gray(page, 1000); a = a.copy()
mk = bc.marks(a, z, page.rect.width); tb = mk['text']
T = track2.line_tracks(a, mk['paper'], tb, z)
im = Image.fromarray(a).convert('RGB'); dr = ImageDraw.Draw(im)
for y, an, sh, rms, n in T:
    ok = rms <= 1.0 and n >= 6 and sh >= 0.3
    if not ok: continue
    s = math.tan(math.radians(an)); xc = (tb[0] + tb[2]) / 2 * z; yc = y * z; half = sh * (tb[2] - tb[0]) * z / 2
    col = (220, 0, 0) if abs(an) > 0.3 else (0, 140, 0)
    dr.line([(xc - half, yc - half * s), (xc + half, yc + half * s)], fill=col, width=2)
    dr.text((tb[2] * z + 4, yc - 6), f'{an:+.2f} r{rms:.2f}', fill=col)
im = im.crop((int(tb[0] * z - 10), int(tb[1] * z - 10), int(tb[2] * z + 90), int(tb[3] * z + 10)))
im.save(out, quality=88); print(out, im.size)
