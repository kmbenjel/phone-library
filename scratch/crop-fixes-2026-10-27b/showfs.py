"""showfs.py OUT BOOK:PAGE … — the page as scanned (100 dpi), its specks in red, its own folio in green, the 26h crop in blue"""
import sys, json, glob
sys.path.insert(0, '/home/k/.local/share/phone-library-tools/site')
import pymupdf
from PIL import Image, ImageDraw
C = '/home/k/.cache/phone-library/crop-regress/'
out = sys.argv[1]
for a in sys.argv[2:]:
    h, i = a.split(':'); i = int(i)
    r = json.load(open(sorted(glob.glob(f'{C}{h}.20d30c2020*.json'))[0])); p = r['pages'][i - 1]
    d = pymupdf.open(C + h + '.pdf'); pg = d[i - 1]; z = 100 / 72
    pix = pg.get_pixmap(matrix=pymupdf.Matrix(z, z), colorspace=pymupdf.csGRAY)
    im = Image.frombytes('L', (pix.width, pix.height), pix.samples).convert('RGB'); dr = ImageDraw.Draw(im)
    for s in p.get('specks') or []: dr.rectangle([s[0] * z - 3, s[1] * z - 3, s[2] * z + 3, s[3] * z + 3], outline=(255, 0, 0), width=2)
    if p.get('folio'): f = p['folio']; dr.rectangle([f[0] * z - 3, f[1] * z - 3, f[2] * z + 3, f[3] * z + 3], outline=(0, 170, 0), width=2)
    if p.get('crop'): c = p['crop']; dr.rectangle([c[0] * z, c[1] * z, c[2] * z, c[3] * z], outline=(0, 0, 255), width=2)
    im.save(f'{out}/{h}-{i}.jpg', quality=80); d.close()
