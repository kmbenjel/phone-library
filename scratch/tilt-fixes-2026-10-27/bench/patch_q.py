"""Fix Q (a projection turn set by the lines' baselines) on a copy of book_crop.py that already has fix P. Usage: patch_q.py SRC DST"""
import sys
src, dst = sys.argv[1:3]
s = open(src, encoding='utf-8').read()

def sub(old, new):
    global s
    assert s.count(old) == 1, old[:80]
    s = s.replace(old, new)

# the module's description (6. SECOND LOOK)
sub("""     page that shows a tilt the first look did not treat is turned here when (b) sees the tilt too (≥ 0.15°) and the turn
     passes the same tests; if (b) sees no tilt it is listed as disputed (`tilt_disputed`), otherwise as
     `untreated_tilt`. An untouched page cannot gain a tilt.
""", """     page that shows a tilt the first look did not treat is turned here when (b) sees the tilt too (≥ 0.15°) and the turn
     passes the same tests; if (b) sees no tilt it is listed as disputed (`tilt_disputed`), otherwise as
     `untreated_tilt`. An untouched page cannot gain a tilt.
   - A PAGE TURNED BY ITS IMAGE (the shear measure left it level — verse, short lines — while the page image lines up
     sharply at ≥ 0.3°: by_proj) is turned by its lines' baselines when at least 6 lines are read and agree (base_tilt:
     each line's baseline fitted to a fraction of a pixel, the median over the lines, 1,400 px); none under 0.2°. The
     second look reads them again on the turned page, corrects the turn once and keeps it when they read ≤ 0.1°.
""")

# the ruler
sub("""def edge_tilt(a, paper):
""", """def base_angles(a, paper, tb, z, K=16):
    \"\"\"EACH LINE'S BASELINE AS A RULER (2026-10-27): the projection path (by_proj) turned verse pages 0.15–0.25° beyond their
    tilt — خزانة الأدب ج 1 ص 68 tilted 0.11° was turned 0.325°, ص 110 tilted −0.80° turned −1.025°, its printed rule agreeing
    with the baselines — because its check, the shear measure, barely moves with the turn on such pages. The lines of the
    text block (tb, pt; z pixels per pt) at least a quarter of its width, each cut into K column chunks; in each chunk the
    baseline (in Arabic the densest ink row) found to a fraction of a pixel (a parabola through the peak row and its two
    neighbours); a straight line through the chunks, those furthest from it dropped twice → the line's angle, in the sign
    of the turn that levels it (read again after a turn d it gives angle − d, within ±0.05° on known turns). Returns
    [(y pt, angle)]\"\"\"
    if tb is None: return []
    H, W = a.shape; mx, my = 0.02 * W, 0.01 * H
    x0, y0 = max(0, int(tb[0] * z - mx)), max(0, int(tb[1] * z - my)); x1, y1 = min(W, int(tb[2] * z + mx)), min(H, int(tb[3] * z + my))
    if x1 - x0 < 50 or y1 - y0 < 50: return []
    ink = np.clip((paper - a[y0:y1, x0:x1].astype(float)) / max(paper, 1), 0, 1); bw = x1 - x0; out = []
    prof = ndimage.uniform_filter1d(ink.sum(1), max(3, int(0.0065 * W))); lab, n = ndimage.label(prof > 0.02 * prof.max())
    for k in range(1, n + 1):
        ys = np.nonzero(lab == k)[0]; r0, r1 = ys[0], ys[-1] + 1
        if r1 - r0 < 0.009 * W: continue
        pad = int(0.3 * (r1 - r0)); b = ink[max(0, r0 - pad):r1 + pad]
        xs = np.nonzero(b.sum(0) > 0.5)[0]
        if len(xs) < 2 or xs[-1] - xs[0] < 0.25 * bw: continue
        b = b[:, xs[0]:xs[-1] + 1]; e = np.linspace(0, b.shape[1], K + 1).astype(int); pts = []
        for j in range(K):
            pr = ndimage.gaussian_filter1d(b[:, e[j]:e[j + 1]].sum(1), 1.0)
            if pr.max() < 0.25 * (e[j + 1] - e[j]): continue      # (a chunk with little ink on any row: no baseline)
            r = int(np.argmax(pr))
            if 0 < r < len(pr) - 1:
                den = pr[r - 1] - 2 * pr[r] + pr[r + 1]; r = r + (0.5 * (pr[r - 1] - pr[r + 1]) / den if den < 0 else 0)
            pts.append(((e[j] + e[j + 1]) / 2, r))
        if len(pts) < 6: continue
        P = np.array(pts)
        for _ in range(2):
            f = np.polyfit(P[:, 0], P[:, 1], 1); res = np.abs(P[:, 1] - np.polyval(f, P[:, 0]))
            if len(P) > 6: P = P[res < max(np.percentile(res, 75), 0.5)]
        f = np.polyfit(P[:, 0], P[:, 1], 1)
        out.append((round(((r0 + r1) / 2 + y0) / z, 1), round(float(np.degrees(np.arctan(f[0]))), 3)))
    return out

def base_tilt(a, paper, tb, z):
    \"\"\"the page's tilt by its lines' baselines (base_angles): their median, when at least 6 lines are read and they agree —
    their interquartile range below 0.3° (a curled leaf, verse set hemistich by hemistich, a dictionary's short entries:
    the lines read too differently and the ruler is not used) → (angle, lines, IQR), else None\"\"\"
    an = [v[1] for v in base_angles(a, paper, tb, z)]
    if len(an) < 6: return None
    iq = float(np.subtract(*np.percentile(an, [75, 25])))
    return (round(float(np.median(an)), 3), len(an), round(iq, 3)) if iq < 0.3 else None

def edge_tilt(a, paper):
""")

