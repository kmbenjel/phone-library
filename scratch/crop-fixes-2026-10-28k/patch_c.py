"""Fix C (2026-10-28, regression 26j: خزانة الأدب ج 1 ص 1 lost its year «١٣٨٧ هـ = ١٩٦٧ م» again). cover_window moves the
cut off the middle to keep a line of print only when the other end's plain ground takes the whole cut AND 3 pt beyond the
print at both ends. Fix H dropped the scan line from 34 pages' text blocks (their boxes had reached it: 25–37 pt taller),
the book's box became 15.6 pt shorter (401.46 → 385.85) and the cover's window 413.1 pt tall: its print, 148.4–560.4 =
412.0 pt, still fits — with 1.1 pt to spare, not 6 — so the even cut was kept and the year went. Now the ground kept beyond
the print is 3 pt when there is room, else what there is, shared alike at both ends (never below 0: a print taller than
the window keeps the even cut). Wherever the old rule moved the window the move is the same (proved: with ≥ 6 pt to spare,
or the move clipped to the cut, both give the same move); it only adds a move where the print fits with under 6 pt to spare.
Usage: patch_c.py SRC DST"""
import sys
src, dst = sys.argv[1:3]
s = open(src, encoding='utf-8').read()

def sub(old, new):
    global s
    assert s.count(old) == 1, old[:80]
    s = s.replace(old, new)

sub('''            need = (lo + d - min(m[I0] for m in lost) + 3) if s < 0 else (max(m[I1] for m in lost) - (hi - d) + 3)
            if need < 2 or need - 3 > d: continue
            need = min(need, d)
            plain = (hi - max(m[I1] for m in mk)) if s < 0 else (min(m[I0] for m in mk) - lo)
            if plain < d + need + 3 or (not vert and plain < 0.4 * cw): continue
            move = s * need; break
''', '''            need = (lo + d - min(m[I0] for m in lost)) if s < 0 else (max(m[I1] for m in lost) - (hi - d))   # (just whole)
            if need < -1 or need > d: continue
            plain = (hi - max(m[I1] for m in mk)) if s < 0 else (min(m[I0] for m in mk) - lo)
            # the ground beyond the print: 3 pt at both ends when there is room, else what there is, alike at both ends
            # (2026-10-28: fix H made خزانة الأدب ج 1's box 15.6 pt shorter — its cover's print fits the window with 1.1 pt
            # to spare, and asking 3 + 3 cut the year again)
            e = min(3.0, (plain - d - need) / 2)
            if e < 0 or (not vert and plain < 0.4 * cw): continue
            move = s * min(need + e, d); break
''')
open(dst, 'w', encoding='utf-8').write(s)
print('patched', dst)
