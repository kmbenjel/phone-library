"""calib.py BOOK:PAGE … — the page turned by known angles (−0.4…+0.4°, 0.05 apart): the median of its lines' readings
(fast line_leans, 1,400 px) and the share of lines within 0.1° of level, per turn — does the reading follow the turn?"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fastleans import fast_line_leans, bc, C
import numpy as np, pymupdf, json, glob
for s in sys.argv[1:]:
    h, pg = s.split(':'); pg = int(pg)
    R = json.load(open(sorted(glob.glob(C + h + '.b32a237bbf*.json'))[-1])); p = R['pages'][pg - 1]
    tb, paper = p.get('text') or p.get('core'), p.get('paper') or 255
    doc = pymupdf.open(C + h + '.pdf'); tu = bc.Turner(doc, pg - 1); row = []
    for d in np.round(np.arange(-0.4, 0.401, 0.05), 3):
        a, z = bc.gray(tu.page(float(d)), 1400); L = [v[2] for v in fast_line_leans(a.copy(), paper, tb, z) if v[2] is not None]
        row.append(f'{d:+.2f}:{np.median(L):+.3f}/{np.mean(L):+.3f}')
    tu.close(); doc.close(); print(h, pg, 'turn:median/mean →', ' '.join(row), flush=True)
