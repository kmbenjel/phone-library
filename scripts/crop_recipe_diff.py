"""The crop recipes of two book_crop versions in the regression cache (~/.cache/phone-library/crop-regress/<book>.<md5>….json),
page by page — turn, crop box, shown part, scale, move, kind — so that every change a method change brings is explained
before anything reaches the phone (the redo, a pilot). Each changed page is printed with its cause, read from the flags the
new recipe carries: the owner's turn, the owner's «leave as scanned» undoing a turn (owner: as scanned — fix F), a turn
read at the turns beside it when the lines' tracks could not read it at its own (tracks: a turn beside — fix N), a
level-by-both turn taken first, a ruler-certified small tilt, a clear tilt whose
image reading fell to a third, a turn refused because it made level lines lean, a turn of a page the projection found set
by its lines' baselines (baselines), a tilt the usual measures' gates left found by them (baselines found), a projection
reading refused for a sheet's line across the page (sheet line), a turn refused for lines at two angles (two angles) or
set again by the angle its lines take (the lines' turn), a projection loop's turn the lines' tracks confirmed within
0.05° (the loop's turn kept — book_crop fix Q4) or taken when the second look could not keep the lines' turn (the
loop's turn, the lines' turn not kept — fix Q5) (turns); the off-band slide held back by the page's box (band: box
kept — fix B2); the scanner bands as scanned no ink on the turned page (band no ink — fix B2); a thin line at a slant
taken for a line by its ink, not its box (slant line — fix L); the scanner bands read before the turn bounding the
turned page (band carried — fix B); the second look's frame slid off a scanner band, 4 pt beside the print (band: second
look off — fix B3); a mark in a scanner band no longer dodged — the off-band slide keeps it out (band: not dodged — fix B4);
a page number read as a stain restored (folio stain); a sideways slide up to 4 % for
side headings (side slide); letters in the paper's edge shadow taken in (edge letters); a second look that
moved, enlarged or no longer moves the box (second look); a cover whose cut moved to keep its print (cover print); else
OTHER. A turn rule explains a page only when its turn changed.
Usage: crop_recipe_diff.py OLDMD5 NEWMD5 [BOOK …]   (md5 = the first 10 hex digits of book_crop.py's md5)"""
import collections, glob, json, os, sys
C = os.path.expanduser('~/.cache/phone-library/crop-regress/')
KEYS = ('skew', 'crop', 'show', 'scale', 'move', 'kind')
BOOK = ('decision', 'size', 'width_quantile', 'gain', 'framed', 'clean_margins', 'parity_offsets', 'folio_axis')

def cause(p, q):
    if p.get('skew') != q.get('skew'):
        for k, v in (('owner_turn', 'owner turn'), ('owner_flat', 'owner: as scanned'), ('tracks_near', 'tracks: a turn beside'),
                     ('level_first', 'level first'), ('image_loose', 'image ≤ 0.35'),
                     ('image_third', 'image to a third'), ('two_angles', 'two angles'), ('loop_confirmed', "the loop's turn kept"),
                     ('loop_fallback', "the loop's turn, the lines' turn not kept"),
                     ('turn_by_tracks', "the lines' turn"),
                     ('lines_lean', 'lines made to lean'),
                     ('base_found', 'baselines found'),
                     ('tilt_by_tracks', "lines' tracks"),
                     ('tilt_by_base', 'baselines'),
                     ('proj_sheet_line', 'sheet line')):
            if q.get(k) is not None: return v
        return None
    if q.get('band_undodged') and p.get('dodged') and not q.get('dodged'): return 'band: not dodged'
    if q.get('band_slide') is not None: return 'band: second look off'
    if q.get('band_box') is not None: return 'band: box kept'
    if q.get('band_ink') or q.get('band_ink2'): return 'band no ink'
    if q.get('slant_lines') != p.get('slant_lines'): return 'slant line'
    if (q.get('band_carried') or p.get('band_carried')) and q.get('allowed') != p.get('allowed'): return 'band carried'
    if q.get('folio_blot') is not None or p.get('folio_blot') is not None: return 'folio stain'
    if q.get('folio_specks') is not None or p.get('folio_specks') is not None: return 'folio specks'
    if q.get('ornament') != p.get('ornament'): return 'ornament'
    if p.get('dodged') and not q.get('dodged') and q.get('stain_kept'): return 'no futile dodge'
    if q.get('verify_cut') is not None: return 'cut edge'
    if q.get('verify_far') is not None: return 'side slide'
    if q.get('edge_letters') and (p.get('verify_moved') or q.get('verify_moved')): return 'edge letters'
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
