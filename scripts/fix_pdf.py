"""Repair one scanned PDF for comfortable reading on a phone, without touching the original.
Needs PyMuPDF + pypdf: PYTHONPATH=~/.local/share/phone-library-tools/site (official wheels, see AGENTS.md §6).

  crop        LOSSLESS: each page's CropBox is set to its content (+3 % padding). Pages are not re-encoded, so the
              file keeps its size; the reader simply shows the text larger. Odd and even pages share a box (the union
              of their typical content box), widened per page when that page has content outside it — nothing is cut.
              Solid dark scanner bands at the page edges are excluded from the content.
  split       landscape spreads (two book pages on one PDF page) → two pages, right half first (Arabic books),
              lossless (same image, two CropBoxes).
  recompress  LOSSY: page images → gray JPEG (quality 60) at most 200 ppi; for bloated colour scans of text.
              Every page is checked afterwards: same count, opens.
Usage: fix_pdf.py in.pdf out.pdf [--crop] [--split] [--recompress] [--boxes boxes.json]
       --boxes writes the computed crop boxes (a «recipe» to apply later without recomputing)."""
import json, statistics, sys
import pymupdf

DARK = bytes(1 if v < 150 else 0 for v in range(256))

def content_box(page, dpi=24):
    """Content rectangle in page.rect coordinates (what the reader shows), from a 24-dpi gray render."""
    pix = page.get_pixmap(dpi=dpi, colorspace=pymupdf.csGRAY, alpha=False)
    w, h = pix.width, pix.height
    if w < 8 or h < 8: return None
    s = pix.samples.translate(DARK)                 # 1 = dark pixel
    rows = [s[y * w:(y + 1) * w].count(1) / w for y in range(h)]
    cols = [s[x::w].count(1) / h for x in range(w)]
    def trim(a):                                    # skip solid dark scanner bands at both ends
        i, j = 0, len(a) - 1
        band_i, band_j = i, j
        while i < j and a[i] > 0.5: i += 1
        while j > i and a[j] > 0.5: j -= 1
        if i > band_i and a[i] > 0.3: i += 1            # the blurred edge of a band
        if j < band_j and a[j] > 0.3: j -= 1
        return i, j
    r0, r1 = trim(rows); c0, c1 = trim(cols)
    ink_r = [y for y in range(r0, r1 + 1) if 0.004 < rows[y] < 0.9]
    ink_c = [x for x in range(c0, c1 + 1) if 0.004 < cols[x] < 0.9]
    if len(ink_r) < 3 or len(ink_c) < 3: return None
    r = page.rect
    sx, sy = r.width / w, r.height / h
    box = pymupdf.Rect(ink_c[0] * sx, ink_r[0] * sy, (ink_c[-1] + 1) * sx, (ink_r[-1] + 1) * sy)
    box.allowed = pymupdf.Rect(c0 * sx, r0 * sy, (c1 + 1) * sx, (r1 + 1) * sy)     # inside the dark bands
    return box

def crop_boxes(doc):
    boxes = [content_box(p) for p in doc]
    out = []
    for parity in (0, 1):
        idx = [i for i in range(len(doc)) if i % 2 == parity and boxes[i] is not None]
        if not idx: continue
        q = lambda vals, f: sorted(vals)[int(f * (len(vals) - 1))]
        typical = pymupdf.Rect(q([boxes[i].x0 for i in idx], 0.10), q([boxes[i].y0 for i in idx], 0.10),
                               q([boxes[i].x1 for i in idx], 0.90), q([boxes[i].y1 for i in idx], 0.90))
        for i in range(parity, len(doc), 2):
            page = doc[i]; r = page.rect
            b = typical | boxes[i] if boxes[i] is not None else pymupdf.Rect(typical)
            pad_x, pad_y = 0.03 * r.width, 0.03 * r.height
            lim = getattr(boxes[i], 'allowed', r) if boxes[i] is not None else r
            b = pymupdf.Rect(max(lim.x0, b.x0 - pad_x), max(lim.y0, b.y0 - pad_y), min(lim.x1, b.x1 + pad_x), min(lim.y1, b.y1 + pad_y))
            if b.width < 0.4 * r.width or b.height < 0.4 * r.height: b = r     # implausible: leave the page whole
            out.append((i, [round(b.x0, 1), round(b.y0, 1), round(b.x1, 1), round(b.y1, 1)]))
    return dict(sorted(out))

def apply_crop(doc, boxes):
    """boxes are in page.rect coordinates (origin = the current CropBox corner); CropBox is set in MediaBox
    coordinates, so shift by the current CropBox origin. Rotated pages are left as they are."""
    for i, b in boxes.items():
        page = doc[int(i)]
        if page.rotation: continue
        cb, mb = page.cropbox, page.mediabox
        r = pymupdf.Rect(b[0] + cb.x0, b[1] + cb.y0, b[2] + cb.x0, b[3] + cb.y0) & mb
        if not r.is_empty: page.set_cropbox(r)

