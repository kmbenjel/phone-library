import json, glob, os, random
C = os.path.expanduser('~/.cache/phone-library/crop-regress/')
T = '/tmp/claude-1000/-home-k-projects-phone-library/37b40576-c90e-4994-a417-028a295f8c53/scratchpad/proj/basesurvey.tsv'
R = {os.path.basename(f)[:12]: json.load(open(f)) for f in glob.glob(C + '*.b32a237bbf*.json')}
rows = []
for l in open(T):
    h, pg, d, why, m, n, iqr, an = l.rstrip('\n').split('\t')
    if 'tilt_by_proj' not in why or m == 'None' or iqr == 'None' or int(n) < 6 or float(iqr) >= 0.3: continue
    p = R[h]['pages'][int(pg) - 1]; d = float(d); m = float(m)
    if abs(d - m) >= 0.2: rows.append((h, int(pg), p['tilt_by_proj'], d, m, int(n), float(iqr)))
random.seed(1); random.shuffle(rows)
seen = {}
for r in rows:
    if seen.get(r[0], 0) < 2: seen[r[0]] = seen.get(r[0], 0) + 1; print(*r)
