"""Fix H (2026-10-28, regression 26i's diff): A SCAN LINE BROKEN INTO DASHES IS NO LETTER at the first look. marks() reads the
text block by gaps from letter-like marks; its thin-line rule takes a line ≤ 0.4 % thick only when ≥ 3 % of the width long,
so a scan line broken into one-pixel pieces 5–17 pt long counted as letters: on خزانة الأدب ج 1 ص 53 and 176 and on
35fbe344b8c6 ص 74, 194, 247 and 491 the pieces of the scan's top line (1.2 pt thick) joined the text block — one of them read
as the page number at the head — and the box was pulled ≈ 20 pt up over the very line the owner had it avoid (2026-10-18).
26h had the same pieces outside the text's columns by a point or two (another turn): the page fell either way. The second
look already reads print only (printlike, 2026-10-26); the first look now does likewise for horizontal hairlines: a mark
under 2.5 px thick and ≥ 4× as long is a letter only when a letter of the page stands on its row (its middle within that
letter's height) within the text's gap (1.5 % of the width) — a printed dash «—» between words, the dashes of «- ٥ -» stay.
Upright hairlines (an alif, a «١») are left as they were.
Usage: patch_h.py SRC DST"""
import sys
src, dst = sys.argv[1:3]
s = open(src, encoding='utf-8').read()

def sub(old, new):
    global s
    assert s.count(old) == 1, old[:80]
    s = s.replace(old, new)

sub('''    letter = ~strip & ~thin & (hh <= 0.15 * H) & ((hh >= 0.004 * H) | (ww >= 0.008 * Wd))
    if not letter.any(): letter = ~strip if (~strip).any() else np.ones(len(cid), bool)
''', '''    letter = ~strip & ~thin & (hh <= 0.15 * H) & ((hh >= 0.004 * H) | (ww >= 0.008 * Wd))
    # A SCAN LINE BROKEN INTO DASHES is no letter (2026-10-28, regression 26i: خزانة الأدب ج 1 ص 53, 176, 35fbe344b8c6
    # ص 74, 194, 247, 491 — one-pixel pieces of the scan's top line joined the text block, one read as the page number, and
    # the box was pulled ≈ 20 pt over the line): a horizontal hairline (under 2.5 px thick, ≥ 4× as long) is a letter only
    # when a letter of the page stands on its row (its middle within that letter's height) within the text's gap — a printed
    # dash «—», the dashes of «- ٥ -»
    hair = letter & (hh < 2.5) & (ww >= 4 * hh)
    if hair.any():
        oth = letter & ~hair; ym = (Y0 + Y1) / 2
        for k in np.nonzero(hair)[0]:
            if not (oth & (Y0 <= ym[k]) & (Y1 >= ym[k]) & (X0 <= X1[k] + gx) & (X1 >= X0[k] - gx)).any(): letter[k] = False
    if not letter.any(): letter = ~strip if (~strip).any() else np.ones(len(cid), bool)
''')
open(dst, 'w', encoding='utf-8').write(s)
print('patched', dst)
