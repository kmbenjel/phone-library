"""hrule14.py BOOK:PAGE:TURN … — every long thin horizontal printed line (≥ 12 % of the page width, ≤ 8 px thick at 1,400 px)
on the page as scanned and as turned: its angle by a straight fit of its centre line (a footnote rule, a head rule: the
surest ruler of a tilt)"""
import os, sys, math
sys.path.insert(0, '/home/k/projects/phone-library/scripts')
import book_crop as bc, numpy as np, pymupdf
from scipy import ndimage
C = os.path.expanduser('~/.cache/phone-library/crop-regress/')
for s in sys.argv[1:]:
    h, pg, d = s.split(':'); pg, d = int(pg), float(d)
    doc = pymupdf.open(C + h + '.pdf'); tu = bc.Turner(doc, pg - 1); out = []
    for k in (0.0, d):
        a, z = bc.gray(tu.page(k), 1400); a = np.asarray(a); paper = float(np.percentile(a, 90)); m = a < paper - 60
        lab, n = ndimage.label(m, structure=np.ones((3, 3), bool)); res = []
        for i, sl in enumerate(ndimage.find_objects(lab), 1):
            hh, ww = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
            if ww < 0.12 * a.shape[1] or hh > 8 + ww * 0.03: continue
            ys, xs = np.nonzero(lab[sl] == i)
            cols = np.unique(xs)
            if len(cols) < 0.8 * ww: continue
            cy = np.array([ys[xs == c].mean() for c in cols]); fit = np.polyfit(cols, cy, 1)
            if np.abs(cy - np.polyval(fit, cols)).max() > 3: continue
            res.append(f'y{(sl[0].start) / z:.0f} x{sl[1].start / z:.0f}-{sl[1].stop / z:.0f} {math.degrees(math.atan(fit[0])):+.3f}°')
        out.append(res)
    tu.close(); doc.close()
    print(f'{h} p. {pg}: as scanned {out[0]}\n      turned {d}: {out[1]}')
