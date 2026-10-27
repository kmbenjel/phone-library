"""cmpo.py BOOK [A B] — (1) is version A (default base) FAITHFUL to regression 26i's recipe (3205efa17f, any owner-turn tag)?
(2) every page whose crop, shown part, turn, move, scale or kind differs between A and B (default o), with the marks that
explain it (ornament, stain kept, dodged, blots) and the largest edge move in pt"""
import sys, os, json, glob
S = os.path.dirname(os.path.abspath(__file__)); C = '/home/k/.cache/phone-library/crop-regress/'
h = sys.argv[1]; a, b = (sys.argv[2:4] if len(sys.argv) >= 4 else ('base', 'o'))
A = json.load(open(f'{S}/{h}.{a}.json')); B = json.load(open(f'{S}/{h}.{b}.json'))
K = ('crop', 'show', 'skew', 'move', 'scale', 'kind')
ref = sorted(glob.glob(f'{C}{h}.3205efa17f*.json'))
if ref:
    R = json.load(open(ref[0]))
    bad = [i + 1 for i, (p, q) in enumerate(zip(A['pages'], R['pages'])) if any(p.get(k) != q.get(k) for k in K)]
    print(h, a, 'vs', os.path.basename(ref[0]), 'FAITHFUL' if not bad and A.get('decision') == R.get('decision') and A.get('size') == R.get('size')
          else f'NOT FAITHFUL: {A.get("decision")} {A.get("size")} vs {R.get("decision")} {R.get("size")}, pages {bad[:30]}')
else: print(h, 'no 26i recipe yet')
print('book:', {k: (A.get(k), B.get(k)) for k in ('decision', 'size', 'gain', 'blot_pages', 'width_quantile') if A.get(k) != B.get(k)} or 'same')
def mv(p, q):
    m = 0.0
    for k in ('crop', 'show'):
        x, y = p.get(k), q.get(k)
        if x and y: m = max(m, max(abs(u - v) for u, v in zip(x, y)))
        elif x != y: m = 999.0
    return round(m, 1)
n = 0
for i, (p, q) in enumerate(zip(A['pages'], B['pages'])):
    d = {k: (p.get(k), q.get(k)) for k in K if p.get(k) != q.get(k)}
    e = {k: (p.get(k), q.get(k)) for k in ('ornament', 'stain_kept', 'dodged', 'anchored_y', 'anchored_x', 'own_centre') if p.get(k) != q.get(k)}
    if d or e:
        n += 1
        print(f'  p. {i + 1} move {mv(p, q)} pt', d, e, 'blots', [[round(v) for v in x] for x in q.get('blots') or []])
print(n, 'pages differ')
