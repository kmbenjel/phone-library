"""Rebuild a book whose two-page spreads were split along the wrong axis (or shown sideways) from its own scan images
(owner 2026-10-14 on plan 320 «cropping should be redone, it was horrible», «to be fixed and every 2 pages divided»;
2026-10-18 on book 414 «أرني»): one page per distinct page image, in the file's order, the image drawn upright over the
whole page — the image streams are the file's own objects, never decoded or re-encoded (LOSSLESS for the scan). The
result is a file of whole spreads for scripts/book_crop.py, which splits each spread into its right and left page
(right first) and crops them. Page height = the old page's height; width from the image's own proportions.
Usage: python3 scripts/spreads_from_images.py IN.pdf OUT.pdf [--rotate 90|180|270]"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import book_crop  # noqa: F401  (sets up pymupdf's path)
import pymupdf

def main(src, dst, rot=0):
    doc = pymupdf.open(src); k = doc.page_count; order = []
    for i in range(k):
        for x in doc[i].get_images(full=True):
            if x[0] not in order and x[2] * x[3] > 0.3 * max(1, max(y[2] * y[3] for y in doc[i].get_images(full=True))): order.append(x[0])
    h = doc[0].rect.height; before = sorted(len(doc.xref_stream_raw(x) or b'') for x in order)
    for x in order:
        w_px, h_px = next((y[2], y[3]) for i in range(k) for y in doc[i].get_images(full=True) if y[0] == x)
        if rot in (90, 270): w_px, h_px = h_px, w_px
        p = doc.new_page(width=round(h * w_px / h_px, 2), height=h)
        p.insert_image(p.rect, xref=x, rotate=rot)
    doc.delete_pages(list(range(k)))
    doc.save(dst, garbage=3, deflate=False)
    out = pymupdf.open(dst)
    raw = lambda d: sorted(len(d.xref_stream_raw(y[0]) or b'') for p in d for y in p.get_images(full=True))
    print(f'{k} pages → {out.page_count} spreads; images {len(order)}; streams identical in size:', raw(out) == before)

if __name__ == '__main__':
    a = sys.argv[1:]; rot = int(a[a.index('--rotate') + 1]) if '--rotate' in a else 0
    main(a[0], a[1], rot)
