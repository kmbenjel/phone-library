"""Guard W (lines at two angles: no turn makes lines lean more — owner 2026-10-27 «Leave as scanned») on a copy of book_crop.py
that already has fixes P, Q and R. Usage: patch_w.py SRC DST"""
import sys
src, dst = sys.argv[1:3]
s = open(src, encoding='utf-8').read()

def sub(old, new):
    global s
    assert s.count(old) == 1, old[:80]
    s = s.replace(old, new)

# the module's description (6. SECOND LOOK)
sub("""     0.15°), is turned by its baselines, kept when they then read ≤ 0.1° (base_found).
""", """     0.15°), is turned by its baselines, kept when they then read ≤ 0.1° (base_found).
   - LINES AT TWO ANGLES (owner 2026-10-27, on crop-tilt-002: «Leave as scanned»): every turn, whatever found it, is checked
     line by line (line_tracks: each line followed across the page strip by strip, column by column, so that lines lying at
     different angles are each read), on the page as scanned and as turned — a line counts when both read it alike. A turn
     that leaves two or more lines more tilted than they were — at least 0.5°, and 0.25° more than before — when they are
     a fifth of the lines read, or the lines do not take the turn (fewer than 80 % of them level once turned), is undone: a
     warped photocopy whose upper lines are level and lower ones tilted, a block of lines at its own angle, have no single
     turn; an index whose column edges lean while its lines stand level is not tilted. Only lines that follow one another
     decide (scattered readings — short index entries — do not). The page stays as scanned and is listed (`two_angles`),
     unless the turn its lines do take (their median) makes none of them worse and levels four fifths of them, the shear
     measure agreeing: then the first turn was off, and the page is turned by its lines (`level_by_tracks`). A turn its
     printed rules certified (a table: its column rules stand straight once turned, the owner's word on خريدة القصر ص 649)
     and the owner's own turns stay.
""")

