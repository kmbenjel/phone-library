"""rulevs.py — printed rules (rulecheck.txt: their angle as scanned, 1,400 px) as the independent ruler: how far is the kept
turn from them, and how far the baselines' tilt (basesurvey)? Pages whose rules agree (spread ≤ 0.15°)"""
import re, ast, numpy as np, collections
P = '/tmp/claude-1000/-home-k-projects-phone-library/37b40576-c90e-4994-a417-028a295f8c53/scratchpad/proj/'
base = {}
for l in open(P + 'basesurvey.tsv'):
    h, pg, d, why, m, n, iqr, an = l.rstrip('\n').split('\t')
    if m != 'None': base[(h, int(pg))] = (float(m), int(n), float(iqr) if iqr != 'None' else 9)
rows = []
for l in open(P + 'rulecheck.txt'):
    mm = re.match(r'(\w+) p\. (\d+) (\w+) turn ([+-][\d.]+): rules before ([+-][\d.]+) after ([+-][\d.]+) → \w+\s+(\[.*\])', l)
    if not mm: continue
    h, pg, kind, d, b0, b1, rl = mm.groups(); pg = int(pg); d = float(d); rl = ast.literal_eval(rl)
    angs = [r[2] for r in rl]
    if max(angs) - min(angs) > 0.15: continue                     # the rules disagree: no ruler
    if (h, pg) not in base: continue
    m, n, iq = base[(h, pg)]; b0 = float(np.median(angs))
    rows.append((h, pg, d, b0, m, n, iq, max(r[1] for r in rl)))
print(len(rows), 'pages with agreeing rules and a baselines reading')
for lab, sel in (('all', lambda r: True), ('baselines reliable (≥ 6 lines, IQR < 0.3)', lambda r: r[5] >= 6 and r[6] < 0.3),
                 ('baselines noisy', lambda r: not (r[5] >= 6 and r[6] < 0.3))):
    R = [r for r in rows if sel(r)]
    if not R: continue
    et = np.array([r[2] - r[3] for r in R]); eb = np.array([r[4] - r[3] for r in R])
    print(f'{lab}: {len(R)} pages')
    print(f'   kept turn − rules : median {np.median(et):+.3f}, mean |e| {np.mean(np.abs(et)):.3f}, |e| ≥ 0.2 on {np.mean(np.abs(et) >= 0.2) * 100:.0f} %')
    print(f'   baselines − rules : median {np.median(eb):+.3f}, mean |e| {np.mean(np.abs(eb)):.3f}, |e| ≥ 0.2 on {np.mean(np.abs(eb) >= 0.2) * 100:.0f} %')
print('\nreliable pages where baselines and the kept turn differ by ≥ 0.15: who agrees with the rules?')
for r in rows:
    if r[5] >= 6 and r[6] < 0.3 and abs(r[2] - r[4]) >= 0.15:
        print(f'  {r[0]} p. {r[1]}: turn {r[2]:+.3f}  baselines {r[4]:+.3f}  rules {r[3]:+.3f} (widest {r[7]})  → {"BASE" if abs(r[4] - r[3]) < abs(r[2] - r[3]) else "TURN"}')
