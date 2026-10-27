"""projvs.py — on the projection-turned pages of 26g (b32a237bbf) with a reliable baseline reading (≥ 6 lines, IQR < 0.3):
the projection's own reading (tilt_by_proj), the turn kept (skew) and the baselines' tilt (basesurvey) — which one is off?"""
import json, glob, os, collections
import numpy as np
C = os.path.expanduser('~/.cache/phone-library/crop-regress/')
T = '/tmp/claude-1000/-home-k-projects-phone-library/37b40576-c90e-4994-a417-028a295f8c53/scratchpad/proj/basesurvey.tsv'
R = {}
for f in glob.glob(C + '*.b32a237bbf*.json'):
    R[os.path.basename(f)[:12]] = json.load(open(f))
rows = []
for l in open(T):
    h, pg, d, why, m, n, iqr, an = l.rstrip('\n').split('\t')
    if 'tilt_by_proj' not in why or m == 'None' or iqr == 'None': continue
    if int(n) < 6 or float(iqr) >= 0.3: continue
    p = R[h]['pages'][int(pg) - 1]
    rows.append((h, int(pg), float(p['tilt_by_proj']), float(d), float(m), int(n), float(iqr), why))
print(len(rows), 'reliable projection pages')
e_proj = np.array([r[2] - r[4] for r in rows]); e_turn = np.array([r[3] - r[4] for r in rows])
for name, e in (('projection reading − baselines', e_proj), ('turn kept − baselines', e_turn)):
    print(f'{name:32}: median {np.median(e):+.3f}, mean |e| {np.mean(np.abs(e)):.3f}, |e| ≥ 0.2: {np.mean(np.abs(e) >= 0.2) * 100:.1f} %, ≥ 0.3: {np.mean(np.abs(e) >= 0.3) * 100:.1f} %')
# how far the loop moved the turn from the projection's reading
mv = np.array([r[3] - r[2] for r in rows]); print('loop moved: ', collections.Counter(np.round(mv, 2)).most_common(12))
# when the loop moved it, was the move toward the baselines?
better = sum(1 for r in rows if abs(r[3] - r[4]) < abs(r[2] - r[4]) - 1e-9); worse = sum(1 for r in rows if abs(r[3] - r[4]) > abs(r[2] - r[4]) + 1e-9)
print('loop brought the turn closer to the baselines on', better, 'pages, further on', worse)
small = [r for r in rows if abs(r[4]) < 0.2]; print('pages the baselines read < 0.2° (level):', len(small))
