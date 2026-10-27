"""dbgw.py BOOK PAGE TURN — guard W's reading of one page (vis.py's 1,000-px views, without verify's stamp whitening):
every line both views read, lines_read's verdict and two_angles' lines"""
import sys, os
sys.path.insert(0, os.path.expanduser("~/.local/share/phone-library-tools/site"))
sys.path.insert(0, '/tmp/claude-1000/-home-k-projects-phone-library/fcd8d325-9813-40ca-94ce-bd6c86424307/scratchpad/w/code')
import numpy as np, pymupdf
import bc_w2 as bc
C = '/home/k/.cache/phone-library/crop-regress/'
h, g, d = sys.argv[1], int(sys.argv[2]), float(sys.argv[3])
doc = pymupdf.open(C + h + '.pdf'); T = []
for turn in (0.0, d):
    tu = bc.Turner(doc, g - 1); page = tu.page(turn, 0, 0); a, z = bc.gray(page, 1000); a = a.copy(); pw = page.rect.width; tu.close()
    mk = bc.marks(a, z, pw); T.append(bc.line_tracks(a, mk['paper'], mk.get('text'), z))
ok = lambda t: t[3] <= 1.0 and t[4] >= 6 and t[2] >= 0.3
print('as scanned:', [(t[0], t[1], t[2], t[3]) for t in T[0] if ok(t)])
print('turned    :', [(t[0], t[1], t[2], t[3]) for t in T[1] if ok(t)])
L = bc.lines_read(T[0], T[1], d)
print('lines_read:', L)
if L:
    print('median step', float(np.median(np.abs(np.diff([v[1] for v in L])))))
print('two_angles:', bc.two_angles(L))
