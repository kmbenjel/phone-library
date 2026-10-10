"""Photographed pages → clean black-and-white pages, levelled, cropped to the text, one size for the book, enlarged
(owner 2026-10-10, «مصباح العقول بنظم أصول ابن باديس: أصلحه بجعله أبيض أسود وتقويمه وتكبيره»). LOSSY BY DESIGN, used only
when the owner asks for it (book_crop.py is the lossless method for ordinary scans).
Per page: the page rendered at its own resolution; the brightest of the three colour channels (black print stays black,
a camera's orange date stamp turns white); the lighting evened out (divided by its own wide blur: shadows, curvature);
Otsu black and white; the tilt measured on that image (jdeskew, then a check by the line profile) and levelled; the text
block = ink marks that are not specks and not attached to the photo's border; one box for the whole book (typical pages,
2 % margin), each page centred on its text; saved as 1-bit pages (lossless Flate) in a new PDF.
Usage: python3 scripts/bw_clean.py IN.pdf OUT.pdf [--dpi 300]"""
import sys, io, os
sys.path.insert(0, os.path.expanduser('~/.local/share/phone-library-tools/site'))   # PyMuPDF (as book_crop.py)
import numpy as np, cv2, pymupdf
from jdeskew.estimator import get_angle

def page_gray(page, zoom):
    pix = page.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom), colorspace=pymupdf.csRGB, alpha=False)
    rgb = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.stride)[:, :pix.width * 3].reshape(pix.height, pix.width, 3)
    return rgb.max(axis=2)                                    # black print dark in every channel; orange stamp bright in red

def even_light(v):
    k = max(31, (min(v.shape) // 12) | 1)
    bg = cv2.morphologyEx(v, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k)))   # paper without the print
    bg = cv2.GaussianBlur(bg, (0, 0), k / 3)
    return cv2.divide(v, np.maximum(bg, 1), scale=255)

def binarise(v):
    _, bw = cv2.threshold(v, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return bw                                                 # 255 paper, 0 ink

def level(bw):
    f = min(1.0, 1200.0 / max(bw.shape))                      # the angle from a smaller copy (much faster, same answer)
    a = get_angle(cv2.resize(bw, None, fx=f, fy=f, interpolation=cv2.INTER_AREA) if f < 1 else bw, angle_max=15)
    if abs(a) < 0.15: return bw, 0.0
    h, w = bw.shape
    M = cv2.getRotationMatrix2D((w / 2, h / 2), a, 1.0)
    out = cv2.warpAffine(bw, M, (w, h), flags=cv2.INTER_NEAREST, borderValue=255)
    def sharp(img):                                           # the line profile must get sharper, or the turn is undone
        p = (img < 128).sum(1).astype(float); return float(np.var(np.diff(p)))
    return (out, a) if sharp(out) >= sharp(bw) else (bw, 0.0)

def text_box(bw):
    """the text block, and the photo's junk painted white in bw: marks attached to the photo's border, bars (long and thin),
    solid blots (letters are never solid shapes), page edges and shadows"""
    ink = (bw < 128).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(ink, connectivity=8)
    h, w = bw.shape; keep = []; junk = np.zeros(n, bool)
    for i in range(1, n):
        x, y, cw, ch, a = st[i]
        if a < 40 or (cw <= 6 and ch <= 6): continue                          # specks: they do not decide the box
        fill = a / max(1, cw * ch)
        if (x <= 2 or y <= 2 or x + cw >= w - 2 or y + ch >= h - 2) \
           or cw > 0.9 * w or ch > 0.9 * h \
           or (cw > 0.25 * w and ch < 0.03 * h) or (ch > 0.25 * h and cw < 0.03 * w) \
           or (fill > 0.6 and a > 0.0004 * w * h):
            junk[i] = True; continue
        keep.append((x, y, x + cw, y + ch))
    bw[junk[lab]] = 255
    if not keep: return None
    B = np.array(keep)                               # the junk is gone: the whole extent of the rest, so a lone heading
    return [int(B[:, 0].min()), int(B[:, 1].min()), int(B[:, 2].max()), int(B[:, 3].max())]   # is never cut (p. 235)

def main(src, dst, dpi=300):
    doc = pymupdf.open(src); pages = []
    for page in doc:
        zoom = dpi / 72.0
        v = page_gray(page, min(zoom, 3000 / max(page.rect.width, page.rect.height)))
        bw, ang = level(binarise(even_light(v)))
        pages.append((bw, ang, text_box(bw)))
    boxes = [b for _, _, b in pages if b]
    ws = sorted(b[2] - b[0] for b in boxes); hs = sorted(b[3] - b[1] for b in boxes)
    q = lambda v, f: v[min(len(v) - 1, int(f * (len(v) - 1)))]
    mw, mh = q(ws, 0.5), q(hs, 0.5)
    W = q([x for x in ws if x <= 1.25 * mw] or ws, 0.95); H = q([x for x in hs if x <= 1.15 * mh] or hs, 0.98)
    mg = int(0.02 * W); W, H = W + 2 * mg, H + 2 * mg
    out = pymupdf.open()
    for bw, ang, b in pages:
        if not b: b = [0, 0, bw.shape[1], bw.shape[0]]
        cx, cy = (b[0] + b[2]) // 2, (b[1] + b[3]) // 2
        bw_ = max(W, b[2] - b[0] + 2 * mg); bh_ = max(H, b[3] - b[1] + 2 * mg)      # a larger page keeps all its text
        x0, y0 = cx - bw_ // 2, cy - bh_ // 2
        canvas = np.full((bh_, bw_), 255, np.uint8)
        sx0, sy0 = max(0, x0), max(0, y0); sx1, sy1 = min(bw.shape[1], x0 + bw_), min(bw.shape[0], y0 + bh_)
        canvas[sy0 - y0:sy1 - y0, sx0 - x0:sx1 - x0] = bw[sy0:sy1, sx0:sx1]
        t = mg // 2                                           # outside the text block (+ half the margin): the photo's
        tx0, ty0, tx1, ty1 = b[0] - x0 - t, b[1] - y0 - t, b[2] - x0 + t, b[3] - y0 + t   # dark surroundings, never print
        canvas[:max(0, ty0)] = 255; canvas[max(0, ty1):] = 255; canvas[:, :max(0, tx0)] = 255; canvas[:, max(0, tx1):] = 255
        if (bw_, bh_) != (W, H): canvas = cv2.resize(canvas, (W, H), interpolation=cv2.INTER_AREA)
        _, canvas = cv2.threshold(canvas, 127, 255, cv2.THRESH_BINARY)
        ok, png = cv2.imencode('.png', canvas, [cv2.IMWRITE_PNG_BILEVEL, 1])
        pw, ph = W * 72.0 / dpi, H * 72.0 / dpi
        pg = out.new_page(width=pw, height=ph); pg.insert_image(pg.rect, stream=png.tobytes())
    out.save(dst, deflate=True, garbage=4)
    print(f'{len(pages)} pages → {dst} ({W}×{H} px at {dpi} dpi); turned: {sum(1 for _, a, _ in pages if a)}')

if __name__ == '__main__':
    a = sys.argv[1:]
    main(a[0], a[1], int(a[a.index('--dpi') + 1]) if '--dpi' in a else 300)
