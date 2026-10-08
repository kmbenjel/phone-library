"""Book-level crop and levelling of scanned books — the method after the 2026-10-07 revert, shaped by the owner's reviews of
three samples (2026-10-08). Owner's rules: nothing of the text may be lost («ولو تعليقة صغيرة في الهامش»); pages must not
sway; the text centred, horizontally and vertically, consistently on every page; ordinary books enlarged moderately;
tilted pages levelled; stains left out but never confused with print or an illustration; no pixel cleaning.

WHAT CHANGES IN THE FILE. A scanned page holds an image (the scan) and drawing instructions (where to draw it, which part
to show). Only the instructions change: (1) each page's CropBox — the part shown; what lies outside stays in the file;
(2) for a tilted or moved page, one stream «q a b c d e f cm» before the page's content and one «Q» after it — the reader
draws the same image turned (and/or shifted). The image streams, the text layer and everything else stay byte for byte
(incremental save; checked: same page count, same images). Removing the CropBox and the two streams restores the page.

1. MEASURE every page: rendered gray 500 px wide; paper = 90th percentile of the grey levels; ink = darker than
   paper − 50; ink marks = 8-connected components. Sizes below are fractions of the page width («pt» = pt on a page scaled
   to 420 pt wide); M = 14 pt (≈ 5 mm), SPECK = 4 pt (≈ 1.4 mm). A page is a picture if more than 35 % of it is dark (or its
   paper is darker than 110), blank if it has no content. A file with fewer than 5 text pages, or text on fewer than half
   its pages, is left as it is.
2. NOT CONTENT (kept out of the box), by careful rules:
   - scanner bands: rows/columns from an edge more than 60 % dark;
   - edge shadows: a mark touching a side, at least 40 % of it long and at most 6 % thick (the box keeps out of them);
   - isolated specks: a mark ≤ SPECK × SPECK with no other mark within M; dust: a group of marks within M of one another,
     all ≤ SPECK, lying wholly outside the text block — unless they form a long thin line (≥ 20 % long, ≤ 3 % thick);
   - scanner edge noise: marks wholly in the outer 3 % of a side, at most 2 % thick, on a side the text block is ≥ 5 % away
     from; the edge of the sheet: a thin sparse line (ink < 8 % of its bounding box) touching the border with < 10 % of its
     ink inside the text block; corner marks: a mark ≤ 5 % × 5 % touching the border in a corner, outside the text block;
   - stains: (a) streaks — beyond the text block, ≥ 25 % of the page tall, 0.6–6 % wide, ragged (ink < 85 % of the box),
     within the outer 15 % of the width; (b) blots — at least M across, solid but irregular (ink 45–85 % of the box), alone
     in their group, at least M from the text block, at most 3 % of the page; plus the detached pieces of a stain on the same
     side. A «stain» found at the same place (centre within 3 %, size within ×2) on ≥ max(3, 3 % of the text pages) other
     pages is print (ornament, logo) and counts as content again.
   Everything else is content, however small or faint, including faint printed rules and frames: beyond the text block,
   light ink (paper − 20) running along ≥ 50 % of the text block's height (or width) in a band 1 % wide.
   The text block, used for these tests and for centring, is measured mark by mark (2nd–98th percentile of the marks'
   edges, each mark counted once, border-strip marks left out of the first estimate), so one heavy streak cannot drag it.
3. LEVEL tilted pages: the tilt is the shear angle that makes the content's row profile sharpest (±4°, to 0.025°), measured
   on the whole text and on its right and left halves; the halves must agree within 0.4° and the whole lie within 0.3° of
   them, else nothing is turned (index pages, verse, tables only look tilted to the profile). A small tilt (0.1–0.35°) is
   measured again at 1,000 px. A page is turned when the tilt is ≥ 0.2° and the profile gets ≥ 2 % sharper; both directions
   are tried and kept only if the turned page's whole-page angle reads level (≤ max(0.1°, a third of the tilt)) and the
   page still shows its ink (×0.6–1.6).
4. BOX SIZE, one for the whole file: width = the content width of 95 % of the text pages (else 98 %, else all — see 7)
   + 8 % of it on each side (at least M); height = the tallest page's content + 5 % above and below. A book whose text is
   framed by a printed border (a rule on both sides on half its full pages or more) keeps only a hairline outside the
   frame: 2 % of the content's width and height. Narrowed only as far as
   needed to centre the text on 95 % of the full pages (a scan with one tight margin), never below the content width,
   never beyond the page.
5. BOX PLACE, page by page: a full page (text block ≥ 90 % of the usual width; content ≥ 90 % of the usual height) is
   centred on its own text block — the same horizontal centre for odd and even pages by default; a different one per parity
   only when the book lays out like that (marginal material on a fixed side: on ≥ 70 % of the full pages of a parity the
   content extends ≥ 1.5 % of the width beyond the text block on the same side), then the box keeps that offset; a short page (a chapter end with a few lines) takes the median place of its 6 nearest
   full pages of the same parity, so its lines stay where the neighbours' lines are. If the page's marks do not fit there
   (a stamp page, a plate, a far marginal note), the box is centred on that page's own content instead. If the box would
   leave the page, on white paper (≥ 235) the content is moved instead so it stays centred; otherwise the box stops at the
   edge. On a page with a stain, the box slides away from it as far as the content allows; when the page edge stops it, on
   white paper the content moves the remaining few points (≤ 3 % of the width) so the stain falls outside. A page whose content is wider
   or taller than the box stays whole (uncropped).
6. SECOND LOOK at 1,000 px, on each page as the reader will see it:
   - LEVEL CHECK: a turned page must read level (whole-page angle ≤ 0.1°); what is left is turned away once more (both
     signs tried); a page still not level (> 0.15°) is NOT turned at all and is listed (`unsure_tilt`) — a tilt the method
     made is never kept. Tilt is only read on pages with real text: at least 8 lines and enough ink. An untouched page that
     shows a consistent tilt the first look did not treat is turned here if that makes it level, else listed
     (`untreated_tilt`). An untouched page cannot gain a tilt.
   - every content mark found outside a page's box must lie (± 3 pt) on something the first look left out on purpose (a
     stain, edge noise); otherwise the box moves up to 2 % to take it in, or the page stays whole.
7. DECISION (plan): the narrowest width (95 %, 98 %, 100 %) with at most 5 % of the text pages left whole after the second
   look. The file is cropped when the text gets ≥ 6 % larger on a phone, or was ≥ 2 % off-centre on the median page, or
   loses scanner bands, or has ≥ 5 % tilted pages; otherwise it is left as it is.
Nothing is applied to the phone without the owner's approval of a sample page (review_page()).
Usage:
  book_crop.py analyse in.pdf recipe.json          → plan(): recipe — per page box, tilt, move, stains (no output PDF)
  book_crop.py apply in.pdf recipe.json out.pdf    → lossless copy with the recipe's boxes and drawing instructions, checked
  book_crop.py sheet in.pdf recipe.json outdir     → JPEGs: before (box red, stains orange, edge noise purple, specks blue) / after
Needs PyMuPDF (~/.local/share/phone-library-tools/site), numpy, scipy."""
import json, os, sys
sys.path.insert(0, os.path.expanduser('~/.local/share/phone-library-tools/site'))
import numpy as np
import pymupdf
from scipy import ndimage

REF = 420.0       # the page width (pt) the sizes below refer to
M = 14            # pt: isolation distance of a speck, and the least margin
SPECK = 4         # pt: a speck is at most SPECK × SPECK
GAIN = 1.06       # least width gain for a crop (owner 2026-10-08: ordinary books too, moderately)
OFFC = 0.02       # or: median off-centre share of the page width worth fixing
MAX_WHOLE = 0.05  # share of measured pages allowed to stay whole

def gray(page, px):
    """the page rendered gray, px pixels wide → (array, pixels per pt)"""
    z = px / page.rect.width
    pix = page.get_pixmap(matrix=pymupdf.Matrix(z, z), colorspace=pymupdf.csGRAY, alpha=False)
    return np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.stride)[:, :pix.width], z

