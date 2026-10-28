"""bandedge.py BOOK V1 V2 … — what each frame takes in at its four edges, on every page of a bench recipe (out/<book>.<v>.json;
r27l = 27l's cached recipe): the strip 3 pt inside each crop edge, read on the page turned as the recipe turns it (2,000 px);
per pixel column (row) across the strip, the share of the frame's length that is black (< 60): a column black over half its
length is BAND (a scanner band or the turn's wedge, not text — text never fills half a frame's length); a column whose median
is 60–200 is SHADOW (a paper edge's grey ramp). One line per page and edge where a version shows band or shadow, and totals
— did B5 (frames freed from the slivers) bring band or edge shadow into view? (2026-10-28)"""
import sys, os, json
sys.path.insert(0, '/home/k/projects/phone-library/scripts')
import book_crop as bc, pymupdf, numpy as np
S = os.path.dirname(os.path.abspath(__file__))
h, vs = sys.argv[1], sys.argv[2:]
R = {v: json.load(open(f'{S}/out/{h}.{v}.json'))['pages'] for v in vs}
doc = pymupdf.open(os.path.expanduser(f'~/.cache/phone-library/crop-regress/{h}.pdf'))
tot = {v: [0, 0, 0] for v in vs}                      # pages with band, pages with shadow, band pt in view (sum)
for i in range(doc.page_count):
    rows = {}
    for v in vs:
        p = R[v][i]; c = p.get('crop')
        if not c: continue
        d = p.get('skew') or 0; mv = p.get('move') or [0, 0]
        tu = bc.Turner(doc, i); page = tu.page(d, *mv[:2]) if len(mv) >= 2 else tu.page(d, 0, 0)
        a, z = bc.gray(page, 2000); tu.close(); H, W = a.shape
        X0, Y0, X1, Y1 = [int(round(t * z)) for t in c]; X0, Y0 = max(0, X0), max(0, Y0); X1, Y1 = min(W, X1), min(H, Y1)
        k = int(round(3 * z)); res = []
        for side, s in (('L', a[Y0:Y1, X0:X0 + k]), ('R', a[Y0:Y1, X1 - k:X1][:, ::-1]),
                        ('T', a[Y0:Y0 + k, X0:X1].T), ('B', a[Y1 - k:Y1, X0:X1][::-1].T)):
            if s.size == 0: continue
            black = (s < 60).mean(axis=0); med = np.median(s, axis=0)          # per column, from the frame edge inward
            band = int((black > 0.5).sum()); shadow = int(((med >= 60) & (med < 200) & (black <= 0.5)).sum())
            if band or shadow: res.append((side, round(band / z, 1), round(shadow / z, 1)))
        rows[v] = res
        if any(b for _, b, _ in res): tot[v][0] += 1; tot[v][2] += sum(b for _, b, _ in res)
        if any(sh for _, _, sh in res): tot[v][1] += 1
    if len({json.dumps(r) for r in rows.values()}) > 1:
        print(f'p. {i + 1:4d} ' + ' | '.join(f'{v}: {rows.get(v)}' for v in vs), flush=True)
print('totals (pages with band in view, pages with edge shadow, band pt summed):', {v: [t[0], t[1], round(t[2], 1)] for v, t in tot.items()})
