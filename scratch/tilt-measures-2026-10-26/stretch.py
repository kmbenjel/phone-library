"""stretch.py BOOK PAGE OUT.jpg Y [Y …] [--turn D] — single text lines (pt from the page's top) at 1,400 px across the text
block, as scanned (beige strip) and as turned (blue strip), stretched ×3 upright so that a slope of 0.3° (3 px over a line)
shows as 9 px; a straight guide through the line's middle"""
import glob, json, os, sys
sys.path.insert(0, '/home/k/projects/phone-library/scripts')
import book_crop as bc
from PIL import Image, ImageDraw
C = os.path.expanduser('~/.cache/phone-library/crop-regress/')
args = sys.argv[1:]; turn = None
if '--turn' in args: k = args.index('--turn'); turn = float(args[k + 1]); del args[k:k + 2]
h, pg, out = args[0], int(args[1]), args[2]; ys = [float(y) for y in args[3:]]
R = json.load(open(sorted(glob.glob(C + h + '.b32a237bbf*.json'))[-1])); p = R['pages'][pg - 1]
d = turn if turn is not None else p.get('skew') or 0.0
import pymupdf, numpy as np
doc = pymupdf.open(C + h + '.pdf'); tu = bc.Turner(doc, pg - 1)
ims = []
for k in (0.0, d):
    a, z = bc.gray(tu.page(k), 1400); ims.append(Image.fromarray(np.asarray(a)).convert('RGB'))
tu.close(); doc.close()
tb = p.get('core') or p.get('text'); X0, X1 = int((tb[0] - 6) * z), int((tb[2] + 6) * z)
tiles = []
for y in ys:
    for n, im in enumerate(ims):
        b = im.crop((X0, int((y - 9) * z), X1, int((y + 9) * z)))
        b = b.resize((b.size[0], b.size[1] * 3), Image.BICUBIC); dr = ImageDraw.Draw(b)
        for f in (0.25, 0.5, 0.75): dr.line([(0, int(f * b.size[1])), (b.size[0], int(f * b.size[1]))], fill=(220, 40, 40), width=1)
        tiles += [Image.new('RGB', (b.size[0], 10), (200, 190, 170) if n == 0 else (120, 160, 210)), b]
    tiles.append(Image.new('RGB', (X1 - X0, 16), (255, 255, 255)))
sh = Image.new('RGB', (X1 - X0, sum(t.size[1] for t in tiles)), (255, 255, 255)); yy = 0
for t in tiles: sh.paste(t, (0, yy)); yy += t.size[1]
sh.save(out, quality=90); print(out, sh.size, 'turn', d)
