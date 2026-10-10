"""Book-level crop and levelling of scanned books — the method after the 2026-10-07 revert, shaped by the owner's reviews of
three samples (2026-10-08). Owner's rules: nothing of the text may be lost («ولو تعليقة صغيرة في الهامش»); pages must not
sway; the text centred, horizontally and vertically, consistently on every page; ordinary books enlarged moderately;
tilted pages levelled; stains left out but never confused with print or an illustration; no pixel cleaning.

WHAT CHANGES IN THE FILE. A scanned page holds an image (the scan) and drawing instructions (where to draw it, which part
to show). Only the instructions change: (1) each page's CropBox — the part shown; what lies outside stays in the file;
(2) for a tilted, moved or scaled page, one stream «q a b c d e f cm» before the page's content and one «Q» after it — the
reader draws the same image turned (shifted, or a little smaller: see 8). The image streams, the text layer and everything else stay byte for byte
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
   on the whole text and on its right and left halves; the whole page's angle must lie within the range of the halves'
   angles (±0.1°) and the halves differ by ≤ 0.6°, else nothing is turned (index pages, two columns, verse and tables only
   look tilted to the whole-page profile: their whole-page angle falls outside their halves'). A small tilt (0.1–0.35°) is
   measured again at 1,000 px. A page is turned when the tilt is ≥ 0.2° and the profile gets ≥ 2 % sharper; both directions
   are tried and kept only if the turned page's whole-page angle reads level (≤ max(0.1°, a third of the tilt)) and the
   page still shows its ink (×0.6–1.6).
4a. A BOOK WITHOUT PRINT IN ITS SIDE MARGINS (owner 2026-10-09, اللآلئ): the text block is measured by gaps — from the
   core's columns, every mark less than 1.5 % of the width away joins it and widens it (a longer line, a heading, a verse
   stays whole); everything above and below inside those columns is text (running head, page number, footnotes); marks
   further out are in a side margin. When ≤ 10 % of the full pages show margin marks bigger than dust, the box is the
   text block + 6 % of its width on every side (the screen used as far as possible; owner 2026-10-09: 2 % left the text
   «مقاربا للحدود», «فحتى 4% قليل»), centred on each page's text block; whatever is in the side margins (dots, pen strokes, scan edges,
   stains) is cut — EXCEPT MARGINAL NOTES (owner, اللآلئ ص 40 «لعله الدارقطني»: «أبق مثل هذه الهوامش ولو اختلف الزوجي عن
   الفردي في موضع النص»): a group of ≥ 3 letter-sized marks (notes_of) is kept, the box moving to hold it (the text then
   off-centre on that page) or growing with the same proportions. No page stays whole for a stray mark. The second look
   checks that the text block and its notes seen at 1,000 px are inside the box and that no mark straddles its edge (a
   cut letter): if one does, the box slides (≤ 2 %) or grows with the same proportions (never beyond the sheet: the
   margin gives way first). A grown box is shown at the book's size (8). Framed books and books printing in their
   margins (folio numbers, glosses) follow 4 and 5 below.
4. BOX SIZE, one for the whole file: width = the content width of 95 % of the text pages (else 98 %, else all — see 7)
   + 8 % of it on each side (at least M); height = the tallest page's content + 5 % above and below. A book whose text is
   framed by a printed border (a rule on both sides on half its full pages or more) keeps only a hairline outside the
   frame: 2 % of the content's width and height. Narrowed only as far as
   needed to centre the text on 95 % of the full pages (a scan with one tight margin), never below the content width,
   never beyond the page.
5. BOX PLACE, page by page: a full page (text block ≥ 90 % of the usual width; content ≥ 90 % of the usual height) is
   centred on its own text block — the same horizontal centre for odd and even pages by default; a different one per parity
   only when the book lays out like that (marginal material on a fixed side: on ≥ 70 % of the full pages of a parity the
   content extends ≥ 1.5 % of the width beyond the text block on the same side), then the box keeps that offset; a short
   page (a chapter end, an index page of short entries) is placed so its lines stay where the neighbours' lines are,
   corrected by its own scan shift (owner 2026-10-09, المثلث ص 569 «ضعف توسيط»): by its page number, when the book prints
   it on its own line at a steady offset from the text (half the full pages within 0.6 % of the page) and it lies where
   the neighbours' does (± 3 %); else by a text edge lying where the neighbours' same edge lies (± 3 %: the right edge of
   right-aligned lines, the top line); else the median place of its 6 nearest full pages of the same parity. If the page's marks do not fit there
   (a stamp page, a plate, a far marginal note), the box is centred on that page's own content instead. If the box would
   leave the page, on white paper (≥ 235) the content is moved instead so it stays centred; otherwise the box stops at the
   edge. On a page with a stain, the box slides away from it as far as the content allows; when the page edge stops it, on
   white paper the content moves the remaining few points (≤ 3 % of the width) so the stain falls outside. A page whose content is wider
   or taller than the box stays whole (uncropped).
6. SECOND LOOK at 1,000 px, on each page as the reader will see it:
   - LEVEL CHECK, by two independent measures: (a) the shear profile of the turned page's ink (whole page), (b) the turned
     page image itself (700 px), rotated in steps and its central rows counted (proj_tilt; coarser — a guard against a
     turn gone wrong). A turned page is kept when (a) reads ≤ 0.15° (its precision near level) and (b) ≤ 0.2°; if the
     first turn does not, the 10 angles around it (0.05° apart) are tried and the one both measures read lowest is
     taken. A slightly curved page that no single rotation levels is kept when both read ≤ 0.25° and ≤ a third of its
     tilt, and is listed as curved. Otherwise the page is NOT turned at all and is listed (`unsure_tilt`) — a tilt the
     method made is never kept. Tilt is only read on pages with real text: at least 8 lines and enough ink. An untouched
     page that shows a tilt the first look did not treat is turned here when (b) sees the tilt too (≥ 0.15°) and the turn
     passes the same tests; if (b) sees no tilt it is listed as disputed (`tilt_disputed`), otherwise as
     `untreated_tilt`. An untouched page cannot gain a tilt.
   - every content mark found outside a page's box must lie (± 3 pt) on something the first look left out on purpose (a
     stain, edge noise); otherwise the box moves up to 2 % to take it in, or the page stays whole.
7. DECISION (plan): the narrowest width (95 %, 98 %, 100 %) with at most 5 % of the text pages left whole after the second
   look. The file is cropped for a real gain or a flaw (owner 2026-10-09: «أرغب في التقطيع عموما لما فيه من أفضلية للهاتف…
   ينظر ما كان على العموم مقاربا، وجودة إعداد الكتاب كله جيدة جدا، فهذا يمكن استبعاده»): the text gets ≥ 15 % larger on
   a phone; or a tilted page, even one (confirmed by the second look); or scanner bands; or the text ≥ 2 % off-centre on
   the median page, or swaying from page to page (its centre's interquartile range ≥ 1.5 % of the page); or stains left
   out on ≥ 5 % of the pages. A very well made scan whose crop would change little is left as it is (`reasons`); if its
   only flaw is tilted pages (or its pages do not fit one box), its tilted pages are levelled and nothing else changes
   (level(): «agree, as far as the margins are not too far from the desired results in the cropped books»).
8. ONE PAGE SIZE FOR THE WHOLE BOOK (frames; owner 2026-10-09: «أعراض الصفحات غير متساوية، هذا مرفوض بالمرّة… أما اتحاد
   العرض فيجب اطّراده في جميع الكتب»): every page is shown in a box of exactly the book's size, to 0.01 pt. A page whose
   needed part is larger (a grown box, a page no box holds, a cover or a plate — فهرسة ابن خير ص 380 «دون قصّ صورة
   الغلاف») shows that part whole, drawn smaller to fit (the same lossless «cm» instruction as a turn); a page smaller
   than the box (a shorter scan) is drawn up to 5 % larger when all it holds still fits, else on blank paper beyond its
   own edge (clipped to its sheet; its MediaBox grows). apply() reads every page's size back and refuses a book whose
   pages differ.
Nothing is applied to the phone without the owner's approval of a sample page (review_page()).
Usage:
  book_crop.py analyse in.pdf recipe.json          → plan(): recipe — per page box, tilt, move, stains (no output PDF)
  book_crop.py apply in.pdf recipe.json out.pdf    → lossless copy with the recipe's boxes and drawing instructions, checked
  book_crop.py sheet in.pdf recipe.json outdir     → JPEGs: before (box red, stains orange, edge noise purple, specks blue) / after
Needs PyMuPDF (~/.local/share/phone-library-tools/site), numpy, scipy."""
import json, os, sys
from concurrent.futures import ProcessPoolExecutor
sys.path.insert(0, os.path.expanduser('~/.local/share/phone-library-tools/site'))
import numpy as np
import pymupdf
from scipy import ndimage

REF = 420.0       # the page width (pt) the sizes below refer to
M = 14            # pt: isolation distance of a speck, and the least margin
SPECK = 4         # pt: a speck is at most SPECK × SPECK
GAIN = 1.15       # least text gain on a phone that makes a crop worth it by itself (owner 2026-10-09: «ينظر ما كان على العموم
                  # مقاربا، وجودة إعداد الكتاب كله جيدة جدا، فهذا يمكن استبعاده من القص»; was 1.06)
OFFC = 0.02       # or: median off-centre share of the page width worth fixing
SWAY = 0.015      # or: the text's place sways from page to page (interquartile range of its centre, share of the page)
STAINED = 0.05    # or: stains or streaks left out on this share of the text pages
MAX_WHOLE = 0.05  # share of measured pages allowed to stay whole
CLEAN_MARGIN = 0.06  # a book without print in its side margins: the margin on every side, as a share of the text width
                     # (owner 2026-10-09: with 2 % the text of سؤالات أبي داود was «مقاربا للحدود بشكل ملفت للنظر»; then
                     # «لا تجب المبالغة فيه فحتى 4% قليل»)
MAGNIFY_MAX = 1.05   # a page smaller than the book's box is shown up to 5 % larger rather than on blank paper beyond its edge

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

