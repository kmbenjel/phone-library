"""Fix L (2026-10-28, regression 27l's diff): A LINE IS THIN BY ITS INK, NOT BY ITS BOX. marks() takes a long thin mark (≤ 0.6 %
of the page thick, ≥ 20 % long) and a shorter one beyond the text block (≤ 0.4 % thick, ≥ 3 % long) for a line — no content —
by the height of its box. Every turn tilts the scanner's own lines with the page: at 500 px a level one-pixel scan line 80 px
long is 2–3 px tall once the page is turned 0.5–0.8°, and 0.4 % of the height is 2.8 px. So the line fell to content by a
fraction of a pixel and joined the text block, at one turn and not the next: خزانة الأدب ج 2 ص 315 (0.5°: a scan line with a
hook at its end, 76 × 3 px, ink 1.8 px — the box took it in, the page shrunk to 0.86 and the book's height rose 3.6 pt) and
00597fea27cf ص 332 (−0.8°: 83 × 3 px, ink 1.1 px — the box pulled 29 pt off the text); 0.025° away both were read as stains,
by chance. Now a mark at a slant (its box at most the limit + a tenth of its length tall) is as thin as a level one when
its ink is: column by column at most the limit thick (90th percentile) and its middles on one straight line within a
pixel (90th percentile), sloping ≤ 0.1 — letters are thick in their stems and do not lie on a line. Both rules, both ways.
Usage: patch_l.py SRC DST"""
import sys
src, dst = sys.argv[1:3]
s = open(src, encoding='utf-8').read()

def sub(old, new):
    global s
    assert s.count(old) == 1, old[:80]
    s = s.replace(old, new)

sub('''    lines = {i for i in content if (wid[i] <= 0.006 * Wd and hgt[i] >= 0.2 * H) or (hgt[i] <= 0.006 * H and wid[i] >= 0.2 * Wd)}
    for i in content:                                 # a shorter thin line (≥ 3 % long, ≤ 0.4 % thick) beyond the text block
        s_ = objs[i - 1]                              # (خزانة الأدب ص 18: 64 × 1.2 pt above the running head)
        yc, xc = (s_[0].start + s_[0].stop) / 2, (s_[1].start + s_[1].stop) / 2
        if (hgt[i] <= 0.004 * H and wid[i] >= 0.03 * Wd and (yc <= cy0 - g or yc >= cy1 + g)) or \\
           (wid[i] <= 0.004 * Wd and hgt[i] >= 0.03 * H and (xc <= cx0 - g or xc >= cx1 + g)): lines.add(i)
''', '''    # A LINE IS THIN BY ITS INK, NOT BY ITS BOX (2026-10-28, regression 27l): every turn tilts the scanner's lines with the
    # page — a level one-pixel scan line 80 px long is 2–3 px tall once turned 0.5–0.8°, over the 0.4 % (2.8 px) by a
    # fraction of a pixel, and joined the text block at one turn and not the next (خزانة الأدب ج 2 ص 315, a hook at its end:
    # the page shrunk to 0.86; 00597fea27cf ص 332: the box 29 pt off the text). A mark at a slant (its box at most the
    # limit + a tenth of its length tall) is as thin as a level one when its ink is: column by column at most the limit
    # thick and its middles on one straight line within a pixel (90th percentiles), sloping ≤ 0.1 — letters are not
    def straight_thin(i, horiz, lim):
        s_ = objs[i - 1]; ys_, xs_ = np.nonzero(lab[s_] == i)
        if not horiz: ys_, xs_ = xs_, ys_
        n_ = int(xs_.max()) + 1; cnt = np.bincount(xs_, minlength=n_); has = cnt > 0
        if has.sum() < 0.8 * n_ or np.percentile(cnt[has], 90) > lim: return False
        xs1 = np.nonzero(has)[0]; mid = np.bincount(xs_, weights=ys_, minlength=n_)[has] / cnt[has]
        fit = np.polyfit(xs1, mid, 1)
        return abs(fit[0]) <= 0.1 and np.percentile(np.abs(mid - np.polyval(fit, xs1)), 90) <= 1.0
    slant = set()                                     # (the lines found only by their ink: the recipe's slant_lines)
    def thin_h(i, lim):
        if hgt[i] <= lim: return True
        if hgt[i] <= lim + 0.1 * wid[i] and straight_thin(i, True, lim): slant.add(i); return True
        return False
    def thin_v(i, lim):
        if wid[i] <= lim: return True
        if wid[i] <= lim + 0.1 * hgt[i] and straight_thin(i, False, lim): slant.add(i); return True
        return False
    lines = {i for i in content if (hgt[i] >= 0.2 * H and thin_v(i, 0.006 * Wd)) or (wid[i] >= 0.2 * Wd and thin_h(i, 0.006 * H))}
    for i in content:                                 # a shorter thin line (≥ 3 % long, ≤ 0.4 % thick) beyond the text block
        s_ = objs[i - 1]                              # (خزانة الأدب ص 18: 64 × 1.2 pt above the running head)
        yc, xc = (s_[0].start + s_[0].stop) / 2, (s_[1].start + s_[1].stop) / 2
        if (wid[i] >= 0.03 * Wd and (yc <= cy0 - g or yc >= cy1 + g) and thin_h(i, 0.004 * H)) or \\
           (hgt[i] >= 0.03 * H and (xc <= cx0 - g or xc >= cx1 + g) and thin_v(i, 0.004 * Wd)): lines.add(i)
    cset = set(content)                               # the detached pieces of a line: grains of its group lying along it,
    for i in list(lines):                             # within its rows (columns) ± 1 px — a scan line the turn broke
        s_ = objs[i - 1]; horiz = wid[i] >= hgt[i]    # (خزانة الأدب ج 2 ص 315: a 3 × 1 px piece 2 px off its end held
        for j in members[int(gid[i])]:                # the box 36 pt up)
            if j in lines or j not in cset or not small[j]: continue
            t = objs[j - 1]
            if (horiz and t[0].start >= s_[0].start - 1 and t[0].stop <= s_[0].stop + 1) or \\
               (not horiz and t[1].start >= s_[1].start - 1 and t[1].stop <= s_[1].stop + 1):
                lines.add(j)
                if i in slant: slant.add(j)
''')
sub('''    out['lines'] = [box_of(i) for i in sorted(lines)]
''', '''    out['lines'] = [box_of(i) for i in sorted(lines)]
    out['slant_lines'] = [box_of(i) for i in sorted(slant)]
''')
sub('''                   rules=mk.get('rules', []), lines=mk.get('lines', []), text=mk.get('text'), margin=mk.get('margin', []), folio=mk.get('folio'))
''', '''                   rules=mk.get('rules', []), lines=mk.get('lines', []), text=mk.get('text'), margin=mk.get('margin', []), folio=mk.get('folio'))
        if mk.get('slant_lines'): rec['slant_lines'] = mk['slant_lines']   # (fix L's own: the lines found by their ink)
''')
open(dst, 'w', encoding='utf-8').write(s)
print('patched', dst)
