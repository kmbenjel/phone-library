"""Fix N3 (2026-10-30, the review of regression 27n's diff): FIX N AS A LAST RESORT. Fix N read the turns beside a turn the
lines' tracks set but could not read (and the shear could not confirm), BEFORE the other measures had their say — on 27n's
first 9 books it changed two pages besides its own, both for the worse: القوافي للتنوخي (8109) p. 102, a warped page (head
prose level as scanned, footnotes 0.7°): 3 lines read at −0.7°, N took −0.675° where 4 footnotes of 5 lines read level, the
rule under the text then leaning 0.29° (27m −0.45°: −0.06°); معجم تيمور الكبير 02 (9da5) p. 166: 18 lines, spread 0.323° at
−0.85°, N took −0.875° (spread 0.299°) over the −0.65° the other measures confirm (after 0.125°, image 0.1°) — the head rule
0.29° instead of 0.07° (/tmp/claude-1000/r27n: turnrows.py, tracksprobe.py). N3: the turn is only REMEMBERED there (ncand,
and only when ≥ 5 lines were read — refused for their spread, as N's note says; fix N2); the turns beside it are read after
guard W, when the page is left unturned (two angles, unsure, disputed or untreated) — إرشاد الساري 10 ص 477, N's own page
(34 lines, spread 0.325° at −0.575°; the loop's −1.5° undone by W), still −0.6° — and the turn taken must pass W's own line
check (two_angles). Its reach is within fix N's (27n's «tracks: a turn beside» pages).
Usage: patch_n3.py SRC DST   (SRC = scripts/book_crop.py a0e20119c2 = code/bc_fn.py)"""
import sys
src, dst = sys.argv[1:3]
s = open(src, encoding='utf-8').read()

def sub(old, new):
    global s
    assert s.count(old) == 1, old[:80]
    s = s.replace(old, new)

# the lines tracks_tilt weighs, shared (N3 asks how many were read)
sub('''    an = [t[1] for t in T if t[3] <= 1.0 and t[4] >= 6 and t[2] >= 0.3 and not t[5]]
    if len(an) < 5: return None
''', '''    an = tracks_read(T)
    if len(an) < 5: return None
''')
sub('''def tracks_tilt(T):
''', '''def tracks_read(T):
    """(tracks_tilt) the angles of the lines read well: ≤ 1 px from their straight line at 1,000 px, ≥ 6 strips, ≥ 30 % of
    the block, printed rules left out"""
    return [t[1] for t in T if t[3] <= 1.0 and t[4] >= 6 and t[2] >= 0.3 and not t[5]]

def tracks_tilt(T):
''')
# N's search at the tracks' turn → the turn remembered
sub('''        tk = None
        if not lbr and p.get('skew') and p.get('tilt_by_tracks') is not None:
''', '''        tk = ncand = None
        if not lbr and p.get('skew') and p.get('tilt_by_tracks') is not None:
''')
sub('''            # (no reading at this turn, and the shear cannot confirm it either: the turns beside it — fix N, 2026-10-29,
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
''', '''            # (lines read at this turn but refused for their spread, and the shear cannot confirm it either: the turn is
            # remembered for the turns beside it, read only if the page is left unturned below — fix N3)
            if tk is None and mk.get('paper') and len(tracks_read(mk['tracks']())) >= 5 and not (
                    p.get('tilt_by_proj') is not None and mk.get('xy') is not None
                    and (p.get('tilt_by_base') is None or base(i, p, mk, rb) is None) and abs(skew_of(mk['xy'], raw=True)[0]) <= 0.2):
                ncand = p['skew']
''')
# the turns beside it, after guard W, when the page is left unturned
sub('''                else:
                    p['two_angles'] = d0; p['lines_lean'] = [list(v) for v in tw]; mk = mz
''', '''                else:
                    p['two_angles'] = d0; p['lines_lean'] = [list(v) for v in tw]; mk = mz
        # THE TURNS BESIDE THE LINES' OWN, A LAST RESORT (fixes N 2026-10-29, N3 2026-10-30): a turn the lines' tracks set,
        # read there but refused for their spread, that the shear could not confirm (ncand) is read at the turns 0.025° and
        # 0.05° beside it — only when the page is left unturned (two angles, unsure, disputed, untreated): إرشاد الساري 10
        # ص 477, text and margin commentary side by side, unread at −0.575°, level at −0.6° (the loop's −1.5° undone by guard
        # W). Read before the other measures (fix N), they overrode turns those confirm: القوافي للتنوخي p. 102 −0.45° →
        # −0.675°, معجم تيمور 02 p. 166 −0.65° → −0.875° — readings squeaking under the 0.3° spread, the rules then leaning
        # 0.29°. The most level of them (≤ 0.1°) is taken if it makes no lines lean (two_angles, as guard W)
        if ncand is not None and not p.get('skew') and (owner_turns or {}).get(i + 1) is None and any(
                p.get(k) is not None for k in ('two_angles', 'unsure_tilt', 'tilt_disputed', 'untreated_tilt')):
            mz = look(i, {k: v for k, v in p.items() if k != 'skew'}); nb = []
            for k_ in (0.025, -0.025, 0.05, -0.05):
                d_ = round(ncand + k_, 3)
                if abs(d_) < SKEW_MIN - 1e-9 or not mz.get('paper'): continue
                m_ = look(i, dict(p, skew=d_)); t_ = tracks_tilt(m_['tracks']()) if m_.get('paper') else None
                if t_ is not None and abs(t_[0]) <= 0.1 + 1e-6 and not two_angles(lines_read(mz['tracks'](), m_['tracks'](), d_)):
                    nb.append((abs(t_[0]), abs(k_), d_, m_, t_))
            if nb:
                _, _, d_, m_, t_ = min(nb, key=lambda v: (v[0], v[1]))
                for k in ('two_angles', 'lines_lean', 'unsure_tilt', 'tilt_disputed', 'untreated_tilt', 'loop_fallback', 'level_by_proj'):
                    p.pop(k, None)
                p.update(skew=d_, tracks_near=ncand, level_by_tracks=t_[0]); mk = m_
''')

open(dst, 'w', encoding='utf-8').write(s)
print('patched', dst)
