"""rulecal.py BOOK:PAGE … — each long thin straight printed line's angle (sub-pixel fit of its centre line, ink-weighted,
1,400 px) on the page turned by known angles: does a rule's reading move by exactly the turn?"""
import os, sys, math
sys.path.insert(0, '/home/k/projects/phone-library/scripts')
import book_crop as bc, numpy as np, pymupdf
from scipy import ndimage
C = os.path.expanduser('~/.cache/phone-library/crop-regress/')

def rules(a, z, min_w=0.12):
    a = np.asarray(a, float); paper = float(np.percentile(a, 90)); m = a < paper - 60
    lab, n = ndimage.label(m, structure=np.ones((3, 3), bool)); res = []
    for i, sl in enumerate(ndimage.find_objects(lab), 1):
        hh, ww = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
        if ww < min_w * a.shape[1] or hh > 8 + ww * 0.03: continue
        y0, y1 = max(0, sl[0].start - 2), sl[0].stop + 2; sub = np.clip(paper - a[y0:y1, sl[1]], 0, None); sub[lab[y0:y1, sl[1]] != i] = 0
        w = sub.sum(0); ok = w > 0
        if ok.sum() < 0.8 * ww: continue
        cy = (sub * np.arange(y1 - y0)[:, None]).sum(0)[ok] / w[ok]; xs = np.arange(ww)[ok]
        fit = np.polyfit(xs, cy, 1)
        if np.abs(cy - np.polyval(fit, xs)).max() > 2.5: continue
        res.append((round((sl[0].start) / z), round(ww / z), math.degrees(math.atan(fit[0]))))
    return res

for s in sys.argv[1:]:
    h, pg = s.split(':'); pg = int(pg)
    doc = pymupdf.open(C + h + '.pdf'); tu = bc.Turner(doc, pg - 1)
    for d in (-0.4, -0.2, 0.0, 0.2, 0.325, 0.4):
        a, z = bc.gray(tu.page(d), 1400); r = rules(a, z)
        print(f'{h} p. {pg} turn {d:+.3f}: ' + '  '.join(f'y{y} len{l}pt {t:+.3f}° (+turn {t + d:+.3f})' for y, l, t in r), flush=True)
    tu.close(); doc.close()
