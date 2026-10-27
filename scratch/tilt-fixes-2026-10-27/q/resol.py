"""resol.py N — basefit at 500 / 700 / 1,000 px against 1,400 px on N random reliable projection pages (the page as
scanned): agreement of the page's median and of the reliability verdict (≥ 6 lines, IQR < 0.3), and the time of each"""
import sys, os, json, glob, random, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from basefit import base_angles, bc, C
import numpy as np, pymupdf
P = '/tmp/claude-1000/-home-k-projects-phone-library/37b40576-c90e-4994-a417-028a295f8c53/scratchpad/proj/basesurvey.tsv'
R = {os.path.basename(f)[:12]: json.load(open(f)) for f in glob.glob(C + '*.b32a237bbf*.json')}
pool = []
for l in open(P):
    h, pg, d, why, m, n, iqr, an = l.rstrip('\n').split('\t')
    if 'tilt_by_proj' in why and m != 'None': pool.append((h, int(pg)))
random.seed(int(sys.argv[2]) if len(sys.argv) > 2 else 3); pool = random.sample(pool, int(sys.argv[1]))
def verdict(L):
    an = [v[1] for v in L]
    if len(an) < 6: return None, len(an), None
    return float(np.median(an)), len(an), float(np.subtract(*np.percentile(an, [75, 25])))
res = {px: [] for px in (500, 700, 1000, 1400)}; tm = {px: 0.0 for px in res}
for h, pg in pool:
    p = R[h]['pages'][pg - 1]; tb, paper = p.get('text') or p.get('core'), p.get('paper') or 255
    doc = pymupdf.open(C + h + '.pdf'); page = doc[pg - 1]
    for px in res:
        t = time.time(); a, z = bc.gray(page, px); t1 = time.time(); L = base_angles(np.array(a), paper, tb, z); t2 = time.time()
        tm[px] += t2 - t1; res[px].append(verdict(L))
    doc.close()
ok = lambda v: v[0] is not None and v[2] < 0.3
for px in (500, 700, 1000):
    both = [(a, b) for a, b in zip(res[px], res[1400]) if ok(a) and ok(b)]
    e = np.array([a[0] - b[0] for a, b in both])
    agree = sum(1 for a, b in zip(res[px], res[1400]) if ok(a) == ok(b))
    print(f'{px:5} px: fit {tm[px] / len(pool) * 1000:.0f} ms a page; reliable verdict same as 1,400 px on {agree}/{len(pool)}; '
          f'both reliable {len(both)}: |Δ| median {np.median(np.abs(e)):.3f}, 90 % {np.percentile(np.abs(e), 90):.3f}, max {np.abs(e).max():.3f}')
print(f' 1400 px: fit {tm[1400] / len(pool) * 1000:.0f} ms a page; reliable {sum(1 for v in res[1400] if ok(v))}/{len(pool)}')
