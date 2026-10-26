"""fastleans — line_leans (book_crop, guard G) with each line's turn found by shearing 16 column chunks of its band instead
of rotating the whole band 80 times (for angles ≤ 2° a turn moves a column by x·tanθ: the same profile, ≈ 100× faster).
Usage: fastleans.py BOOK:PAGE:TURN … (compares with leans14's line_leans when SLOW=1)"""
import os, sys, time
sys.path.insert(0, '/home/k/projects/phone-library/scripts')
import book_crop as bc, numpy as np, pymupdf
from scipy import ndimage
C = os.path.expanduser('~/.cache/phone-library/crop-regress/')
ANG = np.arange(-1.975, 1.976, 0.05)

def fast_line_leans(a, paper, tb, z, K=16):
    if tb is None: return []
    H, W = a.shape; mx, my = 0.02 * W, 0.01 * H
    x0, y0 = max(0, int(tb[0] * z - mx)), max(0, int(tb[1] * z - my)); x1, y1 = min(W, int(tb[2] * z + mx)), min(H, int(tb[3] * z + my))
    if x1 - x0 < 50 or y1 - y0 < 50: return []
    ink = np.clip((paper - a[y0:y1, x0:x1].astype(float)) / max(paper, 1), 0, 1)
    prof = ndimage.uniform_filter1d(ink.sum(1), max(3, int(0.0065 * W))); on = prof > 0.02 * prof.max()
    lab, n = ndimage.label(on); out = []; bw = x1 - x0; tn = np.tan(np.radians(ANG))
    for k in range(1, n + 1):
        ys = np.nonzero(lab == k)[0]; r0, r1 = ys[0], ys[-1] + 1
        if r1 - r0 < 0.009 * W: continue
        pad = int(0.6 * (r1 - r0)); b = ink[max(0, r0 - pad):r1 + pad]
        xs = np.nonzero(b.sum(0) > 0.5)[0]
        if len(xs) < 2 or xs[-1] - xs[0] < 0.25 * bw: continue
        b = ndimage.gaussian_filter1d(b[:, xs[0]:xs[-1] + 1], 1.0, axis=0)
        R_, Wb = b.shape; edges = np.linspace(0, Wb, K + 1).astype(int)
        P = np.stack([b[:, edges[j]:edges[j + 1]].sum(1) for j in range(K)])          # K × R profiles
        xc = (edges[:-1] + edges[1:]) / 2 - Wb / 2                                     # chunk centres from the band's middle
        rows = np.arange(R_, dtype=float); best = None
        for t, tt in zip(ANG, tn):
            s = sum(np.interp(rows + xc[j] * tt, rows, P[j], left=0, right=0) for j in range(K))
            v = float(np.var(s))
            if best is None or v > best[0]: best = (v, t)
        t = best[1]
        out.append((round(((r0 + r1) / 2 + y0) / z, 1), round((xs[-1] - xs[0]) / bw, 2), None if abs(t) >= 1.95 else round(float(t), 3)))
    return out

if __name__ == '__main__':
    slow = os.environ.get('SLOW') == '1'
    if slow:
        sys.path.insert(0, '/tmp/claude-1000/-home-k-projects-phone-library/1b7990ba-6814-49a5-b805-48efc1d260b5/scratchpad/tools')
        from leans14 import line_leans
    for s in sys.argv[1:]:
        h, pg, d = s.split(':'); pg, d = int(pg), float(d)
        doc = pymupdf.open(C + h + '.pdf'); tu = bc.Turner(doc, pg - 1)
        for k in (0.0, d):
            page = tu.page(k); a, z = bc.gray(page, 1000); mk = bc.marks(a.copy(), z, page.rect.width)
            page = tu.page(k); a14, z14 = bc.gray(page, 1400); a14 = a14.copy()
            t0 = time.time(); F = fast_line_leans(a14, mk.get('paper') or 255, mk.get('text'), z14); tf = time.time() - t0
            print(f'{h} p. {pg} view {k:+.3f} fast ({tf:.2f}s): {[v[2] for v in F]}', flush=True)
            if slow:
                t0 = time.time(); L = line_leans(a14, mk.get('paper') or 255, mk.get('text'), z14); ts = time.time() - t0
                print(f'{"":>20} slow ({ts:.2f}s): {[v[2] for v in L]}', flush=True)
        tu.close(); doc.close()
