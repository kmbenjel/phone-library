"""ldiff.py BOOK PAGE [ANGLE] — the marks fix L newly takes for lines on one page (marks() of 27l's code against L's, 500 px,
the page turned by ANGLE or by its bench recipe's turn): each one's box (pt), size (px), and whether it left the text block."""
import sys, os, json, importlib
S = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, S + '/code2'); sys.path.insert(1, '/home/k/projects/phone-library/scripts')
import book_crop as base
lb = importlib.import_module('bc_lb')
h, pg = sys.argv[1], int(sys.argv[2])
C = os.path.expanduser('~/.cache/phone-library/crop-regress/')
if len(sys.argv) > 3: d = float(sys.argv[3])
else: d = json.load(open(f'{S}/out/{h}.lb.json'))['pages'][pg - 1].get('skew') or 0
doc = base.pymupdf.open(f'{C}{h}.pdf'); tu = base.Turner(doc, pg - 1); W = doc[pg - 1].rect.width
a, z = base.gray(tu.page(d), 500)
m0, m1 = base.marks(a, z, W), lb.marks(a, z, W)
r1 = lambda b: [round(v, 1) for v in b]
key = lambda b: tuple(round(v, 1) for v in b)
new = sorted(set(map(key, m1['lines'])) - set(map(key, m0['lines'])))
print(f'p.{pg} turn {d}: text {r1(m0["text"])} → {r1(m1["text"])}, box {r1(m0["box"])} → {r1(m1["box"])}; {len(new)} new lines'
      f' ({len(m1.get("slant_lines") or [])} by their ink)')
for b in new: print(f'   {list(b)}  {round((b[2] - b[0]) * z)}×{round((b[3] - b[1]) * z)} px')
