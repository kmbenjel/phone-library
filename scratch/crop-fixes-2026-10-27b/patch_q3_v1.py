"""Fix Q3 (2026-10-27): fix Q set a projection page's turn by its lines' baselines only when base_tilt read the page — at
least 6 lines within an IQR of 0.3°. On the 26h projection pages (robust-study.tsv: 2,194 of 3,085 read as scanned) it read
40 %: a quarter of the lines run together (two lines tilted ≈ 1° or set tight merge in the row profile: أنساب الأشراف المقدمة
ص 44 read −2.4°, +9.1°, +4.3° among clean lines at 0.00–0.10°; خزانة 01 ص 110 at −0.8°: 4 of 16) and the spread fails.
(1) base_tilt leaves out a line more than 1° from the lines' median before it counts them — +19 % of the projection pages
read; judged by the independent ruler (line_tracks), the 26h turns left ≥ 0.2° on 23.4 % of those pages, the baselines'
turn on 2.4 % (median 0.112° → 0.048°). (2) When even so the baselines cannot read a projection page, the lines followed
across it (line_tracks at 1,000 px: ≥ 5 lines read well, printed rules left out, IQR < 0.3°) set the turn (tilt_by_tracks)
— 28 % of the projection pages; where both rulers read they agree to a median 0.023°. In the second look the same ruler
reads the turned page: corrected once, kept when ≤ 0.1° (level_by_tracks); when it cannot read the turned page, the shear's
≤ 0.2° as for the baselines' turns (fix Q2). Usage: patch_q3.py SRC DST"""
import sys
src, dst = sys.argv[1:3]
s = open(src, encoding='utf-8').read()

def sub(old, new):
    global s
    assert s.count(old) == 1, old[:80]
    s = s.replace(old, new)

sub('''    the lines read too differently and the ruler is not used) → (angle, lines, IQR), else None"""
    an = [v[1] for v in base_angles(a, paper, tb, z)]
    if len(an) < 6: return None
''', '''    the lines read too differently and the ruler is not used) → (angle, lines, IQR), else None. A line more than 1° from
    their median is two lines run together in the row profile (lines tilted about 1° or set tight: أنساب الأشراف المقدمة
    ص 44 read −2.4°, +9.1°, +4.3° among clean lines at 0.00–0.10°; خزانة 01 ص 110 at −0.8°: 4 of 16) — left out before
    they are counted (2026-10-27: +19 % of the projection pages read, judged by line_tracks the turns left ≥ 0.2° fell from
    23 % to 2.4 % of them)"""
    an = np.array([v[1] for v in base_angles(a, paper, tb, z)])
    if len(an): an = an[np.abs(an - np.median(an)) <= 1.0]
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
                # (the lines FOLLOWED ACROSS THE PAGE when the baselines cannot read it — line_tracks at 1,000 px, as the
                # second look reads them: a fifth of the 26h projection pages they alone read, turned ≥ 0.2° off on 18 %)
                if bt is None:
                    a4, z4 = gray(page, 1000); a4 = whiten(np.array(a4), z4, sh)
                    for b in ex0 or []: a4[max(0, int(b[1] * z4)):int(b[3] * z4) + 1, max(0, int(b[0] * z4)):int(b[2] * z4) + 1] = 255
                    bt = tracks_tilt(line_tracks(a4, mk['paper'], mk['text'], z4))
                    if bt is not None: rec['tilt_by_tracks'] = bt[0]
            if bt is not None:
                if rec.get('tilt_by_tracks') is None: rec['tilt_by_base'] = bt[0]
''')

sub('''            if b is not None and abs(b[0]) <= 0.1 + 1e-6: lbr = True; p['level_by_base'] = b[0]
        if not lbr and p.get('skew') and p.get('tilt_by_proj') is not None and mk.get('xy') is not None \\
           and (p.get('tilt_by_base') is None or base(i, p, mk) is None):                                      # turned by the
''', '''            if b is not None and abs(b[0]) <= 0.1 + 1e-6: lbr = True; p['level_by_base'] = b[0]
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
           and (p.get('tilt_by_base') is None or base(i, p, mk) is None) and tk is None:                       # turned by the
''')
open(dst, 'w', encoding='utf-8').write(s)
print('patched', dst)
