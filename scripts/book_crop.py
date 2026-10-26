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
    out['xy0'] = (c0, r0)                           # (xy is measured from the bands' inner corner, in pixels)
    if m.size == 0: return out
    lab, n = ndimage.label(m, structure=np.ones((3, 3), bool))
    if n == 0: return out
    objs = ndimage.find_objects(lab)
    area = np.bincount(lab.ravel(), minlength=n + 1)
    H, Wd = m.shape
    hgt = np.array([0] + [s[0].stop - s[0].start for s in objs]); wid = np.array([0] + [s[1].stop - s[1].start for s in objs])
    # long straight rules standing up the page (a table's column rules): each one's own slope, read on its ink — the
    # surest ruler of a page that holds them (owner 2026-10-18, خريدة القصر ص 649 «الأخير ما زال مائلا»: an index table
    # whose halves read differently was left tilted 1.5°)
    vang = []
    for i, s in enumerate(objs, 1):
        if hgt[i] >= 0.3 * H and wid[i] <= 0.05 * Wd and area[i] <= 0.25 * hgt[i] * wid[i] + 3 * hgt[i]:
            ys_, xs_ = np.nonzero(lab[s] == i)
            if len(ys_) < 30: continue
            rows_ = np.unique(ys_); cxs = np.array([xs_[ys_ == r_].mean() for r_ in rows_])
            if len(rows_) < 0.8 * hgt[i]: continue
            k_ = np.polyfit(rows_, cxs, 1)[0]
            if np.abs(cxs - np.polyval(np.polyfit(rows_, cxs, 1), rows_)).max() <= 3: vang.append(float(np.degrees(np.arctan(k_))))
    out['rule_tilts'] = vang
    # long straight rules across the page (a running head's rule, a table's rows): each one's own slope — a level one
    # vetoes a projection turn (owner's regression, سؤالات أبي داود ص 177: a two-column index of short entries read 1.2° by
    # the projection; its head rule reads 0.19°)
    hang = []
    for i, s in enumerate(objs, 1):
        if wid[i] >= 0.3 * Wd and hgt[i] <= 0.05 * H and area[i] <= 0.25 * hgt[i] * wid[i] + 3 * wid[i]:
            ys_, xs_ = np.nonzero(lab[s] == i)
            if len(xs_) < 30: continue
            cols_ = np.unique(xs_)
            if len(cols_) < 0.8 * wid[i]: continue
            cys = np.array([ys_[xs_ == c_].mean() for c_ in cols_]); fit = np.polyfit(cols_, cys, 1)
            if np.abs(cys - np.polyval(fit, cols_)).max() <= 3:
                hang.append([float(np.degrees(np.arctan(fit[0]))), (s[1].start + c0) / scale, (s[0].start + r0) / scale,
                             (s[1].stop + c0) / scale, (s[0].stop + r0) / scale])
    out['hrules'] = hang
    sp = SPECK * unit
    small = (hgt <= sp) & (wid <= sp); small[0] = False
    # marks closer than M to each other fall in one group (dilation by M/2 on each)
    grp, _ = ndimage.label(ndimage.binary_dilation(m, iterations=max(1, int(M * unit / 2))), structure=np.ones((3, 3), bool))
    gid = np.zeros(n + 1, np.int64)                  # (a mark lies wholly in one group: every pixel of it gives the group)
    gid[lab[m]] = grp[m]
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
    # marks lying in a scanner band (their centre beyond the allowed area by more than 1 % of the width) are the band, not
    # the page: they no longer count as content (owner 2026-10-18, خريدة القصر ص 649: «اليمين كله أسود سنتيمتر إلى
    # سنتيمترين، يمكن قص معظم السواد» — the band's marks held the frame out to the sheet's edge)
    if True:
        lim = [allowed[0] * scale - c0 - 0.01 * Wd, allowed[1] * scale - r0 - 0.01 * H, allowed[2] * scale - c0 + 0.01 * Wd, allowed[3] * scale - r0 + 0.01 * H]
        inband = {i for i in pre if not (lim[0] <= (objs[i - 1][1].start + objs[i - 1][1].stop) / 2 <= lim[2]
                                         and lim[1] <= (objs[i - 1][0].start + objs[i - 1][0].stop) / 2 <= lim[3])}
        if inband and len(inband) < 0.3 * len(pre):
            out['edge'] += [box_of(i) for i in sorted(inband)]; pre = [i for i in pre if i not in inband]
    if not pre: return out
    # THE SHEET'S BORDER ZONE (owner 2026-10-10, القوافي للتنوخي pp. 77, 87, 89, 95: the photographed edges of the other
    # pages — a band of thin lines —, copier bars, broken border lines kept the frame wide and off-centre): from each side
    # inward, ink at the sheet's edge (in its outer 4 %) followed, within 12 % of the side, by a clear gap (2 % of
    # the width with almost no ink) before anything else: everything wholly inside that zone is the sheet, not the page.
    # A printed frame never touches the sheet's edge; a text that runs to the edge leaves no gap — neither is touched.
    def zone(cov, n, limit, gap):
        if cov[:max(1, int(0.04 * n))].max() < 0.05: return 0       # the sheet may sit a little inside the scan
        last, run = -1, 0
        for k in range(min(n, int(limit * n))):
            if cov[k] >= 0.02: last, run = k, 0
            else:
                run += 1
                if run >= gap and last >= 0: return last + 1
        return 0
    gpx = max(2, int(0.02 * Wd)); zl = zr = zt = zb = 0
    for _ in range(2):                               # a bar along one side puts ink in every row: the top and bottom are
        colcov = m[zt:H - zb].mean(0)                # measured without the side zones, the sides without the top and bottom
        zl, zr = zone(colcov, Wd, 0.12, gpx), zone(colcov[::-1], Wd, 0.12, gpx)
        rowcov = m[:, zl:Wd - zr].mean(1)            # (PDF p. 27: bar + top line + bottom line, one mark round the sheet)
        zt, zb = zone(rowcov, H, 0.10, gpx), zone(rowcov[::-1], H, 0.10, gpx)
    if zl or zr or zt or zb:
        Z = np.zeros((H, Wd), bool)                  # the zones; a mark whose ink lies ≥ 90 % inside them is the sheet —
        if zl: Z[:, :zl] = True                      # also an L where the page-edge lines meet the bottom line (p. 89)
        if zr: Z[:, Wd - zr:] = True
        if zt: Z[:zt, :] = True
        if zb: Z[H - zb:, :] = True
        zoned = set()
        for i in pre:
            sl = objs[i - 1]
            if Z[sl].any() and np.count_nonzero((lab[sl] == i) & Z[sl]) >= 0.9 * area[i]: zoned.add(i)
        if zoned and len(zoned) < len(pre):
            out['edge'] += [box_of(i) for i in sorted(zoned)]
            pre = [i for i in pre if i not in zoned]
    # a blank page showing only the edges of the photocopied sheet (owner 2026-10-10, القوافي للتنوخي pp. 54–60: blank
    # versos whose border lines became «text» as wide as the page): every mark lies in the outer 8 % of a side → no content
    if all(small[i] or objs[i - 1][1].stop <= 0.08 * Wd or objs[i - 1][1].start >= 0.92 * Wd or objs[i - 1][0].stop <= 0.08 * H
           or objs[i - 1][0].start >= 0.92 * H for i in pre):          # dust in the middle does not make it a page of text
        out['edge'] += [box_of(i) for i in pre]; return out
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
    # the photocopied sheet's border, broken into pieces (owner 2026-10-10, القوافي للتنوخي): the text block measured
    # without the outer 6 % of each side; a mark lying wholly in that outer 6 %, at most 4 % thick across it, and at least
    # 5 % of the width away from the text block is the sheet's edge (printed margin numbers sit close to their text)
    def out6(i):
        t = objs[i - 1]
        return t[1].stop <= 0.06 * Wd or t[1].start >= 0.94 * Wd or t[0].stop <= 0.06 * H or t[0].start >= 0.94 * H
    inner = [i for i in pre if not small[i] and not out6(i)]
    if inner:
        ex0 = np.percentile([objs[i - 1][1].start for i in inner], 2); ex1 = np.percentile([objs[i - 1][1].stop for i in inner], 98)
        ey0 = np.percentile([objs[i - 1][0].start for i in inner], 2); ey1 = np.percentile([objs[i - 1][0].stop for i in inner], 98)
        for i in pre:
            t = objs[i - 1]; x0, x1, y0, y1 = t[1].start, t[1].stop, t[0].start, t[0].stop
            if (x1 <= 0.06 * Wd and wid[i] <= 0.04 * Wd and ex0 - x1 >= 0.05 * Wd) or (x0 >= 0.94 * Wd and wid[i] <= 0.04 * Wd and x0 - ex1 >= 0.05 * Wd) \
               or (y1 <= 0.06 * H and hgt[i] <= 0.04 * H and ey0 - y1 >= 0.05 * Wd) or (y0 >= 0.94 * H and hgt[i] <= 0.04 * H and y0 - ey1 >= 0.05 * Wd):
                edge.add(i)
    # a tilted edge of the sheet: starts at the very border (outer 3 %), runs along half the side or more, thin on average
    # (its ink over its length — the outline box of a tilted line is tall), and sparse in that box (a printed rule is solid)
    for i in pre:
        t = objs[i - 1]; x0, x1, y0, y1 = t[1].start, t[1].stop, t[0].start, t[0].stop; fill = area[i] / max(1, hgt[i] * wid[i])
        if (wid[i] >= 0.5 * Wd and (y0 <= 0.03 * H or y1 >= 0.97 * H) and area[i] / wid[i] <= 0.03 * H and fill < 0.5) \
           or (hgt[i] >= 0.5 * H and (x0 <= 0.03 * Wd or x1 >= 0.97 * Wd) and area[i] / hgt[i] <= 0.03 * Wd and fill < 0.5):
            edge.add(i)
    for i in pre:
        if i in edge: continue
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
        # the edge of the photocopied sheet (owner 2026-10-10, القوافي للتنوخي: a long line along the border kept the whole
        # page): a long line or band within 6 % of a side and at least 5 % of the width away from the text block — a printed
        # frame hugs its text (a few % away), the sheet's edge lies at the border, far from it
        # (a solid black bar of the copier as well as a hairline: up to 4 % thick, whatever its fill)
        elif (hgt[i] >= 0.3 * H and wid[i] <= 0.04 * Wd and ((x1 <= 0.06 * Wd and cx0 - x1 >= 0.05 * Wd) or (x0 >= 0.94 * Wd and x0 - cx1 >= 0.05 * Wd))) \
             or (wid[i] >= 0.3 * Wd and hgt[i] <= 0.04 * H and ((y1 <= 0.06 * H and cy0 - y1 >= 0.05 * Wd) or (y0 >= 0.94 * H and y0 - cy1 >= 0.05 * Wd))):
            edge.add(i)
        elif (x0 <= 0.01 * Wd or x1 >= 0.99 * Wd or y0 <= 0.01 * H or y1 >= 0.99 * H) and area[i] / max(1, hgt[i] * wid[i]) < 0.08:
            ix0, ix1, iy0, iy1 = int(cx0), int(cx1), int(cy0), int(cy1)
            if np.count_nonzero(lab[iy0:iy1, ix0:ix1] == i) < 0.1 * area[i]: edge.add(i)
    out['edge'] += [box_of(i) for i in sorted(edge)]
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
        #     (the dotted rims of a bitonal photocopy are found at the scan's own resolution: dot_fields — a band across the
        #     top taken here for a rim was a running head: نظم تنقيح فتح الكريم ص 93, 2026-10-18)
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
    # LINES ARE NOT CONTENT HERE (owner 2026-10-14: «وسط ولا تلتفت للخط الذي هو عيب طباعة», مختصر تاريخ دمشق; scan lines and
    # print damage along a side pulled boxes off-centre or kept pages whole — صبح الأعشى ص 47, مشتبهات القرآن ص 8): a long thin
    # mark (≤ 0.6 % thick, ≥ 20 % of the page long), or a dashed line beside the text block (≥ 4 thin dashes in one column or
    # row, spanning ≥ 15 % of the page). A printed rule or frame comes back in decide() when the book prints it (the same rule
    # on many pages); a scan line or a flaw does not
    lines = {i for i in content if (wid[i] <= 0.006 * Wd and hgt[i] >= 0.2 * H) or (hgt[i] <= 0.006 * H and wid[i] >= 0.2 * Wd)}
    for i in content:                                 # a shorter thin line (≥ 3 % long, ≤ 0.4 % thick) beyond the text block
        s_ = objs[i - 1]                              # (خزانة الأدب ص 18: 64 × 1.2 pt above the running head)
        yc, xc = (s_[0].start + s_[0].stop) / 2, (s_[1].start + s_[1].stop) / 2
        if (hgt[i] <= 0.004 * H and wid[i] >= 0.03 * Wd and (yc <= cy0 - g or yc >= cy1 + g)) or \
           (wid[i] <= 0.004 * Wd and hgt[i] >= 0.03 * H and (xc <= cx0 - g or xc >= cx1 + g)): lines.add(i)
    for vert in (True, False):
        pos = (lambda i: (objs[i - 1][1].start + objs[i - 1][1].stop) / 2) if vert else (lambda i: (objs[i - 1][0].start + objs[i - 1][0].stop) / 2)
        lo_c, hi_c, span, tol = (cx0, cx1, H, 0.004 * Wd) if vert else (cy0, cy1, Wd, 0.004 * H)
        cand = sorted((i for i in content if i not in lines and (pos(i) <= lo_c - g or pos(i) >= hi_c + g)
                       and ((wid[i] <= 0.004 * Wd and hgt[i] >= 2 * wid[i]) if vert else (hgt[i] <= 0.004 * H and wid[i] >= 2 * hgt[i]))), key=pos)
        k = 0
        while k < len(cand):
            j = k
            while j + 1 < len(cand) and pos(cand[j + 1]) - pos(cand[k]) <= tol: j += 1
            grp = cand[k:j + 1]
            if len(grp) >= 4:
                lo = min(objs[i - 1][0].start if vert else objs[i - 1][1].start for i in grp)
                hi = max(objs[i - 1][0].stop if vert else objs[i - 1][1].stop for i in grp)
                if hi - lo >= 0.15 * span and sum(hgt[i] if vert else wid[i] for i in grp) >= 0.3 * (hi - lo): lines.update(grp)
            k = j + 1
    # a DOTTED line beside the text block: a column (row) of ≥ 8 tiny marks (≤ 0.5 % × 0.8 % of the page) within 0.6 % of
    # one another, spanning ≥ 15 % of the page — a scanner's speckled edge (owner 2026-10-18, الحروب الصليبية ص 421 «الثانية
    # سيئة»: dots at the sheet's edge chained onto the text widened it from 343 pt to 420, the page shown smaller)
    # (the text block's edges at the 10th / 90th percentile here: a few dashes in the dotted column can be «large» marks and
    # pull the 2nd / 98th percentile out to it)
    bx0 = np.percentile([objs[i - 1][1].start for i in big], 10); bx1 = np.percentile([objs[i - 1][1].stop for i in big], 90)
    by0 = np.percentile([objs[i - 1][0].start for i in big], 10); by1 = np.percentile([objs[i - 1][0].stop for i in big], 90)
    for vert in (True, False):
        pos = (lambda i: (objs[i - 1][1].start + objs[i - 1][1].stop) / 2) if vert else (lambda i: (objs[i - 1][0].start + objs[i - 1][0].stop) / 2)
        lo_c, hi_c, span, tol = (bx0, bx1, H, 0.008 * Wd) if vert else (by0, by1, Wd, 0.008 * H)
        cand = sorted((i for i in content if i not in lines and (pos(i) <= lo_c - g or pos(i) >= hi_c + g)
                       and wid[i] <= 0.006 * Wd and hgt[i] <= 0.03 * H and (hgt[i] >= 2 * wid[i] or hgt[i] <= 0.008 * H if vert
                                                                            else wid[i] >= 2 * hgt[i] or wid[i] <= 0.008 * Wd)), key=pos)
        k = 0
        while k < len(cand):
            j = k
            while j + 1 < len(cand) and pos(cand[j + 1]) - pos(cand[k]) <= tol: j += 1
            grp = cand[k:j + 1]
            if len(grp) >= 8:
                lo = min(objs[i - 1][0].start if vert else objs[i - 1][1].start for i in grp)
                hi = max(objs[i - 1][0].stop if vert else objs[i - 1][1].stop for i in grp)
                if hi - lo >= 0.15 * span: lines.update(grp)
            k = j + 1
    out['lines'] = [box_of(i) for i in sorted(lines)]
    with_lines = list(content)                        # the tilt is read on all the print, lines included (a footnote rule is
    content = [i for i in content if i not in lines] or content   # the straightest line of a page — الاتباع والمزاوجة ص 51)
    # printed rules and frames, even faint ones (a chain border can break into specks): beyond the text block, a column
    # (row) where light ink runs along half the text block's height (width) or more is print — the box takes it in
    faint = a[r0:r1, c0:c1] < paper - 20
    iy0, iy1, ix0, ix1 = int(cy0), max(int(cy1), int(cy0) + 1), int(cx0), max(int(cx1), int(cx0) + 1)
    bw = max(3, int(round(0.01 * Wd)))               # a band ≈ 1 % of the width: chain links alternate across it
    colcov = ndimage.maximum_filter(faint[iy0:iy1, :], size=(1, bw)).mean(0)
    rowcov = ndimage.maximum_filter(faint[:, ix0:ix1], size=(bw, 1)).mean(1)
    sheet = lambda v, lo, hi, n: (v < 0.06 * n and lo - v >= 0.05 * Wd) or (v > 0.94 * n and v - hi >= 0.05 * Wd)   # the sheet's edge, not a rule
    rule_x = [x for x in range(Wd) if colcov[x] >= 0.5 and (x <= cx0 - g or x >= cx1 + g) and 0.03 * Wd < x < 0.97 * Wd and not sheet(x, cx0, cx1, Wd)]
    rule_y = [y for y in range(H) if rowcov[y] >= 0.5 and (y <= cy0 - g or y >= cy1 + g) and 0.03 * H < y < 0.97 * H and not sheet(y, cy0, cy1, H)]
    def runs(v):                                      # one rule per run of columns (rows): a frame's two sides are two rules
        out_, s0 = [], None
        for k, x in enumerate(v):
            if s0 is None: s0 = x
            if k + 1 == len(v) or v[k + 1] > x + 1: out_.append((s0, x)); s0 = None
        return out_
    out['rules'] = [pt(a_, iy0, b_ + 1, iy1) for a_, b_ in runs(rule_x)] + [pt(ix0, a_, ix1, b_ + 1) for a_, b_ in runs(rule_y)]
    def rule_angle(a_, b_, vert):                     # the rule's own slope, read on its ink: one position per row (column),
        sub = faint[iy0:iy1, a_:b_ + 1] if vert else faint[a_:b_ + 1, ix0:ix1].T   # fitted by a line, outliers (a
        rows = np.nonzero(sub.any(1))[0]              # neighbouring letter) dropped once
        if len(rows) < 0.3 * sub.shape[0] or len(rows) < 20: return None
        pos = np.array([np.nonzero(sub[r_])[0].mean() for r_ in rows])
        k, c = np.polyfit(rows, pos, 1); ok = np.abs(pos - (k * rows + c)) <= 2
        if ok.sum() >= 20: k = np.polyfit(rows[ok], pos[ok], 1)[0]
        return float(np.degrees(np.arctan(k)))
    # a printed frame standing level: level rules on two opposite sides of the text block (owner 2026-10-14, روضة المستبين
    # ص 138: a photographed leaf inside a level frame is not turned) — a frame tilted with its page is no such frame
    # (owner 2026-10-18, إرشاد الساري ص 217 «الجديد مائل»: the guard used to stop on any rule, tilted or not)
    lv = lambda a_, b_, vert: (lambda g_: g_ is not None and abs(g_) <= 0.35)(rule_angle(a_, b_, vert))
    sides = {('L' if b_ < cx0 else 'R') for a_, b_ in runs(rule_x) if lv(a_, b_, True)} | \
            {('T' if b_ < cy0 else 'B') for a_, b_ in runs(rule_y) if lv(a_, b_, False)}
    out['level_frame'] = {'L', 'R'} <= sides or {'T', 'B'} <= sides
    keep = np.zeros(n + 1, bool); keep[content] = True
    ys, xs = np.nonzero(keep[lab])
    out['box'] = pt(xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)   # rules join the box in decide(), when the book prints them
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
    # a thin line is not a letter (owner 2026-10-14, خزانة الأدب ص 18 «غير موسطة»: a stray rule beside the running head
    # carried the text block, and the box with it, 33 pt to the left): ≤ 0.4 % thick and ≥ 3 % long, either way
    thin = ((hh <= 0.004 * H) & (ww >= 0.03 * Wd)) | ((ww <= 0.004 * Wd) & (hh >= 0.03 * H))
    letter = ~strip & ~thin & (hh <= 0.15 * H) & ((hh >= 0.004 * H) | (ww >= 0.008 * Wd))
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
    kl = np.zeros(n + 1, bool); kl[with_lines] = True
    out['xy'] = tuple(reversed(np.nonzero(kl[lab]))) if len(with_lines) != len(content) else (xs, ys)
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
        if abs(a0) >= 3.75:                           # the best at the edge of ±4°: look up to ±8° (owner 2026-10-14, أحكام
            angs = np.arange(-8, 8.001, 0.25)         # القرآن للجصاص ص 250 «لم تقوم»: a 4.25° page was left as it was)
            a0 = float(angs[int(np.argmax([score(v) for v in angs]))])
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

