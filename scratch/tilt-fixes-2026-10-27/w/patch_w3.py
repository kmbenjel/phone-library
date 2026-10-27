"""Guard W, step 3 (2026-10-27, after replaying W on 9 books' recipes: two index pages of خريدة القصر 01 left as scanned
though their turn levels their head rules): line_tracks marks each line that is a printed rule (the ink unbroken along it),
and a turn the print certifies — every rule read level once turned while the lines of text give no reading (too few, or
readings that jump at more than a quarter of the steps) — is not undone. Where the text does give a reading the rules stay
lines among the others (a warped leaf's footnote rule bends with it: رسوم دار الخلافة ص 101). Applied on a copy of
book_crop.py that has guard W (patch_w.py). Usage: patch_w3.py SRC DST"""
import sys
src, dst = sys.argv[1:3]
s = open(src, encoding='utf-8').read()

def sub(old, new):
    global s
    assert s.count(old) == 1, old[:80]
    s = s.replace(old, new)

# the module's description
sub("""     measure agreeing: then the first turn was off, and the page is turned by its lines (`level_by_tracks`). A turn its
     printed rules certified (a table: its column rules stand straight once turned, the owner's word on خريدة القصر ص 649)
     and the owner's own turns stay.
""", """     measure agreeing: then the first turn was off, and the page is turned by its lines (`level_by_tracks`). A turn its
     printed rules certified (a table: its column rules stand straight once turned, the owner's word on خريدة القصر ص 649)
     and the owner's own turns stay; so does a turn that levels every printed rule across the text (a head rule, a
     frame's side) when the lines of text give no reading — an index under a head rule, its entries' readings scattered
     by guillemets and digits (`level_by_print`).
""")

# the ruler: each line says whether it is a printed rule
sub("""    strips and 30 % of its column, the points furthest from it dropped twice. Returns [(y pt, angle, share of the block's
    width, rms px, points)] — the angle in the sign of the turn that levels the line, as base_angles (read on the page turned
    by d, a line reads its angle − d)\"\"\"
""", """    strips and 30 % of its column, the points furthest from it dropped twice. Returns [(y pt, angle, share of the block's
    width, rms px, points, rule)] — the angle in the sign of the turn that levels the line, as base_angles (read on the page
    turned by d, a line reads its angle − d); rule: a printed rule, not a line of text — the ink unbroken along it (≥ 90 %
    of its span, a line of text 50–80 %; no gap over 6 pt)\"\"\"
""")
sub("""            f = np.polyfit(X[:, 0], X[:, 1], 1); res = X[:, 1] - np.polyval(f, X[:, 0])
            out.append((round((float(np.polyval(f, (c1 - c0) / 2)) + y0) / z, 1), round(float(np.degrees(np.arctan(f[0]))), 3),
                        round(float(X[-1, 0] - X[0, 0]) / bw, 2), round(float(np.sqrt((res ** 2).mean())), 2), len(X)))
""", """            f = np.polyfit(X[:, 0], X[:, 1], 1); res = X[:, 1] - np.polyval(f, X[:, 0])
            xs = np.arange(int(X[0, 0]), int(X[-1, 0]) + 1); rs = np.rint(np.polyval(f, xs)).astype(int)
            hit = np.array([ink[max(0, r - 1):max(0, r + 2), c0 + x].max(initial=0) >= 0.4 for x, r in zip(xs, rs)])
            rule = bool(hit.mean() >= 0.9 and (np.diff(np.concatenate(([-1], np.nonzero(hit)[0], [len(hit)]))) - 1).max() <= 6 * z)
            out.append((round((float(np.polyval(f, (c1 - c0) / 2)) + y0) / z, 1), round(float(np.degrees(np.arctan(f[0]))), 3),
                        round(float(X[-1, 0] - X[0, 0]) / bw, 2), round(float(np.sqrt((res ** 2).mean())), 2), len(X), rule))
""")

# the print's certificate
sub("""def edge_tilt(a, paper):
""", """def print_turn(t0, t1, d):
    \"\"\"A TURN THE PRINT CERTIFIES (2026-10-27): the page's printed rules (line_tracks' rule lines, read in both views alike —
    their angle moved by the turn within 0.15°) all stand level once turned (≤ 0.15°), and its lines of text give no reading
    of their own (lines_read on them alone: none, or readings that jump over 0.3° at more than a quarter of the steps — an
    index's entries, guillemets and digits beside the words: خريدة القصر 01 ص 703 jumped 0.5–1° at four of nine steps; its
    ص 637's table rows read +0.8° against the head rules' −0.5°, the same misreading in both views). A rule is the print's
    straightest line. Where the text does give a reading, two_angles has already weighed the rules among the lines (a
    warped leaf's footnote rule bends with it — رسوم دار الخلافة ص 101: the turn left it 0.66°). → (certified, the rules
    [(y, before, after)])\"\"\"
    ok = lambda t: t[3] <= 1.0 and t[4] >= 6 and t[2] >= 0.3
    R = []
    for t in t0:
        if not (ok(t) and t[5]): continue
        m_ = [u for u in t1 if ok(u) and abs(u[0] - t[0]) <= 6]
        if not m_: continue
        u = min(m_, key=lambda u: abs(u[0] - t[0]))
        if abs(u[1] - (t[1] - d)) <= 0.15 + 1e-6: R.append((t[0], t[1], round(t[1] - d, 3)))
    if not R or any(abs(v[2]) > 0.15 + 1e-6 for v in R): return False, R
    LT = lines_read([t for t in t0 if not t[5]], [t for t in t1 if not t[5]], d)
    if LT and float((np.abs(np.diff([v[1] for v in LT])) > 0.3 + 1e-6).mean()) <= 0.25: return False, R
    return True, R

def edge_tilt(a, paper):
""")

# the guard: the certificate before the turn is undone
sub("""            mz = look(i, {k: v for k, v in p.items() if k != 'skew'})
            L = lines_read(mz['tracks'](), look(i, p)['tracks'](), p['skew']); tw = two_angles(L)
            if tw:
                d0 = p.pop('skew')
""", """            mz = look(i, {k: v for k, v in p.items() if k != 'skew'})
            t0, t1 = mz['tracks'](), look(i, p)['tracks']()
            L = lines_read(t0, t1, p['skew']); tw = two_angles(L)
            if tw:                                    # (the print's certificate: every rule level once turned, the text
                cert, R = print_turn(t0, t1, p['skew'])   # giving no reading of its own — an index under its head rule)
                if cert: tw = []; p['level_by_print'] = [list(v) for v in R]
            if tw:
                d0 = p.pop('skew')
""")
# (patch_w.py's line continuation inside its string literal was swallowed: the fallback's test ran on as one long line)
sub("len(L2)" + " " * 20 + "and m2['xy'] is not None", "len(L2) \\\n" + " " * 19 + "and m2['xy'] is not None")
open(dst, 'w', encoding='utf-8').write(s)
print('patched', dst)