def bands(mask):
    """rows/columns at the edges more than 60 % dark (scanner bed, black borders) → the allowed area [r0, r1) × [c0, c1)"""
    rows, cols = mask.mean(1), mask.mean(0)
    def trim(a):
        i, j = 0, len(a)
        while i < j and a[i] > 0.6: i += 1
        while j > i and a[j - 1] > 0.6: j -= 1
        if i > 0 and i < j and a[i] > 0.3: i += 1            # the blurred edge of a band
        if j < len(a) and j > i and a[j - 1] > 0.3: j -= 1
        return i, j
    (r0, r1), (c0, c1) = trim(rows), trim(cols)
    return r0, r1, c0, c1

def marks(a, scale, width):
    """ink marks of one page, in pt (page.rect coordinates) → dict:
       box     every content mark;  core  the text block (2–98 % of the content ink: where the page is centred);
       specks  isolated specks;  blots  stains and edge streaks (neither text nor print: left outside the box);
       allowed where the box may go (inside scanner bands and edge shadows);  dark  share of dark pixels;
       xy      content ink pixels (x, y in pixels) for the skew estimate.
    scale = pixels per pt, width = the page width in pt (M and SPECK are scaled to it)"""
    unit = scale * width / REF                      # pixels per «reference pt»
    out = {'box': None, 'core': None, 'specks': [], 'blots': [], 'edge': [], 'rules': [], 'allowed': None, 'dark': 1.0, 'xy': None}
    paper = float(np.percentile(a, 90))
    if paper < 110: return out
    mask = a < paper - 50
    out['dark'] = float(mask.mean()); out['paper'] = paper
    r0, r1, c0, c1 = bands(mask)
    m = mask[r0:r1, c0:c1]
    allowed = [c0 / scale, r0 / scale, c1 / scale, r1 / scale]; out['allowed'] = allowed
    if m.size == 0: return out
    lab, n = ndimage.label(m, structure=np.ones((3, 3), bool))
    if n == 0: return out
    objs = ndimage.find_objects(lab)
    area = np.bincount(lab.ravel(), minlength=n + 1)
    H, Wd = m.shape
    hgt = np.array([0] + [s[0].stop - s[0].start for s in objs]); wid = np.array([0] + [s[1].stop - s[1].start for s in objs])
    sp = SPECK * unit
    small = (hgt <= sp) & (wid <= sp); small[0] = False
    # marks closer than M to each other fall in one group (dilation by M/2 on each)
    grp, _ = ndimage.label(ndimage.binary_dilation(m, iterations=max(1, int(M * unit / 2))), structure=np.ones((3, 3), bool))
    gid = np.zeros(n + 1, np.int64)
    for i, s in enumerate(objs, 1):
        gid[i] = grp[s][lab[s] == i][0]
    members = {}
    for i in range(1, n + 1): members.setdefault(int(gid[i]), []).append(i)
    isolated = {ids[0] for ids in members.values() if len(ids) == 1 and small[ids[0]]}
    # edge shadows: touching a side, long along it, thin across it
    shadow = {i for i, s in enumerate(objs, 1)
              if ((s[1].start <= 1 or s[1].stop >= Wd - 1) and hgt[i] >= 0.4 * H and wid[i] <= 0.06 * Wd)
              or ((s[0].start <= 1 or s[0].stop >= H - 1) and wid[i] >= 0.4 * Wd and hgt[i] <= 0.06 * H)}
    for i in shadow:                                  # the box keeps out of a shadow, as out of a scanner band
        s = objs[i - 1]
        if s[1].start <= 1 and hgt[i] >= 0.4 * H: allowed[0] = max(allowed[0], (s[1].stop + c0) / scale)
        elif s[1].stop >= Wd - 1 and hgt[i] >= 0.4 * H: allowed[2] = min(allowed[2], (s[1].start + c0) / scale)
        elif s[0].start <= 1: allowed[1] = max(allowed[1], (s[0].stop + r0) / scale)
        else: allowed[3] = min(allowed[3], (s[0].start + r0) / scale)
    pre = [i for i in range(1, n + 1) if i not in isolated and i not in shadow]
    pt = lambda x0, y0, x1, y1: [(x0 + c0) / scale, (y0 + r0) / scale, (x1 + c0) / scale, (y1 + r0) / scale]
    box_of = lambda i: pt(objs[i - 1][1].start, objs[i - 1][0].start, objs[i - 1][1].stop, objs[i - 1][0].stop)
    out['specks'] = [box_of(i) for i in sorted(isolated)]
    if not pre: return out
    # the text block: every mark counts once (2nd / 98th percentile of the marks' edges), so one heavy streak cannot drag it;
    # marks lying wholly in the outer 3 % of a side (border grains) are not counted in this first estimate
    def in_strip(i):
        s = objs[i - 1]
        return s[1].stop <= 0.03 * Wd or s[1].start >= 0.97 * Wd or s[0].stop <= 0.03 * H or s[0].start >= 0.97 * H
    big = [i for i in pre if not small[i] and not in_strip(i)] or [i for i in pre if not small[i]] or pre
    cx0 = np.percentile([objs[i - 1][1].start for i in big], 2); cx1 = np.percentile([objs[i - 1][1].stop for i in big], 98)
    cy0 = np.percentile([objs[i - 1][0].start for i in big], 2); cy1 = np.percentile([objs[i - 1][0].stop for i in big], 98)
    # scanner edge noise: grains and broken border lines lying wholly in the outer 3 % of a side, thin across it, on a
    # side where the text block is at least 5 % away (a tight scan whose text reaches the edge keeps everything)
    edge = set()
    for i in pre:
        s = objs[i - 1]; x0, x1, y0, y1 = s[1].start, s[1].stop, s[0].start, s[0].stop
        if (x1 <= 0.03 * Wd and wid[i] <= 0.02 * Wd and cx0 >= 0.05 * Wd) or (x0 >= 0.97 * Wd and wid[i] <= 0.02 * Wd and Wd - cx1 >= 0.05 * Wd) \
           or (y1 <= 0.03 * H and hgt[i] <= 0.02 * H and cy0 >= 0.05 * H) or (y0 >= 0.97 * H and hgt[i] <= 0.02 * H and H - cy1 >= 0.05 * H):
            edge.add(i)
        # the edge of the sheet showing in the scan: a thin sparse line touching the page border, its ink (almost) all
        # outside the text block (letters cut by the edge of a tight scan are dense, not thin lines)
        # a scanner mark in a corner of the sheet (touching the edge there, small): text never sits in the corner itself
        elif (x0 <= 0.01 * Wd or x1 >= 0.99 * Wd or y0 <= 0.01 * H or y1 >= 0.99 * H) and wid[i] <= 0.05 * Wd and hgt[i] <= 0.05 * H \
             and (x0 <= 0.04 * Wd or x1 >= 0.96 * Wd) and (y0 <= 0.04 * H or y1 >= 0.96 * H) \
             and (x1 <= cx0 or x0 >= cx1 or y1 <= cy0 or y0 >= cy1):
            edge.add(i)
        elif (x0 <= 0.01 * Wd or x1 >= 0.99 * Wd or y0 <= 0.01 * H or y1 >= 0.99 * H) and area[i] / max(1, hgt[i] * wid[i]) < 0.08:
            ix0, ix1, iy0, iy1 = int(cx0), int(cx1), int(cy0), int(cy1)
            if np.count_nonzero(lab[iy0:iy1, ix0:ix1] == i) < 0.1 * area[i]: edge.add(i)
    out['edge'] = [box_of(i) for i in sorted(edge)]
    big = [i for i in pre if i not in edge and not small[i]] or [i for i in pre if i not in edge] or pre
    cx0 = np.percentile([objs[i - 1][1].start for i in big], 2); cx1 = np.percentile([objs[i - 1][1].stop for i in big], 98)
    cy0 = np.percentile([objs[i - 1][0].start for i in big], 2); cy1 = np.percentile([objs[i - 1][0].stop for i in big], 98)
    # dust: a group made only of grains (each ≤ SPECK), lying wholly outside the text block — scattered dirt, not text
    # (the small letters and dots of a footnote lie inside the text block)
    g1 = 0.01 * Wd; dust = set()
    for ids in members.values():
        if len(ids) > 1 and all(small[j] for j in ids):
            gx0 = min(objs[j - 1][1].start for j in ids); gx1 = max(objs[j - 1][1].stop for j in ids)
            gy0 = min(objs[j - 1][0].start for j in ids); gy1 = max(objs[j - 1][0].stop for j in ids)
            line = (gy1 - gy0 >= 0.2 * H and gx1 - gx0 <= 0.03 * Wd) or (gx1 - gx0 >= 0.2 * Wd and gy1 - gy0 <= 0.03 * H)
            if line: continue                         # small marks in a long thin line: a printed rule or frame side (chain border)
            if gx1 <= cx0 - g1 or gx0 >= cx1 + g1 or gy1 <= cy0 - g1 or gy0 >= cy1 + g1: dust.update(ids)
    out['specks'] += [box_of(i) for i in sorted(dust) if i not in isolated]
    pre = [i for i in pre if i not in edge and i not in dust]
    if not pre: return out
    g, gap = 0.01 * Wd, M * unit
    blots = set()
    for i in pre:
        s = objs[i - 1]; x0, x1, y0, y1 = s[1].start, s[1].stop, s[0].start, s[0].stop
        fill = area[i] / max(1, hgt[i] * wid[i])
        side = x1 <= cx0 - g or x0 >= cx1 + g
        # (a) a streak along a side (torn edge, binding shadow): tall, ragged, beyond the text block, near the page edge;
        #     a printed rule is straight and thin (fill ≥ 0.85 or narrower than 0.6 % of the width) and stays
        if side and hgt[i] >= 0.25 * H and 0.006 * Wd <= wid[i] <= 0.06 * Wd and fill < 0.85 and (x0 < 0.15 * Wd or x1 > 0.85 * Wd):
            blots.add(i); continue
        # (b) a stain: solid but irregular (a printed tab or box is a near-perfect rectangle), at least M across, alone,
        #     in a margin at least M from the text block, not large (a picture is) — repeated places are checked per book
        far = x1 <= cx0 - gap or x0 >= cx1 + gap or y1 <= cy0 - gap or y0 >= cy1 + gap
        if far and max(hgt[i], wid[i]) >= gap and 0.45 <= fill < 0.85 and hgt[i] * wid[i] <= 0.03 * H * Wd \
           and all(j == i or j in isolated or j in shadow for j in members[int(gid[i])]):
            blots.add(i)
    for i in list(blots):                             # the detached pieces of a stain: marks of its group on the same side
        s = objs[i - 1]; lft = s[1].stop <= cx0 - g; rgt = s[1].start >= cx1 + g
        for j in members[int(gid[i])]:
            if j in pre and j not in blots:
                t = objs[j - 1]
                if (lft and t[1].stop <= cx0 - g) or (rgt and t[1].start >= cx1 + g) or (not lft and not rgt and (t[0].stop <= cy0 - g or t[0].start >= cy1 + g)):
                    blots.add(j)
    out['blots'] = [box_of(i) for i in sorted(blots)]
    content = [i for i in pre if i not in blots]
    if not content: return out
    # printed rules and frames, even faint ones (a chain border can break into specks): beyond the text block, a column
    # (row) where light ink runs along half the text block's height (width) or more is print — the box takes it in
    faint = a[r0:r1, c0:c1] < paper - 20
    iy0, iy1, ix0, ix1 = int(cy0), max(int(cy1), int(cy0) + 1), int(cx0), max(int(cx1), int(cx0) + 1)
    bw = max(3, int(round(0.01 * Wd)))               # a band ≈ 1 % of the width: chain links alternate across it
    colcov = ndimage.maximum_filter(faint[iy0:iy1, :], size=(1, bw)).mean(0)
    rowcov = ndimage.maximum_filter(faint[:, ix0:ix1], size=(bw, 1)).mean(1)
    rule_x = [x for x in range(Wd) if colcov[x] >= 0.5 and (x <= cx0 - g or x >= cx1 + g) and 0.03 * Wd < x < 0.97 * Wd]
    rule_y = [y for y in range(H) if rowcov[y] >= 0.5 and (y <= cy0 - g or y >= cy1 + g) and 0.03 * H < y < 0.97 * H]
    out['rules'] = []
    if rule_x: out['rules'].append(pt(min(rule_x), iy0, max(rule_x) + 1, iy1))
    if rule_y: out['rules'].append(pt(ix0, min(rule_y), ix1, max(rule_y) + 1))
    keep = np.zeros(n + 1, bool); keep[content] = True
    ys, xs = np.nonzero(keep[lab])
    out['box'] = pt(xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)
    for rb in out['rules']:                           # a frame side widens the content to itself
        b = out['box']; out['box'] = [min(b[0], rb[0]), min(b[1], rb[1]), max(b[2], rb[2]), max(b[3], rb[3])]
    out['parts'] = [box_of(i) for i in content]
    qx, qy = np.percentile(xs, [2, 98]), np.percentile(ys, [2, 98])
    out['core'] = pt(qx[0], qy[0], qx[1] + 1, qy[1] + 1)
    out['xy'] = (xs, ys)
    return out