def columns_tilt(a, paper):
    """TWO-COLUMN PAGES (owner 2026-10-09, الفوائد المحصورة: «لم تعالج ص 456 وجميع الفهرس»): an index in two columns fools
    every whole-page measure (the gutter between the columns). The gutter = the emptiest column of pixels between 30 % and
    70 % of the width (smoothed over 1 % of the width), at most 2 % as inked as the fullest column, with ink on both sides
    (each side ≥ 20 % of the ink). Then each column is measured on its own by its lines' edge (edge_tilt): the line starts
    of right-to-left text stand on its right edge. Returns None (not two columns) or [right column, left column] (degrees,
    the sign of skew_of's angle; None for a column whose edge cannot be read)"""
    m = a < max(60, min(200, paper - 50)); H, W = m.shape
    col = ndimage.uniform_filter1d(m.sum(0).astype(float), max(3, int(0.01 * W)))
    lo, hi = int(0.30 * W), int(0.70 * W)
    if hi <= lo or col.max() <= 0: return None
    x = lo + int(np.argmin(col[lo:hi]))
    if col[x] > 0.02 * col.max(): return None
    left, right = m[:, :x].sum(), m[:, x:].sum(); tot = left + right
    if tot == 0 or min(left, right) < 0.2 * tot: return None
    r = edge_tilt(a[:, x:], paper)[0]; l = edge_tilt(a[:, :x], paper)[0]
    return [r, l]

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

def turn_cm(doc, page, deg, dx=0.0, dy=0.0):
    """the «q … cm» line that draws the page's content turned by deg degrees about the page centre, then moved by (dx, dy)
    pt (page coordinates: dy > 0 = down)"""
    import math
    mb = raw_box(doc, page.xref, 'MediaBox'); cx, cy = (mb[0] + mb[2]) / 2, (mb[1] + mb[3]) / 2
    t = math.radians(deg); c, s = math.cos(t), math.sin(t)
    e, f = cx - c * cx + s * cy + dx, cy - s * cx - c * cy - dy
    return f'q {c:.6f} {s:.6f} {-s:.6f} {c:.6f} {e:.4f} {f:.4f} cm\n'.encode()

def rotate_contents(doc, page, deg, dx=0.0, dy=0.0):
    """LOSSLESS deskew / move: the page's content is drawn turned by deg degrees about the page centre, then moved by
    (dx, dy) pt (page coordinates: dy > 0 = down) — one «q … cm» stream before the existing content and one «Q» after it;
    images and text layer are untouched (they turn and move together)"""
    return wrap_contents(doc, page, turn_cm(doc, page, deg, dx, dy))

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

WHOLE_SHOWN = 0.92   # MuPDF decodes an image whole when 90 % of it or more is needed (fz_default_image_decode): 2 % kept aside

def shown_share(quad, r):
    """the share of the convex quadrilateral `quad` (four (x, y) points in order) that lies inside the rectangle r"""
    area = lambda p: abs(sum(p[k - 1][0] * p[k][1] - p[k][0] * p[k - 1][1] for k in range(len(p)))) / 2
    full = area(quad); p = list(quad)
    if full <= 0: return 0.0
    for ax, v, lo in ((0, r[0], True), (0, r[2], False), (1, r[1], True), (1, r[3], False)):   # one side of r at a time
        ins = lambda q: q[ax] >= v if lo else q[ax] <= v
        out = []
        for k in range(len(p)):
            a, b = p[k - 1], p[k]
            if ins(a) != ins(b):
                t = (v - a[ax]) / (b[ax] - a[ax]); out.append((a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1])))
            if ins(b): out.append(b)
        p = out
        if len(p) < 3: return 0.0
    return area(p) / full

def odd_drawing(t):
    """a one-page document MuPDF may draw through clips the page's listings do not show — a soft mask, a pattern or
    shading, a Type 3 font, text used as a clip — or whose images the two listings count differently, or a turned page"""
    import re
    pg = t[0]
    if pg.rotation: return True
    try:
        cs = set(pg.get_contents())
        for x in range(1, t.xref_length()):
            s = t.xref_object(x, compressed=True)
            if '/PatternType' in s or '/ShadingType' in s or '/Type3' in s: return True
            if '/SMask' in s and '/Subtype/Image' not in s and not re.search(r'/SMask\s*/None', s): return True
            if (x in cs or '/Subtype/Form' in s) and t.xref_is_stream(x) and re.search(rb'(?<![\w.])[4-7]\s+Tr(?![\w])', t.xref_stream(x)):
                return True
        log = pg.get_bboxlog()
        if any(k not in ('fill-image', 'fill-imgmask', 'fill-path', 'stroke-path', 'fill-text', 'stroke-text', 'ignore-text') for k, _ in log):
            return True
        return sum(k in ('fill-image', 'fill-imgmask') for k, _ in log) != len(pg.get_image_info())
    except Exception: return True

def whole_shown(pg):
    """every image of the page, as it now stands, shown ≥ 92 % inside the page and every clip and group (the clips' and
    groups' boxes, as MuPDF clips an image's decoding) — so MuPDF decodes each of them whole. pg: a page object made for
    this view (doc[0] makes a new one each time; PyMuPDF keeps get_image_info's answer on the object). In doubt: False"""
    try:
        info = pg.get_image_info()
        if not info: return True
        R = list(pg.rect)
        for d in pg.get_drawings(extended=True):
            k = d.get('type')
            if k not in ('clip', 'group'): continue
            b = d.get('scissor' if k == 'clip' else 'rect')
            if b is None: return False
            R = [max(R[0], b[0]), max(R[1], b[1]), min(R[2], b[2]), min(R[3], b[3])]
        if R[2] <= R[0] or R[3] <= R[1]: return False
        for x in info:
            a, b, c, d, e, f = x['transform']
            if shown_share([(e, f), (a + e, b + f), (a + c + e, b + d + f), (c + e, d + f)], R) < WHOLE_SHOWN: return False
        return True
    except Exception: return False

class Turner:
    """turned() for many angles of ONE page (2026-10-25, speed): a single one-page document whose «q … cm» stream is
    rewritten for each angle, so MuPDF decodes the page's image once instead of once per angle (renders 1.5–5× faster).
    EXACT ONLY WHERE MUPDF DECODES EVERY IMAGE WHOLE (2026-10-26): an image less than 90 % shown — cut by a CropBox (every
    page of 816413b0e765: 9.6 % of its scan above the page), a clip or a group — is decoded in part, and MuPDF keeps every
    decoded image: a view drawn after one that decoded it whole took the whole copy where a fresh document decodes the
    part — the same page a sub-pixel apart (19 of 7,160 renders on the regression's books; marks a pixel wider on
    fbf39d55c6f7 p. 9). So a view is drawn here only when every image of the page is ≥ 92 % shown in it (whole_shown) on
    a page without hidden clips (odd_drawing); any other view comes from a fresh turned() document, as before — the
    method sees the same pixels either way. page(deg, dx, dy) → the page, valid until the next call"""
    def __init__(self, doc, i):
        self.doc, self.i, self.fresh = doc, i, None
        self.t = pymupdf.open(); self.t.insert_pdf(doc, from_page=i, to_page=i)
        self.plain = self.t.xref_get_key(self.t[0].xref, 'Contents')   # the content as turned() leaves it unturned
        self.xa = None; self.wrapped = None
        self.ok = not odd_drawing(self.t)
    def page(self, deg, dx=0.0, dy=0.0):
        if self.fresh: self.fresh.close(); self.fresh = None
        t = self.t; pg = t[0]
        if not (deg or dx or dy):                    # unturned: the page's own content, as turned() leaves it
            if self.xa is not None: t.xref_set_key(pg.xref, 'Contents', self.plain[1])
        elif self.xa is not None: t.update_stream(self.xa, turn_cm(t, pg, deg, dx, dy)); t.xref_set_key(pg.xref, 'Contents', self.wrapped)
        elif wrap_contents(t, pg, turn_cm(t, pg, deg, dx, dy)):   # (no content stream to turn: turned() leaves it so too)
            self.wrapped = t.xref_get_key(pg.xref, 'Contents')[1]; self.xa = int(self.wrapped.strip('[] ').split()[0])
        if self.ok and whole_shown(t[0]): return t[0]
        self.fresh = turned(self.doc, self.i, deg, dx, dy); return self.fresh[0]
    def close(self):
        if self.fresh: self.fresh.close()
        self.t.close()

def inside(b, box, tol=0.5):
    return b[0] >= box[0] - tol and b[1] >= box[1] - tol and b[2] <= box[2] + tol and b[3] <= box[3] + tol

def union(bs):
    return [min(b[0] for b in bs), min(b[1] for b in bs), max(b[2] for b in bs), max(b[3] for b in bs)]

def thin_line(b, w, h):
    """a rule or a scan line, not a letter: ≤ 0.4 % thick and ≥ 3 % long (of the page), either way"""
    bw, bh = b[2] - b[0], b[3] - b[1]
    return (bh <= 0.004 * h and bw >= 0.03 * w) or (bw <= 0.004 * w and bh >= 0.03 * h)

def figures_of(margin, w, h):
    """PICTURES, PLATES, TABLES beside the text (owner 2026-10-14, القائد إلى العقائد ص 15 «خطأ»: the photo of a manuscript
    leaf in its frame was cut — one big mark, not a letter, was taken for margin): a mark at least 15 % of the page wide and
    tall and 4 % of its area is content that must be shown whole, wherever it lies"""
    return [b for b in margin if b[2] - b[0] >= 0.15 * w and b[3] - b[1] >= 0.15 * h and (b[2] - b[0]) * (b[3] - b[1]) >= 0.04 * w * h]

def printed_groups(margin, w, h):
    """PRINT IN THE MARGIN of a book that prints there (folio numbers of the manuscript, glosses, side headings): groups of
    margin marks (less than 1.5 % of the width apart) holding two letter-sized marks or more (≥ 0.6 % of the height tall and
    ≥ 0.3 % of the width wide), or one large glyph (≥ 1.5 % of the height); not lines. A few dots or a speck far from the text
    are not print (owner 2026-10-14, أسرار البلاغة ص 187 «توسيط»: five dots at the foot pulled the box aside)"""
    M_ = [b for b in margin if not thin_line(b, w, h)]
    if not M_: return []
    from scipy.sparse.csgraph import connected_components
    B = np.array(M_, float); g = 0.015 * w
    adj = (B[:, None, 0] < B[None, :, 2] + g) & (B[None, :, 0] < B[:, None, 2] + g) & \
          (B[:, None, 1] < B[None, :, 3] + g) & (B[None, :, 1] < B[:, None, 3] + g)
    k, lab = connected_components(adj, directed=False)
    out = []
    for j in range(k):
        S = B[lab == j]; hh, ww = S[:, 3] - S[:, 1], S[:, 2] - S[:, 0]
        if ((hh >= 0.006 * h) & (ww >= 0.003 * w)).sum() >= 2 or (hh >= 0.015 * h).any():
            out.append([float(S[:, 0].min()), float(S[:, 1].min()), float(S[:, 2].max()), float(S[:, 3].max())])
    return out

def printlike(b, w, h, z):
    """a mark that may be print the box must hold — a letter, a word, a digit, a sign (2026-10-26) — at z pixels per pt: not a
    HAIRLINE (one or two pixels thick and at least four times as long: a scan line broken into dashes, seen only at the
    second look's resolution — خزانة الأدب ج 1 ص 34, 96, 256 …: the dashes above the running head carried the text block up
    and the box with it, over the very lines the owner had the box avoid, 2026-10-18; f134344a7421 ص 165: a dash 2 px
    thick; a letter's stroke apart from its letter is shorter, a printed rule is no text — decide() keeps the book's rules),
    not a BAR (a tenth of the page long or more and eight times as long as thick: a copier's black bar — الحروب الصليبية
    ص 398–426, the page shown 8–21 % smaller)"""
    bw, bh = b[2] - b[0], b[3] - b[1]; th, ln = min(bw, bh), max(bw, bh)
    if th * z < 2.5 and ln >= 4 * th: return False
    return not ((bw >= 0.1 * w and bw >= 8 * bh) or (bh >= 0.1 * h and bh >= 8 * bw))

def hairline(b, z):
    """one or two pixels thick at z pixels per pt and at least four times as long (printlike)"""
    bw, bh = b[2] - b[0], b[3] - b[1]; th, ln = min(bw, bh), max(bw, bh)
    return th * z < 2.5 and ln >= 4 * th

def print_marks(marks, w, h, z):
    """THE PRINT AMONG THE MARKS (2026-10-26): printlike, and a thin upright stroke standing in a word — an alif, a «١», a
    parenthesis of a small font is 1–2 px thick at 1,000 px and four times as tall, a hairline by its shape (خريدة القصر
    064846139175 ص 278: the alif of «انظر» left out, the text block stopped short of the word and the box cut it): print
    when a letter of the page (letterlike, printlike) stands on its row — half of the shorter one's height shared — within
    1 % of the width, and it is at most twice that letter's height. A scan line's dashes lie along it, not in a word"""
    P = [b for b in marks if printlike(b, w, h, z)]
    U = [b for b in marks if b[3] - b[1] > b[2] - b[0] and b[3] - b[1] < 0.1 * h and hairline(b, z)]
    A = np.array([b[:4] for b in P if letterlike(b, w, h)], float).reshape(-1, 4)
    if not U or not len(A): return P
    g, qh = 0.01 * w, A[:, 3] - A[:, 1]
    for b in U:
        bh = b[3] - b[1]; ov = np.minimum(A[:, 3], b[3]) - np.maximum(A[:, 1], b[1])
        if ((A[:, 0] <= b[2] + g) & (A[:, 2] >= b[0] - g) & (ov >= 0.5 * np.minimum(qh, bh)) & (bh <= 2 * qh + 1)).any(): P.append(b)
    return P

def letterlike(b, w, h):
    """a letter-like mark as marks() reads the text block by gaps: not wholly in the sheet's outer 3 %, not a thin line, not
    taller than 15 % of the page, not a speck"""
    bw, bh = b[2] - b[0], b[3] - b[1]
    return not (b[2] <= 0.03 * w or b[0] >= 0.97 * w or b[3] <= 0.03 * h or b[1] >= 0.97 * h) and not thin_line(b, w, h) \
        and bh <= 0.15 * h and (bh >= 0.004 * h or bw >= 0.008 * w)

def text_block(parts, seed, w, h, z, prn=None):
    """THE TEXT BLOCK OF THE SECOND LOOK ON PRINT ONLY (2026-10-26): marks()' text block by gaps — from the seed's columns,
    every letter-like mark less than 1.5 % of the width away widens them, every one inside them is text (running head, page
    number, footnotes) — on the print-like marks alone (printlike): at 1,000 px a scan line breaks into one-pixel dashes that
    count as letters there and chained the text block up to the line (95 pages of the 31 regression books moved or enlarged,
    most for such dashes). None: no letter-like mark in the seed's columns"""
    L = [b for b in (prn if prn is not None else [b for b in parts if printlike(b, w, h, z)]) if letterlike(b, w, h)]
    x0, x1, gx = seed[0], seed[2], 0.015 * w
    while True:
        inn = [b for b in L if b[2] >= x0 - gx and b[0] <= x1 + gx]
        if not inn: return None
        nx0, nx1 = min(b[0] for b in inn), max(b[2] for b in inn)
        if nx0 >= x0 and nx1 <= x1: break
        x0, x1 = min(x0, nx0), max(x1, nx1)
    return union(inn)

def edge_letters(mk, w, h, z, al):
    """LETTERS IN THE EDGE SHADOW (2026-10-26, خريدة القصر 064846139175 ص 231): a heading's first letters and the footnote
    numbers standing out past the verse into the paper's edge shadow were read as the sheet's edge (marks()' border zone) and
    the second look cut «وقوله», «(١)», «(٢)» at the box edge (the box had moved before only because the footnote rule crossed
    it — a hairline, no print since text_block). An edge mark is a letter of the page when it is print (printlike) and
    letter-sized (letterlike), centred in the allowed area (not the scanner band — خريدة القصر ص 649), and continues a line
    of print: on the row of a letter of the page (its centre within that letter's height, at most twice as tall) and
    within the gap that makes text (1.5 % of the width) of it or of another such edge letter"""
    L = [b for b in print_marks(mk.get('parts') or [], w, h, z) if letterlike(b, w, h)]   # (an upright hairline beside it:
    ok = lambda b: letterlike(b, w, h) and (printlike(b, w, h, z) or (b[3] - b[1] > b[2] - b[0] and hairline(b, z)))   # row())
    E = [b for b in mk.get('edge') or [] if ok(b) and (not al or (al[0] - 0.01 * w <= (b[0] + b[2]) / 2 <= al[2] + 0.01 * w
                                                                   and al[1] - 0.01 * h <= (b[1] + b[3]) / 2 <= al[3] + 0.01 * h))]
    gx, got = 0.015 * w, []
    row = lambda e, q: q[1] <= (e[1] + e[3]) / 2 <= q[3] and e[3] - e[1] <= 2 * (q[3] - q[1]) + 1
    while E:
        new = [e for e in E if any(e[0] <= q[2] + gx and e[2] >= q[0] - gx and row(e, q) for q in L + got)]
        if not new: break
        got += new; E = [e for e in E if e not in new]
    return got