def split_spreads(doc):
    out = pymupdf.open()
    for page in doc:
        r = page.rect
        if r.width > r.height * 1.15:
            halves = [pymupdf.Rect(r.x0 + r.width / 2, r.y0, r.x1, r.y1), pymupdf.Rect(r.x0, r.y0, r.x0 + r.width / 2, r.y1)]  # right page first
            for hb in halves:
                np_ = out.new_page(width=hb.width, height=hb.height)
                np_.show_pdf_page(np_.rect, doc, page.number, clip=hb)
        else:
            out.insert_pdf(doc, from_page=page.number, to_page=page.number)
    return out

def recompress(doc, max_ppi=200, quality=60):
    done = set()
    for page in doc:
        for img in page.get_images(full=True):
            xref = img[0]
            if xref in done: continue
            done.add(xref)
            try:
                pix = pymupdf.Pixmap(doc, xref)
                if pix.n - pix.alpha > 1: pix = pymupdf.Pixmap(pymupdf.csGRAY, pix)
                bbox = page.get_image_bbox(img)
                if bbox.width > 0:
                    ppi = pix.width / (bbox.width / 72)
                    if ppi > max_ppi:
                        f = max_ppi / ppi
                        pix = pymupdf.Pixmap(pix, int(pix.width * f), int(pix.height * f), None)
                page.replace_image(xref, stream=pix.tobytes('jpeg', jpg_quality=quality))
            except Exception as e:
                print('skip image', xref, e, file=sys.stderr)

def images_of(doc):
    """every page's image list (xref, width, height, compressed length): proof that no image was touched"""
    return [[(x[0], x[2], x[3], len(doc.xref_stream_raw(x[0]) or b'')) for x in p.get_images(full=True)] for p in doc]

def uncrop(src, dst):
    """undo a crop (owner, 2026-10-07: the crops of plans 139/141/142 were wrong): every page shows its whole MediaBox again.
    Only the page dictionaries change (incremental save: every other byte of the file stays as it was), so no image,
    text layer or annotation can be lost; checked: same pages, same images byte for byte, every CropBox = MediaBox."""
    import shutil
    shutil.copyfile(src, dst)
    before = pymupdf.open(src); imgs = images_of(before); n = len(before); before.close()
    doc = pymupdf.open(dst); changed = 0
    for page in doc:
        mb = page.mediabox
        if page.cropbox != mb:
            try: page.set_cropbox(mb)
            except Exception:                                  # MuPDF refuses some boxes (offset or inherited MediaBox):
                raw = None                                     # copy the page's own MediaBox value into its CropBox key
                x = page.xref
                while x and raw is None:                       # MediaBox may be inherited from a Pages node
                    t, v = doc.xref_get_key(x, 'MediaBox')
                    if t == 'array': raw = v
                    else:
                        t2, par = doc.xref_get_key(x, 'Parent')
                        x = int(par.split()[0]) if t2 == 'xref' else 0
                if raw is None: raise
                doc.xref_set_key(page.xref, 'CropBox', raw)
            changed += 1
    if changed: doc.save(dst, incremental=True, encryption=pymupdf.PDF_ENCRYPT_KEEP)
    doc.close()
    chk = pymupdf.open(dst)
    assert len(chk) == n, 'page count changed'
    def box(d, x, key):                                    # a page's own or inherited box, as numbers
        while x:
            t, v = d.xref_get_key(x, key)
            if t == 'array': return tuple(round(float(z), 3) for z in v.strip('[] ').split())
            t, par = d.xref_get_key(x, 'Parent'); x = int(par.split()[0]) if t == 'xref' else 0
        return None
    # whole page = no CropBox, or a CropBox equal to the MediaBox (raw PDF values: MuPDF's rectangles are shifted on pages
    # whose MediaBox does not start at 0,0, so p.cropbox == p.mediabox can be false there although nothing is cut)
    assert all(p.cropbox == p.mediabox or box(chk, p.xref, 'CropBox') in (None, box(chk, p.xref, 'MediaBox'))
               for p in chk), 'a page still cropped'
    assert images_of(chk) == imgs, 'images changed'
    chk.close()
    return {'pages_in': n, 'pages_out': n, 'uncropped': changed, 'bytes_out': __import__('os').path.getsize(dst)}

def main():
    a = sys.argv[1:]
    src, dst = a[0], a[1]
    if '--uncrop' in a:
        print(json.dumps(uncrop(src, dst))); return
    if '--boxes-only' in a:                       # crop recipe only (used by inspect_files.py in a subprocess)
        json.dump(crop_boxes(pymupdf.open(src)), open(a[a.index('--boxes-only') + 1], 'w')); return
    doc = pymupdf.open(src); n0 = len(doc)
    if '--split' in a:
        doc = split_spreads(doc)
    if '--recompress' in a:
        recompress(doc)
    boxes = None
    if '--crop' in a:
        boxes = crop_boxes(doc); apply_crop(doc, boxes)
        if '--boxes' in a: json.dump(boxes, open(a[a.index('--boxes') + 1], 'w'))
    doc.save(dst, garbage=3, deflate=True)
    chk = pymupdf.open(dst)
    assert len(chk) == (len(doc)), 'page count changed'
    print(json.dumps({'pages_in': n0, 'pages_out': len(chk), 'cropped': len(boxes or {}),
                      'bytes_out': __import__('os').path.getsize(dst)}))

if __name__ == '__main__':
    main()