def marks(a, scale, width, exclude=None):
    """ink marks of one page, in pt (page.rect coordinates) → dict:
       box     every content mark;  core  the text block (2–98 % of the content ink: where the page is centred);
       specks  isolated specks;  blots  stains and edge streaks (neither text nor print: left outside the box);
       allowed where the box may go (inside scanner bands and edge shadows);  dark  share of dark pixels;
       xy      content ink pixels (x, y in pixels) for the skew estimate.
    scale = pixels per pt, width = the page width in pt (M and SPECK are scaled to it)"""
    if exclude:                                     # an uploader's stamp (stamps_of): not part of the page, not measured
        a = a.copy()
        for b in exclude:
            a[max(0, int(b[1] * scale)):int(b[3] * scale) + 1, max(0, int(b[0] * scale)):int(b[2] * scale) + 1] = 255
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
    # THE TEXT BLOCK BY GAPS (2026-10-09, owner on اللآلئ: «ليس فيه كتابة على الهوامش الأفقية… تتسق جميع الصفحات»): starting
    # from the core's columns, every mark less than 1.5 % of the width away joins the text and widens it (so a line longer
    # than the others, a heading, a verse, is whole); everything above and below inside those columns is text too (running
    # head, page number, footnotes). Marks further out sit in a side margin (`margin`): a reader's pen stroke, a dot, a
    # folio number, a gloss — whether the book prints in its margins is decided per book (decide)
    cid = np.array(content); X0 = np.array([objs[i - 1][1].start for i in content]); X1 = np.array([objs[i - 1][1].stop for i in content])
    Y0 = np.array([objs[i - 1][0].start for i in content]); Y1 = np.array([objs[i - 1][0].stop for i in content])
    # only letter-like marks carry the text block outward (2026-10-09: specks along an edge chained up to the scan's dark
    # edge and the «text» reached the page border): not wholly in the outer 3 % of the sheet, not taller than 15 % of the
    # page (a streak, a rule), not a speck
    gx = 0.015 * Wd; tx0, tx1 = float(qx[0]), float(qx[1] + 1)
    strip = (X1 <= 0.03 * Wd) | (X0 >= 0.97 * Wd) | (Y1 <= 0.03 * H) | (Y0 >= 0.97 * H)
    hh, ww = Y1 - Y0, X1 - X0
    letter = ~strip & (hh <= 0.15 * H) & ((hh >= 0.004 * H) | (ww >= 0.008 * Wd))
    if not letter.any(): letter = ~strip if (~strip).any() else np.ones(len(cid), bool)
    tx0, tx1 = float(np.percentile(X0[letter], 2)), float(np.percentile(X1[letter], 98))   # the seed: letters only (a heavy
    while True:                                                                           # edge streak pulls the ink core)
        inn = letter & (X1 >= tx0 - gx) & (X0 <= tx1 + gx)
        if not inn.any(): inn = letter; break
        nx0, nx1 = float(X0[inn].min()), float(X1[inn].max())
        if nx0 >= tx0 and nx1 <= tx1: break
        tx0, tx1 = min(tx0, nx0), max(tx1, nx1)
    out['text'] = pt(float(X0[inn].min()), float(Y0[inn].min()), float(X1[inn].max()), float(Y1[inn].max()))
    # THE PAGE NUMBER (folio), when printed on its own line at the foot or the head of the text block: a short group (≤ 8 %
    # of the width, ≤ 2.5 % of the height) with a clear gap (≥ 1.2 % of the height) to the text — printed at the same
    # place of every page, so a short page can be placed by it (owner 2026-10-09, المثلث ص 569)
    out['folio'] = None
    lx0, lx1, ly0, ly1 = X0[inn], X1[inn], Y0[inn], Y1[inn]
    for foot in (True, False):
        e = ly1.max() if foot else ly0.min()
        g = (ly0 >= e - 0.025 * H) if foot else (ly1 <= e + 0.025 * H)
        if not g.any() or g.all(): continue
        gy0, gy1, gx0, gx1 = ly0[g].min(), ly1[g].max(), lx0[g].min(), lx1[g].max()
        gap = gy0 - ly1[~g].max() if foot else ly0[~g].min() - gy1
        if gap >= 0.012 * H and 0.005 * Wd <= gx1 - gx0 <= 0.08 * Wd and gy1 - gy0 <= 0.025 * H:
            out['folio'] = pt(float(gx0), float(gy0), float(gx1), float(gy1)) + ['foot' if foot else 'head']; break
    tb_ = out['text']; inside_ = lambda b: b[0] >= tb_[0] - 0.5 and b[2] <= tb_[2] + 0.5 and b[1] >= tb_[1] - 0.5 and b[3] <= tb_[3] + 0.5
    out['margin'] = [b for b in (box_of(int(i)) for i in cid) if not inside_(b)]
    out['xy'] = (xs, ys)
    return out