def notes_of(margin, w, h):
    """MARGINAL NOTES (owner 2026-10-09, اللآلئ ج2 ص 40 «لعله الدارقطني»: «جميل، أبق مثل هذه الهوامش ولو اختلف الزوجي عن الفردي
    في موضع النص»): words a reader or the printer put beside the text. Among a page's marks outside its text block: the
    letter-sized ones (≥ 0.5 % of the page tall or ≥ 0.8 % of its width long, ≤ 6 % × 10 %), not in the sheet's outer 3 %,
    grouped when less than 2 % of the width apart; a group is a note when it has 3 such strokes or more, no more tiny
    specks than strokes inside its box (a smudge is a cloud of specks with a blot or two: اللآلئ ج2 ص 465), and spans
    2–30 % of the width and at most 25 % of the height. A single pen stroke, dots, smudges, stains and scan edges are not
    notes: they are cut like the rest of the margin. Returns the notes' boxes"""
    # (a dash of a scan line is not a stroke: ≤ 0.3 % thick and 3 times as long — owner 2026-10-14, مناقب الإمام أحمد ص 578: a
    # column of such dashes along the sheet's edge became a 0.6 pt wide «note», and the page was shrunk to keep it)
    L = [b for b in margin if not (b[2] <= 0.03 * w or b[0] >= 0.97 * w or b[3] <= 0.03 * h or b[1] >= 0.97 * h)
         and b[3] - b[1] <= 0.06 * h and b[2] - b[0] <= 0.10 * w and (b[3] - b[1] >= 0.005 * h or b[2] - b[0] >= 0.008 * w)
         and not (b[2] - b[0] <= 0.003 * w and b[3] - b[1] >= 3 * (b[2] - b[0])) and not (b[3] - b[1] <= 0.003 * h and b[2] - b[0] >= 3 * (b[3] - b[1]))]
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
        if len(S) >= 3 and tiny <= len(S) and max(bw, bh) >= 0.02 * w and min(bw, bh) >= 0.008 * w and bw <= 0.3 * w and bh <= 0.25 * h:
            out.append(box)
    return out

def cover_rect(page, px=360):
    """THE COVER ITSELF (owner 2026-10-14, دلائل الإعجاز ص 1: «اشمل الصفحة بالغلاف فقط»; معجم تيمور ص 1 «يمكن شملها
    بالغلاف»): a cover photographed on the scanner bed or set on a white sheet. Two ways to see it: (a) the region whose
    colour differs from the page's outer 3 % ring (≥ 45 on some channel) — a cover on a white sheet; (b) the region of the
    colour of the page's centre (within 55, holes filled), when that colour differs from the ring's (≥ 12) and is not
    paper's (light and grey) — a dark cloth cover on a dark scanner bed. The largest such region, trimmed to its solid rows and columns (≥ 60 % covered), is the
    cover when: it fills 25–97 % of the page; it is solid (≥ 85 % of its rectangle) and one piece (the trimming left ≤ 5 % of
    it out — a big logo or a block of letters trims down to a part of itself); and beside it lies only what reaches the
    sheet's edge (the scanner bed, a sheet under the cover) — ink standing free beside it is print (a title page with lines
    outside its frame). Returns the rectangle in pt, its sides moved in past a slanted or rounded edge (≤ 3 %), or None"""
    z = px / page.rect.width
    pix = page.get_pixmap(matrix=pymupdf.Matrix(z, z), colorspace=pymupdf.csRGB, alpha=False)
    a = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.stride)[:, :pix.width * 3].reshape(pix.height, pix.width, 3).astype(np.int16)
    H, W = a.shape[:2]; r = max(2, int(0.03 * min(H, W)))
    ring = np.concatenate([a[:r].reshape(-1, 3), a[-r:].reshape(-1, 3), a[:, :r].reshape(-1, 3), a[:, -r:].reshape(-1, 3)])
    bg = np.median(ring, axis=0)
    diff = ndimage.binary_closing(np.abs(a - bg).max(axis=2) >= 45, iterations=2)
    cands = [diff]
    cc = np.median(a[int(0.35 * H):int(0.65 * H), int(0.35 * W):int(0.65 * W)].reshape(-1, 3), axis=0)
    paperish = cc.min() >= 160 and cc.max() - cc.min() < 40     # a light, unsaturated centre is paper, not a cover
    if np.abs(cc - bg).max() >= 12 and not paperish:
        same = np.sqrt(((a - cc) ** 2).sum(axis=2)) <= 55
        cands.append(ndimage.binary_fill_holes(ndimage.binary_closing(same, iterations=3)))
    for mask in cands:
        lab, n = ndimage.label(mask)
        if n == 0: continue
        big = int(np.argmax(np.bincount(lab.ravel())[1:])) + 1
        m = lab == big; ys, xs = np.nonzero(m)
        y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        sub = m[y0:y1, x0:x1]
        rows = np.nonzero(sub.mean(1) >= 0.6)[0]; cols = np.nonzero(sub.mean(0) >= 0.6)[0]
        if len(rows) < 10 or len(cols) < 10: continue
        y0, y1, x0, x1 = y0 + rows[0], y0 + rows[-1] + 1, x0 + cols[0], x0 + cols[-1] + 1
        area = (y1 - y0) * (x1 - x0) / (H * W)
        if not 0.25 <= area <= 0.97 or m[y0:y1, x0:x1].mean() < 0.85: continue
        if m.sum() - m[y0:y1, x0:x1].sum() > 0.05 * m.sum(): continue
        out = diff.copy(); out[y0:y1, x0:x1] = False
        ol, k = ndimage.label(out)
        if k:
            border = set(np.unique(np.concatenate([ol[0], ol[-1], ol[:, 0], ol[:, -1]]))) - {0}
            sz = np.bincount(ol.ravel())                # print is many small marks; a sheet under the cover is one big piece
            small = [j for j in range(1, k + 1) if j not in border and sz[j] < 0.003 * H * W]
            if small and sz[small].sum() > 0.002 * H * W: continue
        y0_, y1_, x0_, x1_ = y0, y1, x0, x1
        # nothing from outside the cover may show, a hair of its edge may go (owner 2026-10-18, دلائل الإعجاز ص 1: «شيء من
        # خارج الغلاف ما زال ظاهرا بالأسفل … ولو نقص شيء لا يؤثر من حواف الغلاف»): each side moves in while its edge row
        # (column) is not wholly cover — a slanted or rounded edge — by at most 3 % of the cover; never a real cut into it
        # (فهرسة ابن خير ص 380 «دون قصّ صورة الغلاف»: the cover image is shown whole but for that hair)
        my, mx = int(0.03 * (y1 - y0)) + 1, int(0.03 * (x1 - x0)) + 1
        for _ in range(max(my, mx)):
            moved = False
            if y1 - y0 > 10 and m[y0, x0:x1].mean() < 0.98 and y0 < y0_ + my: y0 += 1; moved = True
            if y1 - y0 > 10 and m[y1 - 1, x0:x1].mean() < 0.98 and y1 > y1_ - my: y1 -= 1; moved = True
            if x1 - x0 > 10 and m[y0:y1, x0].mean() < 0.98 and x0 < x0_ + mx: x0 += 1; moved = True
            if x1 - x0 > 10 and m[y0:y1, x1 - 1].mean() < 0.98 and x1 > x1_ - mx: x1 -= 1; moved = True
            if not moved: break
        return [round(x0 / z, 2), round(y0 / z, 2), round(x1 / z, 2), round(y1 / z, 2)]
    return None

def cover_marks(page, rect, ppt=1.5):
    """THE COVER'S OWN PRINT (owner 2026-10-25, خزانة الأدب ج 1 ص 1: «cover is there but not filling the page, like incomplete
    measurements»; the fill that answered it cut the cover's last line, the year «١٣٨٧ = ١٩٦٧»): the marks that stand out
    from the cover's ground — lines of print, ornaments, a spine's lettering, labels — as boxes in pt, for cover_window.
    A mark: ≥ T on some channel from the mean of a 7-pt square, T following the ground's own grain (3 × its 75th
    percentile + 12, within 22–60: faint small print on a smooth cover, only real marks on cloth or leather); pieces under
    2.5 pt (grain, dust) and the cover's own edge (2 % — its hair, a shadow) left out"""
    pix = page.get_pixmap(matrix=pymupdf.Matrix(ppt, ppt), clip=pymupdf.Rect(rect), colorspace=pymupdf.csRGB, alpha=False)
    a = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.stride)[:, :pix.width * 3].reshape(pix.height, pix.width, 3).astype(np.float32)
    k = max(3, int(round(7 * ppt)) | 1)
    dev = np.abs(a - ndimage.uniform_filter(a, size=(k, k, 1))).max(axis=2)
    H, W = dev.shape; my, mx = int(0.02 * H) + 1, int(0.02 * W) + 1
    if H <= 2 * my + 2 or W <= 2 * mx + 2: return []
    T = float(np.clip(3 * np.percentile(dev[my:H - my, mx:W - mx], 75) + 12, 22, 60))
    e = dev >= T
    e[:my] = e[H - my:] = False; e[:, :mx] = e[:, W - mx:] = False
    lab, _ = ndimage.label(ndimage.binary_closing(e, structure=np.ones((3, 3)), iterations=1))
    out = []
    for sl in ndimage.find_objects(lab):
        if sl is None or max(sl[0].stop - sl[0].start, sl[1].stop - sl[1].start) < 2.5 * ppt: continue
        out.append([round(rect[0] + sl[1].start / ppt, 1), round(rect[1] + sl[0].start / ppt, 1),
                    round(rect[0] + sl[1].stop / ppt, 1), round(rect[1] + sl[0].stop / ppt, 1)])
    return out

def cover_window(c, A, mk):
    """the part of cover c shown at the book's proportion A (W ÷ H): the same cut at both ends (owner 2026-10-18, دلائل
    الإعجاز «ولو نقص شيء لا يؤثر من حواف الغلاف»), moved off the middle only to keep print the even cut would take, and
    only into plain ground: (a) a cut at the top and bottom keeps a line of print at one end whole (+ 3 pt) — marks across
    the cover's middle, ≥ 10 % of its width, centred within 15 % — when the other end is plain over its whole cut + 3 pt
    (خزانة الأدب ج 1: the year under the publisher); (b) a cut at the sides keeps a spine's lettering whole — marks ≥ 3 pt
    wide down ≥ 30 % of the height — when ≥ 40 % of the cover from the other side is plain (a back cover with its spine,
    روضة المستبين). Never for a hair (< 2 pt), never more than the cut: a frame on both sides, a corner logo, a library
    label or a speck leaves the cut even. mk: cover_marks"""
    cw, ch = c[2] - c[0], c[3] - c[1]
    vert = cw / ch < A                                  # too tall: cut at the top and bottom
    d = (ch - cw / A) / 2 if vert else (cw - ch * A) / 2
    lo, hi = (c[1], c[3]) if vert else (c[0], c[2])
    I0, I1 = (1, 3) if vert else (0, 2)
    move = 0.0
    if d > 1 and mk:
        for s in (-1, 1):                               # -1: keep what lies at lo, cut more at hi; +1: the reverse
            st = (lo, lo + d) if s < 0 else (hi - d, hi)
            lost = [m for m in mk if m[I1] > st[0] and m[I0] < st[1]]
            if vert:
                lost = [m for m in lost if m[2] > c[0] + 0.3 * cw and m[0] < c[2] - 0.3 * cw]
                if lost:
                    x0, x1 = min(m[0] for m in lost), max(m[2] for m in lost)
                    if x1 - x0 < 0.1 * cw or abs((x0 + x1) / 2 - (c[0] + c[2]) / 2) > 0.15 * cw: lost = []
            else:
                lost = [m for m in lost if m[2] - m[0] >= 3]
                if sum_spans([(m[1], m[3]) for m in lost]) < 0.3 * ch: lost = []
            if not lost: continue
            need = (lo + d - min(m[I0] for m in lost) + 3) if s < 0 else (max(m[I1] for m in lost) - (hi - d) + 3)
            if need < 2 or need - 3 > d: continue
            need = min(need, d)
            plain = (hi - max(m[I1] for m in mk)) if s < 0 else (min(m[I0] for m in mk) - lo)
            if plain < d + need + 3 or (not vert and plain < 0.4 * cw): continue
            move = s * need; break
    if vert: return [c[0], c[1] + d + move, c[2], c[3] - d + move]
    return [c[0] + d + move, c[1], c[2] - d + move, c[3]]

def sum_spans(iv):
    """the length covered by intervals [(a, b)] (overlaps counted once)"""
    tot, cur = 0.0, None
    for a, b in sorted(iv):
        if cur is None or a > cur[1]:
            if cur: tot += cur[1] - cur[0]
            cur = [a, b]
        else: cur[1] = max(cur[1], b)
    return tot + (cur[1] - cur[0] if cur else 0.0)

def sheet_rect(page, px=360):
    """A SHEET ON THE SCANNER BED (owner 2026-10-18, صبح الأعشى ج 5 ص 47: «المشكل نابع من عدم الجرأة على تجاوز سواد
    الطباعة»): a page photocopied grey lying on a lighter bed — the region darker than the midpoint between the sheet's
    paper (the centre's 70th percentile) and the bed (the outer 3 % ring), when the bed is lighter by ≥ 15, holes filled,
    the largest piece trimmed to its rows and columns ≥ 90 % covered, filling 40–97 % of the page and solid (≥ 90 %).
    Returns the rectangle 1.2 % inside its edges (the sheet's dark rims stay out), in pt, or None"""
    z = px / page.rect.width
    pix = page.get_pixmap(matrix=pymupdf.Matrix(z, z), colorspace=pymupdf.csGRAY, alpha=False)
    a = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.stride)[:, :pix.width].astype(float)
    H, W = a.shape; r = max(2, int(0.03 * min(H, W)))
    a = ndimage.uniform_filter(a, size=max(3, int(0.03 * W)))   # a black-and-white scan's toner speckle reads as its grey
    bed = float(np.median(np.concatenate([a[:r].ravel(), a[-r:].ravel(), a[:, :r].ravel(), a[:, -r:].ravel()])))
    # the sheet's own paper: its blank margins, between the text block and its edge — the ring 6–12 % in from the page's
    # edge, where a white page shows its white margin and a sheet on the bed shows its grey
    band = np.concatenate([a[int(0.06 * H):int(0.12 * H)].ravel(), a[int(0.88 * H):int(0.94 * H)].ravel(),
                           a[:, int(0.06 * W):int(0.12 * W)].ravel(), a[:, int(0.88 * W):int(0.94 * W)].ravel()])
    sheet = float(np.median(band))
    if bed - sheet < 6 or bed < 235: return None
    m = ndimage.binary_fill_holes(ndimage.binary_closing(a <= (bed + sheet) / 2, iterations=3))
    lab, n = ndimage.label(m)
    if n == 0: return None
    big = int(np.argmax(np.bincount(lab.ravel())[1:])) + 1; m = lab == big; ys, xs = np.nonzero(m)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    sub = m[y0:y1, x0:x1]; rows = np.nonzero(sub.mean(1) >= 0.9)[0]; cols = np.nonzero(sub.mean(0) >= 0.9)[0]
    if len(rows) < 10 or len(cols) < 10: return None
    y0, y1, x0, x1 = y0 + rows[0], y0 + rows[-1] + 1, x0 + cols[0], x0 + cols[-1] + 1
    if not 0.40 <= (y1 - y0) * (x1 - x0) / (H * W) <= 0.90 or m[y0:y1, x0:x1].mean() < 0.9: return None
    dx, dy = 0.012 * W, 0.012 * H
    return [round((x0 + dx) / z, 2), round((y0 + dy) / z, 2), round((x1 - dx) / z, 2), round((y1 - dy) / z, 2)]

def banded(al, w, h):
    """scanner bands at a side of the page: the area inside them (al, pt) falls short of the page's edge by > 1 %"""
    return bool(al) and (al[0] > 0.01 * w or al[1] > 0.01 * h or al[2] < 0.99 * w or al[3] < 0.99 * h)

def ink_ratio(mk0, mk1, z, al0=None, al1=None):
    """the turned page's content ink (mk1) over the page's own (mk0), both measured at z pixels per pt — a turn must not lose
    the page's print. With scanner bands, both are counted inside the area within them (al0; al1 = that area turned): once
    turned, the bands slant, are no longer read as bands and count as ink (2026-10-25, خريدة القصر ص 375: a 1.7° tilt left
    as it was — the turned page showed 6× the ink; 13 pages of that volume)"""
    def n(mk, al):
        if al is None: return len(mk['xy'][0])
        x, y = mk['xy']; ox, oy = mk.get('xy0') or (0, 0); x, y = x + ox, y + oy
        return int(((x >= al[0] * z) & (x <= al[2] * z) & (y >= al[1] * z) & (y <= al[3] * z)).sum())
    return n(mk1, al1) / max(1, n(mk0, al0))

def whiten(a, z, rect):
    """the gray image with everything outside rect (pt) set to white: what lies beyond a sheet's edge is not measured"""
    if not rect: return a
    b = np.full_like(a, 255); x0, y0, x1, y1 = [int(round(v * z)) for v in rect]
    b[max(0, y0):max(0, y1), max(0, x0):max(0, x1)] = a[max(0, y0):max(0, y1), max(0, x0):max(0, x1)]
    return b