# the first look: the turn of a projection page
sub("""            if rec.get('tilt_by_proj') is not None:      # a projection turn: angles around its reading (it is coarse), the
                best = None                              # one after which the page reads level by its own ink is kept
""", """            # THE LINES' BASELINES SET A PROJECTION TURN (2026-10-27): the loop below takes, among angles 0.2° apart, the one
            # the shear measure reads most level, and on the pages the projection turns that reading barely moves with the
            # turn — of the 1,314 such pages of the 31 regression books whose lines agree, 10 % were left ≥ 0.2° off by their
            # own baselines and 127 were turned for a tilt under 0.2° (printed rules agreeing with the baselines: خزانة الأدب
            # ج 1 ص 68 and 110). When at least 6 lines are read and agree (base_tilt, 1,400 px, the page as scanned, its
            # stamps and dot fields left out), their median is the turn, or no turn under 0.2°; else the loop, as before
            bt = None
            if rec.get('tilt_by_proj') is not None and mk.get('text'):
                a3, z3 = gray(page, 1400); a3 = whiten(np.array(a3), z3, sh)
                for b in ex0 or []: a3[max(0, int(b[1] * z3)):int(b[3] * z3) + 1, max(0, int(b[0] * z3)):int(b[2] * z3) + 1] = 255
                bt = base_tilt(a3, mk['paper'], mk['text'], z3)
            if bt is not None:
                rec['tilt_by_base'] = bt[0]
                if abs(bt[0]) >= SKEW_MIN:
                    deg = round(round(bt[0] / 0.025) * 0.025, 3)
                    a2, z2 = gray(tu().page(deg), 500); a2 = whiten(a2, z2, fwd_box(doc, i, {'skew': deg}, sh) if sh else None)
                    mk2 = marks(a2, z2, r.width, fwd_boxes(doc, i, {'skew': deg}, ex0) if ex0 else None)
                    if mk2['box'] is not None and mk2['xy'] is not None: rec['skew'] = deg; mk = mk2
                ang = 0.0                                # (neither loop below is run for it)
            elif rec.get('tilt_by_proj') is not None:    # a projection turn: angles around its reading (it is coarse), the
                best = None                              # one after which the page reads level by its own ink is kept
""")

