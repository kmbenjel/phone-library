"""Fix Q3 v2 (2026-10-27): fix Q set a projection page's turn by its lines' baselines only when base_tilt read the page — at
least 6 lines within an IQR of 0.3°. On the 26h projection pages (2,194 of 3,085 read as scanned) it read 40 %: on the others
lines run together in the row profile and the projection's 0.2°-step loop set the turn — judged by the lines followed across
the page (line_tracks) it left ≥ 0.2° on 18–23 % of them. Now, when base_tilt cannot read a projection page: (1) the lines
followed across it (line_tracks at 1,000 px: ≥ 5 lines read well, printed rules left out, IQR < 0.3°) set the turn
(tilt_by_tracks); (2) only when they cannot either, the baselines with lines more than 1° from their median left out
(base_tilt robust=True; tilt_by_base + base_robust). The second look reads the turned page with the same ruler: corrected
once, kept when ≤ 0.1° (level_by_tracks / level_by_base); when it cannot read the turned page, the shear's ≤ 0.2° (fix Q2).
Why tracks first (v1 had the robust baselines first): on pages base_tilt fails the baselines' ruler is not linear in the turn
(خزانة 01 ص 318 turned −0.55/−0.65/−0.8 read −0.166/−0.13/+0.079); v1 corrected ص 233 from 0.425 to 0.3 and ص 318 from −0.65
to −0.8 against both rulers as scanned; the head rule sides with the tracks on ص 77 (+0.96°, tracks 1.00°, robust 0.79°) and
ص 233 (+0.53°, tracks 0.46°). Pages base_tilt reads keep fix Q as in 3205efa17f; R (base_found) unchanged.
Usage: patch_q3.py SRC DST"""
import sys
src, dst = sys.argv[1:3]
s = open(src, encoding='utf-8').read()

def sub(old, new):
    global s
    assert s.count(old) == 1, old[:80]
    s = s.replace(old, new)

sub('''def base_tilt(a, paper, tb, z):
    """the page's tilt by its lines' baselines (base_angles): their median, when at least 6 lines are read and they agree —
    their interquartile range below 0.3° (a curled leaf, verse set hemistich by hemistich, a dictionary's short entries:
    the lines read too differently and the ruler is not used) → (angle, lines, IQR), else None"""
    an = [v[1] for v in base_angles(a, paper, tb, z)]
    if len(an) < 6: return None
''', '''def base_tilt(a, paper, tb, z, robust=False):
    """the page's tilt by its lines' baselines (base_angles): their median, when at least 6 lines are read and they agree —
    their interquartile range below 0.3° (a curled leaf, verse set hemistich by hemistich, a dictionary's short entries:
    the lines read too differently and the ruler is not used) → (angle, lines, IQR), else None. robust: a line more than
    1° from their median (two lines run together in the row profile) is left out before they are counted — the last
    resort for a projection page neither base_tilt nor the lines' tracks read (fix Q3, 2026-10-27)"""
    an = np.array([v[1] for v in base_angles(a, paper, tb, z)])
    if robust and len(an): an = an[np.abs(an - np.median(an)) <= 1.0]
    if len(an) < 6: return None
''')

sub('''def _line_chains(ink, z, strip_pt, pitch, ref):''', '''def tracks_tilt(T):
    """the page's tilt by its lines followed across it (line_tracks): the median of the lines read well (≤ 1 px from their
    straight line at 1,000 px, ≥ 6 strips, ≥ 30 % of the block; printed rules left out) when at least 5 are read and agree —
    their interquartile range below 0.3° → (angle, lines, IQR), else None (2026-10-27: where base_tilt reads too, the two
    agree to a median 0.023°, 96 % within 0.1°)"""
    an = [t[1] for t in T if t[3] <= 1.0 and t[4] >= 6 and t[2] >= 0.3 and not t[5]]
    if len(an) < 5: return None
    iq = float(np.subtract(*np.percentile(an, [75, 25])))
    return (round(float(np.median(an)), 3), len(an), round(iq, 3)) if iq < 0.3 else None

def _line_chains(ink, z, strip_pt, pitch, ref):''')