def skew_of(xy, raw=False):
    """the angle (degrees) that makes the text lines level: shear the ink by tan(a) and keep the angle whose row profile is
    sharpest. Measured on the whole text and on its right and left halves: a real tilt is the same everywhere (owner,
    2026-10-08: index pages and verse turned by mistake — their whole-page angle disagreed with their halves'). Accepted when
    the halves agree within 0.4° and the whole lies within 0.3° of them; else (0, 1). raw=True: the whole-page angle alone.
    Returns (a, sharpness gain over a = 0); (0, 1) with too little ink"""
    if xy is None or len(xy[0]) < 1500: return 0.0, 1.0
    xs, ys = xy
    if len(xs) > 60000:
        k = np.random.default_rng(0).choice(len(xs), 60000, replace=False); xs, ys = xs[k], ys[k]
    def best(x, y):
        def score(a):
            yy = np.round(y + x * np.tan(np.radians(a))).astype(np.int64); yy -= yy.min()
            c = np.bincount(yy).astype(float); return float((c * c).sum())
        base = score(0.0)
        angs = np.arange(-4, 4.001, 0.25); a0 = float(angs[int(np.argmax([score(v) for v in angs]))])
        fine = np.arange(a0 - 0.25, a0 + 0.2501, 0.025); sc = [score(v) for v in fine]
        return float(fine[int(np.argmax(sc))]), max(sc) / base
    x, y = xs.astype(float), ys.astype(float)
    a, gain = best(x, y)
    if raw: return a, gain
    if len(xs) < 6000: return 0.0, 1.0               # too little text to read a tilt (a heading, a few words)
    yy = np.round(y + x * np.tan(np.radians(a))).astype(np.int64); yy -= yy.min()
    prof = np.bincount(yy).astype(float); thr = 0.3 * prof.max()
    lines = sum(1 for i in range(1, len(prof) - 1) if prof[i] >= thr and prof[i] >= prof[i - 1] and prof[i] > prof[i + 1])
    if lines < 8: return 0.0, 1.0                     # fewer than 8 text lines: not measured
    h = np.percentile(x, 50); parts = []
    for m in (x < h, x >= h):
        if m.sum() >= 500: parts.append(best(x[m] - x[m].min(), y[m])[0])
    if len(parts) < 2 or abs(parts[0] - parts[1]) > 0.4 or abs(a - sum(parts) / 2) > 0.3: return 0.0, 1.0
    return a, gain

SKEW_MIN = 0.2    # degrees: the owner sees a 0.25° tilt on a full line
def raw_box(doc, x, key):
    """a page's own or inherited box, as numbers (PDF coordinates)"""
    while x:
        t, v = doc.xref_get_key(x, key)
        if t == 'array': return [float(z) for z in v.strip('[] ').split()]
        t, par = doc.xref_get_key(x, 'Parent'); x = int(par.split()[0]) if t == 'xref' else 0
    return None

