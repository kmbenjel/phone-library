"""survey.py VERSION — over every cached regression recipe of VERSION: (1) blots that repeat as the same block (same x-centre
± 3 % of the width, both sides within ±10 %) on ≥ 3 other text pages at ANY height (the existing rule needs the same height
too); (2) pages a dodge moved whose final box still holds one of their blots whole (a futile dodge)"""
import sys, json, glob, collections
C = '/home/k/.cache/phone-library/crop-regress/'
v = sys.argv[1]
def inside(a, b, t=0.5): return a[0] >= b[0] - t and a[1] >= b[1] - t and a[2] <= b[2] + t and a[3] <= b[3] + t
for f in sorted(glob.glob(f'{C}*.{v}*.json')):
    h = f.split('/')[-1][:12]; r = json.load(open(f)); P = r['pages']
    text = [i for i, p in enumerate(P) if p.get('kind') == 'text']
    allb = [(i, b) for i in text for b in P[i].get('blots') or []]
    rep = []
    for i, b in allb:
        w = P[i]['w']; bw, bh = b[2] - b[0], b[3] - b[1]
        if bh >= 0.25 * P[i]["h"] or min(bw, bh) < 14 / 420 * w: continue
        same = [j for j, c in allb if j != i and abs((b[0] + b[2]) - (c[0] + c[2])) / 2 <= 0.03 * w
                and 0.9 <= (bw + 1) / (c[2] - c[0] + 1) <= 1.1 and 0.9 <= (bh + 1) / (c[3] - c[1] + 1) <= 1.1]
        if len(same) >= 3: rep.append((i + 1, [round(x) for x in b], len(same)))
    fut = []
    for i in text:
        p = P[i]
        if p.get('dodged') and p.get('crop'):
            for b in p.get('blots') or []:
                if inside(b, p['crop']): fut.append((i + 1, [round(x) for x in b], p['crop']))
    if rep or fut:
        print(h, r.get('decision'), len(P), 'pages')
        if rep: print('  repeated block:', len(rep), rep[:20])
        if fut: print('  futile dodge:', len(fut), [(x[0], x[1]) for x in fut[:30]])
