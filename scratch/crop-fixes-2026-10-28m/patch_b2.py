"""Fix B2 (2026-10-28, the bench of fixes L + B on خريدة القصر 01 0648): THE SCANNER BANDS AS SCANNED ARE NO INK ON A TURNED
PAGE, AND THE OFF-BAND SLIDE NEVER PUSHES THE BOX OUT OF THE FRAME. Fix B carried the bands read before the turn into the
turned page's allowed area; three pages it newly left whole (634 at 1.75°, 652 at 2.525°, 660 at 1.525° — 27l cropped them
with a black wedge down the left side) show why that is not enough:
(1) turned, a band's outermost columns take in the turn's blank wedge and fall under bands()' 60 % (ص 634: 0.52) — the band
    is read as the page's own ink: the content box runs to the sheet's edge, the band becomes «rules», and where a table's
    rules reach it the band and the table are one mark, a «picture» from the sheet's edge to the text (ص 636 and 644, whole
    in 27l too). Now, on a side where bands() reads no band on the turned page, the band read on the page as scanned,
    turned with it (band_mask), is no ink, and the paper's edge shadow beside it is found along its turned edge (thin by
    its ink: slanted); where bands() still reads the band (a small turn) marks() is unchanged — its trim and the edge
    shadow beside it read as before. REJECTED on the bench: the band no ink on every side (ص 406: the band's grey rim
    carried the text block 12 pt); the measured area starting at the band's outermost edge (ص 652 at 2.5°: a table's grid
    and a header word read as the sheet's edge); the sheet's outer 3 % (no letter there) measured from the band's turned
    edge (123 pages lost line ends running within 18 pt of the band — 638, 694: the table's first column, an index's left
    column — and the book's width fell 2.7 pt). The first look
    measures the turned page once more so when its turn is decided (the turn itself is decided as before), and the second
    look's crop checks read the turned page so (look(carry=True)); the recipe keeps the bands as scanned (bands0) and marks
    a page whose box or text they changed (band_ink, band_ink2).
(2) decide()'s off-band slide stops 4 pt from the text — but the box holds more than the text: on ص 634 the table's head
    rules run past its text (66.1) to the sheet's edge (51.4); the slanted band's corner comes into the box at its foot,
    the slide cut the rules and the page was left whole, both bands shown entire. Now the slide never passes the box's
    edge (band_box: how far the box held it back): the band shows as little as the box allows.
Usage: patch_b2.py SRC DST   (SRC = book_crop with fixes L and B: code2/bc_lb.py)"""
import sys
src, dst = sys.argv[1:3]
s = open(src, encoding='utf-8').read()

def sub(old, new):
    global s
    assert s.count(old) == 1, old[:80]
    s = s.replace(old, new)

sub('''def marks(a, scale, width, exclude=None):
    """ink marks of one page, in pt (page.rect coordinates) → dict:
       box     every content mark;  core  the text block (2–98 % of the content ink: where the page is centred);
       specks  isolated specks;  blots  stains and edge streaks (neither text nor print: left outside the box);
       allowed where the box may go (inside scanner bands and edge shadows);  dark  share of dark pixels;
       xy      content ink pixels (x, y in pixels) for the skew estimate.
    scale = pixels per pt, width = the page width in pt (M and SPECK are scaled to it)"""''',
'''def marks(a, scale, width, exclude=None, band=None):
    """ink marks of one page, in pt (page.rect coordinates) → dict:
       box     every content mark;  core  the text block (2–98 % of the content ink: where the page is centred);
       specks  isolated specks;  blots  stains and edge streaks (neither text nor print: left outside the box);
       allowed where the box may go (inside scanner bands and edge shadows);  bands  inside the scanner bands alone;
       dark    share of dark pixels;  xy  content ink pixels (x, y in pixels) for the skew estimate.
    scale = pixels per pt, width = the page width in pt (M and SPECK are scaled to it); band: the scanner bands read before
    a turn, turned with the page (band_mask, one bit a side) — no ink on a side where the turned page shows no band"""''')

