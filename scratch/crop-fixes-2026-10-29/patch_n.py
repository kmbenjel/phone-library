"""Fix N (2026-10-29, the review of regression 27m's diff): A TURN THE LINES' TRACKS SET IS READ AT THE TURNS BESIDE IT when they
cannot read it at its own. إرشاد الساري 10 (5b214426d112) ص 477 — the text and the margin commentary side by side, every line
−0.40 to −0.58° as scanned: 27l read the lines −0.537°, turned −0.525°, the tracks read the turned page −0.077° (34 lines,
spread 0.288°), corrected once to −0.6°: level (−0.008°). 27m read them −0.569° (fix L: the column rule a line now), turned
−0.575°: there the tracks' spread is 0.3° and over (two blocks' lines read across the page) — no reading; the shear measure
(0.6°: it calls −1.5° level on this page) could not confirm either, the projection loop's −1.5° was taken (fix Q5), guard W
undid it (every line made to lean 1°) and its median turn failed the same shear → the page left 0.55° tilted and listed as
two angles. Before the page goes down that road (only when the shear cannot confirm the turn either — what the tracks or
the shear confirm today stays exactly so), the turns 0.025° and 0.05° on either side are read; the one whose lines read
level (≤ 0.1°), the most level of them, is taken (tracks_near: the turn first tried). Same knife edge in 27l at −0.55°.
Usage: patch_n.py SRC DST   (SRC = code/bc_f.py: 4fcdf11f58 + fix F)"""
import sys
src, dst = sys.argv[1:3]
s = open(src, encoding='utf-8').read()

def sub(old, new):
    global s
    assert s.count(old) == 1, old[:80]
    s = s.replace(old, new)

sub('''            tk = tracks_tilt(mk['tracks']()) if mk.get('paper') else None
            if tk is not None and abs(tk[0]) > 0.05:
''', '''            tk = tracks_tilt(mk['tracks']()) if mk.get('paper') else None
            # (no reading at this turn, and the shear cannot confirm it either: the turns beside it — fix N, 2026-10-29,
            # إرشاد الساري 10 ص 477: text and margin commentary side by side, the lines' spread at the 0.3° limit — unread
            # at −0.575° and −0.55°, level at −0.6°; left 0.55° tilted when the shear, which calls −1.5° level there, had
            # the last word)
            if tk is None and mk.get('paper') and not (
                    p.get('tilt_by_proj') is not None and mk.get('xy') is not None
                    and (p.get('tilt_by_base') is None or base(i, p, mk, rb) is None) and abs(skew_of(mk['xy'], raw=True)[0]) <= 0.2):
                nb = []
                for k_ in (0.025, -0.025, 0.05, -0.05):
                    d_ = round(p['skew'] + k_, 3)
                    if abs(d_) < SKEW_MIN - 1e-9: continue
                    m_ = look(i, dict(p, skew=d_)); t_ = tracks_tilt(m_['tracks']()) if m_.get('paper') else None
                    if t_ is not None and abs(t_[0]) <= 0.1 + 1e-6: nb.append((abs(t_[0]), abs(k_), d_, m_, t_))
                if nb:
                    _, _, d_, m_, t_ = min(nb, key=lambda v: (v[0], v[1]))
                    p['tracks_near'] = p['skew']; p['skew'], mk, tk = d_, m_, t_
            if tk is not None and abs(tk[0]) > 0.05:
''')

open(dst, 'w', encoding='utf-8').write(s)
print('patched', dst)