def dot_fields(page, a500=None):
    """A SHADOW PRINTED AS DOTS ON A BITONAL SCAN (owner 2026-10-18, صبح الأعشى ج 5 ص 47: «عدم الجرأة على تجاوز سواد
    الطباعة», then «لا جديد فيها»): a 1-bit scanner renders the grey of a photocopy's edge, a sheet's shadow or a curled
    corner as a field of loose dots; measured at a lower resolution they merge into blots and «text» that held the frame
    out to the sheet's edge (and a false page number at its foot). At the scan's own resolution (≤ 300 dpi): a stroke is a
    mark of ≥ 0.85 × 0.85 pt of ink, the rest are dots; a 2-pt tile is in a field when dots cover ≥ 1.5 % of the 6 × 6 pt
    around it and no stroke lies within 4 pt of it (a letter's own dots and vowels are nearer than that); a field is kept
    when it is a field, not a dotted line (as thick as 4 tiles on average), and reaches beyond the text block (a dotted
    rule or a grey mark between the lines stays). → rectangles in the page's own coordinates: left out of every measure
    (like a stamp) and covered with the paper's white inside the frame (marks_to_erase). Greyscale and colour scans have
    none (their shadows are grey, not dots)"""
    info = [x for x in page.get_image_info() if x.get('bpc') == 1]
    ar = lambda x: abs((x['bbox'][2] - x['bbox'][0]) * (x['bbox'][3] - x['bbox'][1]))
    if not info or sum(ar(x) for x in info) < 0.5 * page.rect.width * page.rect.height: return []
    # a quick look first, on the page 500 px wide as the first look renders it (a500): dots show there as faint grey away
    # from any letter — clean pages hold 200–1,500 such pixels, shaded ones 3,000–10,000 (صبح الأعشى ج 5): 0.6 s a page saved
    if a500 is not None:
        fz = (a500 >= 170) & (a500 <= 245) & ~ndimage.binary_dilation(a500 < 150, iterations=3)
        if int(fz.sum()) < 2000: return []
    z = min(max(max((x['width'] * x['height'] / max(1e-6, ar(x))) ** 0.5 for x in info), 2.0), 300 / 72)
    pix = page.get_pixmap(matrix=pymupdf.Matrix(z, z), colorspace=pymupdf.csGRAY, alpha=False)
    b = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.stride)[:, :pix.width] < 128
    lab, n = ndimage.label(b)                        # (4-connected: dots touching at a corner stay apart)
    if n == 0: return []
    big = np.bincount(lab.ravel()) >= max(12, int((0.85 * z) ** 2)); big[0] = False
    stroke = big[lab]; dot = b & ~stroke; del lab
    T = max(2, int(round(2 * z))); Hh, Ww = (b.shape[0] // T) * T, (b.shape[1] // T) * T
    tiles = lambda m: m[:Hh, :Ww].reshape(Hh // T, T, Ww // T, T).sum((1, 3))
    dt = tiles(dot).astype(np.float32) / (T * T); st = tiles(stroke) > 0
    if not st.any(): return []
    ys, xs = np.nonzero(st)
    tx0, tx1, ty0, ty1 = np.percentile(xs, 1), np.percentile(xs, 99), np.percentile(ys, 1), np.percentile(ys, 99)
    field = (ndimage.uniform_filter(dt, 3) >= 0.015) & ~ndimage.binary_dilation(st, iterations=2)
    fl, fn = ndimage.label(field, structure=np.ones((3, 3), bool))
    if fn == 0: return []
    keep = np.zeros(fn + 1, bool)
    for k, s in enumerate(ndimage.find_objects(fl), 1):
        m_ = fl[s] == k; size = int(m_.sum())
        if size < 8 or size < 4 * max(s[0].stop - s[0].start, s[1].stop - s[1].start): continue
        yy, xx = np.nonzero(m_); yy, xx = yy + s[0].start, xx + s[1].start
        keep[k] = bool(((xx < tx0 - 2) | (xx > tx1 + 2) | (yy < ty0 - 2) | (yy > ty1 + 2)).any())
    field = keep[fl]
    out, used = [], np.zeros_like(field)              # rectangles: a run of tiles grown down while the rows below hold it
    for y in np.nonzero(field.any(1))[0]:
        d = np.diff(np.concatenate([[0], (field[y] & ~used[y]).astype(np.int8), [0]]))
        for x0, x1 in zip(np.nonzero(d == 1)[0], np.nonzero(d == -1)[0]):
            y1 = y + 1
            while y1 < field.shape[0] and field[y1, x0:x1].all() and not used[y1, x0:x1].any(): y1 += 1
            used[y:y1, x0:x1] = True
            out.append([round(x0 * T / z, 1), round(y * T / z, 1), round(x1 * T / z, 1), round(y1 * T / z, 1)])
    return out

def fwd_boxes(doc, i, p, bs):
    """fwd_box for many boxes at once (the dot fields of a page: hundreds)"""
    mv = p.get('move') or [0, 0]; deg = p.get('skew') or 0
    if not deg and not any(mv): return list(bs)
    page = doc[i]; tm = page.transformation_matrix; mb = raw_box(doc, page.xref, 'MediaBox'); cx, cy = (mb[0] + mb[2]) / 2, (mb[1] + mb[3]) / 2
    m = ~tm * (pymupdf.Matrix(1, 0, 0, 1, -cx, -cy) * pymupdf.Matrix(deg) * pymupdf.Matrix(1, 0, 0, 1, cx, cy) * pymupdf.Matrix(1, 0, 0, 1, mv[0], -mv[1])) * tm
    out = []
    for b in bs:
        pts = [pymupdf.Point(x, y) * m for x, y in ((b[0], b[1]), (b[2], b[1]), (b[2], b[3]), (b[0], b[3]))]
        out.append([min(q.x for q in pts), min(q.y for q in pts), max(q.x for q in pts), max(q.y for q in pts)])
    return out

def proj_signed(a, paper, lo=-4.0, hi=4.0, step=0.25, width=800, need=None):
    """THE THIRD TILT MEASURE (owner 2026-10-18: طبقات الفقهاء «الأول فيه ميل», «الثالث والرابع مائلان» — pages 1.5–2.9°
    tilted that the shear measure read level, its halves disagreeing): the page image turned by each angle, the sharpness of
    its ink-row profile (the classic deskew); signed — the angle IS the turn (as rec['skew']). Returns (angle, sharpness:
    the best profile over the median one); with `need`, (None, None) as soon as the coarse peak shows the angle stays below
    it (the fine search keeps within one step of that peak — 2026-10-25, speed: most pages peak at 0°)"""
    from PIL import Image
    im = Image.fromarray(a)
    if im.width > width: im = im.resize((width, max(1, round(im.height * width / im.width))), Image.BILINEAR)
    w, h = im.size; box = (int(w * .08), int(h * .05), int(w * .92), int(h * .95)); thr = max(60, min(200, paper - 50))
    sc = lambda t: float(np.var((np.asarray(im.rotate(float(t), resample=Image.BILINEAR, fillcolor=255).crop(box)) < thr).sum(1)))
    angs = np.arange(lo, hi + 1e-9, step); s = [sc(t) for t in angs]; k = int(np.argmax(s))
    if need is not None and abs(float(angs[k])) + step < need - 1e-6: return None, None
    fine = np.arange(angs[k] - step, angs[k] + step + 1e-9, 0.025); f = [sc(t) for t in fine]; j = int(np.argmax(f))
    return round(float(fine[j]), 3), round(max(f) / max(1e-9, float(np.median(s))), 2)

def by_proj(a, mk, ang, gain, rec):
    """a page the shear measure leaves level (its halves disagree, or it reads nothing) whose text lines line up sharply at
    an angle ≥ 0.3° (sharpness ≥ 1.5): that angle is its turn; the turn is kept only if the turned page then reads ≤ 0.2°
    by the same measure (checked where it is turned)"""
    if abs(ang) >= SKEW_MIN or mk.get('dark', 1) > 0.35: return ang, gain
    t, sh_ = proj_signed(a, mk.get('paper') or 255, need=0.3)
    if t is not None and abs(t) >= 0.3 and sh_ >= 1.5:
        # a long straight printed rule over the text block that reads level (≤ 0.2°): the page is level — the projection
        # was fooled by the layout (columns of short lines). A scanner's or a sheet's line is not over the text block
        tb = mk.get('text') or mk.get('box')
        if tb and any(abs(h[0]) <= 0.2 and h[1] >= tb[0] - 0.02 * (tb[2] - tb[0]) and h[3] <= tb[2] + 0.02 * (tb[2] - tb[0])
                      and h[2] >= tb[1] - 0.03 * (tb[3] - tb[1]) and h[4] <= tb[3] + 0.03 * (tb[3] - tb[1]) for h in mk.get('hrules') or []):
            rec['proj_level_rule'] = round(t, 2); return ang, gain
        rec['tilt_by_proj'] = t; return t, 1.1
    return ang, gain

def by_rules(mk, ang, gain, rec):
    """a page left level by the halves' test (an index: its halves read differently) that holds long straight rules all
    leaning one way (≥ 0.4°): the whole page's own reading, when it agrees with them (within 0.6°), is its tilt (owner
    2026-10-18, خريدة القصر ص 649)"""
    rt = mk.get('rule_tilts') or []
    if abs(ang) >= SKEW_MIN or len(rt) < 2 or mk.get('xy') is None: return ang, gain
    md = float(np.median(rt))
    if abs(md) < 0.4 or not all(np.sign(t) == np.sign(md) for t in rt): return ang, gain
    r_, g_ = skew_of(mk['xy'], raw=True)
    if abs(r_ - md) <= 0.6 and g_ >= 1.02: rec['tilt_by_rules'] = round(md, 2); return r_, g_
    return ang, gain

def colour_stamps(page, px=500):
    """A COLOURED STAMP ON A PAGE PRINTED IN BLACK (owner 2026-10-14, خزانة الأدب ص 18: «لم تزل الطابع في الأولى لتحصل على
    نفس التكبير في غيرها» — a purple «dar-alkotob» octagon above the text): ink of a clear colour (channels differing by ≥ 60);
    its groups (marks within 0.5 % of the width) at least 3 % of the width or 2 % of the height, lying wholly outside the
    black text's extent (2–98 % of the grey ink, rows or columns) — above, below or beside it. A coloured heading or word
    inside the text column stays, and a page printed mostly in colour (coloured ink > 30 % of all ink) is left alone.
    Left out of every measure like an uploader's stamp. Returns their boxes (pt)"""
    z = px / page.rect.width
    pix = page.get_pixmap(matrix=pymupdf.Matrix(z, z), colorspace=pymupdf.csRGB, alpha=False)
    if pix.n < 3: return []
    a = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.stride)[:, :pix.width * 3].reshape(pix.height, pix.width, 3).astype(np.int16)
    g = a.mean(axis=2); paper = float(np.percentile(g, 90))
    if paper < 150: return []
    ink = g < paper - 40; sat = (a.max(axis=2) - a.min(axis=2)) >= 60
    col = ink & sat; black = ink & ~sat; ni = int(ink.sum())
    if ni == 0 or col.sum() == 0 or col.sum() > 0.30 * ni or black.sum() < 200: return []
    H, W = g.shape
    lab, k = ndimage.label(ndimage.binary_dilation(col, iterations=max(1, int(0.005 * W))))
    groups = ndimage.find_objects(lab)
    bl = black.copy(); e = int(0.01 * W)             # the stamp's own black lettering is not the page's text
    for sl in groups: bl[max(0, sl[0].start - e):sl[0].stop + e, max(0, sl[1].start - e):sl[1].stop + e] = False
    if bl.sum() < 200: return []
    by, bx = np.nonzero(bl)
    y0, y1 = np.percentile(by, [2, 98]); x0, x1 = np.percentile(bx, [2, 98])
    out = []
    for sl in groups:
        h_, w_ = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
        if not (w_ >= 0.03 * W or h_ >= 0.02 * H): continue
        if sl[0].stop <= y0 or sl[0].start >= y1 or sl[1].stop <= x0 or sl[1].start >= x1:
            e_ = 0.015 * W                           # its faint, anti-aliased edge too (خزانة الأدب ج 2 ص 18: a corner was left)
            out.append([round(max(0, sl[1].start - e_) / z, 1), round(max(0, sl[0].start - e_) / z, 1),
                        round(min(W, sl[1].stop + e_) / z, 1), round(min(H, sl[0].stop + e_) / z, 1)])
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
        if i < 2 or i >= doc.page_count - 2:              # the first and last two pages: a cover is shown alone, whole
            cv = cover_rect(page)
            if cv: rec.update(kind='cover', cover=cv, box=cv, cover_marks=cover_marks(page, cv)); pages.append(rec); done[i] = rec; continue
        st = list(stamps.get(i) or stamps.get(str(i)) or [])
        cs = colour_stamps(page)                       # a coloured stamp on a page printed in black: left out like the others
        if cs: st += cs; rec['colour_stamp'] = cs
        if st: rec['stamp'] = st
        ex0 = [pad_box(b, r.width) for b in st] if st else None
        a, z = gray(page, 500)
        dots = dot_fields(page, a)                    # a shadow printed as dots (bitonal scans): not measured, covered later
        if dots: rec['dots'] = dots; ex0 = (ex0 or []) + dots
        sh = sheet_rect(page)                         # a grey sheet on a light bed: measured inside its edges
        if sh: rec['sheet'] = sh; rec['sheet_fill'] = sh   # (kept to fill beyond its edge even if not used for measuring)
        a = whiten(a, z, sh)
        mk = marks(a, z, r.width, ex0)
        if sh and mk.get('text') and not inside([mk['text'][0] - 0.01 * r.width, mk['text'][1] - 0.01 * r.height,
                                                mk['text'][2] + 0.01 * r.width, mk['text'][3] + 0.01 * r.height], sh):
            rec.pop('sheet', None); sh = None              # its text reaches the «sheet's» edge: no sheet — measured whole
            a, z = gray(page, 500); mk = marks(a, z, r.width, ex0)
        if sh and mk.get('allowed'): mk['allowed'] = [max(mk['allowed'][0], sh[0]), max(mk['allowed'][1], sh[1]), min(mk['allowed'][2], sh[2]), min(mk['allowed'][3], sh[3])]
        tu_ = []                                       # (the page turned for several angles: one Turner)
        tu = lambda: tu_[0] if tu_ else (tu_.append(Turner(doc, i)) or tu_[0])
        if mk['box'] is not None and mk['dark'] <= 0.35:     # a tilted text page: turn it level (the sign is checked)
            al0 = mk.get('allowed')                      # (its scanner bands, read before the turn: a turned image's
            ang, gain = skew_of(mk['xy'])                #  blank corners hide them)
            if 0.1 <= abs(ang) < 0.35:                   # small: measure again at twice the resolution
                a2, z2 = gray(page, 1000); ang, gain = skew_of(marks(whiten(a2, z2, sh), z2, r.width, ex0)['xy'])
            ang, gain = by_rules(mk, ang, gain, rec)
            ang, gain = by_proj(a, mk, ang, gain, rec)
            # a page whose printed frame or rule stands level while its content reads ≥ 1° (a photographed leaf in a
            # level frame: owner 2026-10-14, روضة المستبين ص 138 «أحدثت ميلا»): not turned — a 1° tilt would have kept
            # the rule from showing as one (it drifts beyond its 1 % band over half the page)
            if abs(ang) >= 1.0 and mk.get('level_frame'):
                rec['frame_level'] = round(ang, 3); ang = 0.0; rec.pop('tilt_by_proj', None)
            if rec.get('tilt_by_proj') is not None:      # a projection turn: angles around its reading (it is coarse), the
                best = None                              # one after which the page reads level by its own ink is kept
                for k in list(range(-5, 6)):
                    deg = round(rec['tilt_by_proj'] + 0.2 * k, 3)
                    if deg * rec['tilt_by_proj'] <= 0: continue
                    a2, z2 = gray(tu().page(deg), 500); a2 = whiten(a2, z2, fwd_box(doc, i, {'skew': deg}, sh) if sh else None)
                    mk2 = marks(a2, z2, r.width, fwd_boxes(doc, i, {'skew': deg}, ex0) if ex0 else None)
                    if mk2['box'] is None or mk2['xy'] is None: continue
                    lv = abs(skew_of(mk2['xy'], raw=True)[0])
                    if best is None or lv < best[0]: best = (lv, deg, mk2)
                if best:                                 # then ± 0.1° around the best
                    for deg in (round(best[1] - 0.1, 3), round(best[1] + 0.1, 3)):
                        a2, z2 = gray(tu().page(deg), 500); a2 = whiten(a2, z2, fwd_box(doc, i, {'skew': deg}, sh) if sh else None)
                        mk2 = marks(a2, z2, r.width, fwd_boxes(doc, i, {'skew': deg}, ex0) if ex0 else None)
                        if mk2['box'] is None or mk2['xy'] is None: continue
                        lv = abs(skew_of(mk2['xy'], raw=True)[0])
                        if lv < best[0]: best = (lv, deg, mk2)
                if best and best[0] <= 0.2: rec['skew'] = best[1]; mk = best[2]
                ang = 0.0                                # (the generic loop below is not run for it)
            if abs(ang) >= SKEW_MIN and gain >= 1.02:
                for deg in (-ang, ang):
                    a2, z2 = gray(tu().page(deg), 500); a2 = whiten(a2, z2, fwd_box(doc, i, {'skew': deg}, sh) if sh else None)
                    mk2 = marks(a2, z2, r.width, fwd_boxes(doc, i, {'skew': deg}, ex0) if ex0 else None)
                    # the turned page must still show the page's ink (a broken drawing would show none); its text block is
                    # naturally narrower once level, so its size is not compared; MORE ink once level is no fault — a
                    # table's slanted rules count as print only when straight (خريدة القصر ص 649: ×3.5, the turn refused);
                    # with scanner bands, counted inside them (ink_ratio)
                    bd = banded(al0, r.width, r.height)
                    if mk2['box'] is None or mk2['xy'] is None or not (0.6 <= ink_ratio(mk, mk2, z2, al0 if bd else None,
                                                                                         fwd_inner(doc, i, {'skew': deg}, al0) if bd else None) <= 5.0):
                        continue
                    left, _ = skew_of(mk2['xy'], raw=True)   # the plain whole-page angle must now read level
                    if abs(left) <= max(0.1, abs(ang) / 3):
                        rec['skew'] = round(deg, 3); mk = mk2
                        if al0 and mk.get('allowed'):
                            a_ = fwd_inner(doc, i, {'skew': deg}, al0)
                            mk['allowed'] = [max(mk['allowed'][0], a_[0]), max(mk['allowed'][1], a_[1]), min(mk['allowed'][2], a_[2]), min(mk['allowed'][3], a_[3])]
                        break
        if tu_: tu_[0].close()
        mk.pop('xy', None); mk.pop('parts', None)
        if sh and mk.get('allowed'):                   # (the sheet's edges bound the box, on the turned page too)
            sh_ = fwd_box(doc, i, {'skew': rec.get('skew') or 0}, sh)
            mk['allowed'] = [max(mk['allowed'][0], sh_[0]), max(mk['allowed'][1], sh_[1]), min(mk['allowed'][2], sh_[2]), min(mk['allowed'][3], sh_[3])]
        rec.update(allowed=mk['allowed'], specks=mk['specks'], blots=mk['blots'], edge=mk['edge'], core=mk['core'], paper=round(mk.get('paper', 0)),
                   rules=mk.get('rules', []), lines=mk.get('lines', []), text=mk.get('text'), margin=mk.get('margin', []), folio=mk.get('folio'))
        if mk['box'] is None: rec['kind'] = 'blank' if mk['dark'] < 0.5 else 'picture'
        elif mk['dark'] > 0.35: rec['kind'] = 'picture'   # dark pages only: a tight light scan is text (stays whole if it cannot fit)
        else: rec['kind'] = 'text'
        rec['box'] = mk['box']
        if rec['kind'] == 'picture' and (i < 2 or i >= doc.page_count - 4):   # the book's own cover, shown whole-page
            rec['cover_marks'] = cover_marks(page, [0.0, 0.0, r.width, r.height])   # (frames): where its print lies
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

def fwd_inner(doc, i, p, b):
    """like fwd_box, but the largest upright rectangle inside the turned box (a limit, not an extent)"""
    page = doc[i]; mv = p.get('move') or [0, 0]; deg = p.get('skew') or 0
    if not deg and not any(mv): return b
    tm = page.transformation_matrix; mb = raw_box(doc, page.xref, 'MediaBox'); cx, cy = (mb[0] + mb[2]) / 2, (mb[1] + mb[3]) / 2
    fwd = pymupdf.Matrix(1, 0, 0, 1, -cx, -cy) * pymupdf.Matrix(deg) * pymupdf.Matrix(1, 0, 0, 1, cx, cy) * pymupdf.Matrix(1, 0, 0, 1, mv[0], -mv[1])
    m = ~tm * fwd * tm
    tl, tr, br, bl = [pymupdf.Point(x, y) * m for x, y in ((b[0], b[1]), (b[2], b[1]), (b[2], b[3]), (b[0], b[3]))]
    return [max(tl.x, bl.x), max(tl.y, tr.y), min(tr.x, br.x), min(bl.y, br.y)]

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
    Returns {page index: [boxes (pt)]}
    (MEMORY, 2026-10-25: every group of ink is a candidate — a word, at 400 px — and its two small images used to be kept
    for all of them: 3.6 GB for a book of 1,531 pages, the memory brake twice. Now only a candidate a test reads keeps
    them: the band candidates both, a foot-corner candidate its grey image; the grey image of any other candidate is made
    again, page by page, only when a stamp was found and the candidate has its proportions — the same result)"""
    doc = pymupdf.open(path); n = doc.page_count; doc.close()
    idx = list(range(n)); found = []
    if jobs > 1:
        with ProcessPoolExecutor(jobs) as ex:
            for part in ex.map(_stamp_chunk, [(path, idx[k::jobs], px) for k in range(jobs)]): found += part
    else: found = _stamp_chunk((path, idx, px))
    out = corner_signatures(found)
    band = [f for f in found if f[6]]
    if not band: return out
    C = np.array([[f[1][0], f[1][1], f[1][2], f[1][3], f[2], f[3]] for f in band], float)
    cxs, cys = (C[:, 0] + C[:, 2]) / 2, (C[:, 1] + C[:, 3]) / 2; bw, bh = C[:, 2] - C[:, 0], C[:, 3] - C[:, 1]
    T = np.array([f[4] for f in band], float); pg = np.array([f[0] for f in band])
    used, refs = np.zeros(len(band), bool), []
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
    want = {}                                         # the candidates of a stamp's proportions without their grey image
    for f in found:
        b = f[1]; w_, h_ = b[2] - b[0], b[3] - b[1]
        if f[5] is None and any(abs((w_ / max(h_, 1e-6)) / asp - 1) <= 0.15 and w_ >= 0.8 * sw for _, asp, sw in refs):
            want.setdefault(f[0], {})[f[7]] = b
    if want:
        gs, pgs = {}, sorted(want)
        if jobs > 1:
            with ProcessPoolExecutor(jobs) as ex:
                for part in ex.map(_stamp_more, [(path, {q: want[q] for q in pgs[k::jobs]}, px) for k in range(jobs)]): gs.update(part)
        else: gs = _stamp_more((path, want, px))
        found = [f[:5] + (gs[(f[0], f[7])],) + f[6:] if (f[0], f[7]) in gs else f for f in found]
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

def corner_signatures(found):
    """A SIGNATURE IN A FOOT CORNER (owner 2026-10-14, روضة المستبين ج 1 ص 16: «أزل الطابع في 1 لتتسق الصفحات كلها» — an
    uploader's calligraphic signature at the foot of pages 8–18, about 13 % of the page tall, a little off from page to
    page: too tall, too rare and too unsteady for the footer rule of stamps_of): the same picture (grey image correlation
    ≥ 0.8, size ± 10 %) in the bottom 30 % of the page and its outer 30 % on either side, 5–25 % of the width wide and
    4–20 % of the height tall, on at least 4 pages. A printed ornament repeats too, but at a chapter's head (روضة المستبين's
    arches, left alone) or as a frame's corners — the same piece at the mirrored corner of the same page (روضة المستبين
    ص 17، 49، 63، 97: a chapter page's frame): a group with such a twin on half its pages is print, not a signature.
    `found`: _stamp_chunk's candidates → {page index: [boxes (pt)]}"""
    corner = lambda f: in_corner(f[1], f[2], f[3])
    def twin(f, page):                                # the same size at the mirrored place of its page
        b, W, H = f[1], f[2], f[3]; w, h = b[2] - b[0], b[3] - b[1]; mx, cy = W - (b[0] + b[2]) / 2, (b[1] + b[3]) / 2
        return any(abs((c[1][0] + c[1][2]) / 2 - mx) <= 0.03 * W and abs((c[1][1] + c[1][3]) / 2 - cy) <= 0.03 * H
                   and abs((c[1][2] - c[1][0]) / w - 1) <= 0.15 and abs((c[1][3] - c[1][1]) / h - 1) <= 0.15 for c in page)
    cand = [f for f in found if corner(f)]; used = [False] * len(cand); out = {}
    on = {}
    for f in cand: on.setdefault(f[0], []).append(f)
    for k, fk in enumerate(cand):
        if used[k]: continue
        wk, hk = fk[1][2] - fk[1][0], fk[1][3] - fk[1][1]
        grp = [j for j, f in enumerate(cand) if not used[j] and abs((f[1][2] - f[1][0]) / wk - 1) <= 0.1
               and abs((f[1][3] - f[1][1]) / hk - 1) <= 0.1 and float((fk[5] * f[5]).mean()) >= 0.8]
        for j in grp: used[j] = True
        if len({cand[j][0] for j in grp}) < 4 or sum(twin(cand[j], on[cand[j][0]]) for j in grp) >= 0.5 * len(grp): continue
        for j in grp: out.setdefault(cand[j][0], []).append([round(float(v), 1) for v in cand[j][1]])
    return out

