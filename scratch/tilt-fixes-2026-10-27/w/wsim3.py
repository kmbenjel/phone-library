"""wsim3.py OUT.jsonl RECIPE.json... [-j J] — guard W's two views of every turned page (not by rules, not the owner's) of
each recipe, read by bc_w2's line_tracks AND a copy that also tells each line's x-span and how much of it is unbroken ink
(a printed rule: ink along the whole line, no word gaps) → one JSON line per page: book, page, turn, flags, t0, t1 with
tracks (y, angle, share, rms, n, x0 pt, x1 pt, coverage, longest gap pt). Offline: wsim3_eval.py. Resumable."""
import sys, os, json
sys.path.insert(0, os.path.expanduser("~/.local/share/phone-library-tools/site"))
import numpy as np, pymupdf
from scipy import ndimage
from concurrent.futures import ProcessPoolExecutor
sys.path.insert(0, '/tmp/claude-1000/-home-k-projects-phone-library/fcd8d325-9813-40ca-94ce-bd6c86424307/scratchpad/w/code')
import bc_w2 as bc
C = '/home/k/.cache/phone-library/crop-regress/'
FL = ('tilt_by_proj', 'level_by_proj', 'tilt_by_base', 'level_by_base', 'image_third', 'level_by_lines', 'tilt_by_edge',
      'curved', 'tilt_by_columns', 'level_by_columns', 'turned_in_check', 'tilt_disputed', 'lines_lean', 'unsure_tilt')