sub('''    out['dark'] = float(mask.mean()); out['paper'] = paper
    r0, r1, c0, c1 = bands(mask)
    m = mask[r0:r1, c0:c1]
    allowed = [c0 / scale, r0 / scale, c1 / scale, r1 / scale]; out['allowed'] = allowed
''', '''    out['dark'] = float(mask.mean()); out['paper'] = paper
    r0, r1, c0, c1 = bands(mask)
    # A SCANNER BAND THE TURNED PAGE LOST IS TAKEN FROM THE PAGE AS SCANNED (fix B2, 2026-10-28): turned, a band's outermost
    # column takes in the turn's blank wedge and can fall under bands()' 60 % (خريدة القصر 0648 ص 634: 0.52 at 1.75°, ص 422:
    # 0.60 at 0.45°) — the band was then read as the page's ink: the content box ran to the sheet's edge, the band became
    # «rules», and where a table's rules reach it the two were one mark, a «picture» from the sheet's edge to the text (ص 636,
    # 644: the pages stayed whole). On a side where bands() reads no band, the band read before the turn is no ink; where it
    # still reads one (a small turn), its trim and the edge shadow beside it are read as before
    if band is not None:
        lost = (1 if c0 == 0 else 0) | (2 if r0 == 0 else 0) | (4 if c1 == mask.shape[1] else 0) | (8 if r1 == mask.shape[0] else 0)
        band = (band & lost) != 0
        if band.any(): mask = mask & ~band
        else: band = None
    m = mask[r0:r1, c0:c1]
    allowed = [c0 / scale, r0 / scale, c1 / scale, r1 / scale]; out['allowed'] = allowed; out['bands'] = list(allowed)
''')

sub('''    H, Wd = m.shape
''', '''    H, Wd = m.shape
    if band is not None:                            # (the lost band's turned edge, row by row and column by column: m pixels
        bb = band[r0:r1, c0:c1]; fr, fc = bb.all(1), bb.all(0)   # of band from each side, 0 where there is none)
        eL, eR = np.where(fr, 0, bb.argmin(1)), np.where(fr, 0, bb[:, ::-1].argmin(1))
        eT, eB = np.where(fc, 0, bb.argmin(0)), np.where(fc, 0, bb[::-1].argmin(0))
''')

sub('''    for i in shadow:                                  # the box keeps out of a shadow, as out of a scanner band
        s = objs[i - 1]
        if s[1].start <= 1 and hgt[i] >= 0.4 * H: allowed[0] = max(allowed[0], (s[1].stop + c0) / scale)
        elif s[1].stop >= Wd - 1 and hgt[i] >= 0.4 * H: allowed[2] = min(allowed[2], (s[1].start + c0) / scale)
        elif s[0].start <= 1: allowed[1] = max(allowed[1], (s[0].stop + r0) / scale)
        else: allowed[3] = min(allowed[3], (s[0].start + r0) / scale)
''', '''    for i in shadow:                                  # the box keeps out of a shadow, as out of a scanner band
        s = objs[i - 1]
        if s[1].start <= 1 and hgt[i] >= 0.4 * H: allowed[0] = max(allowed[0], (s[1].stop + c0) / scale)
        elif s[1].stop >= Wd - 1 and hgt[i] >= 0.4 * H: allowed[2] = min(allowed[2], (s[1].start + c0) / scale)
        elif s[0].start <= 1: allowed[1] = max(allowed[1], (s[0].stop + r0) / scale)
        else: allowed[3] = min(allowed[3], (s[0].start + r0) / scale)
    # (fix B2) THE EDGE SHADOW ALONG A BAND THE TURNED PAGE LOST lies along the band's turned edge, not along the image's: the
    # paper's grey rim beside the band, read before the turn as a shadow, was read as a streak (blot) and took the line ends
    # beside it with it as its «detached pieces» (ص 694: «٣١٠»، «٢٨٨» — the text block 32 pt short). Touching the band's
    # edge where it lies outermost along the mark, long along it, thin by its ink (its area over its length: slanted)
    if band is not None:
        for i, s in enumerate(objs, 1):
            if i in shadow: continue
            y0, y1, x0, x1 = s[0].start, s[0].stop, s[1].start, s[1].stop
            if hgt[i] >= 0.4 * H and area[i] / hgt[i] <= 0.06 * Wd:
                l_, r_ = eL[y0:y1][eL[y0:y1] > 0], eR[y0:y1][eR[y0:y1] > 0]
                if len(l_) and x0 <= l_.min() + 1: shadow.add(i); allowed[0] = max(allowed[0], (x1 + c0) / scale)
                elif len(r_) and x1 >= Wd - r_.min() - 1: shadow.add(i); allowed[2] = min(allowed[2], (x0 + c0) / scale)
            elif wid[i] >= 0.4 * Wd and area[i] / wid[i] <= 0.06 * H:
                t_, b_ = eT[x0:x1][eT[x0:x1] > 0], eB[x0:x1][eB[x0:x1] > 0]
                if len(t_) and y0 <= t_.min() + 1: shadow.add(i); allowed[1] = max(allowed[1], (y1 + r0) / scale)
                elif len(b_) and y1 >= H - b_.min() - 1: shadow.add(i); allowed[3] = min(allowed[3], (y0 + r0) / scale)
''')