def in_corner(b, W, H):
    """a candidate for a signature in a foot corner (corner_signatures): its box b (pt) on a page W × H (pt)"""
    w, h = b[2] - b[0], b[3] - b[1]; cx, cy = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2
    return 0.05 * W <= w <= 0.25 * W and 0.04 * H <= h <= 0.2 * H and (cx <= 0.3 * W or cx >= 0.7 * W) and cy >= 0.7 * H

def _stamp_groups(page, px):
    """the groups of ink of one page that may be a stamp (stamps_of), in order: (number, box (pt), band, ink mask)"""
    a, z = gray(page, px); paper = float(np.percentile(a, 90))
    if paper < 150: return []
    m = a < paper - 50; H, W = m.shape; out = []
    lab, k = ndimage.label(ndimage.binary_dilation(m, iterations=max(1, int(0.003 * W))))
    for j, s in enumerate(ndimage.find_objects(lab), 1):
        y0, y1, x0, x1 = s[0].start, s[0].stop, s[1].start, s[1].stop
        if not (0.03 * W <= x1 - x0 <= 0.45 * W and 0.008 * H <= y1 - y0 <= 0.2 * H): continue
        band = (y1 <= 0.12 * H or y0 >= 0.82 * H) and x1 - x0 <= 0.35 * W and y1 - y0 <= 0.08 * H and abs((x0 + x1) / 2 - W / 2) >= 0.12 * W
        out.append((j, (x0 / z, y0 / z, x1 / z, y1 / z), band, m[y0:y1, x0:x1] & (lab[y0:y1, x0:x1] == j)))
    return out

def _stamp_shape(ink):
    """a group's shape, scaled to 48 × 16 (the band rule compares shapes)"""
    from PIL import Image
    return np.asarray(Image.fromarray(ink.astype(np.uint8) * 255).resize((48, 16), Image.BILINEAR), np.float32) / 255

def _stamp_grey(ink):
    """a group's grey image, 64 × 36, blurred and normalised (correlated with a stamp's)"""
    from PIL import Image, ImageFilter
    g = np.asarray(Image.fromarray(ink.astype(np.uint8) * 255).resize((64, 36), Image.BOX).filter(ImageFilter.GaussianBlur(1.2)), np.float32)
    return (g - g.mean()) / (g.std() + 1e-6)

def _stamp_chunk(args):
    """the candidates of some pages: (page, box, page width, height, shape (band only), grey image (band and foot
    corner only), band, number on its page)"""
    path, idx, px = args
    doc = pymupdf.open(path); out = []
    for i in idx:
        page = doc[i]
        if page.rotation: continue
        W, H = page.rect.width, page.rect.height
        for j, b, band, ink in _stamp_groups(page, px):
            out.append((i, b, W, H, _stamp_shape(ink) if band else None, _stamp_grey(ink) if band or in_corner(b, W, H) else None, band, j))
    doc.close()
    return out

def _stamp_more(args):
    """the grey images of chosen candidates, made again from their pages: {page: {number: box}} → {(page, number): grey}"""
    path, want, px = args
    doc = pymupdf.open(path); out = {}
    for i in sorted(want):
        for j, b, band, ink in _stamp_groups(doc[i], px):
            if j in want[i]:
                if b != want[i][j]: raise RuntimeError(f'stamps_of: page {i + 1} read differently the second time')
                out[(i, j)] = _stamp_grey(ink)
    doc.close()
    return out

def spread_gutters(doc, px=500):
    """TWO BOOK PAGES ON ONE SHEET (owner 2026-10-14, طبقات الفقهاء للشيرازي: «لماذا لم تحاول تقسيم الصفحات المزدوجة؟»; plan
    320: «every 2 pages divided»): for each sheet wider than 1.15 × its height, the gutter between its two pages — the
    longest run of columns between 35 % and 65 % of the width where letters (marks ≤ 4 % tall and ≤ 5 % wide: not the binding's
    shadow, not a rule) leave at most 5 % of their fullest column's ink, rows 10–90 %. A sheet without such a run is not split
    (a map, a table across the sheet). Returns {page index: gutter x (pt, page coordinates)}"""
    out = {}
    for i, page in enumerate(doc):
        r = page.rect
        if page.rotation or r.width <= 1.15 * r.height: continue
        a, z = gray(page, px); paper = float(np.percentile(a, 90))
        if paper < 110: continue
        m = a < paper - 50; H, W = m.shape
        lab, n = ndimage.label(m, structure=np.ones((3, 3), bool))
        if n == 0: continue
        objs = ndimage.find_objects(lab)
        ok = np.zeros(n + 1, bool)
        for k, sl in enumerate(objs, 1):
            hh, ww = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
            ok[k] = hh <= 0.04 * H and ww <= 0.05 * W
        letters = ok[lab]
        prof = ndimage.uniform_filter1d(letters[int(0.1 * H):int(0.9 * H)].sum(0).astype(float), max(3, int(0.01 * W)))
        if prof.max() <= 0: continue
        lo, hi = int(0.35 * W), int(0.65 * W); low = prof[lo:hi] <= 0.05 * prof.max()
        best, run = None, None
        for x in range(len(low) + 1):
            if x < len(low) and low[x]: run = x if run is None else run
            elif run is not None:
                if best is None or x - run > best[1] - best[0]: best = (run, x)
                run = None
        if best and best[1] - best[0] >= 0.005 * W:
            out[i] = round(((lo + (best[0] + best[1]) / 2) / z), 2)
    return out

def split_pages(doc, split):
    """each sheet of `split` ({index: gutter x}) becomes two pages — its right-hand page first (Arabic), then its left —
    the same page content shown through two CropBoxes (fullcopy_page: the images are shared, never copied). In place"""
    for i in sorted((int(k) for k in split), reverse=True):
        g = float(split[str(i)] if str(i) in split else split[i])
        page = doc[i]; inv = ~page.transformation_matrix
        cb = raw_box(doc, page.xref, 'CropBox') or raw_box(doc, page.xref, 'MediaBox')   # the file's own values
        a, b = pymupdf.Point(g, 0) * inv, pymupdf.Point(g, page.rect.height) * inv
        gx = (a.x + b.x) / 2                         # the gutter in the page's own (PDF) coordinates
        doc.fullcopy_page(i, i + 1 if i + 1 < doc.page_count else -1)   # (-1: after the last page)
        doc.xref_set_key(doc[i].xref, 'CropBox', f'[{gx:.2f} {cb[1]:.2f} {cb[2]:.2f} {cb[3]:.2f}]')
        doc.xref_set_key(doc[i + 1].xref, 'CropBox', f'[{cb[0]:.2f} {cb[1]:.2f} {gx:.2f} {cb[3]:.2f}]')

def split_open(src, rec):
    """the book as the method sees it: split first when the recipe says so (in memory)"""
    doc = pymupdf.open(src)
    if rec.get('split'): split_pages(doc, rec['split'])
    return doc

def analyse(path):
    """kept for the old callers: the measured pages and the decision at the narrowest box"""
    return decide(analyse_pages(path))

def plan(path, jobs=1, owner_turns=None):
    """the whole method: measure every page once, then the narrowest box that works — the width of 95 % of the pages,
    else 98 %, else all; each tried with the second check (a book is cropped only if few pages stay whole).
    owner_turns: {page (1-based, as in the recipe): |tilt|} — pages the owner ruled «turn» (verify)"""
    import copy, shutil
    d = pymupdf.open(path); n0 = d.page_count
    spreads = n0 and sum(1 for pg in d if not pg.rotation and pg.rect.width > 1.15 * pg.rect.height) >= 0.5 * n0
    # a WRAP-AROUND COVER among the first or last four pages (back, spine and front on one wide page — owner 2026-10-14,
    # مواد البيان ص 474 «لا تحافظ على مقاس الأوراق ولا شمول الغلاف»): split like a spread, at its gutter or its middle
    wide = {i: round(d[i].rect.width / 2, 2) for i in sorted(set(range(4)) | set(range(n0 - 4, n0))) if 0 <= i < n0 and not d[i].rotation
            and d[i].rect.width > 1.5 * d[i].rect.height} if n0 and not spreads else {}
    if spreads or wide:
        gut = spread_gutters(d)                    # a book of spreads (or a cover spread): split first, then the method
        gut = {i: g for i, g in gut.items() if spreads or i in wide}
        for i, g in wide.items(): gut.setdefault(i, g)
        d.close()
        if gut:
            tmp = path[:-4] + '.split.pdf'; shutil.copyfile(path, tmp)
            dd = pymupdf.open(tmp); split_pages(dd, gut); dd.save(tmp, incremental=True, encryption=pymupdf.PDF_ENCRYPT_KEEP); dd.close()
            try: rec = plan(tmp, jobs, owner_turns)
            finally: os.remove(tmp)
            rec['split'] = {str(k): v for k, v in gut.items()}; rec['split_from'] = n0
            return rec
    else: d.close()
    stamps = stamps_of(path, jobs)
    pages = analyse_pages(path, stamps, jobs=jobs); rec = None
    for wq in (0.95, 0.98, 1.0):
        rec = decide(copy.deepcopy(pages), wq); rec['stamp_pages'] = len(stamps)
        if rec.get('decision') == 'level': break
        if rec.get('decision') != 'crop': continue
        rec = verify(path, rec, jobs=jobs, owner_turns=owner_turns)
        if rec.get('decision') == 'crop': rec['width_quantile'] = wq; return frames(rec)
    if rec.get('decision') == 'level' or (rec.get('skewed') and 'do not fit one box' in (rec.get('decision') or '')):
        r2 = level(path, pages, rec.get('decision'), jobs, owner_turns); r2['stamp_pages'] = len(stamps); return r2
    return rec