def rotate_contents(doc, page, deg, dx=0.0, dy=0.0):
    """LOSSLESS deskew / move: the page's content is drawn turned by deg degrees about the page centre, then moved by
    (dx, dy) pt (page coordinates: dy > 0 = down) — one «q … cm» stream before the existing content and one «Q» after it;
    images and text layer are untouched (they turn and move together)"""
    import math
    mb = raw_box(doc, page.xref, 'MediaBox'); cx, cy = (mb[0] + mb[2]) / 2, (mb[1] + mb[3]) / 2
    t = math.radians(deg); c, s = math.cos(t), math.sin(t)
    e, f = cx - c * cx + s * cy + dx, cy - s * cx - c * cy - dy
    ta, v = doc.xref_get_key(page.xref, 'Contents')
    if ta == 'xref':
        x = int(v.split()[0])
        body = doc.xref_object(x).strip()
        old = body[1:-1] if body.startswith('[') else v          # an indirect array of streams: its elements
    elif ta == 'array': old = v.strip()[1:-1]
    else: return False
    xa = doc.get_new_xref(); doc.update_object(xa, '<<>>'); doc.update_stream(xa, f'q {c:.6f} {s:.6f} {-s:.6f} {c:.6f} {e:.4f} {f:.4f} cm\n'.encode())
    xb = doc.get_new_xref(); doc.update_object(xb, '<<>>'); doc.update_stream(xb, b'\nQ\n')
    doc.xref_set_key(page.xref, 'Contents', f'[{xa} 0 R {old} {xb} 0 R]')
    return True

def turned(doc, i, deg, dx=0.0, dy=0.0):
    """one page of doc in a new document, its content turned by deg and moved by (dx, dy) (to measure or draw it)"""
    t = pymupdf.open(); t.insert_pdf(doc, from_page=i, to_page=i)
    if deg or dx or dy: rotate_contents(t, t[0], deg, dx, dy)
    return t

def inside(b, box, tol=0.5):
    return b[0] >= box[0] - tol and b[1] >= box[1] - tol and b[2] <= box[2] + tol and b[3] <= box[3] + tol

def analyse_pages(path):
    doc = pymupdf.open(path)
    pages = []
    for i, page in enumerate(doc):
        r = page.rect
        rec = {'w': round(r.width, 1), 'h': round(r.height, 1)}
        if page.rotation: rec['kind'] = 'rotated'; pages.append(rec); continue
        a, z = gray(page, 500)
        mk = marks(a, z, r.width)
        if mk['box'] is not None and mk['dark'] <= 0.35:     # a tilted text page: turn it level (the sign is checked)
            ang, gain = skew_of(mk['xy'])
            if 0.1 <= abs(ang) < 0.35:                   # small: measure again at twice the resolution
                a2, z2 = gray(page, 1000); ang, gain = skew_of(marks(a2, z2, r.width)['xy'])
            if abs(ang) >= SKEW_MIN and gain >= 1.02:
                for deg in (-ang, ang):
                    t = turned(doc, i, deg); a2, z2 = gray(t[0], 500); mk2 = marks(a2, z2, r.width); t.close()
                    # the turned page must still show the page's ink (a broken drawing would show none); its text block is
                    # naturally narrower once level, so its size is not compared
                    if mk2['box'] is None or mk2['xy'] is None or not (0.6 <= len(mk2['xy'][0]) / len(mk['xy'][0]) <= 1.6):
                        continue
                    left, _ = skew_of(mk2['xy'], raw=True)   # the plain whole-page angle must now read level
                    if abs(left) <= max(0.1, abs(ang) / 3): rec['skew'] = round(deg, 3); mk = mk2; break
        mk.pop('xy', None); mk.pop('parts', None)
        rec.update(allowed=mk['allowed'], specks=mk['specks'], blots=mk['blots'], edge=mk['edge'], core=mk['core'], paper=round(mk.get('paper', 0)),
                   rules=mk.get('rules', []))
        if mk['box'] is None: rec['kind'] = 'blank' if mk['dark'] < 0.5 else 'picture'
        elif mk['dark'] > 0.35: rec['kind'] = 'picture'   # dark pages only: a tight light scan is text (stays whole if it cannot fit)
        else: rec['kind'] = 'text'
        rec['box'] = mk['box']
        pages.append(rec)
    doc.close()
    return pages

def analyse(path):
    """kept for the old callers: the measured pages and the decision at the narrowest box"""
    return decide(analyse_pages(path))

def plan(path):
    """the whole method: measure every page once, then the narrowest box that works — the width of 95 % of the pages,
    else 98 %, else all; each tried with the second check (a book is cropped only if few pages stay whole)"""
    import copy
    pages = analyse_pages(path); rec = None
    for wq in (0.95, 0.98, 1.0):
        rec = decide(copy.deepcopy(pages), wq)
        if rec.get('decision') != 'crop': continue
        rec = verify(path, rec)
        if rec.get('decision') == 'crop': rec['width_quantile'] = wq; return rec
    return rec

def q(vals, f):
    s = sorted(vals); return s[min(len(s) - 1, max(0, int(round(f * (len(s) - 1)))))]

