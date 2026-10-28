"""zoomcmp.py BOOK PAGE OLDV NEWV OUT.png [DPI] — the page as scanned, with OLD's crop (red) / box (pink) and NEW's crop
(green) / box (light green), blots (orange), lines (blue) of NEW, to judge what each run's frame takes in."""
import sys, os, json, glob
sys.path.insert(0, os.path.expanduser("~/.local/share/phone-library-tools/site")); import pymupdf
from PIL import Image, ImageDraw
C = os.path.expanduser('~/.cache/phone-library/crop-regress/')
h, pg, ov, nv, out = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4], sys.argv[5]
dpi = int(sys.argv[6]) if len(sys.argv) > 6 else 110
rec = lambda v: json.load(open(sorted(glob.glob(f'{C}{h}.{v}*.json'))[-1]))['pages'][pg - 1]
A, B = rec(ov), rec(nv)
doc = pymupdf.open(f'{C}{h}.pdf'); page = doc[pg - 1]
pix = page.get_pixmap(dpi=dpi); im = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
s = pix.width / page.rect.width; d = ImageDraw.Draw(im)
R = lambda b: [b[0] * s, b[1] * s, b[2] * s, b[3] * s]
for b in B.get('blots') or []: d.rectangle(R(b), outline=(255, 140, 0), width=2)
for b in B.get('lines') or []: d.rectangle(R(b), outline=(0, 0, 255), width=1)
for b in B.get('margin') or []: d.rectangle(R(b), outline=(160, 0, 160), width=1)
if A.get('box'): d.rectangle(R(A['box']), outline=(255, 150, 150), width=1)
if B.get('box'): d.rectangle(R(B['box']), outline=(120, 220, 120), width=1)
if A.get('crop'): d.rectangle(R(A['crop']), outline=(220, 0, 0), width=2)
if B.get('crop'): d.rectangle(R(B['crop']), outline=(0, 160, 0), width=2)
im.save(out)
print(out, im.size, 'old skew', A.get('skew'), 'new skew', B.get('skew'))
