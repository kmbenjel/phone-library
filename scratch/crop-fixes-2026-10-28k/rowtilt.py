"""each text row's tilt on one page, independent of book_crop: render at 2,000 px, the row band's ink profile in the
left and right thirds of the text block, cross-correlated (sub-pixel) → angle in book_crop's sign (the turn that levels it)."""
import sys, os, json, glob, math
sys.path.insert(0, os.path.expanduser('~/.local/share/phone-library-tools/site'))
import pymupdf, numpy as np
h, pg = sys.argv[1], int(sys.argv[2]); C = os.path.expanduser('~/.cache/phone-library/crop-regress')
rec = json.load(open(glob.glob(f'{C}/{h}.6a1fad7b21*.json')[0])); pq = rec['pages'][pg - 1]
doc = pymupdf.open(f'{C}/{h}.pdf'); page = doc[pg - 1]; W = 2000; z = W / page.rect.width
pix = page.get_pixmap(matrix=pymupdf.Matrix(z, z), colorspace=pymupdf.csGRAY)
a = 255 - np.frombuffer(pix.samples, np.uint8).reshape(pix.h, pix.w).astype(float)
tb = pq['text']; x0, x1 = int(tb[0] * z), int(tb[2] * z); y0, y1 = int(tb[1] * z), int(tb[3] * z)
wd = x1 - x0; L = a[:, x0:x0 + wd // 3]; R = a[:, x1 - wd // 3:x1]; sep = wd - wd // 3
pl, pr = L.sum(1), R.sum(1); full = a[:, x0:x1].sum(1)
# rows: peaks of the full profile smoothed over ~ a third of the pitch
k = np.ones(9) / 9; f = np.convolve(full, k, 'same'); rows = []
thr = 0.25 * f[y0:y1].max()
for y in range(y0 + 1, y1 - 1):
    if f[y] > thr and f[y] >= f[y - 1] and f[y] > f[y + 1] and (not rows or y - rows[-1] > 25): rows.append(y)
for yc in rows:
    s0, s1 = yc - 22, yc + 22; best = None
    for d in np.arange(-12, 12.01, 0.25):
        idx = np.arange(s0, s1); v = np.interp(idx + d, np.arange(len(pr)), pr)
        c = np.corrcoef(pl[s0:s1], v)[0, 1]
        if best is None or c > best[0]: best = (c, d)
    c, d = best
    ang = -math.degrees(math.atan2(d, sep))          # right part lower (d > 0, y down) ⇒ the line falls to the right
    print(f'y {yc / z:6.1f} pt  offset {d:+5.2f} px  angle {ang:+.2f}  corr {c:.2f}  ink L {pl[s0:s1].sum() / 1e5:.0f} R {pr[s0:s1].sum() / 1e5:.0f}')
