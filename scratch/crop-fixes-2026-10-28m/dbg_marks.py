"""dbg_marks.py BOOK PAGE "x0,y0,x1,y1" ANGLE… — the first look's marks() (500 px, as analyse_pages measures a turned page) at
each angle: allowed / text / core and, for every ink mark meeting the region (pt), its size, fill, mean thickness and what
marks() made of it (blot, line, edge, margin, text)."""
import sys, os
sys.path.insert(0, '/home/k/projects/phone-library/scripts')
import numpy as np
from scipy import ndimage
import book_crop as bc
C = os.path.expanduser('~/.cache/phone-library/crop-regress/')
h, pg = sys.argv[1], int(sys.argv[2]); roi = [float(v) for v in sys.argv[3].split(',')]
doc = bc.pymupdf.open(f'{C}{h}.pdf'); tu = bc.Turner(doc, pg - 1); W = doc[pg - 1].rect.width
inter = lambda a, b: a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]
r1 = lambda b: [round(v, 1) for v in b]
for d in [float(v) for v in sys.argv[4:]]:
    page = tu.page(d); a, z = bc.gray(page, 500); mk = bc.marks(a, z, W)
    print(f'== {d}°  allowed {r1(mk["allowed"])}  text {r1(mk["text"]) if mk.get("text") else None}  core {r1(mk["core"]) if mk.get("core") else None}')
    for k in ('blots', 'lines', 'edge', 'margin', 'specks'):
        v = [r1(b) for b in mk.get(k) or [] if inter(b, roi)]
        if v: print(f'   {k}: {v}')
    paper = float(np.percentile(a, 90)); mask = a < paper - 50
    r0, r1_, c0, c1 = bc.bands(mask); m = mask[r0:r1_, c0:c1]
    lab, n = ndimage.label(m, structure=np.ones((3, 3), bool)); objs = ndimage.find_objects(lab)
    area = np.bincount(lab.ravel(), minlength=n + 1); H, Wd = m.shape
    print(f'   bands (px) rows {r0}-{r1_} cols {c0}-{c1} of {mask.shape}; 0.4% H = {0.004 * H:.1f} px, 0.6% H = {0.006 * H:.1f} px, 3% W = {0.03 * Wd:.1f} px')
    for i, s in enumerate(objs, 1):
        b = [(s[1].start + c0) / z, (s[0].start + r0) / z, (s[1].stop + c0) / z, (s[0].stop + r0) / z]
        if not inter(b, roi): continue
        hh, ww = s[0].stop - s[0].start, s[1].stop - s[1].start
        if hh * ww < 20: continue
        ys, xs = np.nonzero(lab[s] == i)
        cols = np.unique(xs); thick = np.array([np.count_nonzero(xs == c) for c in cols])
        print(f'   mark {r1(b)} px {ww}x{hh} area {area[i]} fill {area[i] / (hh * ww):.2f} mean thick {area[i] / ww:.2f}px '
              f'median col thick {np.median(thick):.1f} p90 {np.percentile(thick, 90):.1f}')
