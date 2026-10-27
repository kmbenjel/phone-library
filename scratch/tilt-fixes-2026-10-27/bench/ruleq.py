"""ruleq.py BOOK [V1 V2] — the independent ruler for a bench: on every page whose turn differs between two bench recipes
(default g2 → q), the long thin printed rules of the page as scanned (≥ 12 % of the width, straight; 1,400 px) — where they
agree (spread ≤ 0.15°), what each turn leaves of their tilt (rule angle − turn, in the turn's sign). Prints the pages and
the summary: mean |left|, pages left ≥ 0.2°, old vs new"""
import sys, os, json, math
sys.path.insert(0, '/home/k/projects/phone-library/scripts')
import book_crop as bc, numpy as np, pymupdf
from scipy import ndimage
S = os.path.dirname(os.path.abspath(__file__)); C = '/home/k/.cache/phone-library/crop-regress/'
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
        res.append(math.degrees(math.atan(fit[0])))
    return res
h = sys.argv[1]; v1, v2 = (sys.argv[2:4] if len(sys.argv) > 3 else ('g2', 'q'))
A, B = json.load(open(f'{S}/{h}.{v1}.json')), json.load(open(f'{S}/{h}.{v2}.json'))
doc = pymupdf.open(C + h + '.pdf'); out = []
for i, (p, q) in enumerate(zip(A['pages'], B['pages'])):
    t0, t1 = p.get('skew') or 0.0, q.get('skew') or 0.0
    if t0 == t1: continue
    a, z = bc.gray(doc[i], 1400); r = rules(a, z)
    if not r or max(r) - min(r) > 0.15: continue
    b = float(np.median(r)); out.append((i + 1, t0, t1, b, b - t0, b - t1, q.get('base_found') is not None))
    print(f'p. {i + 1}: turn {t0:+.3f} → {t1:+.3f}  rules {b:+.3f} ({len(r)})  left {b - t0:+.3f} → {b - t1:+.3f}{"  [found]" if out[-1][6] else ""}', flush=True)
doc.close()
if out:
    o = np.array([x[4] for x in out]); n = np.array([x[5] for x in out])
    print(f'{h}: {len(out)} changed pages with agreeing rules; mean |left| {np.mean(np.abs(o)):.3f} → {np.mean(np.abs(n)):.3f}; '
          f'≥ 0.2° {int((np.abs(o) >= 0.2).sum())} → {int((np.abs(n) >= 0.2).sum())}; better on {int((np.abs(n) < np.abs(o) - 0.02).sum())}, '
          f'worse on {int((np.abs(n) > np.abs(o) + 0.02).sum())}')