sub('''    faint = a[r0:r1, c0:c1] < paper - 20
''', '''    faint = a[r0:r1, c0:c1] < paper - 20
    if band is not None: faint &= ~band[r0:r1, c0:c1]   # (a band is no faint rule either: ص 634's «rules» at 37–60 pt)
''')

sub('''    tl, tr, br, bl = [pymupdf.Point(x, y) * m for x, y in ((b[0], b[1]), (b[2], b[1]), (b[2], b[3]), (b[0], b[3]))]
    return [max(tl.x, bl.x), max(tl.y, tr.y), min(tr.x, br.x), min(bl.y, br.y)]
''', '''    tl, tr, br, bl = [pymupdf.Point(x, y) * m for x, y in ((b[0], b[1]), (b[2], b[1]), (b[2], b[3]), (b[0], b[3]))]
    return [max(tl.x, bl.x), max(tl.y, tr.y), min(tr.x, br.x), min(bl.y, br.y)]

def band_mask(doc, i, p, b, shape, z):
    """THE SCANNER BANDS AS SCANNED, ON THE PAGE TURNED AND MOVED LIKE p (fix B2, 2026-10-28): b, the area inside the bands
    bands() read on the page as scanned (pt; only the sides that have one), its edges turned with the page → the pixels of an
    image of that view (shape, z pixels per pt) lying beyond them, one pixel's allowance in (the turn resamples the edge),
    one bit a side (1 left, 2 head, 4 right, 8 foot: marks() takes a side only where the turned page shows no band)"""
    page = doc[i]; mv = p.get('move') or [0, 0]; deg = p.get('skew') or 0
    tm = page.transformation_matrix; mb = raw_box(doc, page.xref, 'MediaBox'); cx, cy = (mb[0] + mb[2]) / 2, (mb[1] + mb[3]) / 2
    fwd = pymupdf.Matrix(1, 0, 0, 1, -cx, -cy) * pymupdf.Matrix(deg) * pymupdf.Matrix(1, 0, 0, 1, cx, cy) * pymupdf.Matrix(1, 0, 0, 1, mv[0], -mv[1])
    m = ~tm * fwd * tm; w, h = page.rect.width, page.rect.height; e = 1 / z
    ys, xs = (np.arange(shape[0]) + 0.5) / z, (np.arange(shape[1]) + 0.5) / z
    out = np.zeros(shape, np.uint8)
    for k, has in enumerate((b[0] > 0.5, b[1] > 0.5, b[2] < w - 0.5, b[3] < h - 0.5)):
        if not has: continue
        if k in (0, 2):                               # a band down a side: its edge, from the head to the foot, turned
            p0, p1 = pymupdf.Point(b[k], 0) * m, pymupdf.Point(b[k], h) * m
            xe = p0.x + (ys - p0.y) * (p1.x - p0.x) / (p1.y - p0.y)
            out |= (xs[None, :] < (xe + e)[:, None] if k == 0 else xs[None, :] > (xe - e)[:, None]).astype(np.uint8) << k
        else:                                         # a band across the head or the foot
            p0, p1 = pymupdf.Point(0, b[k]) * m, pymupdf.Point(w, b[k]) * m
            ye = p0.y + (xs - p0.x) * (p1.y - p0.y) / (p1.x - p0.x)
            out |= (ys[:, None] < (ye + e)[None, :] if k == 1 else ys[:, None] > (ye - e)[None, :]).astype(np.uint8) << k
    return out
''')