sub('''                bt = base_tilt(a3, mk['paper'], mk['text'], z3)
            if bt is not None:
                rec['tilt_by_base'] = bt[0]
''', '''                bt = base_tilt(a3, mk['paper'], mk['text'], z3)
                # (when the baselines cannot read it: the lines FOLLOWED ACROSS THE PAGE — line_tracks at 1,000 px, as the
                # second look reads them; when these cannot either, the baselines without the lines run together)
                if bt is None:
                    a4, z4 = gray(page, 1000); a4 = whiten(np.array(a4), z4, sh)
                    for b in ex0 or []: a4[max(0, int(b[1] * z4)):int(b[3] * z4) + 1, max(0, int(b[0] * z4)):int(b[2] * z4) + 1] = 255
                    bt = tracks_tilt(line_tracks(a4, mk['paper'], mk['text'], z4))
                    if bt is not None: rec['tilt_by_tracks'] = bt[0]
                    else:
                        bt = base_tilt(a3, mk['paper'], mk['text'], z3, robust=True)
                        if bt is not None: rec['base_robust'] = True
            if bt is not None:
                if rec.get('tilt_by_tracks') is None: rec['tilt_by_base'] = bt[0]
''')

sub('''    def base(i, q, m):                                # the lines' baselines of a view (base_tilt), once per view
        if '_base' not in m:
            a, z = fine(i, q); m['_base'] = base_tilt(a, m['paper'], m.get('text'), z) if m.get('paper') else None
        return m['_base']
''', '''    def base(i, q, m, robust=False):                  # the lines' baselines of a view (base_tilt), once per view
        k = '_base_r' if robust else '_base'
        if k not in m:
            a, z = fine(i, q); m[k] = base_tilt(a, m['paper'], m.get('text'), z, robust) if m.get('paper') else None
        return m[k]
''')

sub('''        if not lbr and p.get('skew') and p.get('tilt_by_base') is not None:
            b = base(i, p, mk)
            if b is not None and abs(b[0]) > 0.05:
                d2 = round(round((p['skew'] + b[0]) / 0.025) * 0.025, 3)
                if abs(d2) >= SKEW_MIN:
                    q2 = dict(p, skew=d2); m2 = look(i, q2); b2 = base(i, q2, m2)
                    if b2 is not None and abs(b2[0]) < abs(b[0]): p['skew'], mk, b = d2, m2, b2
            if b is not None and abs(b[0]) <= 0.1 + 1e-6: lbr = True; p['level_by_base'] = b[0]
        if not lbr and p.get('skew') and p.get('tilt_by_proj') is not None and mk.get('xy') is not None \\
           and (p.get('tilt_by_base') is None or base(i, p, mk) is None):                                      # turned by the
''', '''        rb = bool(p.get('base_robust'))                  # (the robust baselines read it again: fix Q3's last resort)
        if not lbr and p.get('skew') and p.get('tilt_by_base') is not None:
            b = base(i, p, mk, rb)
            if b is not None and abs(b[0]) > 0.05:
                d2 = round(round((p['skew'] + b[0]) / 0.025) * 0.025, 3)
                if abs(d2) >= SKEW_MIN:
                    q2 = dict(p, skew=d2); m2 = look(i, q2); b2 = base(i, q2, m2, rb)
                    if b2 is not None and abs(b2[0]) < abs(b[0]): p['skew'], mk, b = d2, m2, b2
            if b is not None and abs(b[0]) <= 0.1 + 1e-6: lbr = True; p['level_by_base'] = b[0]
        # A TURN THE LINES FOLLOWED ACROSS THE PAGE SET (tilt_by_tracks: the baselines could not read it): read again by them on
        # the page as the reader sees it (this look's line_tracks), corrected once, kept when they read ≤ 0.1°; when they
        # cannot read the turned page, the shear's ≤ 0.2° below, as for the baselines' turns
        tk = None
        if not lbr and p.get('skew') and p.get('tilt_by_tracks') is not None:
            tk = tracks_tilt(mk['tracks']()) if mk.get('paper') else None
            if tk is not None and abs(tk[0]) > 0.05:
                d2 = round(round((p['skew'] + tk[0]) / 0.025) * 0.025, 3)
                if abs(d2) >= SKEW_MIN:
                    q2 = dict(p, skew=d2); m2 = look(i, q2); t2 = tracks_tilt(m2['tracks']()) if m2.get('paper') else None
                    if t2 is not None and abs(t2[0]) < abs(tk[0]): p['skew'], mk, tk = d2, m2, t2
            if tk is not None and abs(tk[0]) <= 0.1 + 1e-6: lbr = True; p['level_by_tracks'] = tk[0]
        if not lbr and p.get('skew') and p.get('tilt_by_proj') is not None and mk.get('xy') is not None \\
           and (p.get('tilt_by_base') is None or base(i, p, mk, rb) is None) and tk is None:                   # turned by the
''')
open(dst, 'w', encoding='utf-8').write(s)
print('patched', dst)
