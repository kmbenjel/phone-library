"""ana3.py — the final W rule on the survey (as scanned only; the consistency test needs the turned view: an upper bound)"""
import json, collections
import numpy as np
tot = 0; fl = []; byp = collections.Counter()
for l in open('tracks.tsv'):
    h, g, d, f, T = l.rstrip('\n').split('\t'); T = json.loads(T); d = float(d)
    if not d or (T and T[0][0] == 'err') or 'level_by_rules' in f or 'owner_turn' in f: continue
    tot += 1
    L = sorted((t[0], t[1], round(t[1] - d, 3)) for t in T if t[3] <= 1.0 and t[4] >= 6 and t[2] >= 0.3)
    if len(L) < 5 or float(np.median(np.abs(np.diff([v[1] for v in L])))) > 0.25: continue
    w = [v for v in L if abs(v[2]) >= max(0.5, abs(v[1]) + 0.25) - 1e-6]; agree = sum(1 for v in L if abs(v[2]) <= 0.35)
    if len(w) >= 2 and (len(w) >= 0.2 * len(L) or agree < 0.8 * len(L)):
        path = 'columns' if 'level_by_columns' in f else 'proj' if 'tilt_by_proj' in f else 'other'
        fl.append((h, int(g), d, path, len(w), len(L))); byp[path] += 1
print(f'{len(fl)} of {tot} turned pages (rules/owner turns excepted) would be left as scanned (upper bound); by path {dict(byp)}')
print(dict(collections.Counter(f[0] for f in fl).most_common()))