sub('''        al0 = None
        if mk['box'] is not None and mk['dark'] <= 0.35:     # a tilted text page: turn it level (the sign is checked)
''', '''        al0 = None; bnd0 = mk.get('bands')                # (the scanner bands alone, as scanned: fix B2)
        if mk['box'] is not None and mk['dark'] <= 0.35:     # a tilted text page: turn it level (the sign is checked)
''')

sub('''                        break
        if tu_: tu_[0].close()
        # THE BANDS AS SCANNED BOUND THE PAGE WHATEVER ITS TURN (fix B, 2026-10-28)''', '''                        break
        # THE TURNED PAGE MEASURED WITHOUT ITS SCANNER BANDS AS SCANNED (fix B2, 2026-10-28): its turn decided as before —
        # every path above measured the turned page with its bands as the turn's blank wedge left them —, its content, text
        # and margins are read with the bands no ink (band_mask); the bands as scanned are kept for the second look (bands0)
        if bnd0 and mk['box'] is not None and mk['dark'] <= 0.35 \\
           and (bnd0[0] > 0.5 or bnd0[1] > 0.5 or bnd0[2] < r.width - 0.5 or bnd0[3] < r.height - 0.5):
            rec['bands0'] = [round(v, 2) for v in bnd0]
            if rec.get('skew'):
                q_ = {'skew': rec['skew']}; a2, z2 = gray(tu().page(rec['skew']), 500)
                a2 = whiten(a2, z2, fwd_box(doc, i, q_, sh) if sh else None)
                mk2 = marks(a2, z2, r.width, fwd_boxes(doc, i, q_, ex0) if ex0 else None, band_mask(doc, i, q_, bnd0, a2.shape, z2))
                if mk2['box'] is not None:
                    if mk2['box'] != mk['box'] or mk2.get('text') != mk.get('text'): rec['band_ink'] = True
                    al_ = mk.get('allowed') or mk2['allowed']   # (the allowed area as the turn's paths read it stays)
                    mk2['allowed'] = [max(mk2['allowed'][0], al_[0]), max(mk2['allowed'][1], al_[1]),
                                      min(mk2['allowed'][2], al_[2]), min(mk2['allowed'][3], al_[3])]
                    mk = mk2
        if tu_: tu_[0].close()
        # THE BANDS AS SCANNED BOUND THE PAGE WHATEVER ITS TURN (fix B, 2026-10-28)''')

sub('''        if al and bx and tb and p['kind'] == 'text':
            for k0, k1, lo_i, hi_i in ((0, 2, 0, 2), (1, 3, 1, 3)):
                over_hi, over_lo = b[k1] - al[hi_i], al[lo_i] - b[k0]
                if over_hi > 1 and over_lo <= 0:
                    sh = -min(over_hi + 1, b[k0] - al[lo_i], max(0, (b[k1] - tb[k1]) - 4))
                elif over_lo > 1 and over_hi <= 0:
                    sh = min(over_lo + 1, al[hi_i] - b[k1], max(0, (tb[k0] - b[k0]) - 4))
                else: continue
''', '''        if al and bx and tb and p['kind'] == 'text':
            for k0, k1, lo_i, hi_i in ((0, 2, 0, 2), (1, 3, 1, 3)):
                over_hi, over_lo = b[k1] - al[hi_i], al[lo_i] - b[k0]
                # (never past the box's edge — what the page must show: a slide to 4 pt from the text that cuts into the box
                # leaves the page whole, both bands shown entire — خريدة القصر 0648 ص 634, 652, 660 turned 1.5–2.5°: a table's
                # rules reach out past its text to the sheet's edge, the slanted band's corner comes into the box; fix B2)
                if over_hi > 1 and over_lo <= 0:
                    s0 = min(over_hi + 1, b[k0] - al[lo_i], max(0, (b[k1] - tb[k1]) - 4)); s1 = min(s0, max(0, b[k1] - bx[k1])); sh = -s1
                elif over_lo > 1 and over_hi <= 0:
                    s0 = min(over_lo + 1, al[hi_i] - b[k1], max(0, (tb[k0] - b[k0]) - 4)); s1 = min(s0, max(0, bx[k0] - b[k0])); sh = s1
                else: continue
                if s0 - s1 > 0.05: p['band_box'] = round(s0 - s1, 1)   # (how far the box held the slide back)
''')

