"""folio_specks.py VERSION — pages whose specks (dust or isolated) lie where the book prints its page number: a group of
specks (within M of one another) whose box sits at the place of the folio of ≥ 3 other text pages (centres within 3 %,
same parity first) — the page number read as dust; and what the page's own folio was read as"""
import sys, json, glob
C = '/home/k/.cache/phone-library/crop-regress/'
v = sys.argv[1]; tot = 0
def union(bs): return [min(b[0] for b in bs), min(b[1] for b in bs), max(b[2] for b in bs), max(b[3] for b in bs)]
for f in sorted(glob.glob(f'{C}*.{v}*.json')):
    h = f.split('/')[-1][:12]; r = json.load(open(f)); P = r['pages']
    text = [i for i, p in enumerate(P) if p.get('kind') == 'text']
    fols = [(j, P[j]['folio']) for j in text if P[j].get('folio')]
    hits = []
    for i in text:
        p = P[i]; sp = p.get('specks') or []
        if not sp: continue
        w, hh = p['w'], p['h']; M = 14 * w / 420
        # group specks within M of one another
        groups = []
        for s in sp:
            for g in groups:
                if any(s[0] - M <= t[2] and t[0] - M <= s[2] and s[1] - M <= t[3] and t[1] - M <= s[3] for t in g): g.append(s); break
            else: groups.append([s])
        for g in groups:
            u = union(g); cx, cy = (u[0] + u[2]) / 2, (u[1] + u[3]) / 2
            n = sum(1 for j, fo in fols if j != i and abs((fo[0] + fo[2]) / 2 - cx) <= 0.03 * w and abs((fo[1] + fo[3]) / 2 - cy) <= 0.03 * hh)
            if n >= 3:
                fo = p.get('folio'); at = fo and abs((fo[0] + fo[2]) / 2 - cx) <= 0.03 * w and abs((fo[1] + fo[3]) / 2 - cy) <= 0.03 * hh
                hits.append((i + 1, len(g), [round(x) for x in u], n, 'own folio there' if at else f'own folio {None if not fo else [round(x) for x in fo[:4]]}', p.get('anchored_y'), p.get('skew')))
    if hits:
        tot += len(hits); print(h, len(P), 'pages:', len(hits))
        for x in hits[:12]: print('   ', x)
print('total', tot)
