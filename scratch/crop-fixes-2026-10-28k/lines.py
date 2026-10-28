"""lines.py BOOK PAGE TURN… — each line followed across the page (line_tracks at 1,000 px, as verify's look) as scanned
and as turned by each TURN; lines_read / two_angles as guard W judges them (code/bc_j.py)"""
import sys, os
S = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, S + '/code'); sys.path.insert(1, '/home/k/projects/phone-library/scripts')
import bc_j as bc, pymupdf
h, pg = sys.argv[1], int(sys.argv[2]); path = os.path.expanduser(f'~/.cache/phone-library/crop-regress/{h}.pdf')
doc = pymupdf.open(path); tu = bc.Turner(doc, pg - 1)
def tracks(d):
    page = tu.page(d, 0, 0); a, z = bc.gray(page, 1000); mk = bc.marks(a, z, page.rect.width)
    return bc.line_tracks(a, mk['paper'], mk.get('text'), z)
t0 = tracks(0)
ok = lambda t: t[3] <= 1.0 and t[4] >= 6 and t[2] >= 0.3
print('as scanned (y, angle, span, rms, strips, rule):')
for t in t0: print('   ', t, '' if ok(t) else '(not read well)')
for d in map(float, sys.argv[3:]):
    L = bc.lines_read(t0, tracks(d), d); tw = bc.two_angles(L)
    agree = sum(1 for v in L if abs(v[2]) <= 0.35 + 1e-6) if L else 0
    print(f'turn {d}: lines read {len(L) if L else None}, agree ≤0.35 {agree}, made worse {len(tw)} → refused {bool(tw)}')
    for v in L or []: print('   ', v, '<< worse' if v in tw else '')
