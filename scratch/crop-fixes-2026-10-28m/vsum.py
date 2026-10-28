"""vsum.py BOOK OLDV NEWV [--min PT] — the pages two bench recipes (out/<book>.<v>.json) treat differently, one line each:
the crop's largest move (pt), whole ↔ cropped, scale / enlargement, the turn, and the band markers of fixes B, B2, B3
(band_carried, band_ink, band_ink2, band_box, band_slide) — the triage before bsheets.py draws them (2026-10-28)."""
import sys, os, json
S = os.path.dirname(os.path.abspath(__file__))
args = sys.argv[1:]; lim = 3.0
if '--min' in args: k = args.index('--min'); lim = float(args[k + 1]); del args[k:k + 2]
h, ov, nv = args[:3]
A, B = (json.load(open(f'{S}/out/{h}.{v}.json')) for v in (ov, nv))
print(f'{h} {ov} → {nv}: size {A.get("size")} → {B.get("size")}, decision {A.get("decision")} → {B.get("decision")}, '
      f'clean {A.get("clean_margins")} → {B.get("clean_margins")}, wq {A.get("width_quantile")} → {B.get("width_quantile")}')
n = {'whole→crop': 0, 'crop→whole': 0, 'moved': 0}
for i, (p, q) in enumerate(zip(A['pages'], B['pages'])):
    a, b = p.get('crop'), q.get('crop')
    mv = max(abs(x - y) for x, y in zip(a, b)) if a and b else None
    ch = [k for k in ('scale', 'kind', 'enlarged', 'skew') if p.get(k) != q.get(k)]
    if not ((a is None) != (b is None) or (mv is not None and mv >= lim) or ch): continue
    tag = 'whole→crop' if a is None and b else 'crop→whole' if a and b is None else 'moved'
    n[tag] += 1
    fl = ' '.join(f'{k}={q.get(k)}' for k in ('band_ink', 'band_ink2', 'band_box', 'band_slide', 'band_carried', 'verify_moved')
                  if q.get(k) is not None)
    print(f'p.{i + 1:4d} {tag:10s} mv {mv if mv is None else round(mv, 1)!s:>5}  skew {p.get("skew")}→{q.get("skew")}  '
          f'crop {a} → {b}' + (f'  {"/".join(f"{k} {p.get(k)}→{q.get(k)}" for k in ch if k != "skew")}' if ch else '') +
          (f'  [{fl}]' if fl else ''))
print(n)