def tracks_ext(a, paper, tb, z, strip_pt=21.0):
    """bc_w2.line_tracks, line for line, with each line's x-span (pt), unbroken-ink share and longest gap (pt) added"""
    if tb is None: return []
    H, W = a.shape; mx, my = 0.02 * W, 0.01 * H
    x0, y0 = max(0, int(tb[0] * z - mx)), max(0, int(tb[1] * z - my)); x1, y1 = min(W, int(tb[2] * z + mx)), min(H, int(tb[3] * z + my))
    if x1 - x0 < 50 or y1 - y0 < 50: return []
    ink = np.clip((paper - a[y0:y1, x0:x1].astype(np.float32)) / max(paper, 1), 0, 1); bh, bw = ink.shape
    m = ink > 0.35; run = np.zeros(bw, int)
    for x in np.nonzero(m.sum(0) >= 0.25 * bh)[0]:
        d_ = np.diff(np.concatenate(([0], m[:, x].astype(np.int8), [0]))); s0, s1 = np.nonzero(d_ == 1)[0], np.nonzero(d_ == -1)[0]
        run[x] = int((s1 - s0).max()) if len(s0) else 0
    rl = np.nonzero(run >= 0.25 * bh)[0]
    if len(rl): ink[:, np.unique(np.clip(np.concatenate([rl - 1, rl, rl + 1]), 0, bw - 1))] = 0
    K = max(8, int(round(bw / (strip_pt * z)))); e = np.linspace(0, bw, K + 1).astype(int)
    P = [ndimage.gaussian_filter1d(ink[:, e[j]:e[j + 1]].sum(1), 1.0) for j in range(K)]
    ac = np.zeros(bh)
    for pr in P:
        q = pr - pr.mean(); f = np.fft.rfft(q, 2 * bh); ac += np.fft.irfft(f * np.conj(f))[:bh]
    hi = min(bh // 2, int(0.08 * W)); up = np.nonzero(np.diff(ac[:hi]) > 0)[0]
    if len(up) == 0: return []
    lo = max(3, int(up[0])); pitch = lo + int(np.argmax(ac[lo:hi]))
    if ac[pitch] <= 0.05 * ac[0]: pitch = int(0.035 * W)
    ref = np.percentile([pr.max() / max(1, e[j + 1] - e[j]) for j, pr in enumerate(P)], 90)
    occ = ndimage.uniform_filter1d(m.mean(0), max(3, int(0.006 * W))); lab, n = ndimage.label(occ < 0.01); cuts = [0]
    for k in range(1, n + 1):
        xs = np.nonzero(lab == k)[0]
        if xs[-1] - xs[0] + 1 >= 0.006 * W and 0.15 * bw <= (xs[0] + xs[-1]) / 2 <= 0.85 * bw: cuts.append(int((xs[0] + xs[-1]) / 2))
    cuts.append(bw); out = []
    for c0, c1 in zip(cuts[:-1], cuts[1:]):
        if c1 - c0 < 0.12 * bw: continue
        for X in bc._line_chains(ink[:, c0:c1], z, strip_pt, pitch, ref):
            if len(X) < 6 or X[-1, 0] - X[0, 0] < 0.3 * (c1 - c0): continue
            for _ in range(2):
                f = np.polyfit(X[:, 0], X[:, 1], 1); res = np.abs(X[:, 1] - np.polyval(f, X[:, 0]))
                if len(X) > 6: X = X[res <= max(1.0, 2.5 * np.median(res))]
            if len(X) < 6: continue
            f = np.polyfit(X[:, 0], X[:, 1], 1); res = X[:, 1] - np.polyval(f, X[:, 0])
            xa, xb = int(X[0, 0]), int(X[-1, 0]); hit = []
            for x in range(xa, xb + 1):
                r = int(round(float(np.polyval(f, x))))
                band = ink[max(0, r - 1):min(bh, r + 2), c0 + x]
                hit.append(bool(band.size and band.max() >= 0.4))
            hit = np.array(hit); gap = 0; g = 0
            for h_ in hit:
                g = 0 if h_ else g + 1; gap = max(gap, g)
            out.append((round((float(np.polyval(f, (c1 - c0) / 2)) + y0) / z, 1), round(float(np.degrees(np.arctan(f[0]))), 3),
                        round(float(X[-1, 0] - X[0, 0]) / bw, 2), round(float(np.sqrt((res ** 2).mean())), 2), len(X),
                        round((x0 + c0 + xa) / z, 1), round((x0 + c0 + xb) / z, 1), round(float(hit.mean()), 3), round(gap / z, 1)))
    return sorted(out)


def view(doc, i, p, d):
    """wsim2's view (verify's: sheet, stamps and dot fields whitened) → (tracks_ext, the shear of the page's marks)"""
    tu = bc.Turner(doc, i); q = dict(p, skew=d); page = tu.page(d, *(p.get('move') or [0, 0])); a, z = bc.gray(page, 1000); a = a.copy()
    if p.get('sheet'): a = bc.whiten(a, z, bc.fwd_box(doc, i, q, p['sheet']))
    ex = [bc.pad_box(b, page.rect.width) for b in p.get('stamp') or []] + (p.get('dots') or [])
    exf = bc.fwd_boxes(doc, i, q, ex) if ex else []
    mk = bc.marks(a, z, page.rect.width, exf or None)
    sh = bc.skew_of(mk['xy'], raw=True)[0] if mk.get('xy') is not None else None
    for x in exf: a[max(0, int(x[1] * z)):int(x[3] * z) + 1, max(0, int(x[0] * z)):int(x[2] * z) + 1] = 255
    T = tracks_ext(a, mk['paper'], mk.get('text'), z) if mk.get('paper') else []
    if T and len(sys.argv) > 1 and os.environ.get('CHECK'):
        T5 = bc.line_tracks(a, mk['paper'], mk.get('text'), z)
        assert [t[:5] for t in T] == [tuple(t) for t in T5], (i, T5[:3], T[:3])
    tu.close(); return T, (round(float(sh), 3) if sh is not None else None)


def one(arg):
    h, items = arg; doc = pymupdf.open(C + h + '.pdf'); out = []
    for i, p in items:
        try:
            d = p['skew']; t0, s0 = view(doc, i, p, 0.0); t1, s1 = view(doc, i, p, d)
            out.append(json.dumps({'h': h, 'g': i + 1, 'd': d, 'fl': {k: p[k] for k in FL if p.get(k) is not None},
                                   's0': s0, 's1': s1, 't0': t0, 't1': t1}, ensure_ascii=False))
        except Exception as e: out.append(json.dumps({'h': h, 'g': i + 1, 'd': p.get('skew'), 'err': repr(e)[:120]}))
    doc.close(); return out


if __name__ == '__main__':
    args = sys.argv[1:]; J = 2
    if '-j' in args: k = args.index('-j'); J = int(args[k + 1]); del args[k:k + 2]
    out, recs = args[0], args[1:]
    done = set()
    if os.path.exists(out):
        for l in open(out):
            try: r = json.loads(l); done.add((r['h'], r['g']))
            except Exception: pass
    jobs = []
    for f in recs:
        h = os.path.basename(f)[:12]; R = json.load(open(f))
        it = [(i, p) for i, p in enumerate(R['pages']) if p.get('skew') and p.get('level_by_rules') is None
              and p.get('owner_turn') is None and (h, i + 1) not in done]
        for k in range(0, len(it), 12): jobs.append((h, it[k:k + 12]))
    print(len(jobs), 'chunks', flush=True)
    with open(out, 'a') as fo, ProcessPoolExecutor(J) as ex:
        for part in ex.map(one, jobs):
            for row in part: fo.write(row + '\n')
            fo.flush()
    print('done', flush=True)
