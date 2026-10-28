"""vplace.py BOOK V1 V2 … — every page's text top inside its frame (text top + move − crop top, pt) against the median of its
6 nearest pages of the same parity whose text is of full height (≥ 90 % of the book's median), per bench recipe: the pages
whose vertical place stands out (|offset| > LIM pt, default 8) in one version and not in the first — a frame moved up or down
for nothing (a futile dodge, a lost anchor) shows here; band slides move frames across, not up and down (2026-10-28)."""
import sys, os, json
S = os.path.dirname(os.path.abspath(__file__)); LIM = float(os.environ.get('LIM', 8))
h, vs = sys.argv[1], sys.argv[2:]
R = {v: json.load(open(f'{S}/out/{h}.{v}.json'))['pages'] for v in vs}
def offs(P):
    th = sorted(p['text'][3] - p['text'][1] for p in P if p.get('text') and p.get('crop'))
    med = th[len(th) // 2]; full = {i for i, p in enumerate(P) if p.get('text') and p.get('crop') and p['text'][3] - p['text'][1] >= 0.9 * med}
    rel = {i: P[i]['text'][1] + (P[i].get('move') or [0, 0])[1] - P[i]['crop'][1] for i in full}
    out = {}
    for i in full:
        nb = sorted((j for j in full if j != i and j % 2 == i % 2), key=lambda j: abs(j - i))[:6]
        if len(nb) >= 3:
            m = sorted(rel[j] for j in nb)[len(nb) // 2]; out[i] = round(rel[i] - m, 1)
    return out
O = {v: offs(R[v]) for v in vs}
base = vs[0]
for v in vs[1:]:
    new = sorted(i for i in O[v] if abs(O[v][i]) > LIM and abs(O[base].get(i, 0)) <= LIM)
    gone = sorted(i for i in O[base] if abs(O[base][i]) > LIM and i in O[v] and abs(O[v][i]) <= LIM)
    print(f'{v} vs {base}: newly out of place {[(i + 1, O[base].get(i), O[v][i]) for i in new]}')
    print(f'   back in place {[(i + 1, O[base][i], O[v].get(i)) for i in gone]}')
    print(f'   out of place in both: {len([i for i in O[v] if abs(O[v][i]) > LIM and abs(O[base].get(i, 0)) > LIM])}')