def skew_of(xy, raw=False):
    """the angle (degrees) that makes the text lines level: shear the ink by tan(a) and keep the angle whose row profile is
    sharpest. Measured on the whole text and on its right and left halves: a real tilt is the same everywhere (owner,
    2026-10-08: index pages and verse turned by mistake — their whole-page angle disagreed with their halves'). Accepted when
    the whole lies within the halves' range (±0.1°) and the halves differ by ≤ 0.6°; else (0, 1). raw=True: the whole-page angle alone.
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
    # a real tilt: the whole page's angle lies within the range of its halves' angles (±0.1°) and the halves differ by
    # ≤ 0.6° (a slightly curved page: halves −0.375 / +0.075, whole −0.25 — the owner's p. 387). Index pages, two columns
    # and verse fool the whole-page profile: there the whole lies outside its halves (p. 98: +0.9 vs −1.0 / −0.4)
    # (± 1e-6: a whole-page angle exactly on the limit once read as outside it — الفوائد المحصورة ص 16, −0.9 vs −0.8 − 0.1)
    if len(parts) < 2 or abs(parts[0] - parts[1]) > 0.6 + 1e-6 or not (min(parts) - 0.1 - 1e-6 <= a <= max(parts) + 0.1 + 1e-6): return 0.0, 1.0
    return a, gain

SKEW_MIN = 0.2    # degrees: the owner sees a 0.25° tilt on a full line
LEVEL = 0.15 + 1e-6  # degrees: a turned page reads level — the shear measure's own precision near level is about ±0.1°
                     # (2026-10-09: pages turned exactly right read 0.125–0.15°); the eye sees a tilt from about 0.25°
IMG_LEVEL = 0.2 + 1e-6  # the image measure is coarser (700 px: level pages read 0.1–0.15°): it guards against a visible tilt
CURVED = 0.25 + 1e-6    # a slightly curved page no single rotation levels: kept if both measures read ≤ 0.25° AND ≤ a third
                        # of the tilt it had (listed as «curved» on the book's card)

def baseline_tilt(a, paper, min_lines=6):
    """THE THIRD TILT MEASURE (owner 2026-10-09, الفوائد المحصورة ص 16 — verse in centred, voweled lines, where the other two
    read 0.2–0.3° on a level page): line by line, the height of the line's baseline (its densest ink row) at its right
    third against its left third; the median slope over the lines at least 20 % of the page wide. What the eye sees. Fooled
    by index pages (a line's two ends in two columns), so it never decides that a page is tilted: it only certifies a turn
    (keep). Returns the signed angle (degrees) or None (fewer than 6 such lines)"""
    m = a < max(60, min(200, paper - 50)); H, W = m.shape
    prof = ndimage.uniform_filter1d(m.sum(1).astype(float), 3)
    thr = 0.25 * prof.max()
    peaks = [i for i in range(2, H - 2) if prof[i] >= thr and prof[i] == prof[max(0, i - int(0.008 * H)):i + int(0.008 * H) + 1].max()]
    if len(peaks) < min_lines: return None
    gaps = np.diff(peaks); sp = float(np.median(gaps)) if len(gaps) else 0
    if sp < 6: return None
    sl = []
    for y in peaks:
        y0, y1 = int(max(0, y - 0.45 * sp)), int(min(H, y + 0.45 * sp))
        band = m[y0:y1]; cols = np.nonzero(band.any(0))[0]
        if len(cols) < 10: continue
        x0, x1 = cols[0], cols[-1]
        if x1 - x0 < 0.2 * W: continue
        t = (x1 - x0) / 3
        L, R = band[:, x0:int(x0 + t)], band[:, int(x1 - t):x1 + 1]
        if L.sum() < 30 or R.sum() < 30: continue
        rl = ndimage.uniform_filter1d(L.sum(1).astype(float), 3); rr = ndimage.uniform_filter1d(R.sum(1).astype(float), 3)
        dy = float(np.argmax(rr) - np.argmax(rl)); dx = (x1 - t / 2) - (x0 + t / 2)
        sl.append(np.degrees(np.arctan2(dy, dx)))
    if len(sl) < min_lines: return None
    return float(np.median(sl))

def edge_tilt(a, paper):
    """THE LINES' EDGE AS A RULER (owner 2026-10-09: «you can just use a ruler against any line!», الفوائد المحصورة ص 526 — a
    list of short right-aligned lines no other measure reads): right-aligned lines all start at one edge (left-aligned ones
    at the other); on a level page those starts stand on a vertical line. Line by line (bands of ink rows), the outermost ink
    on each side; the lines within 1.5 % of the width of the median edge are the aligned ones; the slope is the median of
    the slopes between pairs of them at least 10 % of the page apart. Returns [right, left] (degrees, the sign of
    skew_of's angle; None when fewer than 6 lines are aligned on that side)"""
    m = a < max(60, min(200, paper - 50)); H, W = m.shape
    prof = ndimage.uniform_filter1d(m.sum(1).astype(float), 3); rows = prof >= 0.15 * prof.max()
    pts, y = [], 0
    while y < H:
        if rows[y]:
            y0 = y
            while y < H and rows[y]: y += 1
            if y - y0 >= 0.004 * H:
                cols = np.nonzero(m[y0:y].sum(0) >= 2)[0]
                if len(cols) >= 5: pts.append(((y0 + y) / 2, cols[-1], cols[0]))
        y += 1
    out = []
    for k in (1, 2):
        if len(pts) < 6: out.append(None); continue
        P = np.array(pts); xs = P[:, k]; keep = P[np.abs(xs - np.median(xs)) <= 0.015 * W]
        sl = [(keep[j, k] - keep[i, k]) / (keep[j, 0] - keep[i, 0]) for i in range(len(keep)) for j in range(i + 1, len(keep))
              if keep[j, 0] - keep[i, 0] > 0.1 * H] if len(keep) >= 6 else []
        out.append(float(np.degrees(np.arctan(np.median(sl)))) if sl else None)
    return out

def proj_tilt(a, paper, lo=-0.5, hi=0.5, step=0.05, width=700):
    """the SECOND tilt measure (2026-10-09): the page image itself, scaled to 700 px wide, is turned by each angle and the
    ink rows of its central part (8–92 % of the width, 5–95 % of the height) counted; the sharpest row profile wins
    (coarse steps, then 0.025° around the best). Coarser than the shear measure; sign-free use only: |angle| ≥ 0.15° =
    tilted, ≤ IMG_LEVEL (0.2°) = no visible tilt.
    Returns |angle|"""
    from PIL import Image
    im = Image.fromarray(a)
    if im.width > width: im = im.resize((width, max(1, round(im.height * width / im.width))), Image.BILINEAR)
    w, h = im.size; box = (int(w * .08), int(h * .05), int(w * .92), int(h * .95))
    thr = max(60, min(200, paper - 50))
    def score(t):
        b = np.asarray(im.rotate(float(t), resample=Image.BILINEAR, fillcolor=255).crop(box))
        return float(np.var((b < thr).sum(1)))
    angs = np.arange(lo, hi + step / 2, step); k = int(np.argmax([score(t) for t in angs]))
    fine = np.arange(angs[k] - step, angs[k] + step + 1e-9, 0.025); j = int(np.argmax([score(t) for t in fine]))
    return round(abs(float(fine[j])), 3)
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
    return wrap_contents(doc, page, f'q {c:.6f} {s:.6f} {-s:.6f} {c:.6f} {e:.4f} {f:.4f} cm\n'.encode())

def wrap_contents(doc, page, pre):
    """one new stream `pre` (opening with «q») before the page's existing content and one «Q» after it"""
    ta, v = doc.xref_get_key(page.xref, 'Contents')
    if ta == 'xref':
        x = int(v.split()[0])
        body = doc.xref_object(x).strip()
        old = body[1:-1] if body.startswith('[') else v          # an indirect array of streams: its elements
    elif ta == 'array': old = v.strip()[1:-1]
    else: return False
    xa = doc.get_new_xref(); doc.update_object(xa, '<<>>'); doc.update_stream(xa, pre)
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

def union(bs):
    return [min(b[0] for b in bs), min(b[1] for b in bs), max(b[2] for b in bs), max(b[3] for b in bs)]

def notes_of(margin, w, h):
    """MARGINAL NOTES (owner 2026-10-09, اللآلئ ج2 ص 40 «لعله الدارقطني»: «جميل، أبق مثل هذه الهوامش ولو اختلف الزوجي عن الفردي
    في موضع النص»): words a reader or the printer put beside the text. Among a page's marks outside its text block: the
    letter-sized ones (≥ 0.5 % of the page tall or ≥ 0.8 % of its width long, ≤ 6 % × 10 %), not in the sheet's outer 3 %,
    grouped when less than 2 % of the width apart; a group is a note when it has 3 such strokes or more, no more tiny
    specks than strokes inside its box (a smudge is a cloud of specks with a blot or two: اللآلئ ج2 ص 465), and spans
    2–30 % of the width and at most 25 % of the height. A single pen stroke, dots, smudges, stains and scan edges are not
    notes: they are cut like the rest of the margin. Returns the notes' boxes"""
    L = [b for b in margin if not (b[2] <= 0.03 * w or b[0] >= 0.97 * w or b[3] <= 0.03 * h or b[1] >= 0.97 * h)
         and b[3] - b[1] <= 0.06 * h and b[2] - b[0] <= 0.10 * w and (b[3] - b[1] >= 0.005 * h or b[2] - b[0] >= 0.008 * w)]
    if not L or len(L) > 400: return []              # none, or a margin full of marks (a scan defect, not a note)
    from scipy.sparse.csgraph import connected_components
    B = np.array(L, float); g = 0.02 * w
    adj = (B[:, None, 0] < B[None, :, 2] + g) & (B[None, :, 0] < B[:, None, 2] + g) & \
          (B[:, None, 1] < B[None, :, 3] + g) & (B[None, :, 1] < B[:, None, 3] + g)
    k, lab = connected_components(adj, directed=False)
    out = []
    for j in range(k):
        S = B[lab == j]; box = [float(S[:, 0].min()), float(S[:, 1].min()), float(S[:, 2].max()), float(S[:, 3].max())]
        bw, bh = box[2] - box[0], box[3] - box[1]
        tiny = sum(1 for b in margin if max(b[2] - b[0], b[3] - b[1]) < 0.004 * w and inside(b, box, 1.0))
        if len(S) >= 3 and tiny <= len(S) and max(bw, bh) >= 0.02 * w and bw <= 0.3 * w and bh <= 0.25 * h:
            out.append(box)
    return out

def analyse_pages(path, stamps=None, only=None, jobs=1):
    """the first look at every page (or the pages `only`, in parallel over `jobs` processes); `stamps`: {page: box} of an
    uploader's stamp, left out of every measure"""
    stamps = stamps or {}
    if jobs > 1 and only is None:
        n = pymupdf.open(path).page_count; idx = list(range(n))
        out = {}
        with ProcessPoolExecutor(jobs) as ex:
            for part in ex.map(_analyse_chunk, [(path, stamps, idx[k::jobs]) for k in range(jobs)]): out.update(part)
        return [out[i] for i in idx]
    doc = pymupdf.open(path)
    pages = []; done = {}
    for i, page in enumerate(doc):
        if only is not None and i not in only: continue
        r = page.rect
        rec = {'w': round(r.width, 1), 'h': round(r.height, 1)}
        if page.rotation: rec['kind'] = 'rotated'; pages.append(rec); done[i] = rec; continue
        st = stamps.get(i) or stamps.get(str(i))
        if st: rec['stamp'] = st
        ex0 = [pad_box(b, r.width) for b in st] if st else None
        a, z = gray(page, 500)
        mk = marks(a, z, r.width, ex0)
        if mk['box'] is not None and mk['dark'] <= 0.35:     # a tilted text page: turn it level (the sign is checked)
            ang, gain = skew_of(mk['xy'])
            if 0.1 <= abs(ang) < 0.35:                   # small: measure again at twice the resolution
                a2, z2 = gray(page, 1000); ang, gain = skew_of(marks(a2, z2, r.width, ex0)['xy'])
            if abs(ang) >= SKEW_MIN and gain >= 1.02:
                for deg in (-ang, ang):
                    t = turned(doc, i, deg); a2, z2 = gray(t[0], 500)
                    mk2 = marks(a2, z2, r.width, [fwd_box(doc, i, {'skew': deg}, b) for b in ex0] if ex0 else None); t.close()
                    # the turned page must still show the page's ink (a broken drawing would show none); its text block is
                    # naturally narrower once level, so its size is not compared
                    if mk2['box'] is None or mk2['xy'] is None or not (0.6 <= len(mk2['xy'][0]) / len(mk['xy'][0]) <= 1.6):
                        continue
                    left, _ = skew_of(mk2['xy'], raw=True)   # the plain whole-page angle must now read level
                    if abs(left) <= max(0.1, abs(ang) / 3): rec['skew'] = round(deg, 3); mk = mk2; break
        mk.pop('xy', None); mk.pop('parts', None)
        rec.update(allowed=mk['allowed'], specks=mk['specks'], blots=mk['blots'], edge=mk['edge'], core=mk['core'], paper=round(mk.get('paper', 0)),
                   rules=mk.get('rules', []), text=mk.get('text'), margin=mk.get('margin', []), folio=mk.get('folio'))
        if mk['box'] is None: rec['kind'] = 'blank' if mk['dark'] < 0.5 else 'picture'
        elif mk['dark'] > 0.35: rec['kind'] = 'picture'   # dark pages only: a tight light scan is text (stays whole if it cannot fit)
        else: rec['kind'] = 'text'
        rec['box'] = mk['box']
        pages.append(rec); done[i] = rec
    doc.close()
    return done if only is not None else pages

def _analyse_chunk(args):
    path, stamps, idx = args
    return analyse_pages(path, stamps, only=set(idx))

def pad_box(b, w):
    d = 1.5 + 0.004 * w; return [b[0] - d, b[1] - d, b[2] + d, b[3] + d]

def fwd_box(doc, i, p, b):
    """a box of the original page (page coordinates) as it lies on the page turned and moved like p (the reader's frame)"""
    page = doc[i]; mv = p.get('move') or [0, 0]; deg = p.get('skew') or 0
    if not deg and not any(mv): return b
    tm = page.transformation_matrix; mb = raw_box(doc, page.xref, 'MediaBox'); cx, cy = (mb[0] + mb[2]) / 2, (mb[1] + mb[3]) / 2
    fwd = pymupdf.Matrix(1, 0, 0, 1, -cx, -cy) * pymupdf.Matrix(deg) * pymupdf.Matrix(1, 0, 0, 1, cx, cy) * pymupdf.Matrix(1, 0, 0, 1, mv[0], -mv[1])
    m = ~tm * fwd * tm
    pts = [pymupdf.Point(x, y) * m for x, y in ((b[0], b[1]), (b[2], b[1]), (b[2], b[3]), (b[0], b[3]))]
    return [min(q.x for q in pts), min(q.y for q in pts), max(q.x for q in pts), max(q.y for q in pts)]

def stamps_of(path, jobs=1, px=400):
    """UPLOADERS' STAMPS (owner 2026-10-09, الفوائد المحصورة: «neglect that رفع المساهم stamp in every page's footer, don't
    consider it text. or even: erase it»; «generalize this for when we have such a stamp across the book»): the same small
    picture at the same place of many pages — a forum's or a library's mark, not the book. A quick look at every page:
    groups of ink (marks less than 0.3 % of the width apart). A stamp: in the top 12 % or the bottom 18 % of the page,
    3–35 % of its width wide and 0.8–8 % of its height tall, centred at least 12 % of the width off the page's middle (page
    numbers and running heads stay centred), found at the same place (± 2.5 %), of the same size (± 10 %) and shape (ink
    overlap ≥ 70 % once scaled alike — page numbers differ from page to page) on ≥ 25 % of the pages, odd and even alike (a
    page number in the outer corner alternates sides). Then THE SAME STAMP ELSEWHERE (owner, ص 2: «you could have removed
    the stamp in p2 and centered the text»): on any page, a group of the stamp's proportions (± 15 %), at least 0.8 of its
    size, whose grey image matches the stamp's (correlation ≥ 0.7) — with the small line set right under it (a date).
    Returns {page index: [boxes (pt)]}"""
    doc = pymupdf.open(path); n = doc.page_count; doc.close()
    idx = list(range(n)); found = []
    if jobs > 1:
        with ProcessPoolExecutor(jobs) as ex:
            for part in ex.map(_stamp_chunk, [(path, idx[k::jobs], px) for k in range(jobs)]): found += part
    else: found = _stamp_chunk((path, idx, px))
    band = [f for f in found if f[6]]
    if not band: return {}
    C = np.array([[f[1][0], f[1][1], f[1][2], f[1][3], f[2], f[3]] for f in band], float)
    cxs, cys = (C[:, 0] + C[:, 2]) / 2, (C[:, 1] + C[:, 3]) / 2; bw, bh = C[:, 2] - C[:, 0], C[:, 3] - C[:, 1]
    T = np.array([f[4] for f in band], float); pg = np.array([f[0] for f in band])
    out, used, refs = {}, np.zeros(len(band), bool), []
    for k in range(len(band)):
        if used[k]: continue
        g = (~used) & (np.abs(cxs - cxs[k]) <= 0.025 * C[:, 4]) & (np.abs(cys - cys[k]) <= 0.025 * C[:, 5]) & \
            (np.abs(bw / bw[k] - 1) <= 0.1) & (np.abs(bh / bh[k] - 1) <= 0.1)
        if len(set(pg[g])) < max(5, 0.25 * n): continue
        med = np.median(T[g], axis=0) > 0.5
        ov = np.array([(np.logical_and(t > 0.5, med).sum() / max(1, np.logical_or(t > 0.5, med).sum())) for t in T[g]])
        same = np.nonzero(g)[0][ov >= 0.7]
        P = set(pg[same])
        if len(P) < max(5, 0.25 * n) or min(sum(1 for q in P if q % 2 == 0), sum(1 for q in P if q % 2)) < 0.3 * len(P): continue
        for j in same: out.setdefault(int(pg[j]), []).append([round(float(v), 1) for v in C[j, :4]])
        G = np.mean([band[j][5] for j in same], axis=0); G = (G - G.mean()) / (G.std() + 1e-6)
        refs.append((G, float(np.median(bw[same] / bh[same])), float(np.median(bw[same]))))
        used[g] = True
    for f in found:                                   # the same stamp at another size or place (a title page)
        b = f[1]; w_, h_ = b[2] - b[0], b[3] - b[1]
        if any(inside(b, q, 2.0) for q in out.get(f[0], [])): continue
        for G, asp, sw in refs:
            if abs((w_ / max(h_, 1e-6)) / asp - 1) <= 0.15 and w_ >= 0.8 * sw and float((f[5] * G).mean()) >= 0.7:
                box = list(b)
                for f2 in found:                      # a small line right under it (the stamp's date) belongs to it
                    c = f2[1]
                    if f2[0] == f[0] and c[1] >= b[3] - 1 and c[1] <= b[3] + 0.6 * h_ and c[3] - c[1] <= 0.4 * h_ \
                       and c[0] >= b[0] - 0.2 * w_ and c[2] <= b[2] + 0.2 * w_:
                        box = union([box, list(c)])
                out.setdefault(f[0], []).append([round(float(v), 1) for v in box]); break
    return out

def _stamp_chunk(args):
    from PIL import Image, ImageFilter
    path, idx, px = args
    doc = pymupdf.open(path); out = []
    for i in idx:
        page = doc[i]
        if page.rotation: continue
        a, z = gray(page, px); paper = float(np.percentile(a, 90))
        if paper < 150: continue
        m = a < paper - 50; H, W = m.shape
        lab, k = ndimage.label(ndimage.binary_dilation(m, iterations=max(1, int(0.003 * W))))
        for j, s in enumerate(ndimage.find_objects(lab), 1):
            y0, y1, x0, x1 = s[0].start, s[0].stop, s[1].start, s[1].stop
            if not (0.03 * W <= x1 - x0 <= 0.45 * W and 0.008 * H <= y1 - y0 <= 0.2 * H): continue
            ink = (m[y0:y1, x0:x1] & (lab[y0:y1, x0:x1] == j)).astype(np.uint8) * 255
            t = np.asarray(Image.fromarray(ink).resize((48, 16), Image.BILINEAR), np.float32) / 255
            g = np.asarray(Image.fromarray(ink).resize((64, 36), Image.BOX).filter(ImageFilter.GaussianBlur(1.2)), np.float32)
            g = (g - g.mean()) / (g.std() + 1e-6)
            band = (y1 <= 0.12 * H or y0 >= 0.82 * H) and x1 - x0 <= 0.35 * W and y1 - y0 <= 0.08 * H and abs((x0 + x1) / 2 - W / 2) >= 0.12 * W
            out.append((i, (x0 / z, y0 / z, x1 / z, y1 / z), page.rect.width, page.rect.height, t, g, band))
    doc.close()
    return out

def analyse(path):
    """kept for the old callers: the measured pages and the decision at the narrowest box"""
    return decide(analyse_pages(path))

def plan(path, jobs=1):
    """the whole method: measure every page once, then the narrowest box that works — the width of 95 % of the pages,
    else 98 %, else all; each tried with the second check (a book is cropped only if few pages stay whole)"""
    import copy
    stamps = stamps_of(path, jobs)
    pages = analyse_pages(path, stamps, jobs=jobs); rec = None
    for wq in (0.95, 0.98, 1.0):
        rec = decide(copy.deepcopy(pages), wq); rec['stamp_pages'] = len(stamps)
        if rec.get('decision') == 'level': break
        if rec.get('decision') != 'crop': continue
        rec = verify(path, rec, jobs=jobs)
        if rec.get('decision') == 'crop': rec['width_quantile'] = wq; return frames(rec)
    if rec.get('decision') == 'level' or (rec.get('skewed') and 'do not fit one box' in (rec.get('decision') or '')):
        r2 = level(path, pages, rec.get('decision'), jobs); r2['stamp_pages'] = len(stamps); return r2
    return rec

def level(path, pages, why, jobs=1):
    """LEVEL ONLY (owner 2026-10-09): a good scan whose margins are already close to a crop's and whose only flaw is tilted
    pages («agree, as far as the margins are not too far from the desired results in the cropped books»), or a book whose
    pages no one box holds: its tilted pages are turned level — checked by the second look like any turn, tilts the first
    look missed found there too — and nothing else changes. On white paper a turned page's bare corners do not show; on
    grey or colour paper every page loses the same thin strip, just enough to hide them (half the page × the sine of the
    largest turn, + 1 pt)"""
    import math
    rec = {'pages': pages, 'n': len(pages), 'measured': sum(1 for p in pages if p['kind'] == 'text'), 'decision': 'level',
           'level_why': why}
    for p in pages: p['crop'] = [0.0, 0.0, p['w'], p['h']] if p['kind'] == 'text' else None
    rec = verify(path, rec, tilt_only=True, jobs=jobs)
    rec['skewed'] = sum(1 for p in pages if p.get('skew'))
    if not rec['skewed']:
        rec['decision'] = 'skip: a good scan, the tilts the first look saw were not confirmed'; return rec
    paper = sorted(p.get('paper', 255) for p in pages if p['kind'] == 'text')
    white = not paper or paper[len(paper) // 2] >= 250
    t = math.sin(math.radians(max(abs(p['skew']) for p in pages if p.get('skew'))))
    for p in pages:
        if white or p['kind'] == 'rotated': p['crop'] = None; continue
        tx, ty = p['h'] / 2 * t + 1, p['w'] / 2 * t + 1
        p['crop'] = [round(tx, 2), round(ty, 2), round(p['w'] - tx, 2), round(p['h'] - ty, 2)]
    rec['level_trim'] = None if white else round(t, 5)
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
    # A BOOK WITHOUT PRINT IN ITS SIDE MARGINS (owner 2026-10-09 on اللآلئ: «ليس فيه كتابة على الهوامش الأفقية، فلم لا يستفاد
    # من الشاشة ما أمكن وتزال الأضرار وتتسق جميع الصفحات في التوسط؟ حتى رقم الصفحة موجود في مكان مناسب»): when ≤ 10 % of
    # the full pages show marks bigger than dust in a side margin, the box is the text block itself (running head, page
    # number and footnotes inside — marks.text) + 2 % each side; whatever lies in the side margins (dots, pen strokes, scan
    # edges, stains) is cut; no page stays whole for a stray mark: a page whose text block is larger gets a box of the
    # same proportions, just large enough (`enlarged`). Framed books keep their frame rule; books printing in their
    # margins (folio numbers, glosses) keep the careful rule above.
    tb = {i: pages[i].get('text') for i in text}
    def marg_print(i):                               # letter-sized marks inside the sheet beside the text: print (folio
        w, h = pages[i]['w'], pages[i]['h']          # numbers, glosses); marks at the sheet's edge (scanner corner marks)
        def printish(b):                             # and long streaks are not
            bw, bh = b[2] - b[0], b[3] - b[1]
            edge = b[2] <= 0.03 * w or b[0] >= 0.97 * w or b[3] <= 0.03 * h or b[1] >= 0.97 * h
            return not edge and bh < 0.15 * h and (bh >= 0.008 * h or bw >= 0.015 * w)
        return sum(1 for b in pages[i].get('margin') or [] if printish(b)) >= 2
    clean = (not out['framed']) and len(full_w) >= 5 and all(tb.get(i) for i in full_w) \
            and sum(1 for i in full_w if marg_print(i)) <= 0.10 * len(full_w)
    out['clean_margins'] = clean
    mc = 0.0                                         # the margin a page's needed part keeps when its box must grow
    out['margin_pt'] = round(0.02 * Tw if out['framed'] else max(m0, 0.08 * Tw), 2)
    edges = {i: core[i] for i in text}               # what a short page is anchored on (see below)
    if clean:
        off = {0: 0.0, 1: 0.0}; out['parity_offsets'] = {'0': 0.0, '1': 0.0}
        tw = {i: tb[i][2] - tb[i][0] for i in text if tb.get(i)}; th = {i: tb[i][3] - tb[i][1] for i in text if tb.get(i)}
        full_t = [i for i in full_w if i in tw]
        Tq = q([tw[i] for i in full_t], wq); mc = CLEAN_MARGIN * Tq; out['margin_pt'] = round(mc, 2)
        W = min(Tq + 2 * mc, pw)
        H = min(q([th[i] for i in full_h if i in th] or list(th.values()), 0.98) + 2 * mc, ph)
        cx = {i: ((tb[i][0] + tb[i][2]) / 2 if tb.get(i) else cx[i]) for i in text}
        cy = {i: ((tb[i][1] + tb[i][3]) / 2 if tb.get(i) else cy[i]) for i in text}
        edges = {i: tb[i] for i in text if tb.get(i)}
        for i in text:                                # the text block and its marginal notes must fit; the rest may be cut
            if tb.get(i):
                nts = notes_of(pages[i].get('margin') or [], pages[i]['w'], pages[i]['h'])
                pages[i]['content_box'] = pages[i]['box']; pages[i]['box'] = union([tb[i]] + nts)
                if nts: pages[i]['notes'] = [[round(v, 1) for v in b] for b in nts]
    def near(i, pool, val):                         # a short page takes the place of its full neighbours (same parity)
        same = [j for j in pool if j % 2 == i % 2] or pool
        k = sorted(same, key=lambda j: abs(j - i))[:6]
        return q([val[j] for j in k], 0.5)
    fw, fh = set(full_w), set(full_h)
    # A SHORT PAGE (an index page of short entries, a chapter's end, a section's start) takes its neighbours' place, moved
    # by its own scan shift where that can be read: on a text edge lying where the neighbours' same edge lies (± 3 % of the
    # page) — the right edge of right-aligned Arabic lines, the top line under the running head, the page number at the
    # bottom (owner 2026-10-09, المثلث ص 569: the neighbours' place alone left the page «ضعف توسيط»: its sheet was
    # scanned 7 pt away from theirs). A centred poem or title, whose edges lie far from the neighbours', keeps their place
    EL = {i: edges[i][0] for i in edges}; ER = {i: edges[i][2] for i in edges}
    ET = {i: edges[i][1] for i in edges}; EB = {i: edges[i][3] for i in edges}
    def shift(d0, d1, tol):
        c = [d for d in (d0, d1) if abs(d) <= tol]
        return min(c, key=abs) if c else None
    fwe, fhe = [j for j in full_w if j in edges], [j for j in full_h if j in edges]
    # Better still, THE PAGE NUMBER where the book prints it on its own line: on the full pages it lies at a fixed offset
    # from the text's centre (per parity — outer corners alternate); when that offset is steady (half the pages within
    # 0.6 % of the page), a short page whose number lies where its neighbours' does (± 3 %) is placed by its number
    fol = {i: pages[i]['folio'] for i in text if pages[i].get('folio')}
    fcen = lambda f, ax: (f[0] + f[2]) / 2 if ax == 0 else (f[1] + f[3]) / 2
    FO = {}
    for par in (0, 1):
        for ax, pool, cen, dim in ((0, full_w, cx, pw), (1, full_h, cy, ph)):
            for kind in ('foot', 'head'):
                v = [fcen(fol[j], ax) - cen[j] for j in pool if j % 2 == par and j in fol and fol[j][4] == kind]
                if len(v) >= max(8, 0.3 * sum(1 for j in pool if j % 2 == par)):
                    med = q(v, 0.5)
                    if q([abs(t - med) for t in v], 0.5) <= 0.006 * dim: FO[(par, ax, kind)] = med
    # A PAGE NUMBER CENTRED under (or over) the text is the printed page's own axis: every page carrying it where its
    # neighbours do (± 3 %) is centred on it horizontally — the page number and the headings centred as printed; numbers
    # or dashes jutting out at the line ends (المثلث: the text block reads 3–5 pt right of the number) do not pull the
    # page aside (owner 2026-10-09, المثلث ص 569 «ضعف توسيط»). Not when the book lays out odd and even pages differently
    out['folio_axis'] = None
    for kind in ('foot', 'head'):
        if not (off[0] or off[1]) and all((par, 0, kind) in FO and abs(FO[(par, 0, kind)]) <= 0.02 * pw for par in (0, 1)):
            pool = [j for j in full_w if j in fol and fol[j][4] == kind]
            for i in text:
                f = fol.get(i); others = [j for j in pool if j != i]
                if f and f[4] == kind and others and abs(fcen(f, 0) - near(i, others, {j: fcen(fol[j], 0) for j in others})) <= 0.03 * pw:
                    cx[i] = fcen(f, 0)
            for par in (0, 1): FO[(par, 0, kind)] = 0.0
            out['folio_axis'] = kind; break
    out['folio_anchor'] = {f'{"oe"[k[0]]}{"xy"[k[1]]}-{k[2]}': round(v, 1) for k, v in FO.items()}
    def by_folio(i, ax):
        f = fol.get(i)
        if not f or (i % 2, ax, f[4]) not in FO: return None
        pool = [j for j in (full_w if ax == 0 else full_h) if j in fol and fol[j][4] == f[4]]
        if not pool or abs(fcen(f, ax) - near(i, pool, {j: fcen(fol[j], ax) for j in pool})) > 0.03 * (pw if ax == 0 else ph): return None
        return fcen(f, ax) - FO[(i % 2, ax, f[4])]
    whole, offc, own, moved = [], [], 0, 0
    for i, p in enumerate(pages):
        if p['kind'] in ('rotated', 'picture'): p['crop'] = None; continue
        bx = p.get('box'); e = edges.get(i)
        x = cx[i] if i in fw else (near(i, full_w, cx) if full_w else pw / 2)
        y = cy[i] if i in fh else (near(i, full_h, cy) if full_h else ph / 2)
        if i not in fw and (xf := by_folio(i, 0)) is not None: x = xf; p['anchored_x'] = 'folio'
        elif e and i not in fw and fwe:
            dx_ = shift(e[0] - near(i, fwe, EL), e[2] - near(i, fwe, ER), 0.03 * p['w'])
            if dx_ is not None: x += dx_; p['anchored_x'] = round(dx_, 1)
            else: x = cx[i]; p['anchored_x'] = 'own'  # centred lines (a title page, a poem), no page number: on themselves
                                                      # (owner 2026-10-09, الفوائد المحصورة ص 2: «and centered the text»)
        if i not in fh and (yf := by_folio(i, 1)) is not None: y = yf; p['anchored_y'] = 'folio'
        elif e and i not in fh and fhe:
            dy_ = shift(e[1] - near(i, fhe, ET), e[3] - near(i, fhe, EB), 0.03 * p['h'])
            if dy_: y += dy_; p['anchored_y'] = round(dy_, 1)
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
                        # only while the text keeps balanced margins (the smaller ≥ 60 % of the larger): a lopsided page is
                        # worse than a thin mark in its margin (2026-10-09, الفوائد المحصورة ص 200: a 22 pt slide for a scan bar)
                        cand = min(max(nx, lo), hi); ml, mr = bx[0] - cand, cand + (b[2] - b[0]) - bx[2]
                        if min(ml, mr) < 0.6 * max(ml, mr): p['stain_kept'] = True; continue
                        want = nx; nx = cand; b = [round(nx, 1), b[1], round(nx + b[2] - b[0], 1), b[3]]; p['dodged'] = True
                        short = want - nx                    # the page edge stops the box: on white paper the content moves the
                        if short and p.get('paper', 0) >= 235 and abs(short) <= 0.03 * p['w']:   # last points the other way
                            mv = p.get('move') or [0, 0]; p['move'] = [round(mv[0] - short, 1), mv[1]]
                            sh = -short
                            p['box'] = bx = [bx[0] + sh, bx[1], bx[2] + sh, bx[3]]
                            p['blots'] = [[v[0] + sh, v[1], v[2] + sh, v[3]] for v in p.get('blots', [])]
                            p['specks'] = [[v[0] + sh, v[1], v[2] + sh, v[3]] for v in p.get('specks', [])]
                            p['edge'] = [[v[0] + sh, v[1], v[2] + sh, v[3]] for v in p.get('edge', [])]
        b = [max(0, b[0]), max(0, b[1]), min(p['w'], b[2]), min(p['h'], b[3])]
        hm = 0.5 * mc                                 # half the margin at least, else the box grows (اللآلئ ج2 ص 40: 2 pt)
        if clean and p['kind'] == 'text' and bx and not inside([bx[0] - hm, bx[1] - hm, bx[2] + hm, bx[3] + hm], b):
            sc = max(1.0, (bx[2] - bx[0] + 2 * mc) / W, (bx[3] - bx[1] + 2 * mc) / H)
            smax = min(p['w'] / W, p['h'] / H)       # never beyond the sheet: the margin gives way first
            if sc > smax: sc = max(1.0, smax, (bx[2] - bx[0]) / W, (bx[3] - bx[1]) / H)
            W2, H2 = W * sc, H * sc
            x2, y2 = (bx[0] + bx[2]) / 2, (bx[1] + bx[3]) / 2
            b = [x2 - W2 / 2, y2 - H2 / 2, x2 + W2 / 2, y2 + H2 / 2]
            sx = -b[0] if b[0] < 0 else (p['w'] - b[2] if b[2] > p['w'] else 0); sy = -b[1] if b[1] < 0 else (p['h'] - b[3] if b[3] > p['h'] else 0)
            b = [round(max(0, b[0] + sx), 1), round(max(0, b[1] + sy), 1), round(min(p['w'], b[2] + sx), 1), round(min(p['h'], b[3] + sy), 1)]
            if sc > 1.0001: p['enlarged'] = round(sc, 3)
        if p['kind'] == 'text' and not inside(bx, b): p['crop'] = None; whole.append(i); continue
        p['crop'] = b
        p['cut_specks'] = [v for v in p['specks'] if not inside(v, b, 0)]
        if i in fw and bx: offc.append(abs((b[0] + b[2]) / 2 - (cx[i] + (p.get('move') or [0, 0])[0])) / p['w'])
    out['whole'] = whole; out['own_centre'] = own; out['content_moved'] = moved
    out['enlarged'] = [i + 1 for i, p in enumerate(pages) if p.get('enlarged')]
    out['skewed'] = sum(1 for p in pages if p.get('skew'))
    out['blot_pages'] = sum(1 for p in pages if p.get('crop') and p.get('blots'))
    out['size'] = [round(W, 2), round(H, 2)]
    out['gain'] = round(pw / W, 3); out['gain_h'] = round(ph / H, 3)
    out['offcentre_before'] = round(q([abs(cx[i] - pages[i]['w'] / 2) / pages[i]['w'] for i in full_w], 0.5), 3) if full_w else 0
    out['offcentre_after'] = round(q(offc, 0.5), 3) if offc else 0
    banded = sum(1 for i in text if pages[i]['allowed'][0] > 0.02 * pw or pages[i]['allowed'][2] < 0.98 * pages[i]['w']) > 0.5 * len(text)
    out['banded'] = banded
    def iqr(v):
        v = sorted(v); return v[int(0.75 * (len(v) - 1))] - v[int(0.25 * (len(v) - 1))] if v else 0.0
    out['sway'] = [round(iqr([(edges[i][0] + edges[i][2]) / 2 / pages[i]['w'] for i in fwe]), 4),
                   round(iqr([(edges[i][1] + edges[i][3]) / 2 / pages[i]['h'] for i in fhe]), 4)]
    # WHY CROP (owner 2026-10-09): a crop is worth it for the phone, but a very well made scan whose crop would change
    # little is left as it is. Reasons: the text gets ≥ 15 % larger; a tilted page (even one: «أحب إصلاح الصفحات المائلة
    # ولو كانت تشكل أقل من 5%»); scanner bands; the text off-centre or swaying from page to page; stains on ≥ 5 % of pages
    reasons = []
    if out['gain'] >= GAIN: reasons.append(f'text {round((out["gain"] - 1) * 100)} % larger')
    if out['skewed']: reasons.append(f'{out["skewed"]} tilted pages')
    if banded: reasons.append('scanner bands')
    if out['offcentre_before'] >= OFFC: reasons.append(f'off-centre {round(out["offcentre_before"] * 100, 1)} %')
    if max(out['sway']) >= SWAY: reasons.append(f'text sways {round(max(out["sway"]) * 100, 1)} %')
    if out['blot_pages'] >= STAINED * len(text): reasons.append(f'stains on {out["blot_pages"]} pages')
    out['reasons'] = reasons
    if not reasons:
        out['decision'] = f'skip: a good scan, the crop changes little (gain {out["gain"]}, off-centre {out["offcentre_before"]}, sway {out["sway"]})'
    elif all(r.endswith('tilted pages') for r in reasons):
        out['decision'] = 'level'                     # a good scan, margins close to a crop's, tilted pages: level them only
    elif len(whole) > MAX_WHOLE * len(text): out['decision'] = f'skip: {len(whole)} pages do not fit one box'
    else: out['decision'] = 'crop'
    return out

def transformed(doc, i, p):
    """page i as the reader will see it (turned level, content moved) — in a one-page document"""
    mv = p.get('move') or [0, 0]
    return turned(doc, i, p.get('skew') or 0, mv[0], mv[1])

def verify(path, rec, px=1000, tilt_only=False, jobs=1, only=None, moved_in=None):
    """second look at twice the resolution: every mark found outside a page's box must be one the first look left out on
    purpose (a stain, edge noise — the same place, give or take 3 pt) or an isolated speck; anything else is content:
    the box may move up to 2 % to take it in, else the page stays whole"""
    if jobs > 1 and only is None:                     # pages shared out among `jobs` processes, then summed up here
        idx = list(range(len(rec['pages']))); mv = []
        with ProcessPoolExecutor(jobs) as ex:
            for part, moved_c in ex.map(_verify_chunk, [(path, rec, px, tilt_only, idx[k::jobs]) for k in range(jobs)]):
                for i, pg in part.items(): rec['pages'][i] = pg
                mv += moved_c
        return verify(path, rec, px, tilt_only, only=set(), moved_in=sorted(mv))
    doc = pymupdf.open(path); moved = list(moved_in or [])
    near = lambda b, regions: any(b[0] < r[2] + 3 and b[2] > r[0] - 3 and b[1] < r[3] + 3 and b[3] > r[1] - 3 for r in regions)
    def look(i, q):                                   # the page as the reader will see it, measured at px
        t = transformed(doc, i, q); page = t[0]; a, z = gray(page, px); st = rec['pages'][i].get('stamp')
        mk = marks(a, z, page.rect.width, [fwd_box(doc, i, q, pad_box(b, page.rect.width)) for b in st] if st else None); t.close()
        mk['proj'] = lambda lo=-0.5, hi=0.5, step=0.05: proj_tilt(a, mk['paper'], lo, hi, step)
        mk['lines'] = lambda: baseline_tilt(a, mk['paper']) if mk.get('paper') else None
        mk['edges'] = lambda: edge_tilt(a, mk['paper']) if mk.get('paper') else [None, None]
        return mk
    def best_turn(i, p, d0):                          # the turn near d0 that leaves the least tilt by BOTH measures:
        tried = {}                                    # d0 first; if not level, 10 more angles around it in 0.05° steps
        def ev(d):
            d = round(d, 3)
            if d not in tried:
                m2 = look(i, dict(p, skew=d))
                tried[d] = (9.0, 9.0, m2) if m2['xy'] is None else (abs(skew_of(m2['xy'], raw=True)[0]), m2['proj'](), m2)
            return tried[d]
        r, im, m2 = ev(d0)
        if r <= LEVEL and im <= IMG_LEVEL: return round(d0, 3), r, im, m2
        for k in range(1, 6):
            ev(d0 - 0.05 * k); ev(d0 + 0.05 * k)
        d, (r, im, m2) = min(tried.items(), key=lambda kv: (max(kv[1][0], kv[1][1]), kv[1][0]))
        if not (r <= LEVEL and im <= IMG_LEVEL):      # none level by both: among the turns the two read ≤ 0.35°, the one
            cl = []                                   # whose lines read most level, line by line (baseline_tilt)
            for dd, v in tried.items():
                if max(v[0], v[1]) <= 0.35:
                    b = v[2]['lines'](); cl.append((abs(b) if b is not None else 9, dd, v))
            if cl and min(cl)[0] <= 0.15: _, d, (r, im, m2) = min(cl)
        return d, r, im, m2
    def keep(p, d, r, im, before, m2=None):           # level, or a curved page brought below sight, or (a clear tilt,
        if p.get('tilt_by_edge') is not None:            # a page found by its lines' edge: level by the two usual measures,
            if r <= LEVEL and im <= IMG_LEVEL: p['level_by_edge'] = 0.0; return True   # or its edge standing straight with
            es = [e for e in (m2['edges']() if m2 is not None else []) if e is not None]   # the whole page level
            if es and min(abs(e) for e in es) <= 0.15 and r <= 0.2: p['level_by_edge'] = round(min(es, key=abs), 3); return True
            return False
        if r <= LEVEL and im <= IMG_LEVEL: return True   # ≥ 0.4°) its lines level line by line while the other two
        if r <= CURVED and im <= CURVED and max(r, im) <= abs(before) / 3: p['curved'] = True; return True   # fell to a third
        if m2 is not None and abs(before) >= 0.4 and max(r, im) <= min(0.35, abs(before) - 0.15):   # (index pages keep the
                                                                                                    # image measure near 0.3°)
            b = m2['lines']()
            if b is not None and abs(b) <= 0.15: p['level_by_lines'] = round(b, 3); return True
        return False
    for i, p in enumerate(rec['pages']):
        if only is not None and i not in only: continue
        if not p.get('crop') and not p.get('skew'): continue
        mk = look(i, p)
        # LEVEL CHECK (owner: «اختبار يضمن أننا أزلنا الميل تماما ولم نصطنع ميلا جديدا أو نبق شيئا من الميل»):
        # a turned page must read level by BOTH measures — the shear profile of its ink (≤ 0.15°) and the turned page
        # image (≤ 0.2°: it is coarser); if the first turn does not, the angles around it are tried (best_turn). A curved
        # page is kept when both read ≤ 0.25° and ≤ a third of its tilt. Else the turn is undone (a tilt the method made is
        # never kept). An untouched page showing a tilt the first look did not treat is turned here when the image measure
        # sees the tilt too (≥ 0.15°) and the turn passes the same tests; else it is reported. An untouched page cannot
        # gain a tilt.
        if p.get('skew'):
            before = p['skew']; d, r, im, m2 = best_turn(i, p, before)
            if keep(p, d, r, im, before, m2): p['skew'], mk = d, m2; p['after_tilt'] = round(r, 3); p['after_tilt_image'] = im
            else:
                p.pop('skew', None); p['unsure_tilt'] = True; mk = look(i, p)
        elif mk['xy'] is not None:
            u, g = skew_of(mk['xy'])
            # (no turn when the halves disagree, even if the whole page and its image agree on a tilt: index pages fool
            # all of them alike — 2026-10-09, الفوائد المحصورة ص 432 and 446, «فهرس اللغة», turned 3° by mistake) — unless
            # the lines' edge, a ruler of its own, reads the same clear tilt as the whole page (≥ 0.4°, within 0.2°):
            # a list of short right-aligned lines (ص 526). Such a turn is kept only if the edge then stands straight
            if not (abs(u) >= SKEW_MIN and g >= 1.02):
                r_, g_ = skew_of(mk['xy'], raw=True)
                if abs(r_) >= 0.4 and g_ >= 1.02:
                    es = [e for e in mk['edges']() if e is not None and abs(e - r_) <= 0.2]
                    if es: u, g = r_, g_; p['tilt_by_edge'] = round(min(es, key=lambda e: abs(e - r_)), 3)
            if abs(u) >= SKEW_MIN and g >= 1.02:
                if mk['proj'](-3.0, 3.0, 0.25) < SKEW_MIN - 0.05: p['tilt_disputed'] = round(u, 3)   # the image shows no tilt
                else:
                    tries = []
                    for d0 in (-u, u):                # the direction that lowers the tilt, by the shear measure
                        m2 = look(i, dict(p, skew=round(d0, 3)))
                        if m2['xy'] is None or not (0.6 <= len(m2['xy'][0]) / len(mk['xy'][0]) <= 1.6): continue
                        tries.append((abs(skew_of(m2['xy'], raw=True)[0]), round(d0, 3)))
                    done = False
                    if tries:
                        d, r, im, m2 = best_turn(i, p, min(tries)[1])
                        if keep(p, d, r, im, u, m2):
                            p['skew'] = d; p['after_tilt'] = round(r, 3); p['after_tilt_image'] = im; p['turned_in_check'] = True
                            mk = m2; done = True
                    if not done:                      # (a page found by its edge alone whose turn is not certified: the
                        if p.get('tilt_by_edge') is not None: p['tilt_disputed'] = round(u, 3)   # measures disagree)
                        else: p['untreated_tilt'] = round(u, 3)
        if tilt_only or not p.get('crop'): continue
        c = p['crop']; known = (p.get('blots') or []) + (p.get('edge') or [])
        if rec.get('clean_margins') and mk.get('text'):
            # a book without print in its side margins: the text block seen at 1,000 px must be inside the box, and no mark
            # may straddle the box edge (half in, half out = a cut letter); marks wholly outside the text columns are the
            # margin's dots, pen strokes and scan edges, cut on purpose. If not: the box slides up to 2 %, else takes the
            # same shape just large enough (never a cut line, never a page left whole for a stray mark)
            t = mk['text']; gx_, gy_ = 0.015 * p['w'], 0.015 * p['h']
            nts = notes_of(mk.get('margin') or [], p['w'], p['h'])   # marginal notes seen at 1,000 px: kept, like the text
            if nts: p['notes'] = [[round(v, 1) for v in b] for b in nts]
            tn = union([t] + nts)
            # a cut letter lies next to the text block (within the gap that makes text); a pen stroke or speck further out
            # that happens to cross the box edge is margin, cut like the rest (2026-10-09: اللآلئ ج1 p. 8 stayed whole)
            cross = [b for b in mk.get('parts', []) if not inside(b, c, 1.0) and b[0] < c[2] and b[2] > c[0] and b[1] < c[3] and b[3] > c[1]
                     and not near(b, known) and b[2] >= t[0] - gx_ and b[0] <= t[2] + gx_ and b[3] >= t[1] - gy_ and b[1] <= t[3] + gy_]
            need = ([tn] if not inside(tn, c, 1.0) else []) + cross
            if need:
                u = union(need + [tn])
                # a slide must leave half the book's margin around the text and its notes (2026-10-09: اللآلئ ج2 ص 39 slid
                # until its note touched the edge); else the box grows with the full margin (shown at the book's size)
                mg = rec.get('margin_pt') or 0.01 * (c[2] - c[0]); h_ = 0.5 * mg
                up = [u[0] - h_, u[1] - h_, u[2] + h_, u[3] + h_]
                dx = up[0] - c[0] if up[0] < c[0] else (up[2] - c[2] if up[2] > c[2] else 0)
                dy = up[1] - c[1] if up[1] < c[1] else (up[3] - c[3] if up[3] > c[3] else 0)
                n = [c[0] + dx, c[1] + dy, c[2] + dx, c[3] + dy]
                if not (abs(dx) <= 0.02 * p['w'] and abs(dy) <= 0.02 * p['h'] and inside(up, n, 1.0)
                        and n[0] >= 0 and n[1] >= 0 and n[2] <= p['w'] and n[3] <= p['h']):
                    cw, ch = c[2] - c[0], c[3] - c[1]
                    sc = max(1.0, (u[2] - u[0] + 2 * mg) / cw, (u[3] - u[1] + 2 * mg) / ch)
                    smax = min(p['w'] / cw, p['h'] / ch)        # never beyond the sheet: the margin gives way first
                    if sc > smax: sc = max(1.0, smax, (u[2] - u[0]) / cw, (u[3] - u[1]) / ch)
                    x2, y2 = (u[0] + u[2]) / 2, (u[1] + u[3]) / 2
                    n = [x2 - cw * sc / 2, y2 - ch * sc / 2, x2 + cw * sc / 2, y2 + ch * sc / 2]
                    sx = -n[0] if n[0] < 0 else (p['w'] - n[2] if n[2] > p['w'] else 0); sy = -n[1] if n[1] < 0 else (p['h'] - n[3] if n[3] > p['h'] else 0)
                    n = [n[0] + sx, n[1] + sy, n[2] + sx, n[3] + sy]
                    p['enlarged'] = round(max(sc, p.get('enlarged', 1.0)), 3)
                if n[0] >= -0.5 and n[1] >= -0.5 and n[2] <= p['w'] + 0.5 and n[3] <= p['h'] + 0.5 and inside(u, n, 1.0):
                    p['crop'] = [round(max(0, n[0]), 1), round(max(0, n[1]), 1), round(min(p['w'], n[2]), 1), round(min(p['h'], n[3]), 1)]
                    p['verify_moved'] = True
                else:
                    p['crop'] = None; p['verify'] = u; moved.append(i); continue
            p['cut_specks'] = [x for x in mk['specks'] if not inside(x, p['crop'], 0)]
            p['cut_margin'] = [b for b in mk.get('margin') or [] if not inside(b, p['crop'], 1.0)]
            if any(not inside(b, p['crop'], 1.0) for b in nts): p['notes_cut'] = True     # must never happen (checked)
            continue
        out = [b for b in mk.get('parts', []) if not inside(b, c, 1.0) and not near(b, known)]
        if out:
            ob = [min(b[0] for b in out), min(b[1] for b in out), max(b[2] for b in out), max(b[3] for b in out)]
            dx = ob[0] - c[0] if ob[0] < c[0] else (ob[2] - c[2] if ob[2] > c[2] else 0)
            dy = ob[1] - c[1] if ob[1] < c[1] else (ob[3] - c[3] if ob[3] > c[3] else 0)
            n = [c[0] + dx, c[1] + dy, c[2] + dx, c[3] + dy]
            if abs(dx) <= 0.02 * p['w'] and abs(dy) <= 0.02 * p['h'] and n[0] >= 0 and n[1] >= 0 and n[2] <= p['w'] and n[3] <= p['h'] \
               and (p.get('box') is None or inside(p['box'], n, 1.0)) and all(inside(b, n, 1.0) for b in out):   # a blank page has no box
                p['crop'] = [round(v, 1) for v in n]; p['verify_moved'] = True
            else:
                p['crop'] = None; p['verify'] = ob; moved.append(i); continue
        p['cut_specks'] = [x for x in mk['specks'] if not inside(x, p['crop'], 0)]
    doc.close()
    rec['whole'] = sorted(set(rec.get('whole', [])) | set(moved)); rec['verify_whole'] = moved
    rec['blot_pages'] = sum(1 for p in rec['pages'] if p.get('crop') and p.get('blots'))
    rec['skewed'] = sum(1 for p in rec['pages'] if p.get('skew'))
    rec['residual_tilt'] = [i + 1 for i, p in enumerate(rec['pages']) if p.get('skew') and not (p.get('after_tilt', 9) <= LEVEL and p.get('after_tilt_image', 9) <= IMG_LEVEL)
                            and not (p.get('curved') and p.get('after_tilt', 9) <= CURVED and p.get('after_tilt_image', 9) <= CURVED)
                            and not (p.get('level_by_lines') is not None and max(p.get('after_tilt', 9), p.get('after_tilt_image', 9)) <= 0.35)
                            and not (p.get('level_by_edge') is not None and p.get('after_tilt', 9) <= 0.2)]
    rec['level_by_lines'] = [i + 1 for i, p in enumerate(rec['pages']) if p.get('level_by_lines') is not None and p.get('skew')]
    rec['curved'] = [i + 1 for i, p in enumerate(rec['pages']) if p.get('curved')]
    rec['enlarged'] = [i + 1 for i, p in enumerate(rec['pages']) if p.get('enlarged')]
    rec['tilt_disputed'] = [i + 1 for i, p in enumerate(rec['pages']) if p.get('tilt_disputed')]
    rec['untreated_tilt'] = [i + 1 for i, p in enumerate(rec['pages']) if p.get('untreated_tilt')]
    rec['unsure_tilt'] = [i + 1 for i, p in enumerate(rec['pages']) if p.get('unsure_tilt')]
    if rec.get('decision') == 'crop' and len(rec['whole']) > MAX_WHOLE * max(1, rec['measured']):
        rec['decision'] = f'skip: {len(rec["whole"])} pages do not fit one box (second check, 1,000 px)'
    if rec.get('decision') == 'crop' and not rec['skewed'] and all(r.endswith('tilted pages') for r in rec.get('reasons') or []):
        rec['decision'] = 'skip: a good scan, and the tilts the first look saw were not confirmed'   # tilt was the only reason
    return rec

def frames(rec):
    """ONE PAGE SIZE FOR THE WHOLE BOOK (owner 2026-10-09: «أعراض الصفحات غير متساوية، هذا مرفوض بالمرّة… أما اتحاد العرض فيجب
    اطّراده في جميع الكتب»): every page is shown in a box of exactly the book's size W × H — `show` (the part of the page
    shown, in the reader's frame) and `scale` (W ÷ its width). A page whose needed part is larger than the box — its text
    with a marginal note, a wide table, a page no box holds, a cover or a plate (فهرسة ابن خير ص 380: «كان يمكن ضبط الصفحة
    بوضوح ودون قصّ صورة الغلاف») — shows that part whole, shrunk to the box (scale < 1, the same lossless drawing instruction
    as a turn); never the page left at its own size. A page smaller than the box (a shorter scan) is shown up to 5 % larger
    when all it holds still fits, else on blank paper beyond its own edge (`bands`)"""
    W, H = rec['size']; A = W / H; m = rec.get('margin_pt') or 0.0
    for p in rec['pages']:
        for k in ('show', 'scale', 'bands', 'fit_whole'): p.pop(k, None)
        pw, ph = p['w'], p['h']; c = p.get('crop')
        if p['kind'] == 'rotated': p['fit_whole'] = True; continue    # a page turned by /Rotate: fitted whole (apply)
        if c and abs(c[2] - c[0] - W) <= 1.0 and abs(c[3] - c[1] - H) <= 1.0:      # the book's box
            x, y, rw, rh = (c[0] + c[2]) / 2, (c[1] + c[3]) / 2, W, H
        else:
            if c: N = c                                # a box grown for this page, or cut short by the page's edge
            else:                                       # a page left whole, a picture: all it holds, with the book's margin
                parts = [b for b in (p.get('box'), p.get('content_box'), p.get('verify')) if b]
                N = union(parts) if parts else [0.0, 0.0, pw, ph]
                N = [max(0.0, N[0] - m), max(0.0, N[1] - m), min(pw, N[2] + m), min(ph, N[3] + m)]
            nw, nh = max(N[2] - N[0], 1.0), max(N[3] - N[1], 1.0)
            rw, rh = (nw, nw / A) if nw / nh > A else (nh * A, nh)
            if rw < W: rw, rh = W, H                   # a small part is not magnified
            x, y = (N[0] + N[2]) / 2, (N[1] + N[3]) / 2
            if rw > pw + 0.5 or rh > ph + 0.5:         # beyond the page: rather up to 5 % larger, if all it holds still fits
                fw_ = min(pw, ph * A); fh_ = fw_ / A
                if W / fw_ <= MAGNIFY_MAX:
                    fx, fy = min(max(x, fw_ / 2), pw - fw_ / 2), min(max(y, fh_ / 2), ph - fh_ / 2)
                    F = [fx - fw_ / 2, fy - fh_ / 2, fx + fw_ / 2, fy + fh_ / 2]
                    if all(inside(b, F, 1.0) for b in (p.get('box'), p.get('verify')) if b): x, y, rw, rh = fx, fy, fw_, fh_
        if rw <= pw: x = min(max(x, rw / 2), pw - rw / 2)    # on the page whenever it fits there
        if rh <= ph: y = min(max(y, rh / 2), ph - rh / 2)
        p['show'] = [round(v, 3) for v in (x - rw / 2, y - rh / 2, x + rw / 2, y + rh / 2)]; p['scale'] = round(W / rw, 6)
        if rw > pw + 0.01 or rh > ph + 0.01: p['bands'] = True
    rec['scaled'] = [i + 1 for i, p in enumerate(rec['pages']) if p.get('scale') and abs(p['scale'] - 1) > 1e-4]
    rec['bands'] = [i + 1 for i, p in enumerate(rec['pages']) if p.get('bands')]
    return rec

def _verify_chunk(args):
    path, rec, px, tilt_only, idx = args
    r = verify(path, rec, px, tilt_only, only=set(idx))
    return {i: r['pages'][i] for i in idx}, r['verify_whole']

def append_contents(doc, page, data):
    """one new stream after the page's existing content"""
    ta, v = doc.xref_get_key(page.xref, 'Contents')
    if ta == 'xref':
        x = int(v.split()[0]); body = doc.xref_object(x).strip()
        old = body[1:-1] if body.startswith('[') else v
    elif ta == 'array': old = v.strip()[1:-1]
    else: return False
    xa = doc.get_new_xref(); doc.update_object(xa, '<<>>'); doc.update_stream(xa, data)
    doc.xref_set_key(page.xref, 'Contents', f'[{old} {xa} 0 R]')
    return True

def erase_stamp(doc, page, inv, p):
    """an uploader's stamp on white paper (owner 2026-10-09: «or even: erase it»): a white patch drawn over it after the
    page's own content — inside the page's turn, so it follows the page; the scan itself stays byte for byte"""
    if not p.get('stamp') or p.get('paper', 0) < 245: return False
    cmd = ''
    for st in p['stamp']:
        b = pad_box(st, p['w'])
        a_, b_ = pymupdf.Point(b[0], b[1]) * inv, pymupdf.Point(b[2], b[3]) * inv
        x0, y0, x1, y1 = min(a_.x, b_.x), min(a_.y, b_.y), max(a_.x, b_.x), max(a_.y, b_.y)
        cmd += f'{x0:.2f} {y0:.2f} {x1 - x0:.2f} {y1 - y0:.2f} re '
    return append_contents(doc, page, f'q 1 g {cmd}f Q\n'.encode())

def images_of(doc):
    return [[(x[0], x[2], x[3], len(doc.xref_stream_raw(x[0]) or b'')) for x in p.get_images(full=True)] for p in doc]

def apply(src, rec, dst):
    """LOSSLESS: per page the CropBox — exactly the book's size W × H on every page (frames) — and, for a tilted, moved or
    scaled page, «q … cm» / «Q» pairs around its content (a page shown on blank paper beyond its edge is also clipped to its
    own sheet, and its MediaBox grows to hold the box); incremental save; checked: same pages, same images byte for byte,
    every page the same size"""
    import shutil
    if rec.get('decision') == 'level': return apply_level(src, rec, dst)
    frames(rec)
    shutil.copyfile(src, dst)
    before = pymupdf.open(src); imgs = images_of(before); n = len(before); before.close()
    doc = pymupdf.open(dst); done = turned_n = scaled_n = 0
    W, H = rec['size']
    for i, p in enumerate(rec['pages']):
        page = doc[i]
        inv = ~page.transformation_matrix                # the page's coordinates → PDF coordinates (before any change)
        mb = raw_box(doc, page.xref, 'MediaBox')
        if p.get('fit_whole'):                           # a page turned by /Rotate: all of it, fitted (unrotated coordinates)
            cb = raw_box(doc, page.xref, 'CropBox') or mb
            clip = [max(cb[0], mb[0]), max(cb[1], mb[1]), min(cb[2], mb[2]), min(cb[3], mb[3])]
            tw, th = (W, H) if page.rotation % 180 == 0 else (H, W)
            s = min(tw / (clip[2] - clip[0]), th / (clip[3] - clip[1])); cx, cy = (clip[0] + clip[2]) / 2, (clip[1] + clip[3]) / 2
        elif p.get('show'):
            mv = p.get('move') if p.get('crop') else None
            erase_stamp(doc, page, inv, p)
            if p.get('skew') or mv:
                rotate_contents(doc, page, p.get('skew') or 0, *(mv or [0, 0])); turned_n += 1
            R = p['show']; a, b = pymupdf.Point(R[0], R[1]) * inv, pymupdf.Point(R[2], R[3]) * inv
            cx, cy = (a.x + b.x) / 2, (a.y + b.y) / 2; s = p['scale']; tw, th = W, H; clip = None
            if p.get('bands'):
                r0, r1 = pymupdf.Point(0, 0) * inv, pymupdf.Point(page.rect.width, page.rect.height) * inv
                clip = [min(r0.x, r1.x), min(r0.y, r1.y), max(r0.x, r1.x), max(r0.y, r1.y)]
        else: continue
        if abs(s - 1) > 1e-6 or clip:                    # drawn s times its size about the shown part's centre
            pre = f'q {s:.6f} 0 0 {s:.6f} {cx * (1 - s):.4f} {cy * (1 - s):.4f} cm\n'
            if clip: pre += f'{clip[0]:.4f} {clip[1]:.4f} {clip[2] - clip[0]:.4f} {clip[3] - clip[1]:.4f} re W n\n'
            wrap_contents(doc, page, pre.encode()); scaled_n += 1
        x0, y0 = round(cx - tw / 2, 2), round(cy - th / 2, 2)    # exact to 0.01 pt: every page reads the same size
        T = [x0, y0, round(x0 + tw, 2), round(y0 + th, 2)]
        if T[0] < mb[0] - 1e-3 or T[1] < mb[1] - 1e-3 or T[2] > mb[2] + 1e-3 or T[3] > mb[3] + 1e-3:   # a larger sheet
            doc.xref_set_key(page.xref, 'MediaBox', '[%s]' % ' '.join(f'{v:.2f}' for v in union([mb, T])))
        doc.xref_set_key(page.xref, 'CropBox', '[%s]' % ' '.join(f'{v:.2f}' for v in T))
        done += 1
    doc.save(dst, incremental=True, encryption=pymupdf.PDF_ENCRYPT_KEEP); doc.close()
    chk = pymupdf.open(dst)
    assert len(chk) == n, 'page count changed'
    assert images_of(chk) == imgs, 'images changed'
    off = sorted({(round(pg.rect.width, 3), round(pg.rect.height, 3)) for pg in chk if abs(pg.rect.width - W) > 0.006 or abs(pg.rect.height - H) > 0.006})
    chk.close()
    assert not off, f'pages of different sizes: {off[:6]} (the book: {W} × {H})'
    return {'pages': n, 'cropped': done, 'turned_or_moved': turned_n, 'scaled': scaled_n, 'bytes_out': os.path.getsize(dst)}

def apply_level(src, rec, dst):
    """LOSSLESS, a level-only book: the tilted pages' turn («q … cm» / «Q»); on grey or colour paper every page's CropBox
    inset by the same thin strip. Incremental save; checked: same pages, same images, every page of its intended size"""
    import shutil
    shutil.copyfile(src, dst)
    before = pymupdf.open(src); imgs = images_of(before); n = len(before); want = []
    for i, p in enumerate(rec['pages']):
        r = before[i].rect; c = p.get('crop')
        want.append((c[2] - c[0], c[3] - c[1]) if c else (r.width, r.height))
    before.close()
    doc = pymupdf.open(dst); turned_n = 0
    for i, p in enumerate(rec['pages']):
        page = doc[i]; inv = ~page.transformation_matrix
        erase_stamp(doc, page, inv, p)
        if p.get('skew'): rotate_contents(doc, page, p['skew']); turned_n += 1
        c = p.get('crop')
        if c:
            a, b = pymupdf.Point(c[0], c[1]) * inv, pymupdf.Point(c[2], c[3]) * inv
            T = [min(a.x, b.x), min(a.y, b.y), max(a.x, b.x), max(a.y, b.y)]
            doc.xref_set_key(page.xref, 'CropBox', '[%s]' % ' '.join(f'{v:.2f}' for v in T))
    doc.save(dst, incremental=True, encryption=pymupdf.PDF_ENCRYPT_KEEP); doc.close()
    chk = pymupdf.open(dst)
    assert len(chk) == n, 'page count changed'
    assert images_of(chk) == imgs, 'images changed'
    off = [i + 1 for i, pg in enumerate(chk) if abs(pg.rect.width - want[i][0]) > 0.02 or abs(pg.rect.height - want[i][1]) > 0.02]
    chk.close()
    assert not off, f'pages not of their intended size: {off[:8]}'
    return {'pages': n, 'cropped': sum(1 for p in rec['pages'] if p.get('crop')), 'turned_or_moved': turned_n, 'scaled': 0,
            'bytes_out': os.path.getsize(dst)}

def sample_pages(rec):
    """pages worth showing for approval, with the reason: two facing text pages from the middle, the most tilted page,
    the page with the most stains left out, a page centred on its own text, the tightest margin, a page left whole"""
    P = rec['pages']; text = [i for i, p in enumerate(P) if p.get('crop') and p['kind'] == 'text']
    if not text: return []
    mid = text[len(text) // 2]
    out = [(mid, 'mid'), (mid + 1 if mid + 1 < len(P) and P[mid + 1].get('crop') else mid - 1, 'mid')]
    sk = [i for i in text if P[i].get('skew')]
    if sk: out.append((max(sk, key=lambda i: abs(P[i]['skew'])), 'skew'))
    cv = [i for i in text if P[i].get('curved')]
    if cv: out.append((cv[0], 'curved'))
    en = [i for i in text if P[i].get('enlarged')]
    if en: out.append((max(en, key=lambda i: P[i]['enlarged']), 'enlarged'))
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
    return res[:8]

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
        b = p.get('show') or p.get('crop') or [0, 0, page.rect.width, page.rect.height]; z = px / (b[2] - b[0])
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
          'own': 'صفحة شاذة (ختم، لوحة، تعليقة بعيدة): وُسِّط الإطار على ما فيها هي', 'whole': 'صفحة تبقى كاملة (نصها أعرض من الإطار)',
          'owner': 'صفحة أشرتَ إليها في العينة السابقة', 'curved': 'صفحة مقوسة قليلا: قُوِّمت قدر ما يستطيع تدوير واحد',
          'enlarged': 'صفحة نصها أكبر من المعتاد: أخذت إطارا بالنسبة نفسها أكبر قليلا (لا يُقص من نصها شيء)'}

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
<li>التوسط الأفقي: {"مختلف للفردية والزوجية (في الهامش مادة ثابتة في جهة)" if any(float(v) for v in (rec.get("parity_offsets") or {}).values()) else "واحد للفردية والزوجية"}</li><li>صفحات مائلة قُوِّمت: {rec.get("skewed", 0)}</li><li>بقي فيها ميل بعد التقويم: {len(rec.get("residual_tilt") or [])}{(" (ص " + "، ".join(map(str, rec["residual_tilt"][:8])) + ")") if rec.get("residual_tilt") else ""}</li><li>مقوسة قليلا قُوِّمت قدر ما يستطيع تدوير واحد: {len(rec.get("curved") or [])}{(" (ص " + "، ".join(map(str, rec["curved"][:8])) + ")") if rec.get("curved") else ""}</li><li>{"لا كتابة في هامشيه: الإطار كتلة النص" if rec.get("clean_margins") else "في هامشيه كتابة: إطار بهامش أوسع"}</li><li>صفحات بإطار أكبر قليلا (نصها أعرض): {len(rec.get("enlarged") or [])}</li><li>مائلة لم تُقوَّم: {len(rec.get("untreated_tilt") or [])}{(" (ص " + "، ".join(map(str, rec["untreated_tilt"][:8])) + ")") if rec.get("untreated_tilt") else ""}</li><li>صفحات فيها بقع تُركت خارج الإطار: {rec.get("blot_pages", 0)}</li><li>صفحات شاذة وُسِّطت على نصها: {rec.get("own_centre", 0)}</li></ul>{"".join(figs)}</section>''')
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
<h1>عينة القص الجديد — للموافقة (الصيغة الرابعة)</h1>
<div class="intro"><p>بعد ملاحظاتك على العينة الثالثة: صفحات دُوِّرت وهي غير مائلة (المثلث ص 499، الاتباع ص 98، سؤالات أبي داود ص 177)، وصفحات مائلة لم تُقوَّم (الفتن ص 387، اللآلئ ص 466)، والإطار الخفيف في وحي القلم، والهوامش الكبيرة، وموضع الصفحات الفردية والزوجية. <b>لم يتغير شيء على الهاتف</b>: هذه صور فقط.</p><ul>
<li>ما الذي يتغير في الملف؟ في كل صفحة شيئان: صورة الصفحة الممسوحة، وتعليمات تقول للقارئ أين يرسمها وأي جزء منها يُظهر. الصورة المخزنة تبقى كما هي حرفا بحرف: لا تُعاد معالجتها ولا ضغطها، فلا تنقص جودتها شيئا. الذي يتغير التعليمات وحدها: (1) الإطار الذي يحدد الجزء الظاهر، وما خارجه مخفي باقٍ في الملف لا محذوف؛ (2) في الصفحة المائلة أمرٌ بأن تُرسم مدوَّرة قليلا (أو مزاحة)، فيرسمها القارئ كما يرسمها حين تكبّرها. ولذلك يعود أي كتاب إلى حاله الأول تماما بحذف هذه التعليمات.</li>
<li>إطار بمقاس واحد للكتاب كله، يوضع في كل صفحة بحيث تتوسط كتلةُ نصها أفقيا ورأسيا، ولو أخلّ التصوير بموضعها.</li>
<li>الصفحة القصيرة (كآخر صفحة في فصل ليس فيها إلا أسطر قليلة في أعلاها): لا يوسَّط الإطار على أسطرها وإلا قفزت إلى وسط الشاشة، بل يوضع في الموضع نفسه الذي هو فيه في الصفحات المجاورة الكاملة، فتبقى الأسطر في أعلى الصفحة كما في الكتاب المطبوع.</li>
<li>الصفحة الشاذة (صفحة لا يتسع الموضع المعتاد لما فيها، كصفحة ختم الرافع وسطرها في أقصى الطرف، أو لوحة، أو تعليقة بعيدة في الهامش): يوسَّط الإطار على ما فيها هي، فيظهر في وسطه بهوامش متساوية؛ فإن لم يتسع له في حدود الصفحة أزيح المحتوى نفسه إلى الوسط (على الورق الأبيض فقط).</li>
<li>الكتاب الذي لا كتابة في هامشيه الجانبيين (كاللآلئ): يُعرف بأن أقل من عُشر صفحاته فيها علامات في الهامش الجانبي. فيكون الإطار كتلةَ النص نفسها — ومعها العنوان الجاري ورقم الصفحة والحواشي — وهامشا (6٪)، فيُستفاد من الشاشة ما أمكن؛ وكل ما في الهامشين الجانبيين من نقط وخطوط قلم وحواف تصوير وبقع يُقص؛ ولا تبقى صفحة كاملة لعلامة شاردة، والصفحة التي نصها أعرض من المعتاد تأخذ إطارا بالنسبة نفسها أكبر قليلا فلا يُقص من نصها شيء. وتقاس كتلة النص بالفراغ بين العلامات، فالسطر الأطول من غيره والعنوان والبيت يبقى كاملا، ويُتحقق في النظرة الثانية من ألا يقطع حدُّ الإطار حرفا.</li>
<li>الإطار يحيط بكل أثر كتابة في الصفحة: الحواشي، أرقام الصفحات، العناوين الجارية، التعليقات وأرقام المخطوط في الهامش، والأطر والزخارف المطبوعة ولو كانت باهتة؛ ثم هامش معتدل: 8٪ من عرض النص في كل جانب. وإن كان النص داخل إطار مطبوع صار الإطار هو الحد، بهامش رقيق خارجه.</li>
<li>التوسط الأفقي واحد للصفحات الفردية والزوجية، إلا في كتاب يجعل في هامش جهة بعينها مادة ثابتة (كأرقام أوراق المخطوط في الهامش الخارجي): حينئذ يأخذ كلٌّ من الفردية والزوجية موضعه.</li>
<li>الميل يُقاس بطريقتين مستقلتين: (1) ميل أسطر الحبر نفسها، في الصفحة كلها وفي نصفيها، ولا يُقرأ إلا في صفحة فيها ثمانية أسطر فأكثر؛ (2) صورة الصفحة كاملة تُدار بخطوات صغيرة ويُنظر عند أي زاوية تستقيم صفوفها. لا تُدار صفحة إلا إذا رأت الطريقتان كلتاهما أنها مائلة، ولا يُبقى التدوير إلا إذا استوت بالطريقة الأولى (0.15 درجة فأقل، وهي حدود دقة القياس، والعين لا ترى الميل إلا من نحو ربع درجة) ولم ترَ الثانية فيها ميلا ظاهرا (خُمس درجة فأقل، وهي الأخشن)؛ فإن لم يستوِ التدوير الأول جُرِّبت الزوايا القريبة منه وأُخذت أفضلها. والصفحة المقوسة قليلا التي لا يسوّيها تدوير واحد تُقبل إذا نزل ميلها إلى ربع درجة فأقل وإلى ثلث ما كان، وتُذكر في البطاقة؛ وما سوى ذلك لا يُدار ويُذكر. وكل تغيير في الطريقة يُختبر أولا على كل صفحة أخطأت فيها من قبل أو أشرتَ إليها، ولا تُعرض عينة إلا إذا نجحت كلها.</li>
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