# the second look: the ruler on a view at 1,400 px (shared with guard G's line measure)
sub("""    def leans(i, q, m):                               # each line of a view on its own (line_leans), at 1,400 px — the page
        mv = q.get('move') or [0, 0]                  # as look() sees it (sheet, stamps), finer: only the third rule asks
        page = cur['tu'].page(q.get('skew') or 0, mv[0], mv[1]); a, z = gray(page, 1400); a = a.copy(); pq = rec['pages'][i]
        if pq.get('sheet'): a = whiten(a, z, fwd_box(doc, i, q, pq['sheet']))
        ex = [pad_box(b, page.rect.width) for b in pq.get('stamp') or []] + (pq.get('dots') or [])
        for b in (fwd_boxes(doc, i, q, ex) if ex else []):
            a[max(0, int(b[1] * z)):int(b[3] * z) + 1, max(0, int(b[0] * z)):int(b[2] * z) + 1] = 255
        return line_leans(a, m['paper'], m.get('text'), z) if m.get('paper') else []
""", """    def fine(i, q):                                   # a view at 1,400 px, the page as look() sees it (sheet, stamps): for
        mv = q.get('move') or [0, 0]                  # the measures that read single lines
        page = cur['tu'].page(q.get('skew') or 0, mv[0], mv[1]); a, z = gray(page, 1400); a = a.copy(); pq = rec['pages'][i]
        if pq.get('sheet'): a = whiten(a, z, fwd_box(doc, i, q, pq['sheet']))
        ex = [pad_box(b, page.rect.width) for b in pq.get('stamp') or []] + (pq.get('dots') or [])
        for b in (fwd_boxes(doc, i, q, ex) if ex else []):
            a[max(0, int(b[1] * z)):int(b[3] * z) + 1, max(0, int(b[0] * z)):int(b[2] * z) + 1] = 255
        return a, z
    def leans(i, q, m):                               # each line of a view on its own (line_leans) — only the third rule asks
        a, z = fine(i, q); return line_leans(a, m['paper'], m.get('text'), z) if m.get('paper') else []
    def base(i, q, m):                                # the lines' baselines of a view (base_tilt), once per view
        if '_base' not in m:
            a, z = fine(i, q); m['_base'] = base_tilt(a, m['paper'], m.get('text'), z) if m.get('paper') else None
        return m['_base']
""")

# the second look: a turn the baselines set is checked by them
sub("""        if not lbr and p.get('skew') and p.get('tilt_by_proj') is not None and mk.get('xy') is not None:   # turned by the
""", """        # A TURN ITS LINES' BASELINES SET (tilt_by_base): read again by them on the page as the reader sees it, corrected once
        # when they still read more than 0.05° (the ruler is linear; never below 0.2°), kept when they read ≤ 0.1°; else the
        # ordinary checks below decide — not the shear measure's ≤ 0.2°, which such pages pass at almost any turn
        if not lbr and p.get('skew') and p.get('tilt_by_base') is not None:
            b = base(i, p, mk)
            if b is not None and abs(b[0]) > 0.05:
                d2 = round(round((p['skew'] + b[0]) / 0.025) * 0.025, 3)
                if abs(d2) >= SKEW_MIN:
                    q2 = dict(p, skew=d2); m2 = look(i, q2); b2 = base(i, q2, m2)
                    if b2 is not None and abs(b2[0]) < abs(b[0]): p['skew'], mk, b = d2, m2, b2
            if b is not None and abs(b[0]) <= 0.1 + 1e-6: lbr = True; p['level_by_base'] = b[0]
        if not lbr and p.get('skew') and p.get('tilt_by_proj') is not None and p.get('tilt_by_base') is None and mk.get('xy') is not None:   # turned by the
""")

# the book's list of pages still tilted
sub("""                            and not (p.get('level_by_proj') is not None and p['level_by_proj'] <= 0.2)
""", """                            and not (p.get('level_by_proj') is not None and p['level_by_proj'] <= 0.2)
                            and not (p.get('level_by_base') is not None and abs(p['level_by_base']) <= 0.1 + 1e-6)
""")
open(dst, 'w', encoding='utf-8').write(s)
print('patched', dst)