# the ruler
sub("""def edge_tilt(a, paper):
""", """def _line_chains(ink, z, strip_pt, pitch, ref):
    \"\"\"(line_tracks) the chains of baseline peaks of one column of a text block: in every strip about strip_pt wide the peaks
    of the ink-row profile (in Arabic the baseline is the densest row; a parabola through the peak gives a fraction of a
    pixel), at most one within 0.45 of the line pitch and at least a quarter as dark as a full strip's (ref: per pixel of
    width); each peak linked to the line heading towards it in the next strips (within a fifth of the pitch, up to 3 strips
    on: the space between words) → [array of (x, y) px]\"\"\"
    bh, bw = ink.shape
    K = max(3, int(round(bw / (strip_pt * z)))); e = np.linspace(0, bw, K + 1).astype(int); peaks = []
    for j in range(K):
        pr = ndimage.gaussian_filter1d(ink[:, e[j]:e[j + 1]].sum(1), 1.0)
        mxf = ndimage.maximum_filter1d(pr, 2 * max(2, int(0.45 * pitch)) + 1); pk = []
        for r in np.nonzero((pr == mxf) & (pr >= 0.25 * ref * (e[j + 1] - e[j])))[0]:
            rr = float(r)
            if 0 < r < len(pr) - 1:
                den = pr[r - 1] - 2 * pr[r] + pr[r + 1]
                if den < 0: rr = r + 0.5 * (pr[r - 1] - pr[r + 1]) / den
            pk.append(rr)
        peaks.append(pk)
    chains = []                                       # [points, last strip]
    for j in range(K):
        xc = (e[j] + e[j + 1]) / 2; cand = []
        for ci, (pts, last) in enumerate(chains):
            if j - last > 3: continue
            if len(pts) >= 3: X = np.array(pts); yp = np.polyval(np.polyfit(X[:, 0], X[:, 1], 1), xc)
            else: yp = pts[-1][1]
            cand += [(abs(y - yp), ci, k) for k, y in enumerate(peaks[j]) if abs(y - yp) <= 0.2 * pitch]
        uc, uk = set(), set()
        for _, ci, k in sorted(cand):
            if ci in uc or k in uk: continue
            uc.add(ci); uk.add(k); chains[ci][0].append((xc, peaks[j][k])); chains[ci][1] = j
        chains += [[[(xc, y)], j] for k, y in enumerate(peaks[j]) if k not in uk]
    return [np.array(c[0]) for c in chains]

def line_tracks(a, paper, tb, z, strip_pt=21.0):
    \"\"\"EACH LINE FOLLOWED ACROSS THE PAGE (2026-10-27, owner on crop-tilt-002: a page whose lines lie at two angles is left as
    scanned): base_angles and line_leans find the lines on the page's row profile, where lines tilted about 1° run into each
    other (الموسوعة الشاملة 38 ص 892: its lower paragraph read −9.2°, +3.7° and −8.1°). Here each line is followed strip by
    strip (_line_chains) inside the text block (tb, pt; z pixels per pt): its vertical rules and frame sides (an ink run down a
    quarter of the block) whitened, the block cut at its white gutters (≥ 0.6 % of the page wide, inside 15–85 % of the
    block: an index in columns — a line is never linked across them), the line pitch read from the strips' row profiles
    correlated with themselves (narrow strips: a tilt barely blurs them); a straight line through each chain of at least 6
    strips and 30 % of its column, the points furthest from it dropped twice. Returns [(y pt, angle, share of the block's
    width, rms px, points)] — the angle in the sign of the turn that levels the line, as base_angles (read on the page turned
    by d, a line reads its angle − d)\"\"\"
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
    hi = min(bh // 2, int(0.08 * W)); up = np.nonzero(np.diff(ac[:hi]) > 0)[0]   # (the pitch past the central lobe)
    if len(up) == 0: return []
    lo = max(3, int(up[0])); pitch = lo + int(np.argmax(ac[lo:hi]))
    if ac[pitch] <= 0.05 * ac[0]: pitch = int(0.035 * W)   # (no rhythm of lines: an ordinary page's pitch)
    ref = np.percentile([pr.max() / max(1, e[j + 1] - e[j]) for j, pr in enumerate(P)], 90)
    occ = ndimage.uniform_filter1d(m.mean(0), max(3, int(0.006 * W))); lab, n = ndimage.label(occ < 0.01); cuts = [0]
    for k in range(1, n + 1):
        xs = np.nonzero(lab == k)[0]
        if xs[-1] - xs[0] + 1 >= 0.006 * W and 0.15 * bw <= (xs[0] + xs[-1]) / 2 <= 0.85 * bw: cuts.append(int((xs[0] + xs[-1]) / 2))
    cuts.append(bw); out = []
    for c0, c1 in zip(cuts[:-1], cuts[1:]):
        if c1 - c0 < 0.12 * bw: continue
        for X in _line_chains(ink[:, c0:c1], z, strip_pt, pitch, ref):
            if len(X) < 6 or X[-1, 0] - X[0, 0] < 0.3 * (c1 - c0): continue
            for _ in range(2):
                f = np.polyfit(X[:, 0], X[:, 1], 1); res = np.abs(X[:, 1] - np.polyval(f, X[:, 0]))
                if len(X) > 6: X = X[res <= max(1.0, 2.5 * np.median(res))]
            if len(X) < 6: continue
            f = np.polyfit(X[:, 0], X[:, 1], 1); res = X[:, 1] - np.polyval(f, X[:, 0])
            out.append((round((float(np.polyval(f, (c1 - c0) / 2)) + y0) / z, 1), round(float(np.degrees(np.arctan(f[0]))), 3),
                        round(float(X[-1, 0] - X[0, 0]) / bw, 2), round(float(np.sqrt((res ** 2).mean())), 2), len(X)))
    return sorted(out)

def lines_read(t0, t1, d):
    \"\"\"the lines a turn d can be judged by: line_tracks of the page as scanned (t0) and as turned by d (t1). A line counts when
    it is read well (≤ 1 px from its straight line at 1,000 px, ≥ 6 strips, ≥ 30 % of the block) and the same in both views —
    its angle moved by the turn within 0.15° (a line misread — an index entry's guillemets, digits and signs — is not read
    alike twice); they must follow one another (the median change from one line to the next ≤ 0.25°: a warped leaf's tilt
    grows line by line, a block of lines stands at its own angle; scattered readings are no reading). → [(y, before, after)]
    by height, or None (fewer than 5)\"\"\"
    ok = lambda t: t[3] <= 1.0 and t[4] >= 6 and t[2] >= 0.3
    B = [u for u in t1 if ok(u)]; L = []
    for t in t0:
        if not ok(t): continue
        m_ = [u for u in B if abs(u[0] - t[0]) <= 6]
        if m_ and abs(min(m_, key=lambda u: abs(u[0] - t[0]))[1] - (t[1] - d)) <= 0.15 + 1e-6: L.append((t[0], t[1], round(t[1] - d, 3)))
    L.sort()
    if len(L) < 5 or float(np.median(np.abs(np.diff([v[1] for v in L])))) > 0.25 + 1e-6: return None
    return L

def two_angles(L):
    \"\"\"A TURN THE LINES DO NOT TAKE (owner: «ولم نصطنع ميلا جديدا»; 2026-10-27, «Leave as scanned» for a page whose lines lie
    at two angles), judged on lines_read: a line is made worse when it ends ≥ 0.5° and ≥ 0.25° more tilted than it was →
    those lines [(y, before, after)] when two or more are, and they are a fifth of the lines or the lines do not take the
    turn (fewer than 80 % of them within 0.35° of level once turned); else []\"\"\"
    if not L: return []
    w = [v for v in L if abs(v[2]) >= max(0.5, abs(v[1]) + 0.25) - 1e-6]
    agree = sum(1 for v in L if abs(v[2]) <= 0.35 + 1e-6)
    return w if len(w) >= 2 and (len(w) >= 0.2 * len(L) or agree < 0.8 * len(L)) else []

def edge_tilt(a, paper):
""")

