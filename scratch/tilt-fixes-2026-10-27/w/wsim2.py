"""wsim2.py RECIPE.json [J] — guard W with its fallback (bc_w2) replayed on a recipe's turns: every turned page (not by rules,
not the owner's) → kept / re-turned by its lines (the median, none made worse, 80 % level, shear ≤ 0.2) / left as scanned"""
import sys, os, json
sys.path.insert(0, os.path.expanduser("~/.local/share/phone-library-tools/site"))
import numpy as np, pymupdf
from concurrent.futures import ProcessPoolExecutor
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, D + '/code')
import bc_w2 as bc
C = '/home/k/.cache/phone-library/crop-regress/'

def view(doc, i, p, d):
    tu = bc.Turner(doc, i); q = dict(p, skew=d); page = tu.page(d, *(p.get('move') or [0, 0])); a, z = bc.gray(page, 1000); a = a.copy()
    if p.get('sheet'): a = bc.whiten(a, z, bc.fwd_box(doc, i, q, p['sheet']))
    ex = [bc.pad_box(b, page.rect.width) for b in p.get('stamp') or []] + (p.get('dots') or [])
    exf = bc.fwd_boxes(doc, i, q, ex) if ex else []
    mk = bc.marks(a, z, page.rect.width, exf or None)
    sh = abs(bc.skew_of(mk['xy'], raw=True)[0]) if mk.get('xy') is not None else None
    for x in exf: a[max(0, int(x[1] * z)):int(x[3] * z) + 1, max(0, int(x[0] * z)):int(x[2] * z) + 1] = 255
    T = bc.line_tracks(a, mk['paper'], mk.get('text'), z) if mk.get('paper') else []
    tu.close(); return T, sh

def one(arg):
    path, items = arg; doc = pymupdf.open(path); out = []
    for i, p in items:
        try:
            d = p['skew']; t0, _ = view(doc, i, p, 0.0); t1, _ = view(doc, i, p, d); L = bc.lines_read(t0, t1, d); tw = bc.two_angles(L)
            if not tw: out.append((i + 1, d, 'kept', None)); continue
            m = round(round(float(np.median([v[1] for v in L])) / 0.025) * 0.025, 3); res = ('left', [(round(v[1], 2), round(v[2], 2)) for v in tw][:6])
            if abs(m) >= bc.SKEW_MIN:
                t2, sh = view(doc, i, p, m); L2 = bc.lines_read(t0, t2, m)
                if L2 and not bc.two_angles(L2) and sum(1 for v in L2 if abs(v[2]) <= 0.2 + 1e-6) >= 0.8 * len(L2) and sh is not None and sh <= 0.2 + 1e-6:
                    res = ('re-turned', m, round(float(np.median([v[2] for v in L2])), 3), round(sh, 3))
            out.append((i + 1, d, res[0], res[1:]))
        except Exception as e: out.append((i + 1, p['skew'], 'ERR', repr(e)[:80]))
    doc.close(); return out

if __name__ == '__main__':
    f = sys.argv[1]; J = int(sys.argv[2]) if len(sys.argv) > 2 else 2; h = os.path.basename(f)[:12]
    R = json.load(open(f)); path = C + h + '.pdf'
    it = [(i, p) for i, p in enumerate(R['pages']) if p.get('skew') and p.get('level_by_rules') is None and p.get('owner_turn') is None]
    ch = [(path, it[k::J * 4]) for k in range(J * 4)]; res = []
    with ProcessPoolExecutor(J) as ex:
        for part in ex.map(one, ch): res += part
    res.sort(); c = {}
    for r in res: c[r[2]] = c.get(r[2], 0) + 1
    print(h, os.path.basename(f), f'{len(it)} turned pages checked:', c, flush=True)
    for g, d, k, x in res:
        if k != 'kept': print(f'  p. {g} turn {d}: {k} {x}')
