"""why.py BOOK:PAGE … — the first look's and the second look's tilt reasoning on a page as scanned (book_crop 20d30c2020):
skew_of at 500 and 1,000 px (whole, halves), the projection's reading, why no turn"""
import sys, json, glob
sys.path.insert(0, '/home/k/projects/phone-library/scripts')
import book_crop as bc, numpy as np, pymupdf
C = '/home/k/.cache/phone-library/crop-regress/'
def halves(xy):
    xs, ys = xy
    if len(xs) > 60000:
        k = np.random.default_rng(0).choice(len(xs), 60000, replace=False); xs, ys = xs[k], ys[k]
    x, y = xs.astype(float), ys.astype(float); h = np.percentile(x, 50); out = []
    for m in (x < h, x >= h):
        out.append(bc.skew_of((xs[m], ys[m]), raw=True)[0] if m.sum() >= 1500 else None)
    return out
for s in sys.argv[1:]:
    h, pg = s.split(':'); pg = int(pg)
    R = json.load(open(sorted(glob.glob(C + h + '.b32a237bbf*.json'))[-1])); p = R['pages'][pg - 1]
    doc = pymupdf.open(C + h + '.pdf'); page = doc[pg - 1]
    for px in (500, 1000):
        a, z = bc.gray(page, px); mk = bc.marks(a, z, page.rect.width)
        if mk.get('xy') is None: print(h, pg, px, 'no xy'); continue
        print(f'{h} p. {pg} @{px}: skew_of {bc.skew_of(mk["xy"])}, raw {bc.skew_of(mk["xy"], raw=True)}, halves raw {halves(mk["xy"])}, ink points {len(mk["xy"][0])}, dark {mk.get("dark"):.2f}')
        if px == 500: print('    proj_signed', bc.proj_signed(a, mk.get('paper') or 255), 'need 0.3 →', bc.proj_signed(a, mk.get('paper') or 255, need=0.3))
        else: print('    proj_tilt ±3', bc.proj_tilt(a, mk['paper'], -3.0, 3.0, 0.25))
    print('    recipe:', {k: p.get(k) for k in ('skew', 'tilt_by_proj', 'untreated_tilt', 'tilt_disputed', 'unsure_tilt', 'proj_level_rule', 'kind')})
    doc.close()
