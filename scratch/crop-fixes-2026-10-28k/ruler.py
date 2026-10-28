"""ruler.py BOOK PAGE TURN… — a plain ruler against each long line (owner 2026-10-09: «you can just use a ruler against any
line!»), independent of book_crop's three measures: the page turned by TURN at 1,800 px; text lines by the row profile; on
each line its baseline (the densest ink row, ±1 row refined) in its right quarter and its left quarter → the line's tilt
left after the turn. Prints each turn's lines and their median (degrees; 0 = level)"""
import sys, os, math
sys.path.insert(0, '/home/k/projects/phone-library/scripts')
import book_crop as bc, numpy as np, pymupdf
from scipy import ndimage
h, pg = sys.argv[1], int(sys.argv[2]); turns = [float(t) for t in sys.argv[3:]]
doc = pymupdf.open(os.path.expanduser(f'~/.cache/phone-library/crop-regress/{h}.pdf')); tu = bc.Turner(doc, pg - 1)
for t in turns:
    a, z = bc.gray(tu.page(t), 1800); a = np.array(a).astype(float); H, W = a.shape
    ink = np.clip((np.percentile(a, 90) - a) / 255.0, 0, 1)
    cols = ink.sum(0); xs = np.nonzero(cols > 0.02 * cols.max())[0]
    x0, x1 = int(np.percentile(xs, 3)), int(np.percentile(xs, 97))           # the text block's width
    prof = ndimage.gaussian_filter1d(ink[:, x0:x1].sum(1), 2); on = prof > 0.15 * prof.max()
    lab, n = ndimage.label(on); out = []
    for sl in ndimage.find_objects(lab):
        y0, y1 = sl[0].start, sl[0].stop
        if y1 - y0 < 8: continue
        band = ink[y0:y1, x0:x1]; w = band.shape[1]
        if band.sum(0).nonzero()[0].ptp() < 0.8 * w: continue                    # a long line only (≥ 80 % of the block)
        ys = []
        for c0, c1 in ((int(0.75 * w), w), (0, int(0.25 * w))):              # right quarter, left quarter
            r = ndimage.gaussian_filter1d(band[:, c0:c1].sum(1), 1.0); k = int(np.argmax(r))
            if 0 < k < len(r) - 1:
                den = r[k - 1] - 2 * r[k] + r[k + 1]; k = k + (0.5 * (r[k - 1] - r[k + 1]) / den if den < 0 else 0)
            ys.append(k)
        out.append(math.degrees(math.atan((ys[1] - ys[0]) / (0.75 * w))))       # left lower than right → positive
    print(f'turn {t:+.3f}: {len(out)} long lines, median {np.median(out):+.3f}°, |each| ≤ 0.15°: {sum(1 for v in out if abs(v) <= 0.15)}/{len(out)}  ' +
          ' '.join(f'{v:+.2f}' for v in out))
