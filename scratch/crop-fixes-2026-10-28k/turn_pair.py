"""turn_pair.py BOOK PAGE TURN_A TURN_B OUT.jpg — the page as the reader sees it turned by TURN_A (left) and by TURN_B
(right), the text block's region, level guide lines every 30 px: which turn leaves its lines level?"""
import sys, os, json
sys.path.insert(0, '/home/k/projects/phone-library/scripts')
import book_crop as bc, numpy as np, pymupdf
from PIL import Image, ImageDraw, ImageFont
h, pg, ta, tb_, out = sys.argv[1], int(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]), sys.argv[5]
C = os.path.expanduser('~/.cache/phone-library/crop-regress')
doc = pymupdf.open(f'{C}/{h}.pdf'); tu = bc.Turner(doc, pg - 1)
F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 18)
ims = []
for t in (ta, tb_):
    a, z = bc.gray(tu.page(t), 900); im = Image.fromarray(np.array(a)).convert('RGB'); d = ImageDraw.Draw(im)
    for y in range(0, im.height, 30): d.line([(0, y), (im.width, y)], fill=(80, 160, 255), width=1)
    d.text((10, 10), f'p.{pg} turned {t:+.3f}', fill=(220, 0, 0), font=F); ims.append(im)
W = sum(i.width for i in ims) + 10; c = Image.new('RGB', (W, max(i.height for i in ims)), 'white'); x = 0
for i in ims: c.paste(i, (x, 0)); x += i.width + 10
c = c.resize((1600, c.height * 1600 // c.width)); c.save(out, quality=85); print(out)
