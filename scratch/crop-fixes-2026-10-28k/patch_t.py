"""Fix T (2026-10-28, regression 26j: صبح الأعشى ج 5 ص 234 «turn no» failed). Guard W (two_angles) undoes a turn that
leaves two or more lines «made worse» — ending ≥ 0.5° and ≥ 0.25° more tilted than they were — when they are a fifth of
the lines read or the lines do not take the turn (fewer than 80 % within 0.35° of level). On ص 234 the main text stands at
−0.35 to −0.66° and its last section («الجملة الثالثة», 3 lines of 15) level: the projection's −0.675° made those three lean
0.64–0.77° and was undone (26i), but fixes G and Q3 read the main text truly (−0.42 / −0.44°) and their −0.425° made them
lean 0.39 / 0.52 / 0.45° — one line over 0.5°, so the turn stayed. The 0.5° bar does not fit the guard's own scale: a line
within 0.35° of level is one that «takes the turn» (the line just below), and the owner sees 0.25° on a full line (SKEW_MIN).
The bar matters only for lines that were near level (for any line already ≥ 0.25° off, «0.25° more» is ≥ 0.5° anyway):
a near-level line made to lean beyond 0.35° is a new tilt (owner: «ولم نصطنع ميلا جديدا»; crop-tilt-002 «Leave as scanned»).
Now a line is made worse when it ends beyond 0.35° and ≥ 0.25° more tilted than it was. Usage: patch_t.py SRC DST"""
import sys
src, dst = sys.argv[1:3]
s = open(src, encoding='utf-8').read()

def sub(old, new):
    global s
    assert s.count(old) == 1, old[:80]
    s = s.replace(old, new)

sub('''    at two angles), judged on lines_read: a line is made worse when it ends ≥ 0.5° and ≥ 0.25° more tilted than it was →
    those lines [(y, before, after)] when two or more are, and they are a fifth of the lines or the lines do not take the
    turn (fewer than 80 % of them within 0.35° of level once turned); else []"""
    if not L: return []
    w = [v for v in L if abs(v[2]) >= max(0.5, abs(v[1]) + 0.25) - 1e-6]
''', '''    at two angles), judged on lines_read: a line is made worse when it ends beyond 0.35° — the band within which a line
    takes the turn, below — and ≥ 0.25° more tilted than it was → those lines [(y, before, after)] when two or more are, and
    they are a fifth of the lines or the lines do not take the turn (fewer than 80 % of them within 0.35° of level once
    turned); else []. (The bar was 0.5° until 2026-10-28: صبح الأعشى ج 5 ص 234's level last section, three lines of
    fifteen, leaned 0.39–0.52° under the −0.425° that fixes G and Q3 read in its main text, and the turn stayed — a near-level
    line made to lean beyond 0.35° is a new tilt: «ولم نصطنع ميلا جديدا»)"""
    if not L: return []
    w = [v for v in L if abs(v[2]) > 0.35 + 1e-6 and abs(v[2]) >= abs(v[1]) + 0.25 - 1e-6]
''')
open(dst, 'w', encoding='utf-8').write(s)
print('patched', dst)
