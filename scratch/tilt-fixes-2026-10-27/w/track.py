"""line_tracks — each text line followed across the page in narrow strips (its baseline in each strip, linked strip to strip),
so that lines at different angles on one page are each read: base_angles segments lines on the page's row profile, where
lines tilted ≈ 1° run into each other (الموسوعة 38 ص 892: its lower paragraph read −9.2°, +3.7°, −8.1°)."""
import numpy as np
from scipy import ndimage

def line_tracks(a, paper, tb, z, strip_pt=21.0):
    """the lines of the text block (tb, pt; z px per pt), each followed strip by strip: in every strip (≈ strip_pt wide) the
    peaks of the ink-row profile (in Arabic the baseline is the densest row; a parabola through the peak gives a fraction of a
    pixel), linked to the nearest peak of the next strips (within a fifth of the line pitch from where the line is heading,
    up to 2 strips skipped: the space between words); a straight line through each chain, the points furthest from it dropped
    twice. Returns [(y pt, angle °, share of the block's width, rms px, points)] — the angle in the sign of the turn that
    levels the line (read again after a turn d: angle − d), as base_angles"""
    if tb is None: return []
    H, W = a.shape; mx, my = 0.02 * W, 0.01 * H
    x0, y0 = max(0, int(tb[0] * z - mx)), max(0, int(tb[1] * z - my)); x1, y1 = min(W, int(tb[2] * z + mx)), min(H, int(tb[3] * z + my))
    if x1 - x0 < 50 or y1 - y0 < 50: return []
    ink = np.clip((paper - a[y0:y1, x0:x1].astype(np.float32)) / max(paper, 1), 0, 1); bh, bw = ink.shape
    K = max(8, int(round(bw / (strip_pt * z)))); e = np.linspace(0, bw, K + 1).astype(int); sw = bw / K
    P = [ndimage.gaussian_filter1d(ink[:, e[j]:e[j + 1]].sum(1), 1.0) for j in range(K)]
    # the line pitch: the strips' row profiles correlated with themselves (narrow strips: a tilt barely blurs them)
    ac = np.zeros(bh)
    for pr in P:
        q = pr - pr.mean(); f = np.fft.rfft(q, 2 * bh); ac += np.fft.irfft(f * np.conj(f))[:bh]
    hi = min(bh // 2, int(0.08 * W))                  # (past the central lobe: from the first rise of the curve)
    up = np.nonzero(np.diff(ac[:hi]) > 0)[0]
    if len(up) == 0: return []
    lo = max(3, int(up[0])); pitch = lo + int(np.argmax(ac[lo:hi]))
    if ac[pitch] <= 0.05 * ac[0]: pitch = int(0.035 * W)   # (no rhythm of lines: a pitch of an ordinary page)
    ref = np.percentile([pr.max() for pr in P], 90)
    peaks = []                                        # per strip: [(y px, height)]
    for pr in P:
        sep = max(2, int(0.45 * pitch)); mxf = ndimage.maximum_filter1d(pr, 2 * sep + 1)
        ys = np.nonzero((pr == mxf) & (pr >= 0.25 * ref))[0]; pk = []
        for r in ys:
            if 0 < r < len(pr) - 1:
                den = pr[r - 1] - 2 * pr[r] + pr[r + 1]; rr = r + (0.5 * (pr[r - 1] - pr[r + 1]) / den if den < 0 else 0)
            else: rr = float(r)
            pk.append((float(rr), float(pr[r])))
        peaks.append(pk)
    win = 0.2 * pitch; chains = []                    # each: {'pts': [(x, y)], 'j': last strip}
    for j in range(K):
        xc = (e[j] + e[j + 1]) / 2; cand = []
        for ci, c in enumerate(chains):
            if j - c['j'] > 3: continue
            pts = c['pts']
            if len(pts) >= 3:
                X = np.array(pts); f = np.polyfit(X[:, 0], X[:, 1], 1); yp = np.polyval(f, xc)
            else: yp = pts[-1][1]
            for pi, (y, hgt) in enumerate(peaks[j]):
                if abs(y - yp) <= win: cand.append((abs(y - yp), ci, pi))
        used_c, used_p = set(), set()
        for dlt, ci, pi in sorted(cand):
            if ci in used_c or pi in used_p: continue
            used_c.add(ci); used_p.add(pi); chains[ci]['pts'].append((xc, peaks[j][pi][0])); chains[ci]['j'] = j
        for pi, (y, hgt) in enumerate(peaks[j]):
            if pi not in used_p: chains.append({'pts': [(xc, y)], 'j': j})
    out = []
    for c in chains:
        X = np.array(c['pts'])
        if len(X) < 6 or X[-1, 0] - X[0, 0] < 0.3 * bw: continue
        for _ in range(2):
            f = np.polyfit(X[:, 0], X[:, 1], 1); res = np.abs(X[:, 1] - np.polyval(f, X[:, 0]))
            if len(X) > 6: X = X[res <= max(1.0, 2.5 * np.median(res))]
        if len(X) < 6: continue
        f = np.polyfit(X[:, 0], X[:, 1], 1); res = X[:, 1] - np.polyval(f, X[:, 0])
        out.append((round((float(np.polyval(f, bw / 2)) + y0) / z, 1), round(float(np.degrees(np.arctan(f[0]))), 3),
                    round(float(X[-1, 0] - X[0, 0]) / bw, 2), round(float(np.sqrt((res ** 2).mean())), 2), len(X)))
    return sorted(out)