def level(path, pages, why, jobs=1, owner_turns=None):
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
    rec = verify(path, rec, tilt_only=True, jobs=jobs, owner_turns=owner_turns)
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
    # TWO BOOK PAGES ON ONE SHEET (owner 2026-10-14, طبقات الفقهاء: «لماذا لم تحاول تقسيم الصفحات المزدوجة؟»): a box for
    # one page cannot serve a spread — such a book is split first (each sheet into its right and left pages), not cropped
    if sum(1 for i in text if pages[i]['w'] > 1.15 * pages[i]['h']) >= 0.5 * len(text):
        out['decision'] = 'skip: two pages per sheet — to be split first'; out['spreads'] = True; return out
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
    # a «stain» where the book prints its page number (the folio of 3 other pages or more, 3 %) is that number — its bold
    # digits merge into one solid mark on a page turned at the first look (2026-10-26, 1d12000b2925 ص 323: «٣٢٣» read as a
    # stain at 0.475°, the box placed off it, the second look slid it to a text block held at 3 % and cut the number at the
    # foot): print again, part of the text block (as marks() counts a page number inside its columns), the page's folio
    fols = [(j, pages[j]['folio']) for j in text if pages[j].get('folio')]
    for i in text:
        p = pages[i]; w, h = p['w'], p['h']
        for bl in list(p.get('blots') or []):
            if sum(1 for j, f in fols if j != i and same_place(bl, f, w, h)) < max(3, int(0.03 * len(text))): continue
            p['blots'].remove(bl); p['box'] = union([p['box'], bl]); t = p.get('text'); p['folio_blot'] = [round(v, 1) for v in bl]
            if t and bl[2] >= t[0] and bl[0] <= t[2]: p['text'] = union([t, bl])
            if not p.get('folio'): p['folio'] = list(bl[:4]) + ['foot' if (bl[1] >= t[3] - 1 if t else bl[1] > h / 2) else 'head']
    # PRINTED RULES AND FRAMES belong to the page when the book prints them (marks() leaves every line out): a rule on the
    # same side of the text block at the same distance (± 2 % of the page) on ≥ 40 % of the text pages (at least 3); a rule
    # inside the text block's span stays; a rule further than 6 % of the page from the text is the scanner's or the sheet's
    # edge, however often it recurs. Scan lines and print damage do not repeat (owner 2026-10-14: «لا تلتفت للخط الذي هو
    # عيب طباعة», مختصر تاريخ دمشق; صبح الأعشى ص 47 «خلل في التوسيط وفي تحديد الإطار»)
    def rkey(i, r):
        c = pages[i].get('core') or pages[i]['box']; w_, h_ = pages[i]['w'], pages[i]['h']
        if r[3] - r[1] >= r[2] - r[0]:
            return ('L', (c[0] - r[2]) / w_) if r[2] <= c[0] else (('R', (r[0] - c[2]) / w_) if r[0] >= c[2] else ('I', 0.0))
        return ('T', (c[1] - r[3]) / h_) if r[3] <= c[1] else (('B', (r[1] - c[3]) / h_) if r[1] >= c[3] else ('I', 0.0))
    rk = {i: [(rkey(i, r), r) for r in pages[i].get('rules') or []] for i in text}
    allk = [k for i in text for k, _ in rk[i]]
    for i in text:
        # (a printed frame hugs its text — within 6 % of the page; the scanner's or the sheet's edges recur at one place on
        # most pages too, but further out: صبح الأعشى ج 5, bars 13 % from the edge on both sides made the book «framed»)
        kept = [r for k, r in rk[i] if k[0] == 'I' or (k[1] <= 0.06 and sum(1 for k2 in allk if k2[0] == k[0] and abs(k2[1] - k[1]) <= 0.02) >= max(3, 0.4 * len(text)))]
        dropped = [r for k, r in rk[i] if not any(r is x for x in kept)]
        if dropped: pages[i]['rules_dropped'] = dropped
        pages[i]['rules'] = kept
        c_ = pages[i].get('core')                     # a dropped rule at the box's edge (a photocopy's rim of specks, counted
        for r_ in dropped if c_ else []:              # with the text) no longer holds the box out (صبح الأعشى ج 5 ص 47)
            for key in ('box', 'text'):
                b_ = pages[i].get(key)
                if not b_: continue
                if r_[3] - r_[1] >= r_[2] - r_[0]:
                    if r_[0] >= c_[2] and r_[0] - 1 < b_[2] <= r_[2] + 2: b_[2] = max(c_[2], r_[0] - 1)
                    elif r_[2] <= c_[0] and r_[0] - 2 <= b_[0] < r_[2] + 1: b_[0] = min(c_[0], r_[2] + 1)
                else:
                    if r_[1] >= c_[3] and r_[1] - 1 < b_[3] <= r_[3] + 2: b_[3] = max(c_[3], r_[1] - 1)
                    elif r_[3] <= c_[1] and r_[1] - 2 <= b_[1] < r_[3] + 1: b_[1] = min(c_[1], r_[3] + 1)
        if kept: pages[i]['box'] = union([pages[i]['box']] + kept)
    bw = {i: pages[i]['box'][2] - pages[i]['box'][0] for i in text}; bh = {i: pages[i]['box'][3] - pages[i]['box'][1] for i in text}
    core = {i: pages[i].get('core') or pages[i]['box'] for i in text}
    cw = {i: core[i][2] - core[i][0] for i in text}
    pw = q([pages[i]['w'] for i in text], 0.5); ph = q([pages[i]['h'] for i in text], 0.5)
    # typical pages decide the width (owner 2026-10-10, القوافي للتنوخي: a title page, blank versos with the sheet's edges and
    # a plate — 6 % of the book — held the box at the full page): a page whose box is > 25 % wider than the median page is
    # not typical; it gets the book's size all the same (its content shrunk to fit / centred on its own content)
    _mw = q(bw.values(), 0.5)
    Tw, Th = q([v for v in bw.values() if v <= 1.25 * _mw] or list(bw.values()), wq), q(bh.values(), 1.0)
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
    def needed(i):                                   # what a page needs (stray dots far from the text do not lay a book
        p_ = pages[i]; mg = p_.get('margin') or []   # out by parity — أسرار البلاغة ص 187 «توسيط»)
        if not p_.get('text'): return p_['box']
        return union([p_['text']] + notes_of(mg, p_['w'], p_['h']) + figures_of(mg, p_['w'], p_['h']) + printed_groups(mg, p_['w'], p_['h'])
                     + (p_.get('rules') or []) + ([p_['folio'][:4]] if p_.get('folio') else []))
    ext = {i: (needed(i)[0] + needed(i)[2]) / 2 - cx[i] for i in full_w}
    for par in (0, 1):
        v = [ext[i] for i in full_w if i % 2 == par]
        if len(v) >= 10:
            med = q(v, 0.5)
            same = sum(1 for x in v if x * med > 0 and abs(x) >= 0.005 * pw) / len(v)
            if abs(med) >= 0.015 * pw and same >= 0.7: off[par] = med
    out['parity_offsets'] = {str(k): round(v, 1) for k, v in off.items()}
    if off[0] or off[1]:
        # the box follows the page's printed layout, per parity — on the pages that carry that marginal material; a page
        # without it is centred on its text (owner 2026-10-14, أسرار البلاغة ص 187 «توسيط»)
        def carries(i):
            o = off[i % 2]; nb = needed(i); t_ = pages[i].get('text') or pages[i]['box']
            return (o > 0 and nb[2] - t_[2] >= 0.015 * pw) or (o < 0 and t_[0] - nb[0] >= 0.015 * pw)
        cx = {i: v + (off[i % 2] if carries(i) else 0.0) for i, v in cx.items()}
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
        def printish(b):                             # and long streaks are not; nor slivers of a scan line (thin and long:
            bw, bh = b[2] - b[0], b[3] - b[1]        # صبح الأعشى ج 5 — a bar's pieces made the book «print in its margins»)
            edge = b[2] <= 0.03 * w or b[0] >= 0.97 * w or b[3] <= 0.03 * h or b[1] >= 0.97 * h
            sliver = (bw <= 0.006 * w and bh >= 4 * bw) or (bh <= 0.006 * h and bw >= 4 * bh)
            return not edge and not sliver and bh < 0.15 * h and (bh >= 0.008 * h or bw >= 0.015 * w)
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
        _mt = q([tw[i] for i in full_t], 0.5)                       # typical pages only (see Tw above)
        Tq = q([tw[i] for i in full_t if tw[i] <= 1.25 * _mt] or [tw[i] for i in full_t], wq); mc = CLEAN_MARGIN * Tq; out['margin_pt'] = round(mc, 2)
        W = min(Tq + 2 * mc, pw)
        _th = [th[i] for i in full_h if i in th] or list(th.values()); _mh = q(_th, 0.5)   # typical pages decide the height
        H = min(q([v for v in _th if v <= 1.15 * _mh] or _th, 0.98) + 2 * mc, ph)             # too (taller ones shrink to fit)
        cx = {i: ((tb[i][0] + tb[i][2]) / 2 if tb.get(i) else cx[i]) for i in text}
        cy = {i: ((tb[i][1] + tb[i][3]) / 2 if tb.get(i) else cy[i]) for i in text}
        edges = {i: tb[i] for i in text if tb.get(i)}
        for i in text:                                # the text block and its marginal notes must fit; the rest may be cut
            if tb.get(i):
                nts = notes_of(pages[i].get('margin') or [], pages[i]['w'], pages[i]['h'])
                figs = figures_of(pages[i].get('margin') or [], pages[i]['w'], pages[i]['h'])
                pages[i]['content_box'] = pages[i]['box']; pages[i]['box'] = union([tb[i]] + nts + figs)
                if nts: pages[i]['notes'] = [[round(v, 1) for v in b] for b in nts]
                if figs: pages[i]['figures'] = [[round(v, 1) for v in b] for b in figs]
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
        if p['kind'] == 'cover': p['crop'] = p['cover']; continue          # the cover alone (frames shows it at the book's size)
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
        # A PAGE MUCH NARROWER THAN THE BOOK'S PAGES (its content < 75 % of the usual width — a frame without the
        # commentary its neighbours carry beside it): centred on itself across (owner 2026-10-14, إرشاد الساري ص 492
        # «الإطار كله يتوسط»)
        if bx and i not in fw and (bx[2] - bx[0]) < 0.75 * Tw:
            x = (bx[0] + bx[2]) / 2; p['anchored_x'] = 'own-narrow'
        # A PAGE WHOSE CONTENT STANDS IN THE MIDDLE — a section's title page, a heading, a dedication — not a chapter's end
        # (which starts where the neighbours' lines start): its top lies ≥ 15 % of the page below theirs. It is centred on
        # itself both ways (owner 2026-10-14, رسوم دار الخلافة ص 9 «توسيط»: placed by a line end matching the neighbours')
        if e and bx and i not in fh and fhe and e[1] - near(i, fhe, ET) >= 0.15 * p['h']:
            x, y = (bx[0] + bx[2]) / 2, (bx[1] + bx[3]) / 2; p['anchored_x'] = p['anchored_y'] = 'own-middle'
        if bx:
            b = [x - W / 2, y - H / 2, x + W / 2, y + H / 2]
            dx = bx[0] - b[0] if bx[0] < b[0] else (bx[2] - b[2] if bx[2] > b[2] else 0)
            dy = bx[1] - b[1] if bx[1] < b[1] else (bx[3] - b[3] if bx[3] > b[3] else 0)
            if (dx or dy) and not clean and p.get('text'):
                # what the page needs (owner 2026-10-14): its text block, notes, pictures, the book's printed rules and its
                # print in the margin (printed_groups) — stray dots and specks do not move the box (they are cut)
                need = union([p['text']] + notes_of(p.get('margin') or [], p['w'], p['h']) + figures_of(p.get('margin') or [], p['w'], p['h'])
                             + printed_groups(p.get('margin') or [], p['w'], p['h']) + (p.get('rules') or []) + ([p['folio'][:4]] if p.get('folio') else []))
                if inside(need, bx, 1.0) and not inside(bx, need, 1.0):
                    p['cut_stray'] = [m for m in (p.get('margin') or []) if not inside(m, need, 1.0)]
                    p['content_box'] = bx; p['box'] = bx = need
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
        # (on any paper when the box would otherwise leave the text ≥ 3 % off-centre: a strip beyond the sheet's edge is
        # better than a page pushed aside — owner 2026-10-14, إرشاد الساري ص 492 «الإطار كله يتوسط»)
        if (sx or sy) and bx and (p.get('paper', 0) >= 235 or max(abs(sx) / p['w'], abs(sy) / p['h']) >= 0.03):   # with it
            nb = [bx[0] + sx, bx[1] + sy, bx[2] + sx, bx[3] + sy]
            if nb[0] >= 0 and nb[1] >= 0 and nb[2] <= p['w'] and nb[3] <= p['h']:
                p['move'] = [round(sx, 1), round(sy, 1)]; moved += 1
                p['box'] = bx = [round(v, 1) for v in nb]
                p['blots'] = [[v[0] + sx, v[1] + sy, v[2] + sx, v[3] + sy] for v in p.get('blots', [])]
                p['specks'] = [[v[0] + sx, v[1] + sy, v[2] + sx, v[3] + sy] for v in p.get('specks', [])]
                p['edge'] = [[v[0] + sx, v[1] + sy, v[2] + sx, v[3] + sy] for v in p.get('edge', [])]
        b = [round(b[0] + sx, 1), round(b[1] + sy, 1), round(b[2] + sx, 1), round(b[3] + sy, 1)]
        tbx = p.get('text') or bx                    # a line beside the text (a scan line, an edge, print damage) is dodged
        avoid = (p.get('blots') or []) + [ln for ln in (p.get('lines') or []) if tbx and not (ln[0] >= tbx[0] - 1 and ln[2] <= tbx[2] + 1 and ln[1] >= tbx[1] - 1 and ln[3] <= tbx[3] + 1)]
        # with a little room around each (0.6 % of the page): a mark is measured on its dark core, its blur and a slant
        # reach further, and a box that stops 2 pt short of it still shows it (owner 2026-10-18, خزانة الأدب ج 1: «ضع الإطار
        # بحيث عيوب الطباعة أعلى الصفحات تختفي»)
        px_, py_ = 0.006 * p['w'], 0.006 * p['h']
        avoid = [[v[0] - px_, v[1] - py_, v[2] + px_, v[3] + py_] for v in avoid]
        if bx and avoid:                             # dodge a stain: slide the box away from it, as far as the content and
            lo, hi = max(0, bx[2] - (b[2] - b[0])), min(bx[0], p['w'] - (b[2] - b[0]))      # the page allow (same size)
            for bl in avoid:
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
        if bx and avoid:                             # the same up and down: a line or stain along the top or the bottom edge
            lo_y, hi_y = max(0, bx[3] - (b[3] - b[1])), min(bx[1], p['h'] - (b[3] - b[1]))   # (owner 2026-10-14, خزانة
            for bl in avoid:                                                                  # الأدب ج 4 ص 44: a dark line)
                if bl[2] > b[0] and bl[0] < b[2] and bl[3] > b[1] and bl[1] < b[3]:
                    ny = bl[3] + 2 if bl[3] <= bx[1] else (bl[1] - 2 - (b[3] - b[1]) if bl[1] >= bx[3] else None)
                    if ny is not None and lo_y <= hi_y:
                        cand = min(max(ny, lo_y), hi_y); mt, mbm = bx[1] - cand, cand + (b[3] - b[1]) - bx[3]
                        # (up and down the eye forgives unequal margins more than a dark bar: الحروب الصليبية ص 426)
                        if min(mt, mbm) < 0.35 * max(mt, mbm): p['stain_kept'] = True; continue
                        b = [b[0], round(cand, 1), b[2], round(cand + b[3] - b[1], 1)]; p['dodged'] = True
        # a SCANNER BAND OR BLACK BORDER stays outside, even at the cost of unequal margins (owner 2026-10-18: خريدة القصر
        # «أيمان الصفحات مداخلة للحافة» — a black strip 20 pt wide kept beside the text; صبح الأعشى «المشكل نابع من عدم
        # الجرأة على تجاوز سواد الطباعة»): the book's box fits 95 % of the pages between their bands; on the others it
        # slides off the band as far as the content allows (≥ 4 pt left beside the text), the other side taking the rest
        al = p.get('allowed'); tb = p.get('text') or bx; mv_ = p.get('move') or [0, 0]
        # (only a side that HAS a band limits the box: the page's own edge is no band — moved with the content it read as
        # one, and a lone line moved 91 pt across was left 92 pt off-centre: فهرسة ابن خير ص 381)
        if al: al = [al[0] if al[0] > 0.5 else -1e9, al[1] if al[1] > 0.5 else -1e9,
                     al[2] if al[2] < p['w'] - 0.5 else 1e9, al[3] if al[3] < p['h'] - 0.5 else 1e9]
        if al and mv_ != [0, 0]: al = [al[0] + mv_[0], al[1] + mv_[1], al[2] + mv_[0], al[3] + mv_[1]]   # (moved with the content)
        if mv_ != [0, 0] and tb and tb is not bx: tb = [tb[0] + mv_[0], tb[1] + mv_[1], tb[2] + mv_[0], tb[3] + mv_[1]]
        if al and bx and tb and p['kind'] == 'text':
            for k0, k1, lo_i, hi_i in ((0, 2, 0, 2), (1, 3, 1, 3)):
                over_hi, over_lo = b[k1] - al[hi_i], al[lo_i] - b[k0]
                if over_hi > 1 and over_lo <= 0:
                    sh = -min(over_hi + 1, b[k0] - al[lo_i], max(0, (b[k1] - tb[k1]) - 4))
                elif over_lo > 1 and over_hi <= 0:
                    sh = min(over_lo + 1, al[hi_i] - b[k1], max(0, (tb[k0] - b[k0]) - 4))
                else: continue
                if abs(sh) >= 1:
                    b[k0] = round(b[k0] + sh, 1); b[k1] = round(b[k1] + sh, 1); p['off_band'] = round(sh, 1)
        b = [max(0, b[0]), max(0, b[1]), min(p['w'], b[2]), min(p['h'], b[3])]
        hm = 0.5 * mc                                 # half the margin at least, else the box grows (اللآلئ ج2 ص 40: 2 pt)
        if clean and p['kind'] == 'text' and bx and not p.get('off_band') and not inside([bx[0] - hm, bx[1] - hm, bx[2] + hm, bx[3] + hm], b):
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

