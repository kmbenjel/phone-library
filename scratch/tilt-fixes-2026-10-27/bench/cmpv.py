"""cmpv.py BOOK V1 V2 — two bench recipes of one book, page by page: turn, box, shown part, scale, move, kind"""
import json, os, sys
S = os.path.dirname(os.path.abspath(__file__)); h, v1, v2 = sys.argv[1:4]
A, B = json.load(open(f'{S}/{h}.{v1}.json')), json.load(open(f'{S}/{h}.{v2}.json'))
K = ('skew', 'crop', 'show', 'scale', 'move', 'kind')
print(h, v1, A.get('decision'), A.get('width_quantile'), '|', v2, B.get('decision'), B.get('width_quantile'))
ch = [i for i, (p, q) in enumerate(zip(A['pages'], B['pages'])) if any(p.get(k) != q.get(k) for k in K)]
print(len(ch), 'pages differ')
for i in ch:
    p, q = A['pages'][i], B['pages'][i]
    print(f'  p. {i + 1}', {k: (p.get(k), q.get(k)) for k in K if p.get(k) != q.get(k)},
          {k: q.get(k) for k in ('lines_lean', 'tilt_disputed', 'untreated_tilt', 'image_third') if q.get(k) is not None})
