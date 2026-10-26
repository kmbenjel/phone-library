"""basestats.py [CLASS [PATH]] — basesurvey.tsv: each turned page's residual after its turn (tilt − turn, by the baselines);
classes: good (needed, ≤ 0.15 left) / under / over (needed, > 0.15 left) / needless (the page under 0.2°, the turn leaves
more than it found and > 0.15) / harmless (under 0.2°, ≤ 0.15 left) / spread (lines disagree: IQR ≥ 0.35) / few lines;
unturned sampled pages: level / untreated (≥ 0.25°)"""
import sys, os, json, collections
import numpy as np
D = os.path.dirname(os.path.abspath(__file__)); want = sys.argv[1] if len(sys.argv) > 1 else None; wp = sys.argv[2] if len(sys.argv) > 2 else None
c = collections.defaultdict(collections.Counter); ex = collections.defaultdict(list); res = collections.defaultdict(list)
for l in open(f'{D}/basesurvey.tsv'):
    h, pg, d, why, m, n, iqr, an = l.rstrip('\n').split('\t'); d = float(d)
    path = 'unturned' if not d else 'proj' if 'tilt_by_proj' in why else 'owner' if 'owner_turn' in why else 'other'
    if m == 'None' or int(n) < 4: c[path]['few lines'] += 1; continue
    m = float(m); r = m - d; iq = float(iqr) if iqr != 'None' else 0
    if path == 'unturned': k = 'untreated' if abs(m) >= 0.25 else 'level'
    elif abs(m) >= 0.2: k = 'good' if abs(r) <= 0.15 else ('under' if m * r > 0 else 'over')
    else: k = 'harmless' if abs(r) <= 0.15 else ('needless' if abs(r) > abs(m) else 'harmless')
    c[path][k] += 1; res[path].append(abs(r)) if path != 'unturned' else None
    ex[(k, path)].append(f'{h} p. {pg} turn {d:+.3f} tilt {m:+.3f} → left {r:+.3f} (IQR {iq}) [{why}]')
bins = collections.defaultdict(list)
for l in open(f'{D}/basesurvey.tsv'):
    h, pg, d, why, m, n, iqr, an = l.rstrip('\n').split('\t'); d = float(d)
    if not d or m == 'None' or int(n) < 4: continue
    iq = float(iqr) if iqr != 'None' else 0; b = '<0.15' if iq < 0.15 else '0.15-0.3' if iq < 0.3 else '0.3-0.5' if iq < 0.5 else '>=0.5'
    bins[b].append(abs(float(m) - d))
for b in ('<0.15', '0.15-0.3', '0.3-0.5', '>=0.5'):
    if bins[b]: print(f'IQR {b:8} {len(bins[b]):5} pages: residual median {np.median(bins[b]):.3f}, ≥ 0.2 {np.mean(np.array(bins[b]) >= 0.2) * 100:.1f} %')
for p_ in c:
    s = f'{p_:9} {sum(c[p_].values()):5}  ' + ', '.join(f'{k} {v}' for k, v in c[p_].most_common())
    if res[p_]: s += f'  | residual median {np.median(res[p_]):.3f}, ≥ 0.2: {np.mean(np.array(res[p_]) >= 0.2) * 100:.1f} %'
    print(s)
if want:
    for (k, p_), v in sorted(ex.items()):
        if k == want and (wp is None or p_ == wp):
            for e in v: print(' ', p_, e)