sub('''    def look(i, q):                                   # the same view is never measured twice (2026-10-25, speed: the
        if cur['i'] != i:                             # first look's angle came back in best_turn, the trial turns of an
            if cur['tu']: cur['tu'].close()           # untouched page in it too)
            cur.update(i=i, tu=Turner(doc, i), looks={})
        mv = q.get('move') or [0, 0]; key = (q.get('skew') or 0, mv[0], mv[1])
        if key in cur['looks']: return cur['looks'][key]
        page = cur['tu'].page(*key); a, z = gray(page, px); st = rec['pages'][i].get('stamp')   # the page as the reader
        if rec['pages'][i].get('sheet'): a = whiten(a, z, fwd_box(doc, i, q, rec['pages'][i]['sheet']))   # will see it, at px
        ex = [pad_box(b, page.rect.width) for b in st or []] + (rec['pages'][i].get('dots') or [])
        mk = marks(a, z, page.rect.width, fwd_boxes(doc, i, q, ex) if ex else None); mk['z'] = z
''', '''    def look(i, q, carry=False):                      # the same view is never measured twice (2026-10-25, speed: the
        if cur['i'] != i:                             # first look's angle came back in best_turn, the trial turns of an
            if cur['tu']: cur['tu'].close()           # untouched page in it too)
            cur.update(i=i, tu=Turner(doc, i), looks={})
        mv = q.get('move') or [0, 0]; key = (q.get('skew') or 0, mv[0], mv[1])
        b0 = rec['pages'][i].get('bands0') if carry and key[0] else None   # (carry: the scanner bands as scanned are no ink
        if (key, b0 is not None) in cur['looks']: return cur['looks'][(key, b0 is not None)]   # on the turned page — fix B2)
        page = cur['tu'].page(*key); a, z = gray(page, px); st = rec['pages'][i].get('stamp')   # the page as the reader
        if rec['pages'][i].get('sheet'): a = whiten(a, z, fwd_box(doc, i, q, rec['pages'][i]['sheet']))   # will see it, at px
        ex = [pad_box(b, page.rect.width) for b in st or []] + (rec['pages'][i].get('dots') or [])
        mk = marks(a, z, page.rect.width, fwd_boxes(doc, i, q, ex) if ex else None,
                   band_mask(doc, i, q, b0, a.shape, z) if b0 else None); mk['z'] = z
''')

sub('''        cur['looks'][key] = mk
        return mk
''', '''        cur['looks'][(key, b0 is not None)] = mk
        return mk
''')

sub('''        if tilt_only or not p.get('crop'): continue
        c = p['crop']; known = ''', '''        if tilt_only or not p.get('crop'): continue
        if p.get('skew') and p.get('bands0'):         # the crop checks read the turned page without its scanner bands as
            mc = look(i, p, carry=True)                # scanned (fix B2: the turn's blank wedge hides a band from bands())
            if mc.get('box') != mk.get('box') or mc.get('text') != mk.get('text'): p['band_ink2'] = True
            mk = mc
        c = p['crop']; known = ''')

open(dst, 'w', encoding='utf-8').write(s)
print('patched', dst)
