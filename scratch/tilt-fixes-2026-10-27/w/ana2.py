"""ana2.py RMS [FRAC] [MINN] [list] — guard W's rule on the track survey (as scanned): made worse = |a − d| ≥ max(0.5, |a| + 0.25);
flagged when ≥ 2, ≥ FRAC of the lines read, ≥ MINN lines read; turns certified by rules exempt"""
import json, sys, collections
import numpy as np
RMS = float(sys.argv[1]); FR = float(sys.argv[2]) if len(sys.argv) > 2 else 0.2; MN = int(sys.argv[3]) if len(sys.argv) > 3 else 5
LIST = 'list' in sys.argv
tot = 0; fl_ = []; byp = collections.Counter(); tp = collections.Counter()
for l in open('tracks.tsv'):
    h, g, d, fl, T = l.rstrip('\n').split('\t'); T = json.loads(T); d = float(d)
    if not d or (T and T[0][0] == 'err'): continue
    path = 'rules' if 'level_by_rules' in fl else 'columns' if 'level_by_columns' in fl else 'proj' if 'tilt_by_proj' in fl else \
           'third' if 'image_third' in fl else 'owner' if 'owner_turn' in fl else 'other'
    tp[path] += 1; tot += 1
    if path in ('rules', 'owner'): continue
    ok = [t for t in T if t[3] <= RMS and t[4] >= 6 and t[2] >= 0.3]
    mw = [t for t in ok if abs(t[1] - d) >= max(0.5, abs(t[1]) + 0.25) - 1e-6]
    if len(ok) >= MN and len(mw) >= 2 and len(mw) >= FR * len(ok):
        fl_.append((h, int(g), d, path, len(mw), len(ok), [round(t[1], 2) for t in ok])); byp[path] += 1
print(f'rms ≤ {RMS}, ≥ {FR} of lines, ≥ {MN} lines: {len(fl_)} of {tot} turned pages flagged; by path {dict(byp)} of {dict(tp)}')
print('  by book', dict(collections.Counter(f[0] for f in fl_).most_common()))
if LIST:
    for f in fl_: print('  ', f[0], 'p.', f[1], 'turn', f[2], f[3], f'{f[4]}/{f[5]}', f[6])
