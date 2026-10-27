"""line_tracks v2: vertical rules whitened, the block split at its white gutters, lines followed within each column"""
import numpy as np
from scipy import ndimage

def _chains(ink, z, strip_pt, pitch, ref):
    bh, bw = ink.shape
    K = max(3, int(round(bw / (strip_pt * z)))); e = np.linspace(0, bw, K + 1).astype(int)
    P = [ndimage.gaussian_filter1d(ink[:, e[j]:e[j + 1]].sum(1), 1.0) for j in range(K)]
    peaks = []
    for pr in P:
        mxf = ndimage.maximum_filter1d(pr, 2 * max(2, int(0.45 * pitch)) + 1); pk = []
        for r in np.nonzero((pr == mxf) & (pr >= 0.25 * ref * (e[1] - e[0])))[0]:
            rr = float(r)
            if 0 < r < len(pr) - 1:
                den = pr[r - 1] - 2 * pr[r] + pr[r + 1]
                if den < 0: rr = r + 0.5 * (pr[r - 1] - pr[r + 1]) / den
            pk.append(rr)
        peaks.append(pk)
    chains = []
    for j in range(K):
        xc = (e[j] + e[j + 1]) / 2; cand = []
        for ci, (pts, last) in enumerate(chains):
            if j - last > 3: continue
            if len(pts) >= 3: X = np.array(pts); yp = np.polyval(np.polyfit(X[:, 0], X[:, 1], 1), xc)
            else: yp = pts[-1][1]
            cand += [(abs(y - yp), ci, k) for k, y in enumerate(peaks[j]) if abs(y - yp) <= 0.2 * pitch]
        uc, up_ = set(), set()
        for _, ci, k in sorted(cand):
            if ci in uc or k in up_: continue
            uc.add(ci); up_.add(k); chains[ci][0].append((xc, peaks[j][k])); chains[ci][1] = j
        chains += [[[(xc, y)], j] for k, y in enumerate(peaks[j]) if k not in up_]
    return [np.array(c[0]) for c in chains]

def line_tracks(a, paper, tb, z, strip_pt=21.0):
    if tb is None: return []
    H, W = a.shape; mx, my = 0.02 * W, 0.01 * H
    x0, y0 = max(0, int(tb[0] * z - mx)), max(0, int(tb[1] * z - my)); x1, y1 = min(W, int(tb[2] * z + mx)), min(H, int(tb[3] * z + my))
    if x1 - x0 < 50 or y1 - y0 < 50: return []
    ink = np.clip((paper - a[y0:y1, x0:x1].astype(np.float32)) / max(paper, 1), 0, 1); bh, bw = ink.shape
    # vertical rules and frame sides (an ink run down a quarter of the block): no line's part — whitened
    m = ink > 0.35; run = np.zeros(bw, int)
    for x in np.nonzero(m.sum(0) >= 0.25 * bh)[0]:
        c = m[:, x].astype(np.int8); d = np.diff(np.concatenate(([0], c, [0]))); s, t = np.nonzero(d == 1)[0], np.nonzero(d == -1)[0]
        run[x] = int((t - s).max()) if len(s) else 0
    rl = np.nonzero(run >= 0.25 * bh)[0]
    if len(rl): ink[:, np.unique(np.clip(np.concatenate([rl - 1, rl, rl + 1]), 0, bw - 1))] = 0
    # the pitch: the strips' row profiles correlated with themselves
    K0 = max(8, int(round(bw / (strip_pt * z)))); e0 = np.linspace(0, bw, K0 + 1).astype(int)
    P0 = [ndimage.gaussian_filter1d(ink[:, e0[j]:e0[j + 1]].sum(1), 1.0) for j in range(K0)]
    ac = np.zeros(bh)
    for pr in P0:
        q = pr - pr.mean(); f = np.fft.rfft(q, 2 * bh); ac += np.fft.irfft(f * np.conj(f))[:bh]
    hi = min(bh // 2, int(0.08 * W)); up = np.nonzero(np.diff(ac[:hi]) > 0)[0]
    if len(up) == 0: return []
    lo = max(3, int(up[0])); pitch = lo + int(np.argmax(ac[lo:hi]))
    if ac[pitch] <= 0.05 * ac[0]: pitch = int(0.035 * W)
    ref = np.percentile([pr.max() / max(1, e0[j + 1] - e0[j]) for j, pr in enumerate(P0)], 90)   # (per pixel of strip width)
    # white gutters (a column of the block where hardly any row has ink, ≥ 0.6 % of the page wide, inside 15–85 % of the
    # block): the columns are followed one by one, a line never linked across them
    occ = ndimage.uniform_filter1d((ink > 0.35).mean(0), max(3, int(0.006 * W)))   # (share of the rows inked, per column)
    gut = occ < 0.01; cuts = [0]
    lab, n = ndimage.label(gut)
    for k in range(1, n + 1):
        xs = np.nonzero(lab == k)[0]
        if xs[-1] - xs[0] + 1 >= 0.006 * W and 0.15 * bw <= (xs[0] + xs[-1]) / 2 <= 0.85 * bw: cuts.append(int((xs[0] + xs[-1]) / 2))
    cuts.append(bw); out = []
    import os
    if os.environ.get('TDBG'): print('pitch', pitch, 'rules', list(rl[:10]), 'cuts', cuts, 'bw', bw)
    for c0, c1 in zip(cuts[:-1], cuts[1:]):
        if c1 - c0 < 0.12 * bw: continue
        for X in _chains(ink[:, c0:c1], z, strip_pt, pitch, ref):
            if len(X) < 6 or X[-1, 0] - X[0, 0] < 0.3 * (c1 - c0): continue
            for _ in range(2):
                f = np.polyfit(X[:, 0], X[:, 1], 1); res = np.abs(X[:, 1] - np.polyval(f, X[:, 0]))
                if len(X) > 6: X = X[res <= max(1.0, 2.5 * np.median(res))]
            if len(X) < 6: continue
            f = np.polyfit(X[:, 0], X[:, 1], 1); res = X[:, 1] - np.polyval(f, X[:, 0])
            out.append((round((float(np.polyval(f, (c1 - c0) / 2)) + y0) / z, 1), round(float(np.degrees(np.arctan(f[0]))), 3),
                        round(float(X[-1, 0] - X[0, 0]) / bw, 2), round(float(np.sqrt((res ** 2).mean())), 2), len(X)))
    return sorted(out)
