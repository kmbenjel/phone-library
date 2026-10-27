"""basefit — each line's BASELINE (Arabic: the densest ink row) found to a fraction of a pixel in K column chunks, a straight
line fitted through the chunks (robust: the worst chunks dropped) → the line's angle; the page's tilt = the median over the
lines at least a quarter of the text block wide. Usage: basefit.py BOOK:PAGE … — calibration on known turns (the reading
plus the turn must stay constant)"""
import os, sys, json, glob
sys.path.insert(0, '/home/k/projects/phone-library/scripts')
import book_crop as bc, numpy as np, pymupdf
from scipy import ndimage
C = os.path.expanduser('~/.cache/phone-library/crop-regress/')

def line_bands(ink, W):
    prof = ndimage.uniform_filter1d(ink.sum(1), max(3, int(0.0065 * W))); on = prof > 0.02 * prof.max()
    lab, n = ndimage.label(on)
    for k in range(1, n + 1):
        ys = np.nonzero(lab == k)[0]; yield ys[0], ys[-1] + 1

def base_angles(a, paper, tb, z, K=16):
    H, W = a.shape; mx, my = 0.02 * W, 0.01 * H
    x0, y0 = max(0, int(tb[0] * z - mx)), max(0, int(tb[1] * z - my)); x1, y1 = min(W, int(tb[2] * z + mx)), min(H, int(tb[3] * z + my))
    ink = np.clip((paper - a[y0:y1, x0:x1].astype(float)) / max(paper, 1), 0, 1); bw = x1 - x0; out = []
    for r0, r1 in line_bands(ink, W):
        if r1 - r0 < 0.009 * W: continue
        pad = int(0.3 * (r1 - r0)); R0 = max(0, r0 - pad); b = ink[R0:r1 + pad]
        xs = np.nonzero(b.sum(0) > 0.5)[0]
        if len(xs) < 2 or xs[-1] - xs[0] < 0.25 * bw: continue
        b = b[:, xs[0]:xs[-1] + 1]; Wb = b.shape[1]; e = np.linspace(0, Wb, K + 1).astype(int); pts = []
        for j in range(K):
            pr = ndimage.gaussian_filter1d(b[:, e[j]:e[j + 1]].sum(1), 1.0)
            if pr.max() < 0.25 * (e[j + 1] - e[j]): continue      # (a chunk with little ink on any row: no baseline)
            i = int(np.argmax(pr))
            if 0 < i < len(pr) - 1:                               # the peak to a fraction of a pixel (a parabola through 3 rows)
                den = pr[i - 1] - 2 * pr[i] + pr[i + 1]; i = i + (0.5 * (pr[i - 1] - pr[i + 1]) / den if den < 0 else 0)
            pts.append(((e[j] + e[j + 1]) / 2, i))
        if len(pts) < 6: continue
        P = np.array(pts)
        for _ in range(2):                                        # the chunks furthest from the line dropped twice
            f = np.polyfit(P[:, 0], P[:, 1], 1); res = np.abs(P[:, 1] - np.polyval(f, P[:, 0]))
            if len(P) > 6: P = P[res < max(np.percentile(res, 75), 0.5)]
        f = np.polyfit(P[:, 0], P[:, 1], 1)
        out.append((round(((r0 + r1) / 2 + y0) / z, 1), round(float(np.degrees(np.arctan(f[0]))), 3), len(P)))
    return out

if __name__ == '__main__':
    for s in sys.argv[1:]:
        h, pg = s.split(':')[:2]; pg = int(pg)
        R = json.load(open(sorted(glob.glob(C + h + '.b32a237bbf*.json'))[-1])); p = R['pages'][pg - 1]
        tb, paper = p.get('text') or p.get('core'), p.get('paper') or 255
        doc = pymupdf.open(C + h + '.pdf'); tu = bc.Turner(doc, pg - 1); row = []
        for d in (-0.4, -0.2, 0.0, 0.2, 0.4, p.get('skew') or 0.0):
            a, z = bc.gray(tu.page(d), 1400); L = base_angles(a.copy(), paper, tb, z)
            m = float(np.median([v[1] for v in L])) if L else float('nan')
            row.append(f'{d:+.3f}: {m:+.3f} (+turn {m + d:+.3f}, {len(L)} lines)')
        tu.close(); doc.close(); print(h, pg, 'recipe turn', p.get('skew'), '|', ' | '.join(row), flush=True)