def verify(path, rec, px=1000, tilt_only=False, jobs=1, only=None, moved_in=None, owner_turns=None):
    """second look at twice the resolution: every mark found outside a page's box must be one the first look left out on
    purpose (a stain, edge noise — the same place, give or take 3 pt) or an isolated speck; anything else is content:
    the box may move up to 2 % to take it in, else the page stays whole"""
    if jobs > 1 and only is None:                     # pages shared out among `jobs` processes, then summed up here
        idx = list(range(len(rec['pages']))); mv = []
        with ProcessPoolExecutor(jobs) as ex:
            for part, moved_c in ex.map(_verify_chunk, [(path, rec, px, tilt_only, idx[k::jobs], owner_turns) for k in range(jobs)]):
                for i, pg in part.items(): rec['pages'][i] = pg
                mv += moved_c
        return verify(path, rec, px, tilt_only, only=set(), moved_in=sorted(mv), owner_turns=owner_turns)
    doc = pymupdf.open(path); moved = list(moved_in or [])
    near = lambda b, regions: any(b[0] < r[2] + 3 and b[2] > r[0] - 3 and b[1] < r[3] + 3 and b[3] > r[1] - 3 for r in regions)
    cur = {'i': None, 'tu': None, 'looks': {}}       # the page being checked: its Turner and its looks by (turn, move) —
    def look(i, q):                                   # the same view is never measured twice (2026-10-25, speed: the
        if cur['i'] != i:                             # first look's angle came back in best_turn, the trial turns of an
            if cur['tu']: cur['tu'].close()           # untouched page in it too)
            cur.update(i=i, tu=Turner(doc, i), looks={})
        mv = q.get('move') or [0, 0]; key = (q.get('skew') or 0, mv[0], mv[1])
        if key in cur['looks']: return cur['looks'][key]
        page = cur['tu'].page(*key); a, z = gray(page, px); st = rec['pages'][i].get('stamp')   # the page as the reader
        if rec['pages'][i].get('sheet'): a = whiten(a, z, fwd_box(doc, i, q, rec['pages'][i]['sheet']))   # will see it, at px
        ex = [pad_box(b, page.rect.width) for b in st or []] + (rec['pages'][i].get('dots') or [])
        mk = marks(a, z, page.rect.width, fwd_boxes(doc, i, q, ex) if ex else None); mk['z'] = z
        memo = {}
        def once(k, f):                               # each measure of this view taken once
            if k not in memo: memo[k] = f()
            return memo[k]
        mk['proj'] = lambda lo=-0.5, hi=0.5, step=0.05: once(('proj', lo, hi, step), lambda: proj_tilt(a, mk['paper'], lo, hi, step))
        mk['lines'] = lambda: once('lines', lambda: baseline_tilt(a, mk['paper']) if mk.get('paper') else None)
        mk['edges'] = lambda: once('edges', lambda: edge_tilt(a, mk['paper']) if mk.get('paper') else [None, None])
        mk['cols'] = lambda: once('cols', lambda: columns_tilt(a, mk['paper']) if mk.get('paper') else None)
        cur['looks'][key] = mk
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
        # a turn level by BOTH measures is taken before any other, whatever the others read (2026-10-25, الحروب الصليبية ص 407:
        # 0.35° read 0.025° / 0.175° — level — but 0.25° won the least-of-the-two by 0.17499… against 0.175, its shear reading
        # 0.175° above the limit, and the page was left untreated)
        key = lambda kv: (max(kv[1][0], kv[1][1]), kv[1][0])
        lv = [kv for kv in tried.items() if kv[1][0] <= LEVEL and kv[1][1] <= IMG_LEVEL]
        d, (r, im, m2) = min(lv or tried.items(), key=key)
        if lv and min(tried.items(), key=key)[0] != d: p['level_first'] = True
        if not (r <= LEVEL and im <= IMG_LEVEL):      # none level by both: among the turns the two read ≤ 0.35°, the one
            cl = []                                   # whose lines read most level, line by line (baseline_tilt); of
            for dd, v in tried.items():               # several alike (it reads in steps of 0.14°), the one the shear
                if max(v[0], v[1]) <= 0.35:           # measure reads most level (until 2026-10-25: the smallest angle —
                    b = v[2]['lines'](); cl.append((round(abs(b), 3) if b is not None else 9, v[0], dd, v))   # 0.125° for
            if cl and min(cl, key=lambda c: c[:3])[0] <= 0.15:                                               # a 0.325° tilt)
                _, _, d, (r, im, m2) = min(cl, key=lambda c: c[:3])
        return d, r, im, m2
    def keep(p, d, r, im, before, m2=None, m0=None):  # level, or a curved page brought below sight, or (a clear tilt,
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
        # A SMALL TILT A RULER CONFIRMS (2026-10-25: 33 pages of 8 regression books, 0.2–0.7°, left tilted — once turned the
        # shear measure read them level, the coarse image measure 0.22–0.3°; معجم تيمور ص 75, مشتبهات القرآن ص 58): a ruler of
        # the page's own — its lines' baselines, or their aligned edge — that read the tilt on the page as it was (≥ 0.2°: one
        # pixel over a line's third is 0.14° at 1,000 px; within 0.25° of the turn and in its direction: the baselines' angle
        # has the turn's sign, the edge's the opposite) and reads ≤ 0.15° once turned, the shear measure level and the image
        # ≤ 0.35°: two measures agree that the page was tilted and is now level (the image measure's floor on such pages is
        # 0.22–0.35° whatever the turn — the owner approved all 14 pages held back by a 0.3° limit, crop-tilt-001, 2026-10-25;
        # 0.35° is the bound the method allows such certified turns elsewhere)
        if m0 is not None and m2 is not None and r <= LEVEL and im <= 0.35 + 1e-6:
            b0 = m0['lines']()
            if b0 is not None and abs(b0) >= SKEW_MIN and b0 * d > 0 and abs(abs(b0) - abs(d)) <= 0.25:
                b1 = m2['lines']()
                if b1 is not None and abs(b1) <= 0.15:
                    p['level_by_lines'] = round(b1, 3)
                    if im > 0.3 + 1e-6: p['image_loose'] = im
                    return True
            e0, e1 = m0['edges'](), m2['edges']()
            for s in (0, 1):
                if e0[s] is not None and e1[s] is not None and abs(e0[s]) >= SKEW_MIN and e0[s] * d < 0 \
                   and abs(abs(e0[s]) - abs(d)) <= 0.25 and abs(e1[s]) <= 0.15:
                    p['level_by_edge'] = round(e1[s], 3)
                    if im > 0.3 + 1e-6: p['image_loose'] = im
                    return True
        # A BIG TILT NO SINGLE TURN LEVELS (a warped leaf; owner 2026-10-14, أحكام القرآن ص 250 «لم تقوم», 4–6°): a turn that
        # leaves both measures ≤ 20 % of the tilt (at most 0.4° left from 2°) is far better than the page as it was
        if abs(before) >= 1.5 and max(r, im) <= max(0.4, 0.2 * abs(before)): p['reduced'] = round(max(r, im), 3); return True
        return False
    for i, p in enumerate(rec['pages']):
        if only is not None and i not in only: continue
        if not p.get('crop') and not p.get('skew'): continue
        if p.get('kind') == 'cover': continue          # a cover is shown as found (cover_rect), never turned or widened
        mk = look(i, p)
        # LEVEL CHECK (owner: «اختبار يضمن أننا أزلنا الميل تماما ولم نصطنع ميلا جديدا أو نبق شيئا من الميل»):
        # a turned page must read level by BOTH measures — the shear profile of its ink (≤ 0.15°) and the turned page
        # image (≤ 0.2°: it is coarser); if the first turn does not, the angles around it are tried (best_turn). A curved
        # page is kept when both read ≤ 0.25° and ≤ a third of its tilt. Else the turn is undone (a tilt the method made is
        # never kept). An untouched page showing a tilt the first look did not treat is turned here when the image measure
        # sees the tilt too (≥ 0.15°) and the turn passes the same tests; else it is reported. An untouched page cannot
        # gain a tilt.
        # TWO COLUMNS (owner 2026-10-09, الفوائد ص 456–457): the page untouched is measured column by column; when both
        # columns' line starts read the same clear tilt (≥ 0.3°, within 0.15° of each other), the turns around it are tried
        # and the one leaving both columns' edges ≤ 0.15° is kept; else (columns disagree, a small tilt, one side
        # unreadable) the page is not turned — the whole-page measures are not trusted on such a page
        # A PAGE TURNED BY ITS RULES (a table — by_rules) whose rules stand straight once turned (≤ 0.35°): the turn stays;
        # its columns of short entries are no measure of it (owner 2026-10-18, خريدة القصر ص 649 «الأخير ما زال مائلا»:
        # the column test read the index as two disagreeing columns and undid a turn its own rules confirmed)
        rl = mk.get('rule_tilts') or []
        if p.get('skew') and p.get('tilt_by_rules') and len(rl) >= 2 and abs(float(np.median(rl))) > 0.35:
            # the page's ink (entries and rules together) turned it short: the angles towards the rules' own reading are
            # tried, and the one that leaves the rules straightest is kept (خريدة القصر ص 649: 1.52° read, 1.96° by its rules)
            s0, best = p['skew'], None
            for k in range(0, 9):
                d = round(s0 + (k * 0.1 if s0 > 0 else -k * 0.1), 3); m2 = look(i, dict(p, skew=d)); r2 = m2.get('rule_tilts') or []
                if len(r2) < 2: continue
                v = abs(float(np.median(r2)))
                if best is None or v < best[0]: best = (v, d, m2)
            if best and best[0] <= 0.35: p['skew'], mk, rl = best[1], best[2], best[2].get('rule_tilts')
        lbr = bool(p.get('skew') and p.get('tilt_by_rules') and len(rl) >= 2 and abs(float(np.median(rl))) <= 0.35)
        if lbr: p['level_by_rules'] = round(float(np.median(rl)), 3)
        if not lbr and p.get('skew') and p.get('tilt_by_proj') is not None and mk.get('xy') is not None:   # turned by the
            pl = abs(skew_of(mk['xy'], raw=True)[0])     # projection: it stays when the page now reads level by its own ink
            if pl <= 0.2: lbr = True; p['level_by_proj'] = round(pl, 3)
        m0 = mk if lbr else (look(i, {k: v for k, v in p.items() if k != 'skew'}) if p.get('skew') else mk)
        ct = None if lbr else (m0['cols']() if m0.get('paper') else None)
        if lbr: pass
        elif ct is not None:
            tr, tl = ct
            # (within 15 % of the tilt, at least 0.15°, from 0.25° on — owner 2026-10-14, أنساب الأشراف ص 42: columns
            # reading 1.59° and 1.44° were left tilted for 0.0007° over a fixed 0.15°)
            if tr is not None and tl is not None and tr * tl > 0 and abs(tr - tl) <= max(0.15, 0.15 * max(abs(tr), abs(tl))) + 1e-6 \
               and min(abs(tr), abs(tl)) >= 0.25:
                u2 = (tr + tl) / 2; best = None
                for sgn in (-1, 1):
                    for k in range(-3, 4):
                        d = round(sgn * u2 + 0.05 * k, 3); m2 = look(i, dict(p, skew=d)); c2 = m2['cols']()
                        if not c2 or c2[0] is None or c2[1] is None: continue
                        sc = max(abs(c2[0]), abs(c2[1]))
                        if best is None or sc < best[0]: best = (sc, d, m2)
                if best and best[0] <= 0.15:
                    sc, d, m2 = best; p['skew'] = d; p['tilt_by_columns'] = [round(tr, 3), round(tl, 3)]
                    p['level_by_columns'] = round(sc, 3); mk = m2
                    if m2['xy'] is not None: p['after_tilt'] = round(abs(skew_of(m2['xy'], raw=True)[0]), 3)
                    p['after_tilt_image'] = m2['proj']()
                else:
                    p.pop('skew', None); p['tilt_disputed'] = round(u2, 3); mk = m0
            else:
                if p.get('skew'): p.pop('skew', None); p['unsure_tilt'] = True
                mk = m0
        elif p.get('skew'):
            before = p['skew']; d, r, im, m2 = best_turn(i, p, before)
            if keep(p, d, r, im, before, m2, m0): p['skew'], mk = d, m2; p['after_tilt'] = round(r, 3); p['after_tilt_image'] = im
            else:
                p.pop('skew', None); p['unsure_tilt'] = True; mk = look(i, p)
        elif mk['xy'] is not None and ct is None:
            u, g = skew_of(mk['xy'])
            # (no turn when the halves disagree, even if the whole page and its image agree on a tilt: index pages fool
            # all of them alike — 2026-10-09, الفوائد المحصورة ص 432 and 446, «فهرس اللغة», turned 3° by mistake) — unless
            # the lines' edge, a ruler of its own, reads the same clear tilt as the whole page (≥ 0.4°, within 0.2°):
            # a list of short right-aligned lines (ص 526). Such a turn is kept only if the edge then stands straight
            u, g = by_rules(mk, u, g, p)
            if not (abs(u) >= SKEW_MIN and g >= 1.02):
                r_, g_ = skew_of(mk['xy'], raw=True)
                if abs(r_) >= 0.4 and g_ >= 1.02:
                    es = [e for e in mk['edges']() if e is not None and abs(e - r_) <= 0.2]
                    if es: u, g = r_, g_; p['tilt_by_edge'] = round(min(es, key=lambda e: abs(e - r_)), 3)
            if abs(u) >= 1.0 and mk.get('level_frame'): p['frame_level'] = round(u, 3); u = 0.0   # a level frame: not turned
            if abs(u) >= SKEW_MIN and g >= 1.02:
                if mk['proj'](-3.0, 3.0, 0.25) < SKEW_MIN - 0.05: p['tilt_disputed'] = round(u, 3)   # the image shows no tilt
                else:
                    tries = []; al0 = p.get('allowed'); bd = banded(al0, p['w'], p['h'])
                    for d0 in (-u, u):                # the direction that lowers the tilt, by the shear measure
                        m2 = look(i, dict(p, skew=round(d0, 3)))
                        if m2['xy'] is None or not (0.6 <= ink_ratio(mk, m2, mk['z'], al0 if bd else None,
                                                                     fwd_inner(doc, i, dict(p, skew=round(d0, 3)), al0) if bd else None) <= 5.0):
                            continue
                        tries.append((abs(skew_of(m2['xy'], raw=True)[0]), round(d0, 3)))
                    done = False
                    if tries:
                        d, r, im, m2 = best_turn(i, p, min(tries)[1])
                        if keep(p, d, r, im, u, m2, mk):
                            p['skew'] = d; p['after_tilt'] = round(r, 3); p['after_tilt_image'] = im; p['turned_in_check'] = True
                            mk = m2; done = True
                    if not done:                      # (a page found by its edge alone whose turn is not certified: the
                        if p.get('tilt_by_edge') is not None: p['tilt_disputed'] = round(u, 3)   # measures disagree)
                        else: p['untreated_tilt'] = round(u, 3)
        # THE OWNER'S TURN (data/crop/owner-turns.tsv, owner 2026-10-25 on crop-tilt-001: «أجيز هذا وجميع ما سبق»): a page he
        # ruled «turn» after seeing it turned by its measured tilt, which the measures above leave as it is, is turned by
        # that tilt — u measured here, on the page as it is (sign and size); the readings after it are kept for the record
        ot = (owner_turns or {}).get(i + 1)
        if ot is not None and not p.get('skew'):
            m0_ = look(i, {k: v for k, v in p.items() if k != 'skew'})
            u = p.get('untreated_tilt') or p.get('tilt_disputed') or 0.0
            if not u and m0_['xy'] is not None: u = skew_of(m0_['xy'])[0] or skew_of(m0_['xy'], raw=True)[0]
            if u:
                d = round(-u, 3); m2 = look(i, dict(p, skew=d))
                for k in ('untreated_tilt', 'tilt_disputed', 'unsure_tilt'): p.pop(k, None)
                p['skew'] = d; p['owner_turn'] = round(float(ot), 3); mk = m2
                if abs(abs(u) - float(ot)) > 0.05: p['owner_turn_measured'] = round(u, 3)   # (not the tilt he saw: shown)
                if m2['xy'] is not None:
                    p['after_tilt'] = round(abs(skew_of(m2['xy'], raw=True)[0]), 3); p['after_tilt_image'] = m2['proj']()
        if tilt_only or not p.get('crop'): continue
        c = p['crop']; known = (p.get('blots') or []) + (p.get('edge') or []) + (p.get('rules_dropped') or []) + (p.get('lines') or []) + (p.get('cut_stray') or [])
        el = edge_letters(mk, p['w'], p['h'], mk['z'], p.get('allowed')) if mk.get('parts') else []
        if el: p['edge_letters'] = [[round(v, 1) for v in b[:4]] for b in el]   # letters in the edge shadow (edge_letters)
        pts = (mk.get('parts') or []) + el
        pk = {tuple(b[:4]) for b in print_marks(pts, p['w'], p['h'], mk['z'])} if pts else set()
        prn = [b for b in pts if tuple(b[:4]) in pk]; isp = lambda b: tuple(b[:4]) in pk   # the print (print_marks)
        if rec.get('clean_margins') and mk.get('text'):
            # a book without print in its side margins: the text block seen at 1,000 px must be inside the box, and no mark
            # may straddle the box edge (half in, half out = a cut letter); marks wholly outside the text columns are the
            # margin's dots, pen strokes and scan edges, cut on purpose. If not: the box slides up to 2 %, else takes the
            # same shape just large enough (never a cut line, never a page left whole for a stray mark)
            gx_, gy_, z_ = 0.015 * p['w'], 0.015 * p['h'], mk['z']
            t0 = p.get('text')                       # (the text block on print only: a scan line's one-pixel dashes are no
            t = (text_block(pts, t0, p['w'], p['h'], z_, prn) if t0 else None) or mk['text']   # letters — text_block)
            mg2 = (mk.get('margin') or []) if t == mk['text'] else [b for b in pts if not inside(b, t, 0.5)]
            if t0 and t:                             # at 1,000 px a photocopy's border breaks into letter-sized dashes that
                t = [max(t[0], t0[0] - 0.03 * p['w']), max(t[1], t0[1] - 0.03 * p['h']),   # chain onto the text (owner
                     min(t[2], t0[2] + 0.03 * p['w']), min(t[3], t0[3] + 0.03 * p['h'])]   # 2026-10-10, القوافي ص 25 و44):
            nts = notes_of(mg2, p['w'], p['h'])      # the text may grow by a cut letter (3 %), not to the sheet's edge
            if nts: p['notes'] = [[round(v, 1) for v in b] for b in nts]   # marginal notes seen at 1,000 px: kept, like the text
            figs = figures_of(mg2, p['w'], p['h'])   # a picture or plate beside the text: whole
            alc = p.get('allowed')                    # nothing the frame must hold lies in a scanner band (خريدة القصر ص 649)
            if alc and t:
                cl = lambda b: [max(b[0], alc[0] - 0.01 * p['w']), max(b[1], alc[1] - 0.01 * p['h']), min(b[2], alc[2] + 0.01 * p['w']), min(b[3], alc[3] + 0.01 * p['h'])]
                enters = lambda b: b[2] > alc[2] + 0.01 * p['w'] or b[0] < alc[0] - 0.01 * p['w'] or b[3] > alc[3] + 0.01 * p['h'] or b[1] < alc[1] - 0.01 * p['h']
                figs = [b for b in figs if not enters(b)]   # a «picture» running into the band is the band itself
                t = cl(t); nts = [cl(b) for b in nts]
            tn = union([t] + nts + figs)
            # a cut letter lies next to the text block (within the gap that makes text); a pen stroke or speck further out
            # that happens to cross the box edge is margin, cut like the rest (2026-10-09: اللآلئ ج1 p. 8 stayed whole)
            al_ = p.get('allowed')                    # (a mark whose centre lies in a scanner band is the band — خريدة القصر ص 649)
            inal = lambda b: not al_ or (al_[0] - 0.01 * p['w'] <= (b[0] + b[2]) / 2 <= al_[2] + 0.01 * p['w']
                                         and al_[1] - 0.01 * p['h'] <= (b[1] + b[3]) / 2 <= al_[3] + 0.01 * p['h'])
            # (a hairline or a copier's bar crossing the edge is no letter: printlike)
            straddles = lambda b, r, s: (not inside(b, r, 1.0) and b[0] < r[2] and b[2] > r[0] and b[1] < r[3] and b[3] > r[1]
                                         and (b in el or not near(b, known)) and b[2] >= s[0] - gx_ and b[0] <= s[2] + gx_ and b[3] >= s[1] - gy_
                                         and b[1] <= s[3] + gy_ and not thin_line(b, p['w'], p['h']) and inal(b) and isp(b))
            cross = [b for b in pts if straddles(b, c, t)]
            need = ([tn] if not inside(tn, c, 1.0) else []) + cross
            if need:
                u = union(need + [tn])
                # a slide must leave half the book's margin around the text and its notes (2026-10-09: اللآلئ ج2 ص 39 slid
                # until its note touched the edge); else the box grows with the full margin (shown at the book's size)
                mg = rec.get('margin_pt') or 0.01 * (c[2] - c[0]); h_ = 0.5 * mg
                def place(u):                            # → the box holding u, and its scale when it had to grow (else None)
                    up = [u[0] - h_, u[1] - h_, u[2] + h_, u[3] + h_]
                    dx = up[0] - c[0] if up[0] < c[0] else (up[2] - c[2] if up[2] > c[2] else 0)
                    dy = up[1] - c[1] if up[1] < c[1] else (up[3] - c[3] if up[3] > c[3] else 0)
                    n = [c[0] + dx, c[1] + dy, c[2] + dx, c[3] + dy]
                    if abs(dx) <= 0.02 * p['w'] and abs(dy) <= 0.02 * p['h'] and inside(up, n, 1.0) \
                       and n[0] >= 0 and n[1] >= 0 and n[2] <= p['w'] and n[3] <= p['h']:
                        return n, None
                    cw, ch = c[2] - c[0], c[3] - c[1]
                    sc = max(1.0, (u[2] - u[0] + 2 * mg) / cw, (u[3] - u[1] + 2 * mg) / ch)
                    smax = min(p['w'] / cw, p['h'] / ch)        # never beyond the sheet: the margin gives way first
                    if sc > smax: sc = max(1.0, smax, (u[2] - u[0]) / cw, (u[3] - u[1]) / ch)
                    x2, y2 = (u[0] + u[2]) / 2, (u[1] + u[3]) / 2
                    n = [x2 - cw * sc / 2, y2 - ch * sc / 2, x2 + cw * sc / 2, y2 + ch * sc / 2]
                    sx = -n[0] if n[0] < 0 else (p['w'] - n[2] if n[2] > p['w'] else 0); sy = -n[1] if n[1] < 0 else (p['h'] - n[3] if n[3] > p['h'] else 0)
                    return [n[0] + sx, n[1] + sy, n[2] + sx, n[3] + sy], sc
                n, sc = place(u)
                # NO PRINT CUT BY THE MOVED BOX (2026-10-26, 1d12000b2925 ص 323: the box slid to a text block held at the 3 %
                # bound and its foot ran through the page number): a mark the moved box cuts is taken in, once
                st = [b for b in pts if straddles(b, n, u)]
                if st: p['verify_cut'] = len(st); u = union([u] + st); n, sc = place(u)
                if sc is not None: p['enlarged'] = round(max(sc, p.get('enlarged', 1.0)), 3)
                if n[0] >= -0.5 and n[1] >= -0.5 and n[2] <= p['w'] + 0.5 and n[3] <= p['h'] + 0.5 and inside(u, n, 1.0):
                    p['crop'] = [round(max(0, n[0]), 1), round(max(0, n[1]), 1), round(min(p['w'], n[2]), 1), round(min(p['h'], n[3]), 1)]
                    p['verify_moved'] = True
                else:
                    p['crop'] = None; p['verify'] = u; moved.append(i); continue
            p['cut_specks'] = [x for x in mk['specks'] if not inside(x, p['crop'], 0)]
            p['cut_margin'] = [b for b in mk.get('margin') or [] if not inside(b, p['crop'], 1.0)]
            if any(not inside(b, p['crop'], 1.0) for b in nts): p['notes_cut'] = True     # must never happen (checked)
            continue
        al_ = p.get('allowed')
        out = [b for b in pts if not inside(b, c, 1.0) and (b in el or not near(b, known))
               and (not al_ or (al_[0] - 0.01 * p['w'] <= (b[0] + b[2]) / 2 <= al_[2] + 0.01 * p['w']
                                and al_[1] - 0.01 * p['h'] <= (b[1] + b[3]) / 2 <= al_[3] + 0.01 * p['h']))]
        if out:
            # only what the page needs moves the box or keeps the page whole (owner 2026-10-14): its text block's letters,
            # notes, pictures and print in the margin; slivers of a scan line and stray specks outside are cut (the text
            # block on print only, and only print-like marks move the box: text_block, printlike — 2026-10-26)
            tq = (text_block(pts, p['text'], p['w'], p['h'], mk['z'], prn) if p.get('text') else None) or mk.get('text')
            mg_ = (mk.get('margin') or []) if tq == mk.get('text') else [b for b in pts if not inside(b, tq, 0.5)]
            needs = ([tq] if tq else []) + notes_of(mg_, p['w'], p['h']) + figures_of(mg_, p['w'], p['h']) \
                    + printed_groups(mg_, p['w'], p['h'])
            meets = lambda b, n: b[0] < n[2] + 1 and b[2] > n[0] - 1 and b[1] < n[3] + 1 and b[3] > n[1] - 1
            keep_ = lambda b: any(meets(b, n) for n in needs) and isp(b)
            cut = [b for b in out if not keep_(b)]
            if cut: p['cut_stray'] = (p.get('cut_stray') or []) + [[round(v, 1) for v in b] for b in cut]
            out = [b for b in out if keep_(b)]
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
    if cur['tu']: cur['tu'].close()
    doc.close()
    rec['whole'] = sorted(set(rec.get('whole', [])) | set(moved)); rec['verify_whole'] = moved
    rec['blot_pages'] = sum(1 for p in rec['pages'] if p.get('crop') and p.get('blots'))
    rec['skewed'] = sum(1 for p in rec['pages'] if p.get('skew'))
    rec['residual_tilt'] = [i + 1 for i, p in enumerate(rec['pages']) if p.get('skew') and p.get('reduced') is None and not (p.get('after_tilt', 9) <= LEVEL and p.get('after_tilt_image', 9) <= IMG_LEVEL)
                            and not (p.get('curved') and p.get('after_tilt', 9) <= CURVED and p.get('after_tilt_image', 9) <= CURVED)
                            and not (p.get('level_by_lines') is not None and max(p.get('after_tilt', 9), p.get('after_tilt_image', 9)) <= 0.35)
                            and not (p.get('level_by_edge') is not None and p.get('after_tilt', 9) <= 0.2)
                            and not (p.get('level_by_columns') is not None and p['level_by_columns'] <= 0.15)
                            # (a turn certified by the page's straight rules or by its own ink: no after-turn reading is
                            # taken for it — these were listed as «still tilted» until 2026-10-25: 2,348 pages of the
                            # regression's 31 books)
                            and not (p.get('level_by_rules') is not None and abs(p['level_by_rules']) <= 0.35)
                            and not (p.get('level_by_proj') is not None and p['level_by_proj'] <= 0.2)
                            and p.get('owner_turn') is None]          # (the owner saw that turn and asked for it)
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
        k_ = rec['pages'].index(p); n_ = len(rec['pages'])
        own_cover = (k_ < 2 or k_ >= n_ - 4) and p['kind'] in ('cover', 'picture')
        if own_cover and not c: c = [0.0, 0.0, pw, ph]
        if p['kind'] == 'cover' and c or own_cover:   # A COVER FILLS THE FRAME, cut to the book's proportions (owner
            cw, chh = c[2] - c[0], c[3] - c[1]        # 2026-10-18, دلائل الإعجاز ص 1: «الملاحظة على حالها … ولو نقص شيء لا
            lim = 1.0 if own_cover else 0.08          # يؤثر من حواف الغلاف»; مواد البيان: «هل العرض مستو مع جميع الصفحات؟ يمكن
            if (cw / chh > A and (cw - chh * A) / cw <= lim     # القص من الجوانب … فهو غلاف فقط»): the book's own covers (its
                    or cw / chh < A and (chh - cw / A) / chh <= lim):   # first two and last four pages) always; a cover
                c = cover_window(c, A, p.get('cover_marks') or [])     # picture inside the book only when ≤ 4 % a side
                # goes (فهرسة ابن خير ص 380 «دون قصّ صورة الغلاف»); the cut placed where it takes no print (cover_window)
        if c and abs(c[2] - c[0] - W) <= 1.0 and abs(c[3] - c[1] - H) <= 1.0:      # the book's box
            x, y, rw, rh = (c[0] + c[2]) / 2, (c[1] + c[3]) / 2, W, H
        else:
            if c: N = c                                # a box grown for this page, or cut short by the page's edge
            elif p['kind'] == 'picture':               # a picture (a cover photographed edge to edge, a plate): the whole
                N = [0.0, 0.0, pw, ph]                 # page, centred (owner 2026-10-18, مواد البيان: «لا تحافظ على مقاس
                                                       # الأوراق ولا شمول الغلاف» — framed on a measured part, its foot was cut)
            else:                                       # a page left whole: all it holds, with the book's margin
                parts = [b for b in (p.get('box'), p.get('content_box'), p.get('verify')) if b]
                N = union(parts) if parts else [0.0, 0.0, pw, ph]
                N = [max(0.0, N[0] - m), max(0.0, N[1] - m), min(pw, N[2] + m), min(ph, N[3] + m)]
            nw, nh = max(N[2] - N[0], 1.0), max(N[3] - N[1], 1.0)
            rw, rh = (nw, nw / A) if nw / nh > A else (nh * A, nh)
            if rw < W and p['kind'] != 'cover' and not own_cover: rw, rh = W, H   # a small part is not magnified — a cover is: it fills the page
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
    path, rec, px, tilt_only, idx, owner_turns = args
    r = verify(path, rec, px, tilt_only, only=set(idx), owner_turns=owner_turns)
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

