"""rulers.py BOOK:PAGE … — every ruler of a page as scanned, 1,000/1,400 px: the baselines (basefit, by thirds of the text
block's height), the lines' aligned edges (edge_tilt), book_crop's baseline_tilt, the shear (skew_of raw), the projection
(proj_signed), long printed rules (hrule14's rule fit) — all in the turn's sign (the turn that levels the page)"""
import sys, os, json, glob, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, '/home/k/projects/phone-library/scripts')
from basefit import base_angles, bc, C
import numpy as np, pymupdf
from scipy import ndimage
def rules(a, z):
    a = np.asarray(a); paper = float(np.percentile(a, 90)); m = a < paper - 60
    lab, n = ndimage.label(m, structure=np.ones((3, 3), bool)); res = []
    for i, sl in enumerate(ndimage.find_objects(lab), 1):
        hh, ww = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
        if ww < 0.12 * a.shape[1] or hh > 8 + ww * 0.03: continue
        ys, xs = np.nonzero(lab[sl] == i); cols = np.unique(xs)
        if len(cols) < 0.8 * ww: continue
        cy = np.array([ys[xs == c].mean() for c in cols]); fit = np.polyfit(cols, cy, 1)
        if np.abs(cy - np.polyval(fit, cols)).max() > 3: continue
        res.append((round(sl[0].start / z), round(ww / a.shape[1], 2), round(math.degrees(math.atan(fit[0])), 3)))
    return res
for s in sys.argv[1:]:
    h, pg = s.split(':')[:2]; pg = int(pg)
    R = json.load(open(sorted(glob.glob(C + h + '.b32a237bbf*.json'))[-1])); p = R['pages'][pg - 1]
    tb, paper = p.get('text') or p.get('core'), p.get('paper') or 255
    doc = pymupdf.open(C + h + '.pdf'); page = doc[pg - 1]
    a14, z14 = bc.gray(page, 1400); a14 = np.array(a14); L = base_angles(a14.copy(), paper, tb, z14)
    an = [v[1] for v in L]; ys = [v[0] for v in L]
    th = np.percentile(ys, [33.3, 66.7]) if len(ys) >= 3 else [0, 0]
    parts = [[v[1] for v in L if v[0] < th[0]], [v[1] for v in L if th[0] <= v[0] < th[1]], [v[1] for v in L if v[0] >= th[1]]]
    a10, z10 = bc.gray(page, 1000); a10 = np.array(a10)
    mk = bc.marks(a10, z10, page.rect.width)
    e = bc.edge_tilt(a10, mk['paper']); bt = bc.baseline_tilt(a10, mk['paper'])
    sk = bc.skew_of(mk['xy'], raw=True)[0] if mk.get('xy') is not None else None
    ps = bc.proj_signed(a10, mk['paper'])
    print(f'{h} p. {pg}: recipe turn {p.get("skew")} (proj read {p.get("tilt_by_proj")})')
    print(f'   baselines: median {np.median(an):+.3f} over {len(an)} lines; by thirds (top/mid/bottom) ' + ' '.join(f'{np.median(x):+.3f}' if x else '—' for x in parts))
    print(f'   aligned edges (skew_of sign: the turn is the opposite) right {e[0]}, left {e[1]}')
    print(f'   baseline_tilt {bt}; shear raw {sk}; projection {ps}; rules {rules(a14, z14)}')
    doc.close()
