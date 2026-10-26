"""The crop recipes of two book_crop versions in the regression cache (~/.cache/phone-library/crop-regress/<book>.<md5>….json),
page by page — turn, crop box, shown part, scale, move, kind — so that every change a method change brings is explained
before anything reaches the phone (the redo, a pilot). Each changed page is printed with its cause, read from the flags the
new recipe carries: the owner's turn, a level-by-both turn taken first, a ruler-certified small tilt (turns); a page number
read as a stain restored (folio stain); a second look that moved, enlarged or no longer moves the box (second look); a
cover whose cut moved to keep its print (cover print); else OTHER. A turn rule explains a page only when its turn changed.
Usage: crop_recipe_diff.py OLDMD5 NEWMD5 [BOOK …]   (md5 = the first 10 hex digits of book_crop.py's md5)"""
import collections, glob, json, os, sys
C = os.path.expanduser('~/.cache/phone-library/crop-regress/')
KEYS = ('skew', 'crop', 'show', 'scale', 'move', 'kind')
BOOK = ('decision', 'size', 'width_quantile', 'gain', 'framed', 'clean_margins', 'parity_offsets', 'folio_axis')

def cause(p, q):
    if p.get('skew') != q.get('skew'):
        for k, v in (('owner_turn', 'owner turn'), ('level_first', 'level first'), ('image_loose', 'image ≤ 0.35')):
            if q.get(k) is not None: return v
        return None
    if q.get('folio_blot') is not None or p.get('folio_blot') is not None: return 'folio stain'
    if q.get('verify_cut') is not None: return 'cut edge'
    if p.get('verify_moved') or q.get('verify_moved'): return 'second look'
    if q.get('cover_marks') is not None and p.get('show') != q.get('show') and all(p.get(k) == q.get(k) for k in ('crop', 'scale', 'move', 'kind')):
        return 'cover print'
    return None

def main(old, new, only):
    tot, other = collections.Counter(), []
    for f in sorted(glob.glob(C + f'*.{old}*.json')):
        h = os.path.basename(f)[:12]
        if only and h not in only: continue
        nf = sorted(glob.glob(C + f'{h}.{new}*.json'))
        if not nf: print(h, 'no new recipe'); continue
        A, B = json.load(open(f)), json.load(open(nf[-1]))
        head = [k for k in BOOK if A.get(k) != B.get(k)]
        ch = [(i + 1, cause(p, q), {k: (p.get(k), q.get(k)) for k in KEYS if p.get(k) != q.get(k)})
              for i, (p, q) in enumerate(zip(A['pages'], B['pages'])) if any(p.get(k) != q.get(k) for k in KEYS)]
        by = collections.Counter(c or 'OTHER' for _, c, _ in ch); tot.update(by)
        print(f'{h} {len(A["pages"])} pages | book-level changes: {head or "none"} | pages changed: {dict(by) or 0}')
        for k in head: print(f'   {k}: {A.get(k)} → {B.get(k)}')
        for pg, c, d in ch:
            q = B['pages'][pg - 1]
            if c is None: other.append((h, pg, d))
            fl = {k: q.get(k) for k in ('after_tilt', 'after_tilt_image', 'owner_turn', 'enlarged', 'verify_moved', 'verify_cut', 'folio_blot')
                  if q.get(k) is not None}
            print(f'   p. {pg} [{c or "OTHER"}] {d} {fl}')
    print('\nALL:', dict(tot))
    print(len(other), 'pages changed for another cause' + (':' if other else ''))
    for h, pg, d in other[:80]: print('  ', h, pg, d)

if __name__ == '__main__':
    main(sys.argv[1][:10], sys.argv[2][:10], set(sys.argv[3:]))