def marks_to_erase(doc, i, p):
    """A PHOTOCOPY'S RIM INSIDE THE FRAME, ON WHITE PAPER (owner 2026-10-18, صبح الأعشى ج 5 «عدم الجرأة على تجاوز سواد
    الطباعة»): a rule the book does not print (rules_dropped) that is a thin band (≤ 2.5 % of the page across) beyond the
    content, from it out to the frame's edge — covered with the paper's white (the scan stays byte for byte). NOTHING ELSE:
    stains and loose lines are only kept out by the frame — a running head the first look took for a stain (نظم تنقيح فتح
    الكريم ص 93: title, rule and page number as «blots») must never be painted over. Never on two opposite sides (a printed
    frame). Boxes in the page's own coordinates"""
    if p.get('kind') != 'text' or p.get('paper', 0) < 235 or not p.get('crop') or not p.get('box'): return []
    deg = p.get('skew') or 0; mv = p.get('move') or [0, 0]; crop, box = p['crop'], p['box']
    unturn = lambda b: fwd_box(doc, i, {'skew': -deg}, b) if deg else b
    hit = lambda r, q_, e=0: r[2] > q_[0] - e and r[0] < q_[2] + e and r[3] > q_[1] - e and r[1] < q_[3] + e
    sh = lambda b, k=1: [b[0] + k * mv[0], b[1] + k * mv[1], b[2] + k * mv[0], b[3] + k * mv[1]]
    rims, sides = [], set()
    for r_ in p.get('rules_dropped') or []:
        r_ = sh(r_); v = r_[3] - r_[1] >= r_[2] - r_[0]
        if (r_[2] - r_[0] if v else r_[3] - r_[1]) > 0.025 * (p['w'] if v else p['h']): continue   # not a thin band
        if v:
            if r_[0] >= box[2]: long_ = [r_[0], crop[1], crop[2], crop[3]]; sides.add('R')
            elif r_[2] <= box[0]: long_ = [crop[0], crop[1], r_[2], crop[3]]; sides.add('L')
            else: continue
        else:
            if r_[3] <= box[1]: long_ = [crop[0], crop[1], crop[2], r_[3]]; sides.add('T')
            elif r_[1] >= box[3]: long_ = [crop[0], r_[1], crop[2], crop[3]]; sides.add('B')
            else: continue
        others = [sh(x) for x in (p.get('lines') or []) + (p.get('rules') or [])] + list(p.get('blots') or []) + list(p.get('edge') or [])
        if hit(long_, box, -0.5) or any(hit(long_, o) for o in others): continue   # print (or anything) out there: left
        rims.append(long_)
    if {'L', 'R'} <= sides or {'T', 'B'} <= sides: rims = []
    out = []
    for b in rims:
        if not hit(b, crop): continue
        o = unturn(sh(b, -1)); e = 1.5
        out.append([o[0] - e, o[1] - e, o[2] + e, o[3] + e])
    # A SHADOW PRINTED AS DOTS (dot_fields, already in the page's own coordinates; 4 pt from any stroke by construction):
    # covered too, never inside the content box nor over a printed rule (owner: «أرنيها مصلحة»)
    if p.get('dots'):
        cr = unturn(sh(crop, -1))
        keep = [unturn(sh(x, -1)) for x in [box] + list(p.get('rules') or [])]
        keep = [[k[0] - 1.5, k[1] - 1.5, k[2] + 1.5, k[3] + 1.5] for k in keep]
        out += [q for d in p['dots'] if hit(d, cr, 2) for q in rect_minus(d, keep)]
    return out

def rect_minus(r, cuts):
    """the parts of rect r outside every rect of cuts (a stamp's patch kept off anything printed)"""
    parts = [r]
    for c in cuts:
        nxt = []
        for q in parts:
            if not (c[2] > q[0] and c[0] < q[2] and c[3] > q[1] and c[1] < q[3]): nxt.append(q); continue
            if c[1] > q[1]: nxt.append([q[0], q[1], q[2], c[1]])
            if c[3] < q[3]: nxt.append([q[0], c[3], q[2], q[3]])
            y0, y1 = max(q[1], c[1]), min(q[3], c[3])
            if c[0] > q[0]: nxt.append([q[0], y0, c[0], y1])
            if c[2] < q[2]: nxt.append([c[2], y0, q[2], y1])
        parts = [q for q in nxt if q[2] - q[0] > 0.5 and q[3] - q[1] > 0.5]
    return parts

def hide_stamp_annots(page):
    """AN UPLOADER'S STAMP MADE AS A PDF ANNOTATION (owner 2026-10-18, خزانة الأدب ج 2 ص 18: «فيمكن حذف ما بقي ظاهرا من
    الطابع» — the «dar-alkotob» octagon is a Stamp annotation over the page, so no patch beneath it can cover it): stamp and
    watermark annotations are set hidden (their flag only — the annotation stays in the file, the scan is untouched)"""
    n = 0
    for a in page.annots() or []:
        if a.type[1] in ('Stamp', 'Watermark') and not a.flags & pymupdf.PDF_ANNOT_IS_HIDDEN:
            a.set_flags(a.flags | pymupdf.PDF_ANNOT_IS_HIDDEN); n += 1
    return n

def erase_stamp(doc, page, inv, p):
    """an uploader's stamp on white paper (owner 2026-10-09: «or even: erase it»): a white patch drawn over it after the
    page's own content — inside the page's turn, so it follows the page; the scan itself stays byte for byte"""
    # (on near-white paper too, in the paper's own grey — owner 2026-10-14, خزانة الأدب ج 2 ص 18: a coloured stamp the box
    # cut in half; on darker or coloured paper a patch would show, and the stamp stays outside the box as far as it can)
    # (a stamp is covered in THE COLOUR OF THE PAGE AROUND IT — the median of a ring 8 pt wide around the patch — on any
    # paper: owner 2026-10-18, نظم تنقيح فتح الكريم «لو تستعمل أداة تجعل مكان الطابع مثل الخلفية»; the other marks only
    # on white paper, in its white)
    er = marks_to_erase(doc, page.number, p)
    # (a «rule» thicker than 1.2 % of the page is no rule — ص 93: the stamp and the running head read as one 52 pt band,
    # and the stamp's patch stopped at it, the stamp left in view)
    thin = lambda r: min(r[2] - r[0], r[3] - r[1]) <= 0.012 * max(p['w'], p['h'])
    printed = [x for x in (p.get('blots') or []) + (p.get('lines') or []) + [r for r in p.get('rules') or [] if thin(r)]
               + ([p['box']] if p.get('box') else [])]
    def to_rule(b):                                   # a stamp's box ends above a printed rule running through its lower
        X0, Y0, X1, Y1 = [int(round(v * z)) for v in b]   # part (نظم تنقيح فتح الكريم ص 93: the box reached 20 pt below the
        X0, Y0 = max(0, X0), max(0, Y0); X1, Y1 = min(pix.width, X1), min(pix.height, Y1)   # stamp, onto the head's rule)
        if X1 - X0 < 10 or Y1 - Y0 < 10: return b
        dark = (img[Y0:Y1, X0:X1].sum(2) < 3 * 128).mean(1)
        for k in range(int(0.6 * (Y1 - Y0)), Y1 - Y0):
            if dark[k] >= 0.4: return [b[0], b[1], b[2], (Y0 + k) / z - 2]
        return b
    if not p.get('stamp') and not er and not (p.get('sheet_fill') and p.get('kind') == 'text'): return False
    z = 100 / 72; pix = page.get_pixmap(matrix=pymupdf.Matrix(z, z), colorspace=pymupdf.csRGB, alpha=False)
    img = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.stride)[:, :pix.width * 3].reshape(pix.height, pix.width, 3)
    stamps_ = [to_rule(pad_box(st, p['w'])) for st in p.get('stamp') or []]
    sts = [q for st in stamps_ for q in rect_minus(st, [x for x in printed if not inside(x, st, 0)])]   # (off the print)
    def around(b):                                    # the page's own colour around a box
        X0, Y0, X1, Y1 = [int(round(v * z)) for v in (b[0] - 8, b[1] - 8, b[2] + 8, b[3] + 8)]
        X0, Y0 = max(0, X0), max(0, Y0); X1, Y1 = min(pix.width, X1), min(pix.height, Y1)
        m = np.ones((max(0, Y1 - Y0), max(0, X1 - X0)), bool)
        ix0, iy0 = int(b[0] * z) - X0, int(b[1] * z) - Y0; ix1, iy1 = int(b[2] * z) - X0, int(b[3] * z) - Y0
        m[max(0, iy0):max(0, iy1), max(0, ix0):max(0, ix1)] = False
        ring = img[Y0:Y1, X0:X1][m]
        if len(ring) < 10: return (1.0, 1.0, 1.0)
        bright = ring[ring.sum(1) >= np.percentile(ring.sum(1), 40)]   # the paper, not a stray letter beside it
        return tuple(float(v) / 255 for v in np.median(bright, axis=0))
    if p.get('paper', 0) < 225: er = []
    # BEYOND THE SHEET'S EDGE (owner 2026-10-18, نظم تنقيح فتح الكريم ص 50: «في الحافة، ولك أن تملأها بنفس الخلفية» — the
    # grey page photographed a little askew on a white bed: its slanted edge inside the frame read as a tilt): the page
    # outside the sheet's inner rectangle is filled with the sheet's own colour, never over the content or anything printed
    fills = []; col_s = None
    if p.get('sheet_fill') and p.get('kind') == 'text':
        S = p['sheet_fill']; W_, H_ = p['w'], p['h']
        X0, Y0, X1, Y1 = [int(round(v * z)) for v in S]
        # EACH SIDE IN ITS OWN COLOUR — the paper just inside that edge (owner, ص 93 «غير متقنة بالمرة»: one colour for
        # all four, lighter than a sheet that darkens towards one edge, showed the seam); the ink of a line near the edge
        # is left out of the median
        def paper_of(px_):
            px_ = px_.reshape(-1, 3)
            if len(px_) < 20: return None
            sm = px_.sum(1); px_ = px_[sm >= np.median(sm) - 30]
            return tuple(float(v) / 255 for v in np.median(px_, axis=0))
        sides = [paper_of(img[Y0:Y0 + 8, X0:X1]), paper_of(img[Y1 - 8:Y1, X0:X1]), paper_of(img[Y0:Y1, X0:X0 + 8]), paper_of(img[Y0:Y1, X1 - 8:X1])]
        if all(sides):
            col_s = tuple(float(v) for v in np.median(np.array(sides), axis=0))
            strips = list(zip([[0, 0, W_, S[1]], [0, S[3], W_, H_], [0, S[1], S[0], S[3]], [S[2], S[1], W_, S[3]]], sides))
            # (only what lies wholly inside the sheet is print: a «rule» across its inner edge is the sheet's own edge or
            # its shadow — kept off, it left a white line of the bed along the bottom (نظم تنقيح فتح الكريم ص 93, owner «غير
            # متقنة بالمرة»); the stamps are not kept off either: their patches are in the same colour, and a 2 pt ring kept
            # around them showed the bed as white outlines)
            inS = lambda x: x[0] >= S[0] - 1 and x[2] <= S[2] + 1 and x[1] >= S[1] - 1 and x[3] <= S[3] + 1
            mv_ = p.get('move') or [0, 0]; tb = p.get('text')    # (the text block, not the box: the box took in that edge)
            tb = [tb[0] + mv_[0], tb[1] + mv_[1], tb[2] + mv_[0], tb[3] + mv_[1]] if tb else p.get('box')
            keep_off = [x for x in (p.get('blots') or []) + (p.get('lines') or []) + (p.get('rules') or []) + (p.get('margin') or [])
                        if inS(x)] + ([tb] if tb else [])
            for st, col in strips:
                for q in rect_minus(st, [[x[0] - 2, x[1] - 2, x[2] + 2, x[3] + 2] for x in keep_off]):
                    fills.append((q, col))
            def side_col(b):                          # a stamp's patch: the colour of the sheet's side nearest to it
                cx_, cy_ = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2
                return sides[int(np.argmin([abs(cy_ - S[1]), abs(cy_ - S[3]), abs(cx_ - S[0]), abs(cx_ - S[2])]))]
    cmd = ''
    for b, col in fills:                              # (first: the stamps' patches go over them)
        a_, b_ = pymupdf.Point(b[0], b[1]) * inv, pymupdf.Point(b[2], b[3]) * inv
        x0, y0, x1, y1 = min(a_.x, b_.x), min(a_.y, b_.y), max(a_.x, b_.x), max(a_.y, b_.y)
        cmd += f'{col[0]:.3f} {col[1]:.3f} {col[2]:.3f} rg {x0:.2f} {y0:.2f} {x1 - x0:.2f} {y1 - y0:.2f} re f '
    rim = col_s or (min(1.0, p.get('paper', 255) / 255),) * 3   # (a page on a bed: its rims in its own colour, not the bed's)
    for b, col in [(b, side_col(b) if col_s else around(b)) for b in sts] + [(b, rim) for b in er]:   # (on a bed: the page's own colour —
                                                      # «أريد أن تملأ بما يشبه الورقة تماما»)
        a_, b_ = pymupdf.Point(b[0], b[1]) * inv, pymupdf.Point(b[2], b[3]) * inv
        x0, y0, x1, y1 = min(a_.x, b_.x), min(a_.y, b_.y), max(a_.x, b_.x), max(a_.y, b_.y)
        cmd += f'{col[0]:.3f} {col[1]:.3f} {col[2]:.3f} rg {x0:.2f} {y0:.2f} {x1 - x0:.2f} {y1 - y0:.2f} re f '
    # the page's own drawing may end with a clip still active (its image's area): it is closed first («q … Q» around
    # it), so the patches can reach beyond the photographed page (نظم تنقيح فتح الكريم ص 4 و88: the fill was clipped away)
    wrap_contents(doc, page, b'q\n')
    return append_contents(doc, page, f'q {cmd}Q\n'.encode())

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
    if rec.get('split'): imgs, n = split_first(dst, rec, imgs)
    doc = pymupdf.open(dst); done = turned_n = scaled_n = 0
    W, H = rec['size']
    for i, p in enumerate(rec['pages']):
        page = doc[i]
        if hide_stamp_annots(page): page = doc[i]       # (an annotation stamp hidden: the page read afresh)
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

def split_first(dst, rec, imgs):
    """the recipe's split done on dst (incremental): the expected images per page (a split sheet's two pages show the same
    images) and the new page count"""
    d = pymupdf.open(dst); split_pages(d, rec['split']); d.save(dst, incremental=True, encryption=pymupdf.PDF_ENCRYPT_KEEP); d.close()
    out = []
    for i, im in enumerate(imgs):
        out.append(im)
        if str(i) in rec['split']: out.append(im)
    return out, len(out)

def apply_level(src, rec, dst):
    """LOSSLESS, a level-only book: the tilted pages' turn («q … cm» / «Q»); on grey or colour paper every page's CropBox
    inset by the same thin strip. Incremental save; checked: same pages, same images, every page of its intended size"""
    import shutil
    shutil.copyfile(src, dst)
    before = pymupdf.open(src); imgs = images_of(before); n = len(before)
    if rec.get('split'): before.close(); imgs, n = split_first(dst, rec, imgs); before = pymupdf.open(dst)
    want = []
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
    doc = split_open(src, rec); made = []; reasons = {}
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
        t = pymupdf.open(); t.insert_pdf(doc, from_page=i, to_page=i)     # what apply() draws: the stamp erased, then the turn
        hide_stamp_annots(t[0]); erase_stamp(t, t[0], ~t[0].transformation_matrix, p)
        mv = p.get('move') or [0, 0]
        if p.get('skew') or any(mv): rotate_contents(t, t[0], p.get('skew') or 0, mv[0], mv[1])
        t = pymupdf.open('pdf', t.tobytes())          # drawn from the finished page (a page object kept in memory does not
        page = t[0]                                   # show the patches appended to it: خزانة الأدب ج 2 ص 18, 2026-10-18)
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