# the views: the lines followed across the page, once per view
sub("""        mk['cols'] = lambda: once('cols', lambda: columns_tilt(a, mk['paper']) if mk.get('paper') else None)
        cur['looks'][key] = mk
""", """        mk['cols'] = lambda: once('cols', lambda: columns_tilt(a, mk['paper']) if mk.get('paper') else None)
        def tracks():                                 # (stamps and dot fields whitened, as fine() does)
            b = a.copy()
            for x in (fwd_boxes(doc, i, q, ex) if ex else []):
                b[max(0, int(x[1] * z)):int(x[3] * z) + 1, max(0, int(x[0] * z)):int(x[2] * z) + 1] = 255
            return line_tracks(b, mk['paper'], mk.get('text'), z)
        mk['tracks'] = lambda: once('tracks', lambda: tracks() if mk.get('paper') else [])
        cur['looks'][key] = mk
""")

# the guard: after every path (fix R's included), before the owner's turn
sub("""        # THE OWNER'S TURN (data/crop/owner-turns.tsv, owner 2026-10-25 on crop-tilt-001: «أجيز هذا وجميع ما سبق»): a page he
""", """        # LINES AT TWO ANGLES (owner 2026-10-27, crop-tilt-002 «Leave as scanned»): a warped photocopy whose upper lines stand
        # level and lower ones lie 1–1.5° (الموسوعة الشاملة 38 ص 892, 42, 423: the tilt grows down the page) was turned by its
        # average — 0.7° on ص 892 left its upper lines 0.6–1.0° and its lower ones up to 0.75°; صبح الأعشى 05 ص 234, its last
        # section level under lines tilted 0.4–0.7°, turned 0.675°: the section leaned 0.7°; indexes whose column edges lean
        # while their lines stand level (2a8c4bfeff47 ص 37، 47؛ فهرس الرواة 0c32c1a4815b ص 183: turned 0.43–0.51° by the
        # columns, every line then leaning). Every turn, whatever found it, is checked line by line on the page as scanned and
        # as turned (line_tracks, two_angles): when it leaves two or more lines more tilted than they were, and they are a fifth
        # of the lines read or the lines do not take the turn, it is undone and the page listed. (Footnotes set at their own
        # angle — 2 lines of 20, مناقب أحمد ص 208 — may follow the text, as every turn lets them.) A table's turn its column
        # rules certified stays: a sheared scan whose rules and lines disagree (خريدة القصر ص 627: rules 0.7°, lines 0.25°)
        # — the owner had ص 649 turned by its rules
        if p.get('skew') and p.get('level_by_rules') is None and (owner_turns or {}).get(i + 1) is None:
            mz = look(i, {k: v for k, v in p.items() if k != 'skew'})
            L = lines_read(mz['tracks'](), look(i, p)['tracks'](), p['skew']); tw = two_angles(L)
            if tw:
                d0 = p.pop('skew')
                for k in ('after_tilt', 'after_tilt_image', 'turned_in_check'): p.pop(k, None)
                # (the turn the lines do take — their median — when it makes none of them worse, leaves four fifths of them
                # within 0.2° of level, read alike again, and the shear measure of the page then reads ≤ 0.2°: the first turn
                # was off, the page is not at two angles — خزانة الأدب ج 4 ص 469: lines −0.36°, turned −0.75° by the
                # projection's 0.2° steps; turned −0.35° every ruler reads it level)
                m = round(round(float(np.median([v[1] for v in L])) / 0.025) * 0.025, 3); L2 = None
                if abs(m) >= SKEW_MIN:
                    q2 = dict(p, skew=m); m2 = look(i, q2); L2 = lines_read(mz['tracks'](), m2['tracks'](), m)
                if L2 and not two_angles(L2) and sum(1 for v in L2 if abs(v[2]) <= 0.2 + 1e-6) >= 0.8 * len(L2) \
                   and m2['xy'] is not None and abs(skew_of(m2['xy'], raw=True)[0]) <= 0.2 + 1e-6:
                    p['skew'] = m; p['turn_by_tracks'] = d0; p['level_by_tracks'] = round(float(np.median([v[2] for v in L2])), 3)
                    p['after_tilt'] = round(abs(skew_of(m2['xy'], raw=True)[0]), 3); p['after_tilt_image'] = m2['proj'](); mk = m2
                else:
                    p['two_angles'] = d0; p['lines_lean'] = [list(v) for v in tw]; mk = mz
        # THE OWNER'S TURN (data/crop/owner-turns.tsv, owner 2026-10-25 on crop-tilt-001: «أجيز هذا وجميع ما سبق»): a page he
""")

# the book's lists
sub("""                            and not (p.get('level_by_base') is not None and abs(p['level_by_base']) <= 0.1 + 1e-6)
""", """                            and not (p.get('level_by_base') is not None and abs(p['level_by_base']) <= 0.1 + 1e-6)
                            and not (p.get('level_by_tracks') is not None and abs(p['level_by_tracks']) <= 0.2 + 1e-6)
""")
sub("""    rec['unsure_tilt'] = [i + 1 for i, p in enumerate(rec['pages']) if p.get('unsure_tilt')]
""", """    rec['unsure_tilt'] = [i + 1 for i, p in enumerate(rec['pages']) if p.get('unsure_tilt')]
    rec['two_angles'] = [i + 1 for i, p in enumerate(rec['pages']) if p.get('two_angles') is not None and not p.get('skew')]
""")
open(dst, 'w', encoding='utf-8').write(s)
print('patched', dst)
