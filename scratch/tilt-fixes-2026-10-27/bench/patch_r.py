"""Fix R (a tilt the measures' gates left, turned by the lines' baselines when the shear measure agrees) on a copy of book_crop.py
that already has fixes P and Q. Usage: patch_r.py SRC DST"""
import sys
src, dst = sys.argv[1:3]
s = open(src, encoding='utf-8').read()

def sub(old, new):
    global s
    assert s.count(old) == 1, old[:80]
    s = s.replace(old, new)

sub("""     second look reads them again on the turned page, corrects the turn once and keeps it when they read ≤ 0.1°.
""", """     second look reads them again on the turned page, corrects the turn once and keeps it when they read ≤ 0.1°.
   - A page still left as scanned, of one column, with no level printed rule or frame over its text, whose lines agree on
     a tilt of 0.25° or more — what the eye sees on a full line — that the shear measure of the whole page reads too (within
     0.15°), is turned by its baselines, kept when they then read ≤ 0.1° (base_found).
""")


sub("""                        else: p['untreated_tilt'] = round(u, 3)   # disagree; or its lines do — lines_lean)
        # THE OWNER'S TURN (data/crop/owner-turns.tsv""", """                        else: p['untreated_tilt'] = round(u, 3)   # disagree; or its lines do — lines_lean)
        # A TILT THE MEASURES' GATES LEFT (2026-10-27): of 478 sampled pages of the regression books left as scanned whose lines
        # agree, 26 read ≥ 0.25° by their baselines, the other rulers mostly reading the same — the halves' test refused a whole
        # page's angle that its narrower halves read smaller (روضة المستبين ص 491: −0.35° whole, −0.10 / −0.20° halves, every
        # ruler 0.29–0.35°), the projection read 0.225–0.275° under its 0.3° start, the shear's gain fell short of 1.02 by a
        # thousandth (مشتبهات القرآن ص 66). A page still unturned here, of one column, with no level printed rule or frame over
        # its text and no lines a turn was refused for: turned by its baselines (base_tilt) when they read ≥ 0.25° and the
        # shear measure of the whole page reads the same tilt (within 0.15°); kept when the baselines then read ≤ 0.1° and the
        # page still shows its ink
        if not p.get('skew') and ct is None and mk.get('xy') is not None and p.get('kind') == 'text' and not p.get('lines_lean') \\
           and p.get('frame_level') is None and p.get('proj_level_rule') is None and not mk.get('level_frame') \\
           and (owner_turns or {}).get(i + 1) is None:
            r_, g_ = skew_of(mk['xy'], raw=True); tb_ = mk.get('text')   # (the shear first: the baselines are read only when
            b = base(i, p, mk) if g_ >= 1.02 and abs(r_) >= 0.1 and tb_ is not None else None   # it sees a tilt at all)
            if b is not None and abs(b[0]) >= 0.25 - 1e-6 and abs(-r_ - b[0]) <= 0.15 + 1e-6 and not any(
                    abs(h[0]) <= 0.2 and h[1] >= tb_[0] - 0.02 * (tb_[2] - tb_[0]) and h[3] <= tb_[2] + 0.02 * (tb_[2] - tb_[0])
                    and h[2] >= tb_[1] - 0.03 * (tb_[3] - tb_[1]) and h[4] <= tb_[3] + 0.03 * (tb_[3] - tb_[1]) for h in mk.get('hrules') or []):
                d = round(round(b[0] / 0.025) * 0.025, 3); q2 = dict(p, skew=d); m2 = look(i, q2); b2 = base(i, q2, m2)
                al0 = p.get('allowed'); bd = banded(al0, p['w'], p['h'])
                if m2['xy'] is not None and b2 is not None and abs(b2[0]) <= 0.1 + 1e-6 \\
                   and 0.6 <= ink_ratio(mk, m2, mk['z'], al0 if bd else None, fwd_inner(doc, i, q2, al0) if bd else None) <= 5.0:
                    for k in ('untreated_tilt', 'tilt_disputed', 'unsure_tilt'): p.pop(k, None)
                    p.update(skew=d, tilt_by_base=b[0], level_by_base=b2[0], base_found=round(-r_, 3), turned_in_check=True)
                    mk = m2
        # THE OWNER'S TURN (data/crop/owner-turns.tsv""")
open(dst, 'w', encoding='utf-8').write(s)
print('patched', dst)
