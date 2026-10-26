"""One-off (2026-10-26, the crop revisit + the cover print rule): the new regression recipes against those of book_crop 5d6113b97c (the last
regression), page by page — turn, crop box, shown part, scale, move, kind — every change sorted by its cause: the owner's
turn (data/crop/owner-turns.tsv), a level-by-both turn taken first (best_turn), a small tilt certified by a ruler with the
image measure up to 0.35° (keep), a cover whose cut moved to keep its print (cover_window), or OTHER (to be explained before the redo). Usage: crop_recipe_diff_2026-10-26.py NEWMD5"""
import json, os, glob, sys, collections
C = os.path.expanduser('~/.cache/phone-library/crop-regress/')
new = sys.argv[1][:10]; OLD = '5d6113b97c'
KEYS = ('skew', 'crop', 'show', 'scale', 'move', 'kind')
tot = collections.Counter(); other = []
def cause(p, q):
    if q.get('owner_turn') is not None: return 'owner turn'
    if q.get('level_first'): return 'level first'
    if q.get('image_loose') is not None: return 'image ≤ 0.35'
    if q.get('cover_marks') is not None and p.get('show') != q.get('show') and all(p.get(k) == q.get(k) for k in ('skew', 'crop', 'scale', 'move', 'kind')): return 'cover print'
    return None
for f in sorted(glob.glob(C + f'*.{OLD}.json')):
    h = os.path.basename(f)[:12]
    nf = sorted(glob.glob(C + f'{h}.{new}*.json'))
    if not nf: print(h, 'no new recipe'); continue
    A, B = json.load(open(f)), json.load(open(nf[-1]))
    head = [k for k in ('decision', 'size', 'width_quantile', 'gain', 'framed', 'clean_margins', 'parity_offsets') if A.get(k) != B.get(k)]
    ch = []
    for i, (p, q) in enumerate(zip(A['pages'], B['pages'])):
        d = {k: (p.get(k), q.get(k)) for k in KEYS if p.get(k) != q.get(k)}
        if d: ch.append((i + 1, cause(p, q), d))
    by = collections.Counter(c or 'OTHER' for _, c, _ in ch); tot.update(by)
    print(f'{h} {len(A["pages"])} pages | book-level changes: {head or "none"} | pages changed: {dict(by) or 0}')
    for k in head: print(f'   {k}: {A.get(k)} → {B.get(k)}')
    for pg, c, d in ch:
        if c is None: other.append((h, pg, d))
        tl = {k: B['pages'][pg - 1].get(k) for k in ('after_tilt', 'after_tilt_image', 'level_by_lines', 'level_by_edge', 'owner_turn', 'owner_turn_measured') if B['pages'][pg - 1].get(k) is not None}
        if c is not None or 'skew' in d: print(f'   p. {pg} [{c or "OTHER"}] skew {d.get("skew", ("=", "="))} {tl}')
print('\nALL:', dict(tot))
print(len(other), 'pages changed for another cause' + (':' if other else ''))
for h, pg, d in other[:80]: print('  ', h, pg, d)