def iou(a, b):
    x0, y0, x1, y1 = max(a[0], b[0]), max(a[1], b[1]), min(a[2], b[2]), min(a[3], b[3])
    if x1 <= x0 or y1 <= y0: return 0.0
    i = (x1 - x0) * (y1 - y0); return i / ((a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - i)

def decide(pages, wq=0.95):
    out = {'pages': pages, 'n': len(pages)}
    text = [i for i, p in enumerate(pages) if p['kind'] == 'text']
    out['measured'] = len(text)
    if len(text) < 5 or len(text) < 0.5 * len(pages):
        out['decision'] = 'skip: few text pages'; return out
    # a «stain» found at the same place on 3 other pages or more is part of the print (ornament, logo): content again
    allb = [(i, bl) for i in text for bl in pages[i].get('blots', [])]
    def same_place(a, b, w, h):                       # scans shift a little from page to page: centres within 3 %, sizes ×2
        aw, ah, bw_, bh_ = a[2] - a[0], a[3] - a[1], b[2] - b[0], b[3] - b[1]
        return abs((a[0] + a[2]) - (b[0] + b[2])) / 2 <= 0.03 * w and abs((a[1] + a[3]) - (b[1] + b[3])) / 2 <= 0.03 * h \
            and 0.5 <= (aw + 1) / (bw_ + 1) <= 2 and 0.5 <= (ah + 1) / (bh_ + 1) <= 2
    for i, bl in allb:
        w, h = pages[i]['w'], pages[i]['h']
        if sum(1 for j, c in allb if j != i and same_place(bl, c, w, h)) >= max(3, int(0.03 * len(text))):
            p = pages[i]; p['blots'].remove(bl); bx = p['box']
            p['box'] = [min(bx[0], bl[0]), min(bx[1], bl[1]), max(bx[2], bl[2]), max(bx[3], bl[3])]
    bw = {i: pages[i]['box'][2] - pages[i]['box'][0] for i in text}; bh = {i: pages[i]['box'][3] - pages[i]['box'][1] for i in text}
    core = {i: pages[i].get('core') or pages[i]['box'] for i in text}
    cw = {i: core[i][2] - core[i][0] for i in text}
    pw = q([pages[i]['w'] for i in text], 0.5); ph = q([pages[i]['h'] for i in text], 0.5)
    Tw, Th = q(bw.values(), wq), q(bh.values(), 1.0)            # width: wq of the pages (wider ones centre on their own content); height: the tallest page
    full_w = [i for i in text if cw[i] >= 0.9 * q(cw.values(), 0.5)]
    full_h = [i for i in text if bh[i] >= 0.9 * q(bh.values(), 0.5)]
    # a printed frame around the text (a vertical rule on both sides on most full pages) is the page's own border: the box
    # keeps a hairline outside it (owner, وحي القلم: «كل ما خارج الإطار الظاهر الخفيف… يمكن أن يقص»); otherwise a margin of
    # 8 % of the text width each side (owner: the margins of the third sample were «كبيرة قليلا»), 5 % above and below
    def framed(i):
        c = core[i]; rs = pages[i].get('rules') or []
        return any(r[2] <= c[0] for r in rs) and any(r[0] >= c[2] for r in rs)
    out['framed'] = sum(1 for i in full_w if framed(i)) >= 0.5 * max(1, len(full_w))
    m0 = M * pw / REF
    if out['framed']: W, H = Tw + 2 * 0.02 * Tw, Th + 2 * 0.02 * Th
    else: W, H = Tw + 2 * max(m0, 0.08 * Tw), Th + 2 * max(m0, 0.05 * Th)
    cx = {i: (core[i][0] + core[i][2]) / 2 for i in text}            # centred on the text block, not on a stray mark
    cy = {i: (pages[i]['box'][1] + pages[i]['box'][3]) / 2 for i in text}
    lim = lambda i: pages[i].get('allowed') or [0, 0, pages[i]['w'], pages[i]['h']]
    fitW = [2 * min(cx[i] - lim(i)[0], lim(i)[2] - cx[i]) for i in full_w]
    fitH = [2 * min(cy[i] - lim(i)[1], lim(i)[3] - cy[i]) for i in full_h]
    W = min(W, max(Tw, q(fitW, 0.05)) if fitW else W, pw); H = min(H, max(Th, q(fitH, 0.05)) if fitH else H, ph)
    # odd and even pages: the same horizontal centre by default; a different one per parity only when the book really
    # lays out like that — marginal material (folio numbers of the manuscript, side glosses, outer page numbers) on a
    # fixed side, odd pages one way and even pages the other (owner 2026-10-08: «على حسب المصلحة… والأصل التوسط الواحد»)
    off = {0: 0.0, 1: 0.0}
    ext = {i: (pages[i]['box'][0] + pages[i]['box'][2]) / 2 - cx[i] for i in full_w}
    for par in (0, 1):
        v = [ext[i] for i in full_w if i % 2 == par]
        if len(v) >= 10:
            med = q(v, 0.5)
            same = sum(1 for x in v if x * med > 0 and abs(x) >= 0.005 * pw) / len(v)
            if abs(med) >= 0.015 * pw and same >= 0.7: off[par] = med
    out['parity_offsets'] = {str(k): round(v, 1) for k, v in off.items()}
    if off[0] or off[1]:
        cx = {i: v + off[i % 2] for i, v in cx.items()}   # the box follows the page's printed layout, per parity
        fitW = [2 * min(cx[i] - lim(i)[0], lim(i)[2] - cx[i]) for i in full_w]
        W = min((Tw + 2 * 0.02 * Tw) if out['framed'] else (Tw + 2 * max(m0, 0.08 * Tw)), max(Tw, q(fitW, 0.05)) if fitW else W, pw)
    def near(i, pool, val):                         # a short page takes the place of its full neighbours (same parity)
        same = [j for j in pool if j % 2 == i % 2] or pool
        k = sorted(same, key=lambda j: abs(j - i))[:6]
        return q([val[j] for j in k], 0.5)
    fw, fh = set(full_w), set(full_h)
    whole, offc, own, moved = [], [], 0, 0
    for i, p in enumerate(pages):
        if p['kind'] in ('rotated', 'picture'): p['crop'] = None; continue
        bx = p.get('box')
        x = cx[i] if i in fw else (near(i, full_w, cx) if full_w else pw / 2)
        y = cy[i] if i in fh else (near(i, full_h, cy) if full_h else ph / 2)
        if bx:
            b = [x - W / 2, y - H / 2, x + W / 2, y + H / 2]
            dx = bx[0] - b[0] if bx[0] < b[0] else (bx[2] - b[2] if bx[2] > b[2] else 0)
            dy = bx[1] - b[1] if bx[1] < b[1] else (bx[3] - b[3] if bx[3] > b[3] else 0)
            if dx or dy:
                # the usual place does not hold this page's marks (a stamp, a plate, a chapter start, a marginal note):
                # centre the box on the page's own content on that axis — equal margins, never text against the frame
                if dx: x = (bx[0] + bx[2]) / 2
                if dy: y = (bx[1] + bx[3]) / 2
                p['own_centre'] = True; own += 1
        b = [x - W / 2, y - H / 2, x + W / 2, y + H / 2]
        sx = -b[0] if b[0] < 0 else (p['w'] - b[2] if b[2] > p['w'] else 0)     # the box must stay on the page:
        sy = -b[1] if b[1] < 0 else (p['h'] - b[3] if b[3] > p['h'] else 0)     # on white paper the CONTENT moves
        if (sx or sy) and bx and p.get('paper', 0) >= 235:                       # with it, so the text stays centred
            nb = [bx[0] + sx, bx[1] + sy, bx[2] + sx, bx[3] + sy]
            if nb[0] >= 0 and nb[1] >= 0 and nb[2] <= p['w'] and nb[3] <= p['h']:
                p['move'] = [round(sx, 1), round(sy, 1)]; moved += 1
                p['box'] = bx = [round(v, 1) for v in nb]
                p['blots'] = [[v[0] + sx, v[1] + sy, v[2] + sx, v[3] + sy] for v in p.get('blots', [])]
                p['specks'] = [[v[0] + sx, v[1] + sy, v[2] + sx, v[3] + sy] for v in p.get('specks', [])]
                p['edge'] = [[v[0] + sx, v[1] + sy, v[2] + sx, v[3] + sy] for v in p.get('edge', [])]
        b = [round(b[0] + sx, 1), round(b[1] + sy, 1), round(b[2] + sx, 1), round(b[3] + sy, 1)]
        if bx and p.get('blots'):                    # dodge a stain: slide the box away from it, as far as the content and
            lo, hi = max(0, bx[2] - (b[2] - b[0])), min(bx[0], p['w'] - (b[2] - b[0]))      # the page allow (same size)
            for bl in p['blots']:
                if bl[2] > b[0] and bl[0] < b[2] and bl[3] > b[1] and bl[1] < b[3]:
                    nx = bl[2] + 2 if bl[2] <= bx[0] else (bl[0] - 2 - (b[2] - b[0]) if bl[0] >= bx[2] else None)
                    if nx is not None and lo <= hi:
                        want = nx; nx = min(max(nx, lo), hi); b = [round(nx, 1), b[1], round(nx + b[2] - b[0], 1), b[3]]; p['dodged'] = True
                        short = want - nx                    # the page edge stops the box: on white paper the content moves the
                        if short and p.get('paper', 0) >= 235 and abs(short) <= 0.03 * p['w']:   # last points the other way
                            mv = p.get('move') or [0, 0]; p['move'] = [round(mv[0] - short, 1), mv[1]]
                            sh = -short
                            p['box'] = bx = [bx[0] + sh, bx[1], bx[2] + sh, bx[3]]
                            p['blots'] = [[v[0] + sh, v[1], v[2] + sh, v[3]] for v in p.get('blots', [])]
                            p['specks'] = [[v[0] + sh, v[1], v[2] + sh, v[3]] for v in p.get('specks', [])]
                            p['edge'] = [[v[0] + sh, v[1], v[2] + sh, v[3]] for v in p.get('edge', [])]
        b = [max(0, b[0]), max(0, b[1]), min(p['w'], b[2]), min(p['h'], b[3])]
        if p['kind'] == 'text' and not inside(bx, b): p['crop'] = None; whole.append(i); continue
        p['crop'] = b
        p['cut_specks'] = [v for v in p['specks'] if not inside(v, b, 0)]
        if i in fw and bx: offc.append(abs((b[0] + b[2]) / 2 - (cx[i] + (p.get('move') or [0, 0])[0])) / p['w'])
    out['whole'] = whole; out['own_centre'] = own; out['content_moved'] = moved
    out['skewed'] = sum(1 for p in pages if p.get('skew'))
    out['blot_pages'] = sum(1 for p in pages if p.get('crop') and p.get('blots'))
    out['size'] = [round(W, 1), round(H, 1)]
    out['gain'] = round(pw / W, 3); out['gain_h'] = round(ph / H, 3)
    out['offcentre_before'] = round(q([abs(cx[i] - pages[i]['w'] / 2) / pages[i]['w'] for i in full_w], 0.5), 3) if full_w else 0
    out['offcentre_after'] = round(q(offc, 0.5), 3) if offc else 0
    banded = sum(1 for i in text if pages[i]['allowed'][0] > 0.02 * pw or pages[i]['allowed'][2] < 0.98 * pages[i]['w']) > 0.5 * len(text)
    out['banded'] = banded
    if out['gain'] < GAIN and out['offcentre_before'] < OFFC and not banded and out['skewed'] < 0.05 * len(text):
        out['decision'] = f'skip: already fine (gain {out["gain"]}, off-centre {out["offcentre_before"]})'
    elif len(whole) > MAX_WHOLE * len(text): out['decision'] = f'skip: {len(whole)} pages do not fit one box'
    else: out['decision'] = 'crop'
    return out

def transformed(doc, i, p):
    """page i as the reader will see it (turned level, content moved) — in a one-page document"""
    mv = p.get('move') or [0, 0]
    return turned(doc, i, p.get('skew') or 0, mv[0], mv[1])

def verify(path, rec, px=1000):
    """second look at twice the resolution: every mark found outside a page's box must be one the first look left out on
    purpose (a stain, edge noise — the same place, give or take 3 pt) or an isolated speck; anything else is content:
    the box may move up to 2 % to take it in, else the page stays whole"""
    doc = pymupdf.open(path); moved = []
    near = lambda b, regions: any(b[0] < r[2] + 3 and b[2] > r[0] - 3 and b[1] < r[3] + 3 and b[3] > r[1] - 3 for r in regions)
    def look(i, q):                                   # the page as the reader will see it, measured at px
        t = transformed(doc, i, q); page = t[0]; a, z = gray(page, px); mk = marks(a, z, page.rect.width); t.close()
        return mk
    for i, p in enumerate(rec['pages']):
        if not p.get('crop') and not p.get('skew'): continue
        mk = look(i, p)
        # LEVEL CHECK (owner: «اختبار يضمن أننا أزلنا الميل تماما ولم نصطنع ميلا جديدا أو نبق شيئا من الميل»):
        # a turned page must read level (whole-page angle ≤ 0.1°); what is left is turned away once more (both signs tried),
        # else the smaller of the remaining tilts is kept and reported. An untouched page showing a tilt the first look did
        # not treat is turned here if that makes it level, else reported; an untouched page cannot gain a tilt.
        if p.get('skew'):
            res, _ = skew_of(mk['xy'], raw=True)
            if abs(res) > 0.1:
                best = (abs(res), p['skew'], mk)
                for d2 in (p['skew'] - res, p['skew'] + res):
                    mk2 = look(i, dict(p, skew=round(d2, 3)))
                    if mk2['xy'] is None: continue
                    r2, _ = skew_of(mk2['xy'], raw=True)
                    if abs(r2) < best[0]: best = (abs(r2), round(d2, 3), mk2)
                p['skew'], mk, res = best[1], best[2], best[0]
            if abs(res) > 0.15:                      # still not level: the turn is undone — never keep a tilt we made
                p.pop('skew', None); p['unsure_tilt'] = True; mk = look(i, p)
            else: p['after_tilt'] = round(abs(res), 3)
        elif mk['xy'] is not None:
            u, g = skew_of(mk['xy'])
            if abs(u) >= SKEW_MIN and g >= 1.02:
                for d2 in (-u, u):
                    mk2 = look(i, dict(p, skew=round(d2, 3)))
                    if mk2['xy'] is None or not (0.6 <= len(mk2['xy'][0]) / len(mk['xy'][0]) <= 1.6): continue
                    r2, _ = skew_of(mk2['xy'], raw=True)
                    if abs(r2) <= max(0.1, abs(u) / 3): p['skew'] = round(d2, 3); p['after_tilt'] = round(abs(r2), 3); p['turned_in_check'] = True; mk = mk2; break
                else: p['untreated_tilt'] = round(u, 3)
        if not p.get('crop'): continue
        c = p['crop']; known = (p.get('blots') or []) + (p.get('edge') or [])
        out = [b for b in mk.get('parts', []) if not inside(b, c, 1.0) and not near(b, known)]
        if out:
            ob = [min(b[0] for b in out), min(b[1] for b in out), max(b[2] for b in out), max(b[3] for b in out)]
            dx = ob[0] - c[0] if ob[0] < c[0] else (ob[2] - c[2] if ob[2] > c[2] else 0)
            dy = ob[1] - c[1] if ob[1] < c[1] else (ob[3] - c[3] if ob[3] > c[3] else 0)
            n = [c[0] + dx, c[1] + dy, c[2] + dx, c[3] + dy]
            if abs(dx) <= 0.02 * p['w'] and abs(dy) <= 0.02 * p['h'] and n[0] >= 0 and n[1] >= 0 and n[2] <= p['w'] and n[3] <= p['h'] \
               and inside(p['box'], n, 1.0) and all(inside(b, n, 1.0) for b in out):
                p['crop'] = [round(v, 1) for v in n]; p['verify_moved'] = True
            else:
                p['crop'] = None; p['verify'] = ob; moved.append(i); continue
        p['cut_specks'] = [x for x in mk['specks'] if not inside(x, p['crop'], 0)]
    doc.close()
    rec['whole'] = sorted(set(rec.get('whole', [])) | set(moved)); rec['verify_whole'] = moved
    rec['blot_pages'] = sum(1 for p in rec['pages'] if p.get('crop') and p.get('blots'))
    rec['skewed'] = sum(1 for p in rec['pages'] if p.get('skew'))
    rec['residual_tilt'] = [i + 1 for i, p in enumerate(rec['pages']) if p.get('skew') and p.get('after_tilt', 0) > 0.15]
    rec['untreated_tilt'] = [i + 1 for i, p in enumerate(rec['pages']) if p.get('untreated_tilt')]
    rec['unsure_tilt'] = [i + 1 for i, p in enumerate(rec['pages']) if p.get('unsure_tilt')]
    if rec.get('decision') == 'crop' and len(rec['whole']) > MAX_WHOLE * max(1, rec['measured']):
        rec['decision'] = f'skip: {len(rec["whole"])} pages do not fit one box (second check, 1,000 px)'
    return rec

def images_of(doc):
    return [[(x[0], x[2], x[3], len(doc.xref_stream_raw(x[0]) or b'')) for x in p.get_images(full=True)] for p in doc]

def apply(src, rec, dst):
    """LOSSLESS: per page the CropBox, and for tilted or moved pages one «q … cm» / «Q» pair around the content;
    incremental save; checked: same pages, same images byte for byte"""
    import shutil
    shutil.copyfile(src, dst)
    before = pymupdf.open(src); imgs = images_of(before); n = len(before); before.close()
    doc = pymupdf.open(dst); done = turned_n = 0
    for i, p in enumerate(rec['pages']):
        page = doc[i]
        mv = p.get('move') if p.get('crop') else None
        if p.get('skew') or mv:
            rotate_contents(doc, page, p.get('skew') or 0, *(mv or [0, 0])); turned_n += 1
        b = p.get('crop')
        if not b: continue
        cb = page.cropbox
        r = pymupdf.Rect(b[0] + cb.x0, b[1] + cb.y0, b[2] + cb.x0, b[3] + cb.y0) & page.mediabox
        if not r.is_empty: page.set_cropbox(r); done += 1
    doc.save(dst, incremental=True, encryption=pymupdf.PDF_ENCRYPT_KEEP); doc.close()
    chk = pymupdf.open(dst)
    assert len(chk) == n, 'page count changed'
    assert images_of(chk) == imgs, 'images changed'
    chk.close()
    return {'pages': n, 'cropped': done, 'turned_or_moved': turned_n, 'bytes_out': os.path.getsize(dst)}

def sample_pages(rec):
    """pages worth showing for approval, with the reason: two facing text pages from the middle, the most tilted page,
    the page with the most stains left out, a page centred on its own text, the tightest margin, a page left whole"""
    P = rec['pages']; text = [i for i, p in enumerate(P) if p.get('crop') and p['kind'] == 'text']
    if not text: return []
    mid = text[len(text) // 2]
    out = [(mid, 'mid'), (mid + 1 if mid + 1 < len(P) and P[mid + 1].get('crop') else mid - 1, 'mid')]
    sk = [i for i in text if P[i].get('skew')]
    if sk: out.append((max(sk, key=lambda i: abs(P[i]['skew'])), 'skew'))
    bl = [i for i in text if P[i].get('blots')]
    if bl: out.append((max(bl, key=lambda i: sum((b[2] - b[0]) * (b[3] - b[1]) for b in P[i]['blots'])), 'blot'))
    ow = [i for i in text if P[i].get('own_centre') or P[i].get('move')]
    if ow: out.append((ow[0], 'own'))
    sp = max(text, key=lambda i: len(P[i].get('cut_specks', [])))
    if P[sp].get('cut_specks'): out.append((sp, 'speck'))
    def slack(i):
        b, c = P[i]['box'], P[i]['crop']; return min(b[0] - c[0], c[2] - b[2], b[1] - c[1], c[3] - b[3]) / P[i]['w']
    out.append((min(text, key=slack), 'tight'))
    out += [(i, 'whole') for i in rec.get('whole', [])[:1]]
    seen, res = set(), []
    for i, r in out:
        if i not in seen: seen.add(i); res.append((i, r))
    return res[:7]

def back_to_original(page, p):
    """maps points of the reader's frame (turned level, moved) back onto the original page, to draw on it"""
    mv = p.get('move') or [0, 0]; deg = p.get('skew') or 0
    tm = page.transformation_matrix
    doc = page.parent; mb = raw_box(doc, page.xref, 'MediaBox'); cx, cy = (mb[0] + mb[2]) / 2, (mb[1] + mb[3]) / 2
    fwd = pymupdf.Matrix(1, 0, 0, 1, -cx, -cy) * pymupdf.Matrix(deg) * pymupdf.Matrix(1, 0, 0, 1, cx, cy) * pymupdf.Matrix(1, 0, 0, 1, mv[0], -mv[1])
    m = ~tm * ~fwd * tm
    return lambda x, y: pymupdf.Point(x, y) * m

def sheet(src, rec, outdir, pages=None, px=480):
    """before: the page as scanned — the box in red, stains left out in orange, hidden specks circled in blue (all drawn
    back onto the original, so a tilted page shows its box tilted); after: what the reader shows, fit to the same width.
    pages: [(index, reason)] — written to reasons.json for the review page"""
    os.makedirs(outdir, exist_ok=True)
    doc = pymupdf.open(src); made = []; reasons = {}
    for i, why in pages or []:
        p = rec['pages'][i]; reasons[str(i)] = why
        tmp = pymupdf.open(); tmp.insert_pdf(doc, from_page=i, to_page=i); tp = tmp[0]
        z0 = px / tp.rect.width
        bk = back_to_original(tp, p)
        sh = tp.new_shape()
        poly = lambda r: [bk(r[0], r[1]), bk(r[2], r[1]), bk(r[2], r[3]), bk(r[0], r[3]), bk(r[0], r[1])]
        if p.get('crop'): sh.draw_polyline(poly(p['crop'])); sh.finish(color=(0.85, 0, 0), width=2.5)
        for b in p.get('blots', []): sh.draw_polyline(poly([b[0] - 3, b[1] - 3, b[2] + 3, b[3] + 3])); sh.finish(color=(1, 0.55, 0), width=2.5)
        for b in p.get('edge', []):
            if p.get('crop') and not inside(b, p['crop'], 0): sh.draw_polyline(poly([b[0] - 2, b[1] - 2, b[2] + 2, b[3] + 2])); sh.finish(color=(0.6, 0, 0.8), width=1.5)
        for s in p.get('cut_specks', []):
            sh.draw_circle(bk((s[0] + s[2]) / 2, (s[1] + s[3]) / 2), 9); sh.finish(color=(0, 0.3, 0.9), width=2)
        sh.commit()
        bpix = tp.get_pixmap(matrix=pymupdf.Matrix(z0, z0), alpha=False)
        fb = os.path.join(outdir, f'p{i + 1:04d}-before.jpg'); bpix.save(fb, jpg_quality=72)
        t = transformed(doc, i, p); page = t[0]
        b = p.get('crop') or [0, 0, page.rect.width, page.rect.height]; z = px / (b[2] - b[0])
        apix = page.get_pixmap(matrix=pymupdf.Matrix(z, z), clip=pymupdf.Rect(b), alpha=False)
        fa = os.path.join(outdir, f'p{i + 1:04d}-after.jpg'); apix.save(fa, jpg_quality=72); t.close()
        made.append({'page': i + 1, 'why': why, 'before': fb, 'after': fa})
        tmp.close()
    doc.close()
    json.dump(reasons, open(os.path.join(outdir, 'reasons.json'), 'w'))
    return made

WHY_AR = {'mid': 'صفحة من وسط الكتاب', 'speck': 'أكثر صفحة فيها نقط معزولة (الدوائر الزرقاء)',
          'tight': 'الصفحة التي يقترب نصها من الإطار أكثر من غيرها', 'skew': 'أشد الصفحات ميلا: قُوِّمت',
          'blot': 'صفحة فيها بقعة أو خط داكن ليس من الكتاب (بالبرتقالي): يبقى خارج الإطار',
          'own': 'صفحة شاذة (ختم، لوحة، تعليقة بعيدة): وُسِّط الإطار على ما فيها هي', 'whole': 'صفحة تبقى كاملة (نصها أعرض من الإطار)'}

def review_page(cases, skipped, outdir, stats):
    """one self-contained Arabic page (+ images/) for the owner's approval: per book the gain, the pages left whole, the
    hidden specks and before/after pairs. cases: [{path, rec, sheet_dir}], skipped: [{path, rec, image}]"""
    import html, shutil
    img = os.path.join(outdir, 'images'); os.makedirs(img, exist_ok=True)
    esc = html.escape
    cards = []
    for n, c in enumerate(cases, 1):
        rec = c['rec']; P = rec['pages']
        why = {int(k): v for k, v in json.load(open(os.path.join(c['sheet_dir'], 'reasons.json'))).items()}
        pages = list(why)
        specks = sum(len(p.get('cut_specks', [])) for p in P if p.get('crop'))
        figs = []
        for i in pages:
            pair = []
            for s, cap in (('before', 'قبل — الإطار الأحمر هو ما سيظهر، والبرتقالي بقعة تبقى خارجه'), ('after', 'بعد — بعرض الشاشة نفسه')):
                f = os.path.join(c['sheet_dir'], f'p{i + 1:04d}-{s}.jpg')
                if not os.path.exists(f): continue
                dst = f'{n:02d}-p{i + 1:04d}-{s}.jpg'; shutil.copyfile(f, os.path.join(img, dst))
                pair.append(f'<figure><img src="images/{dst}" alt=""><figcaption>{cap}</figcaption></figure>')
            figs.append(f'<div class="pair"><h4>ص {i + 1} — {WHY_AR[why[i]]}</h4><div class="imgs">{"".join(pair)}</div></div>')
        title = esc(c['path'].rsplit('/', 1)[-1].rsplit('.', 1)[0]); where = esc(c['path'].rsplit('/', 1)[0])
        cards.append(f'''<section class="card"><h3>{n}. {title}</h3><p class="where">{where}</p>
<ul class="facts"><li>يكبر النص على الهاتف <b>{round((rec["gain"] - 1) * 100)}٪</b></li><li>{rec["n"]} صفحة، منها {len(rec.get("whole", []))} تبقى كاملة</li>
<li>انحراف النص عن وسط الصفحة: {round(rec.get("offcentre_before", 0) * 100, 1)}٪ ← {round(rec.get("offcentre_after", 0) * 100, 1)}٪</li>
<li>التوسط الأفقي: {"مختلف للفردية والزوجية (في الهامش مادة ثابتة في جهة)" if any(float(v) for v in (rec.get("parity_offsets") or {}).values()) else "واحد للفردية والزوجية"}</li><li>صفحات مائلة قُوِّمت: {rec.get("skewed", 0)}</li><li>بقي فيها ميل بعد التقويم: {len(rec.get("residual_tilt") or [])}{(" (ص " + "، ".join(map(str, rec["residual_tilt"][:8])) + ")") if rec.get("residual_tilt") else ""}</li><li>مائلة لم تُقوَّم: {len(rec.get("untreated_tilt") or [])}{(" (ص " + "، ".join(map(str, rec["untreated_tilt"][:8])) + ")") if rec.get("untreated_tilt") else ""}</li><li>صفحات فيها بقع تُركت خارج الإطار: {rec.get("blot_pages", 0)}</li><li>صفحات شاذة وُسِّطت على نصها: {rec.get("own_centre", 0)}</li></ul>{"".join(figs)}</section>''')
    skips = []
    for s in skipped:
        dst = 'skip-' + os.path.basename(s['image']); shutil.copyfile(s['image'], os.path.join(img, dst))
        skips.append(f'<figure class="skip"><img src="images/{dst}" alt=""><figcaption><b>{esc(s["path"].rsplit("/", 1)[-1].rsplit(".", 1)[0])}</b><br>{esc(s["why"])}</figcaption></figure>')
    doc = f'''<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>عينة القص الجديد</title><style>
:root{{--bg:#f6f4ef;--card:#fff;--ink:#222;--mute:#666;--line:#ddd;--accent:#8a1c1c}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--bg:#1b1b1b;--card:#252525;--ink:#eee;--mute:#aaa;--line:#3a3a3a;--accent:#e07070}}}}
:root[data-theme="dark"]{{--bg:#1b1b1b;--card:#252525;--ink:#eee;--mute:#aaa;--line:#3a3a3a;--accent:#e07070}}
body{{margin:0;background:var(--bg);color:var(--ink);font:17px/1.7 "Noto Naskh Arabic","Amiri",serif}}
main{{max-width:1100px;margin:auto;padding:16px}}h1{{color:var(--accent);margin:.2em 0}}
.card,.intro{{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px 16px;margin:16px 0}}
.where{{color:var(--mute);font-size:.85em;margin:0}}.facts{{display:flex;flex-wrap:wrap;gap:6px 22px;padding:0;list-style:none;margin:.5em 0}}
.pair h4{{margin:.8em 0 .3em;font-weight:normal;color:var(--mute)}}.imgs{{display:grid;grid-template-columns:1fr 1fr;gap:10px}}
figure{{margin:0}}img{{width:100%;height:auto;border:1px solid var(--line);background:#fff}}figcaption{{font-size:.8em;color:var(--mute);text-align:center}}
.skips{{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:12px}}
@media (max-width:640px){{.imgs{{grid-template-columns:1fr}}}}</style></head><body><main>
<h1>عينة القص الجديد — للموافقة (الصيغة الثالثة)</h1>
<div class="intro"><p>بعد ملاحظاتك على العينة الثانية: البقع والخطوط السوداء الممزقة عند حافة الورقة (كالتي في اللآلئ ج 1 ص 4)، تقويم الصفحات المائلة، التوسط الرأسي، توسيط الصفحات الشاذة، وترك التنظيف. <b>لم يتغير شيء على الهاتف</b>: هذه صور فقط.</p><ul>
<li>ما الذي يتغير في الملف؟ في كل صفحة شيئان: صورة الصفحة الممسوحة، وتعليمات تقول للقارئ أين يرسمها وأي جزء منها يُظهر. الصورة المخزنة تبقى كما هي حرفا بحرف: لا تُعاد معالجتها ولا ضغطها، فلا تنقص جودتها شيئا. الذي يتغير التعليمات وحدها: (1) الإطار الذي يحدد الجزء الظاهر، وما خارجه مخفي باقٍ في الملف لا محذوف؛ (2) في الصفحة المائلة أمرٌ بأن تُرسم مدوَّرة قليلا (أو مزاحة)، فيرسمها القارئ كما يرسمها حين تكبّرها. ولذلك يعود أي كتاب إلى حاله الأول تماما بحذف هذه التعليمات.</li>
<li>إطار بمقاس واحد للكتاب كله، يوضع في كل صفحة بحيث تتوسط كتلةُ نصها أفقيا ورأسيا، ولو أخلّ التصوير بموضعها.</li>
<li>الصفحة القصيرة (كآخر صفحة في فصل ليس فيها إلا أسطر قليلة في أعلاها): لا يوسَّط الإطار على أسطرها وإلا قفزت إلى وسط الشاشة، بل يوضع في الموضع نفسه الذي هو فيه في الصفحات المجاورة الكاملة، فتبقى الأسطر في أعلى الصفحة كما في الكتاب المطبوع.</li>
<li>الصفحة الشاذة (صفحة لا يتسع الموضع المعتاد لما فيها، كصفحة ختم الرافع وسطرها في أقصى الطرف، أو لوحة، أو تعليقة بعيدة في الهامش): يوسَّط الإطار على ما فيها هي، فيظهر في وسطه بهوامش متساوية؛ فإن لم يتسع له في حدود الصفحة أزيح المحتوى نفسه إلى الوسط (على الورق الأبيض فقط).</li>
<li>الإطار يحيط بكل أثر كتابة في الصفحة: الحواشي، أرقام الصفحات، العناوين الجارية، التعليقات وأرقام المخطوط في الهامش، والأطر والزخارف المطبوعة؛ ثم هامش سخي.</li>
<li>يبقى خارج الإطار ما ليس كتابة ولا طباعة، بقواعد حذرة: البقع والخطوط الداكنة الممزقة عند الحافة (بالبرتقالي)، وحبيبات الماسح وحافة الورقة وعلامات الزوايا (بالبنفسجي)، والغبار المعزول (بالأزرق). ما تكرر في موضع واحد من صفحات كثيرة يُعدّ من الطباعة فيبقى.</li>
<li>كل صفحة تُفحص مرة ثانية بدقة مضاعفة: كل ما يُرى خارج الإطار يجب أن يكون مما تُرك عمدا، وإلا زُحزح الإطار قليلا ليشمله أو بقيت الصفحة كاملة.</li>
<li>لا تنظيف ولا تلوين (كما اتفقنا): ما لا يدخل الإطار يُترك كما هو.</li>
</ul>
<p>{esc(stats)}</p></div>
{"".join(cards)}
<h2>أمثلة لكتب تبقى كما هي</h2><div class="skips">{"".join(skips)}</div>
<div class="intro"><p>إن رضيت بهذه الطريقة أطبقها على دفعات، كل دفعة بعينة مثل هذه قبل استبدال أي ملف، والأصل محفوظ حتى توافق.</p></div>
</main></body></html>'''
    open(os.path.join(outdir, 'index.html'), 'w', encoding='utf-8').write(doc)
    return os.path.join(outdir, 'index.html')

if __name__ == '__main__':
    cmd, a = sys.argv[1], sys.argv[2:]
    if cmd == 'analyse':
        rec = plan(a[0])
        json.dump(rec, open(a[1], 'w'), ensure_ascii=False)
        print(json.dumps({k: rec.get(k) for k in ('decision', 'n', 'measured', 'gain', 'gain_h', 'banded', 'boxes')} | {'whole': len(rec.get('whole', []))}, ensure_ascii=False))
    elif cmd == 'apply':
        print(json.dumps(apply(a[0], json.load(open(a[1])), a[2])))
    elif cmd == 'sheet':
        rec = json.load(open(a[1]))
        pg = [int(x) - 1 for x in a[3].split(',')] if len(a) > 3 else None
        print(json.dumps(sheet(a[0], rec, a[2], pg), ensure_ascii=False))
