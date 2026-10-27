"""cmpq.py BOOK [V1 V2] — two bench recipes (default g2 → q), every page that differs sorted by why: a turn the baselines set
(tilt_by_base: now level by them, or their check failed), no longer turned (the baselines read < 0.2°), a sheet's line (fix P),
turned now by another rule, or a page the projection never touched (unexpected unless the book's box moved). With the
baselines' reading of the page as scanned (the survey, 1,400 px) the old turn's residual is shown beside the new one"""
import json, sys, os, collections
S = os.path.dirname(os.path.abspath(__file__))
SV = '/tmp/claude-1000/-home-k-projects-phone-library/37b40576-c90e-4994-a417-028a295f8c53/scratchpad/proj/basesurvey.tsv'
h = sys.argv[1]; v1, v2 = (sys.argv[2:4] if len(sys.argv) > 3 else ('g2', 'q'))
A, B = json.load(open(f'{S}/{h}.{v1}.json')), json.load(open(f'{S}/{h}.{v2}.json'))
sv = {}
for l in open(SV):
    x = l.rstrip('\n').split('\t')
    if x[0] == h and x[4] != 'None': sv[int(x[1])] = (float(x[4]), int(x[5]), None if x[6] == 'None' else float(x[6]))
K = ('skew', 'crop', 'show', 'scale', 'move', 'kind')
print(h, v1, A.get('decision'), A.get('width_quantile'), A.get('size'), '|', v2, B.get('decision'), B.get('width_quantile'), B.get('size'))
cl = collections.defaultdict(list)
for i, (p, q) in enumerate(zip(A['pages'], B['pages'])):
    if not any(p.get(k) != q.get(k) for k in K): continue
    g = i + 1; t0, t1 = p.get('skew'), q.get('skew')
    if q.get('proj_sheet_line') is not None: c = 'sheet line (P)'
    elif q.get('tilt_by_base') is not None:
        if t0 == t1: c = 'baselines: same turn, box/show only'
        elif not t1: c = 'baselines: not turned (< 0.2°)' if abs(q['tilt_by_base']) < 0.2 else 'baselines: turn undone in the check'
        elif q.get('level_by_base') is not None: c = 'baselines: turned, level by them'
        else: c = 'baselines: turned, NOT confirmed by them'
    elif q.get('tilt_by_proj') is not None: c = 'projection, old path (lines disagree)' if t0 != t1 else 'projection, old path, box/show only'
    elif t0 != t1: c = 'OTHER TURN'
    else: c = 'box/show only (no turn change)'
    cl[c].append((g, t0, t1, q))
for c, v in sorted(cl.items()):
    print(f'\n{c}: {len(v)}')
    for g, t0, t1, q in v[:400]:
        s = sv.get(g)
        extra = f' | as scanned by the survey {s[0]:+.3f} ({s[1]} lines, IQR {s[2]}) → old leaves {s[0] - (t0 or 0):+.3f}, new {s[0] - (t1 or 0):+.3f}' if s else ''
        fl = {k: q.get(k) for k in ('tilt_by_proj', 'tilt_by_base', 'level_by_base', 'level_by_proj', 'unsure_tilt', 'tilt_disputed',
                                    'untreated_tilt', 'tilt_by_columns', 'level_by_columns', 'turned_in_check', 'curved', 'level_by_lines',
                                    'image_third', 'lines_lean') if q.get(k) is not None}
        print(f'  p. {g}: turn {t0} → {t1} {fl}{extra}')
