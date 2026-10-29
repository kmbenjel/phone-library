"""wcheck.py BOOK PAGE [VARIANT=MD5 …] — guard W (book_crop.verify: the line check on a turn) replayed on ONE page under each
code variant (crop-fixes-2026-10-28m/code/bc_<v>.py) with that variant's regression recipe (its turn, or the turn it refused):
the text block line_tracks reads in, each view's tracks, lines_read and two_angles — why a variant keeps or refuses a turn.
Default variants: base=6a1fad7b21 (27l) lbb5=4fcdf11f58 (27m). For 27m's turn of صبح الأعشى 05 ص 367 (2026-10-29)."""
import sys, json, importlib, glob, os
sys.path.insert(0, '/home/k/projects/phone-library/scratch/crop-fixes-2026-10-28m/code'); sys.path.insert(1, '/home/k/projects/phone-library/scripts')
C = os.path.expanduser('~/.cache/phone-library/crop-regress/')
h, pg = sys.argv[1], int(sys.argv[2]); i = pg - 1
vs = [a.split('=') for a in sys.argv[3:]] or [('base', '6a1fad7b21'), ('lbb5', '4fcdf11f58')]
r1 = lambda b: [round(x, 1) for x in b[:4]] if b else b
for v, md in vs:
    bc = importlib.import_module('bc_' + v)
    rec = json.load(open(sorted(glob.glob(f'{C}{h}.{md}*.json'))[-1])); P = rec['pages'][i]
    d = P.get('skew') or P.get('two_angles'); mv = P.get('move') or [0, 0]
    doc = bc.pymupdf.open(f'{C}{h}.pdf'); tu = bc.Turner(doc, i)
    def look(t):
        q = dict(P, skew=t); page = tu.page(t or 0, mv[0], mv[1]); a, z = bc.gray(page, 1000)
        if P.get('sheet'): a = bc.whiten(a, z, bc.fwd_box(doc, i, q, P['sheet']))
        ex = [bc.pad_box(b, page.rect.width) for b in P.get('stamp') or []] + (P.get('dots') or [])
        fb = bc.fwd_boxes(doc, i, q, ex) if ex else None
        mk = bc.marks(a, z, page.rect.width, fb)
        b = a.copy()
        for x in fb or []: b[max(0, int(x[1] * z)):int(x[3] * z) + 1, max(0, int(x[0] * z)):int(x[2] * z) + 1] = 255
        return mk, (bc.line_tracks(b, mk['paper'], mk.get('text'), z) if mk.get('paper') else [])
    m0, t0 = look(None); m1, t1 = look(d)
    L = bc.lines_read(t0, t1, d); tw = bc.two_angles(L)
    print(f'== {v} ({md}) p. {pg}: recipe skew {P.get("skew")} two_angles {P.get("two_angles")} move {mv} | replay turn {d}')
    print('   text as scanned', r1(m0.get('text')), '| turned', r1(m1.get('text')))
    print('   tracks as scanned:', [(t[0], t[1], t[2], t[3], t[4]) for t in t0])
    print('   tracks turned    :', [(t[0], t[1], t[2], t[3], t[4]) for t in t1])
    print('   lines_read:', L)
    print('   two_angles →', tw, '→', 'REFUSED (left as scanned)' if tw else 'turn kept')
    tu.close(); doc.close()
