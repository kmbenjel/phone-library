"""views.py BOOK:PAGE:TURN … — verify's measures of a page as scanned and as turned (1,000 px): shear (raw), image (proj_tilt
±0.5), baselines (baseline_tilt), edges (edge_tilt), columns; and the signed projection (proj_signed ±4) at 500 px"""
import os, sys
sys.path.insert(0, '/home/k/projects/phone-library/scripts')
import book_crop as bc, numpy as np, pymupdf
C = os.path.expanduser('~/.cache/phone-library/crop-regress/')
for s in sys.argv[1:]:
    h, pg, d = s.split(':'); pg, d = int(pg), float(d)
    doc = pymupdf.open(C + h + '.pdf'); tu = bc.Turner(doc, pg - 1); out = []
    for k in (0.0, d):
        a, z = bc.gray(tu.page(k), 1000); a = np.array(a); mk = bc.marks(a.copy(), z, tu.page(k).rect.width); paper = mk.get('paper') or 255
        sh = bc.skew_of(mk['xy'], raw=True)[0] if mk.get('xy') is not None else None
        sh2 = bc.skew_of(mk['xy']) if mk.get('xy') is not None else None
        a5, z5 = bc.gray(tu.page(k), 500); a5 = np.array(a5)
        out.append(f'shear raw {sh:+.3f} (halves {sh2[0]:+.3f} g {sh2[1]:.2f}) image {bc.proj_tilt(a, paper):.3f} baselines {bc.baseline_tilt(a, paper)} edges {bc.edge_tilt(a, paper)} proj500 {bc.proj_signed(a5, paper)}')
    tu.close(); doc.close()
    print(f'{h} p. {pg}\n   as scanned: {out[0]}\n   turned {d}: {out[1]}', flush=True)
