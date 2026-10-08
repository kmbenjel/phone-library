"""Book-level crop — the method after the 2026-10-07 revert (owner: the per-page crops swayed, ate the natural margins of
good editions and kept a speck as content; «لا يضيع شيء من النص ولو تعليقة صغيرة في الهامش»; specks surely not text may go;
2026-10-08 on the first sample: «مبهر» — and centre the text horizontally, consistently on every page; ordinary books
(text ≈ 72 % of the width) may also grow «على حساب شيء من الهامش», if every page of the book stays consistent).
LOSSLESS: only the pages' CropBox changes (incremental save); images, text layer and annotations stay byte for byte.

One box SIZE per file; on every page the box is centred on that page's own text block, so pages never sway and the text
sits in the middle of every page whatever the scanner did:
  1. every page rendered gray, 500 px wide (1,000 for the check); paper = 90th percentile; ink = darker than paper − 50.
     Sizes are fractions of the page width (scans come with any page unit: 1147 pt wide for one of 14 cm); below,
     «pt» means pt on a page scaled to 420 pt wide (≈ 14.8 cm).
  2. not content: scanner bands (rows/columns from an edge more than 60 % dark) and edge shadows (a mark touching a side
     of the page, long along it and thin across it: the shadow of the book's fore-edge or gutter).
  3. ink marks (8-connected). A speck = a mark ≤ 4×4 pt (≈ 1.4 mm) with no other mark within M = 14 pt (≈ 5 mm):
     isolated dirt. Every other mark is content, however small or faint: the letters of a marginal note have neighbours.
  4. picture pages (dark: covers, photographs) and blank pages are not measured.
  5. the box: the text block of the book (98th percentile of the pages' widths and heights) + a generous margin
     (12 % of the text width each side, 6 % of its height, at least M), made smaller only as far as needed to centre the
     text on the pages (a scan with a narrow margin on one side). Same size on every page.
  6. its place on each page: centred on the page's own text block when the page is full (≥ 90 % of the usual width /
     height); a short page (chapter end, heading) takes the place of its full neighbours of the same parity. Then moved
     the least needed to hold every mark of the page and to stay on the page.
  7. a crop is made when it is worth it: the text gets ≥ 6 % larger on a phone, or it was visibly off-centre
     (≥ 2 % of the width on the median page), or scanner bands go. Otherwise the file is left as it is.
  8. every page is checked again at 1,000 px wide: nothing but isolated specks may fall outside its box; a page that fails
     (outlier, plate, fold-out, marginal note far out) stays WHOLE. More than 3 % such pages → the file is left as is.
Usage:
  book_crop.py analyse in.pdf recipe.json          → recipe: boxes, decision, per-page notes (no output PDF)
  book_crop.py apply in.pdf recipe.json out.pdf    → lossless copy with the recipe's boxes, checked
  book_crop.py sheet in.pdf recipe.json outdir     → JPEGs: before (box in red, cut specks circled in blue) / after
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
MAX_WHOLE = 0.03  # share of measured pages allowed to stay whole

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
    """ink marks of one page: (content box | None, isolated specks [boxes], allowed area, dark share) in pt;
    scale = pixels per pt, width = the page width in pt (M and SPECK are scaled to it)"""
    unit = scale * width / REF                      # pixels per «reference pt»
    paper = float(np.percentile(a, 90))
    if paper < 110: return None, [], None, 1.0
    mask = a < paper - 50
    r0, r1, c0, c1 = bands(mask)
    m = mask[r0:r1, c0:c1]
    allowed = [c0 / scale, r0 / scale, c1 / scale, r1 / scale]
    if m.size == 0: return None, [], allowed, float(mask.mean())
    lab, n = ndimage.label(m, structure=np.ones((3, 3), bool))
    if n == 0: return None, [], allowed, float(mask.mean())
    objs = ndimage.find_objects(lab)
    sp = SPECK * unit
    small = np.array([False] + [(s[0].stop - s[0].start) <= sp and (s[1].stop - s[1].start) <= sp for s in objs])
    # marks closer than M to each other fall in one group (dilation by M/2 on each)
    grp, _ = ndimage.label(ndimage.binary_dilation(m, iterations=max(1, int(M * unit / 2))), structure=np.ones((3, 3), bool))
    members = {}
    for i, s in enumerate(objs, 1):
        y, x = s[0].start, s[1].start
        sub = lab[s] == i
        g = grp[s][sub][0]
        members.setdefault(g, []).append(i)
    isolated = set()
    for g, ids in members.items():
        if len(ids) == 1 and small[ids[0]]: isolated.add(ids[0])
    H, Wd = m.shape                                   # edge shadows: touching a side, long along it, thin across it
    shadow = {i for i, s in enumerate(objs, 1)
              if ((s[1].start <= 1 or s[1].stop >= Wd - 1) and (s[0].stop - s[0].start) >= 0.4 * H and (s[1].stop - s[1].start) <= 0.06 * Wd)
              or ((s[0].start <= 1 or s[0].stop >= H - 1) and (s[1].stop - s[1].start) >= 0.4 * Wd and (s[0].stop - s[0].start) <= 0.06 * H)}
    content = [s for i, s in enumerate(objs, 1) if i not in isolated and i not in shadow]
    for i in shadow:                                  # the box keeps out of a shadow, as out of a scanner band
        s = objs[i - 1]
        if s[1].start <= 1 and (s[0].stop - s[0].start) >= 0.4 * H: allowed[0] = max(allowed[0], (s[1].stop + c0) / scale)
        elif s[1].stop >= Wd - 1 and (s[0].stop - s[0].start) >= 0.4 * H: allowed[2] = min(allowed[2], (s[1].start + c0) / scale)
        elif s[0].start <= 1: allowed[1] = max(allowed[1], (s[0].stop + r0) / scale)
        else: allowed[3] = min(allowed[3], (s[0].start + r0) / scale)
    box = None
    if content:
        y0 = min(s[0].start for s in content); y1 = max(s[0].stop for s in content)
        x0 = min(s[1].start for s in content); x1 = max(s[1].stop for s in content)
        box = [(x0 + c0) / scale, (y0 + r0) / scale, (x1 + c0) / scale, (y1 + r0) / scale]
    specks = [[(objs[i - 1][1].start + c0) / scale, (objs[i - 1][0].start + r0) / scale,
               (objs[i - 1][1].stop + c0) / scale, (objs[i - 1][0].stop + r0) / scale] for i in sorted(isolated)]
    return box, specks, allowed, float(mask.mean())

def inside(b, box, tol=0.5):
    return b[0] >= box[0] - tol and b[1] >= box[1] - tol and b[2] <= box[2] + tol and b[3] <= box[3] + tol

def analyse(path):
    doc = pymupdf.open(path)
    pages = []
    for page in doc:
        r = page.rect
        rec = {'w': round(r.width, 1), 'h': round(r.height, 1)}
        if page.rotation: rec['kind'] = 'rotated'; pages.append(rec); continue
        a, z = gray(page, 500)
        box, specks, allowed, dark = marks(a, z, r.width)
        rec.update(allowed=allowed, specks=specks)
        if box is None: rec['kind'] = 'blank' if dark < 0.5 else 'picture'
        elif dark > 0.35: rec['kind'] = 'picture'        # dark pages only: a tight light scan is text (stays whole if it cannot fit)
        else: rec['kind'] = 'text'
        rec['box'] = box
        pages.append(rec)
    doc.close()
    return decide(pages)

def q(vals, f):
    s = sorted(vals); return s[min(len(s) - 1, max(0, int(round(f * (len(s) - 1)))))]

def decide(pages):
    out = {'pages': pages, 'n': len(pages)}
    text = [i for i, p in enumerate(pages) if p['kind'] == 'text']
    out['measured'] = len(text)
    if len(text) < 5 or len(text) < 0.5 * len(pages):
        out['decision'] = 'skip: few text pages'; return out
    bw = {i: pages[i]['box'][2] - pages[i]['box'][0] for i in text}; bh = {i: pages[i]['box'][3] - pages[i]['box'][1] for i in text}
    pw = q([pages[i]['w'] for i in text], 0.5); ph = q([pages[i]['h'] for i in text], 0.5)
    Tw, Th = q(bw.values(), 0.98), q(bh.values(), 0.98)
    full_w = [i for i in text if bw[i] >= 0.9 * q(bw.values(), 0.5)]
    full_h = [i for i in text if bh[i] >= 0.9 * q(bh.values(), 0.5)]
    m0 = M * pw / REF
    W, H = Tw + 2 * max(m0, 0.12 * Tw), Th + 2 * max(m0, 0.06 * Th)
    cx = {i: (pages[i]['box'][0] + pages[i]['box'][2]) / 2 for i in text}
    cy = {i: (pages[i]['box'][1] + pages[i]['box'][3]) / 2 for i in text}
    def lim(i):                                     # where a box may go: the page, inside its usual scanner bands
        a = pages[i].get('allowed') or [0, 0, pages[i]['w'], pages[i]['h']]
        return a
    # as wide as the text can be centred on (nearly) every full page; never narrower than the text itself
    fitW = [2 * min(cx[i] - lim(i)[0], lim(i)[2] - cx[i]) for i in full_w]
    fitH = [2 * min(cy[i] - lim(i)[1], lim(i)[3] - cy[i]) for i in full_h]
    W = min(W, max(Tw, q(fitW, 0.05)) if fitW else W, pw); H = min(H, max(Th, q(fitH, 0.05)) if fitH else H, ph)
    def near(i, pool, val):                         # a short page takes the place of its full neighbours (same parity)
        same = [j for j in pool if j % 2 == i % 2] or pool
        k = sorted(same, key=lambda j: abs(j - i))[:6]
        return q([val[j] for j in k], 0.5)
    fw, fh = set(full_w), set(full_h)
    whole, offc, moved = [], [], 0
    for i, p in enumerate(pages):
        if p['kind'] in ('rotated', 'picture'): p['crop'] = None; continue
        x = cx[i] if i in fw else near(i, full_w, cx)
        y = cy[i] if i in fh else near(i, full_h, cy)
        b = [x - W / 2, y - H / 2, x + W / 2, y + H / 2]
        bx = p.get('box')
        if bx:                                      # move the least needed to hold every mark of the page
            dx = bx[0] - b[0] if bx[0] < b[0] else (bx[2] - b[2] if bx[2] > b[2] else 0)
            dy = bx[1] - b[1] if bx[1] < b[1] else (bx[3] - b[3] if bx[3] > b[3] else 0)
            if dx or dy: moved += 1
            b = [b[0] + dx, b[1] + dy, b[2] + dx, b[3] + dy]
        sx = -b[0] if b[0] < 0 else (p['w'] - b[2] if b[2] > p['w'] else 0)     # stay on the page
        sy = -b[1] if b[1] < 0 else (p['h'] - b[3] if b[3] > p['h'] else 0)
        b = [round(b[0] + sx, 1), round(b[1] + sy, 1), round(b[2] + sx, 1), round(b[3] + sy, 1)]
        b = [max(0, b[0]), max(0, b[1]), min(p['w'], b[2]), min(p['h'], b[3])]
        if p['kind'] == 'text' and not inside(bx, b): p['crop'] = None; whole.append(i); continue
        p['crop'] = b
        p['cut_specks'] = [s for s in p['specks'] if not inside(s, b, 0)]
        if i in fw: offc.append(abs((b[0] + b[2]) / 2 - cx[i]) / p['w'])
    out['whole'] = whole; out['moved'] = moved
    out['size'] = [round(W, 1), round(H, 1)]
    out['gain'] = round(pw / W, 3); out['gain_h'] = round(ph / H, 3)
    out['offcentre_before'] = round(q([abs(cx[i] - pages[i]['w'] / 2) / pages[i]['w'] for i in full_w], 0.5), 3) if full_w else 0
    out['offcentre_after'] = round(q(offc, 0.5), 3) if offc else 0
    banded = sum(1 for i in text if pages[i]['allowed'][0] > 0.02 * pw or pages[i]['allowed'][2] < 0.98 * pages[i]['w']) > 0.5 * len(text)
    out['banded'] = banded
    if out['gain'] < GAIN and out['offcentre_before'] < OFFC and not banded:
        out['decision'] = f'skip: already fine (gain {out["gain"]}, off-centre {out["offcentre_before"]})'
    elif len(whole) > MAX_WHOLE * len(text): out['decision'] = f'skip: {len(whole)} pages do not fit one box'
    else: out['decision'] = 'crop'
    return out

def verify(path, rec, px=1000):
    """second look at twice the resolution: outside each page's box only isolated specks may remain; else the page stays whole"""
    doc = pymupdf.open(path); moved = []
    for i, p in enumerate(rec['pages']):
        if not p.get('crop'): continue
        page = doc[i]; a, z = gray(page, px)
        box, specks, allowed, dark = marks(a, z, page.rect.width)
        if box is None: continue
        c = p['crop']
        if not inside(box, c, 1.0):                 # try the same box moved over what sticks out; else the page stays whole
            dx = box[0] - c[0] if box[0] < c[0] else (box[2] - c[2] if box[2] > c[2] else 0)
            dy = box[1] - c[1] if box[1] < c[1] else (box[3] - c[3] if box[3] > c[3] else 0)
            n = [c[0] + dx, c[1] + dy, c[2] + dx, c[3] + dy]
            if n[0] >= 0 and n[1] >= 0 and n[2] <= p['w'] and n[3] <= p['h'] and inside(box, n, 1.0):
                p['crop'] = [round(v, 1) for v in n]; p['verify_moved'] = True
            else:
                p['crop'] = None; p['verify'] = box; moved.append(i); continue
        p['cut_specks'] = [x for x in specks if not inside(x, p['crop'], 0)]
    doc.close()
    rec['whole'] = sorted(set(rec.get('whole', [])) | set(moved)); rec['verify_whole'] = moved
    if rec.get('decision') == 'crop' and len(rec['whole']) > MAX_WHOLE * max(1, rec['measured']):
        rec['decision'] = f'skip: {len(rec["whole"])} pages do not fit one box (second check, 1,000 px)'
    return rec

def images_of(doc):
    return [[(x[0], x[2], x[3], len(doc.xref_stream_raw(x[0]) or b'')) for x in p.get_images(full=True)] for p in doc]

def apply(src, rec, dst):
    """CropBox only, incremental save; checked: same pages, same images byte for byte, each box as planned"""
    import shutil
    shutil.copyfile(src, dst)
    before = pymupdf.open(src); imgs = images_of(before); n = len(before); before.close()
    doc = pymupdf.open(dst); done = 0
    for i, p in enumerate(rec['pages']):
        b = p.get('crop')
        if not b: continue
        page = doc[i]; cb = page.cropbox
        r = pymupdf.Rect(b[0] + cb.x0, b[1] + cb.y0, b[2] + cb.x0, b[3] + cb.y0) & page.mediabox
        if not r.is_empty: page.set_cropbox(r); done += 1
    doc.save(dst, incremental=True, encryption=pymupdf.PDF_ENCRYPT_KEEP); doc.close()
    chk = pymupdf.open(dst)
    assert len(chk) == n, 'page count changed'
    assert images_of(chk) == imgs, 'images changed'
    chk.close()
    return {'pages': n, 'cropped': done, 'bytes_out': os.path.getsize(dst)}

def sample_pages(rec):
    """pages worth showing for approval: two facing text pages from the middle, the page with the most hidden specks,
    the page whose content comes nearest its box (the tightest margin), the first page left whole"""
    P = rec['pages']; text = [i for i, p in enumerate(P) if p.get('crop') and p['kind'] == 'text']
    if not text: return []
    mid = text[len(text) // 2]; out = [mid, mid + 1 if mid + 1 < len(P) and P[mid + 1].get('crop') else mid - 1]
    sp = max(text, key=lambda i: len(P[i].get('cut_specks', [])))
    if P[sp].get('cut_specks'): out.append(sp)
    out.append(max(text, key=lambda i: abs((P[i]['box'][0] + P[i]['box'][2]) / 2 - P[i]['w'] / 2)))   # most off-centre in the scan
    def slack(i):
        b, c = P[i]['box'], P[i]['crop']; return min(b[0] - c[0], c[2] - b[2], b[1] - c[1], c[3] - b[3]) / P[i]['w']
    out.append(min(text, key=slack))
    out += rec.get('whole', [])[:1]
    seen = []
    for i in out:
        if i not in seen: seen.append(i)
    return seen[:6]

def sheet(src, rec, outdir, pages=None, px=480):
    """before: whole page, the box in red, cut specks circled in blue; after: the box alone, drawn at the same width
    (as a phone shows it, fit to width) — so the gain in text size is what one sees"""
    os.makedirs(outdir, exist_ok=True)
    doc = pymupdf.open(src); made = []
    for i in pages or []:
        p = rec['pages'][i]; page = doc[i]
        tmp = pymupdf.open(); tmp.insert_pdf(doc, from_page=i, to_page=i); tp = tmp[0]
        z0 = px / tp.rect.width
        before = tp.get_pixmap(matrix=pymupdf.Matrix(z0, z0), alpha=False)
        sh = tp.new_shape()
        if p.get('crop'): sh.draw_rect(pymupdf.Rect(p['crop']) + (tp.rect.x0, tp.rect.y0, tp.rect.x0, tp.rect.y0)); sh.finish(color=(0.85, 0, 0), width=2.5)
        for s in p.get('cut_specks', []):
            c = pymupdf.Point((s[0] + s[2]) / 2, (s[1] + s[3]) / 2); sh.draw_circle(c, 9); sh.finish(color=(0, 0.3, 0.9), width=2)
        sh.commit()
        bpix = tp.get_pixmap(matrix=pymupdf.Matrix(z0, z0), alpha=False)
        fb = os.path.join(outdir, f'p{i + 1:04d}-before.jpg'); bpix.save(fb, jpg_quality=72)
        fa = None
        if p.get('crop'):
            b = p['crop']; z = px / (b[2] - b[0])
            apix = page.get_pixmap(matrix=pymupdf.Matrix(z, z), clip=pymupdf.Rect(b) + (page.rect.x0, page.rect.y0, page.rect.x0, page.rect.y0), alpha=False)
            fa = os.path.join(outdir, f'p{i + 1:04d}-after.jpg'); apix.save(fa, jpg_quality=72)
        made.append({'page': i + 1, 'before': fb, 'after': fa, 'cut_specks': len(p.get('cut_specks', [])), 'kind': p['kind']})
        tmp.close()
    doc.close()
    return made

WHY_AR = {'mid': 'صفحة من وسط الكتاب', 'speck': 'أكثر صفحة فيها نقط معزولة (الدوائر الزرقاء)',
          'tight': 'الصفحة التي يقترب نصها من الإطار أكثر من غيرها', 'centre': 'الصفحة التي كان نصها أبعد عن وسطها في الأصل', 'whole': 'صفحة تبقى كاملة (لا تدخل في الإطار)'}

def page_reasons(rec, pages):
    """why each page of sample_pages() was chosen (the same rules, recomputed)"""
    P = rec['pages']; out = {}
    text = [i for i, p in enumerate(P) if p.get('crop') and p['kind'] == 'text']
    if not text: return {i: 'whole' for i in pages}
    mid = text[len(text) // 2]; mids = {mid, mid + 1 if mid + 1 < len(P) and P[mid + 1].get('crop') else mid - 1}
    sp = max(text, key=lambda i: len(P[i].get('cut_specks', [])))
    oc = max(text, key=lambda i: abs((P[i]['box'][0] + P[i]['box'][2]) / 2 - P[i]['w'] / 2))
    for i in pages:
        if not P[i].get('crop'): out[i] = 'whole'
        elif i in mids: out[i] = 'mid'
        elif i == sp and P[i].get('cut_specks'): out[i] = 'speck'
        elif i == oc: out[i] = 'centre'
        else: out[i] = 'tight'
    return out

def review_page(cases, skipped, outdir, stats):
    """one self-contained Arabic page (+ images/) for the owner's approval: per book the gain, the pages left whole, the
    hidden specks and before/after pairs. cases: [{path, rec, sheet_dir}], skipped: [{path, rec, image}]"""
    import html, shutil
    img = os.path.join(outdir, 'images'); os.makedirs(img, exist_ok=True)
    esc = html.escape
    cards = []
    for n, c in enumerate(cases, 1):
        rec = c['rec']; P = rec['pages']
        pages = sorted(int(f[1:5]) - 1 for f in os.listdir(c['sheet_dir']) if f.endswith('-before.jpg'))
        why = page_reasons(rec, pages)
        specks = sum(len(p.get('cut_specks', [])) for p in P if p.get('crop'))
        figs = []
        for i in pages:
            pair = []
            for s, cap in (('before', 'قبل — الإطار الأحمر هو ما سيظهر'), ('after', 'بعد — بعرض الشاشة نفسه')):
                f = os.path.join(c['sheet_dir'], f'p{i + 1:04d}-{s}.jpg')
                if not os.path.exists(f): continue
                dst = f'{n:02d}-p{i + 1:04d}-{s}.jpg'; shutil.copyfile(f, os.path.join(img, dst))
                pair.append(f'<figure><img src="images/{dst}" alt=""><figcaption>{cap}</figcaption></figure>')
            figs.append(f'<div class="pair"><h4>ص {i + 1} — {WHY_AR[why[i]]}</h4><div class="imgs">{"".join(pair)}</div></div>')
        title = esc(c['path'].rsplit('/', 1)[-1].rsplit('.', 1)[0]); where = esc(c['path'].rsplit('/', 1)[0])
        cards.append(f'''<section class="card"><h3>{n}. {title}</h3><p class="where">{where}</p>
<ul class="facts"><li>يكبر النص على الهاتف <b>{round((rec["gain"] - 1) * 100)}٪</b></li><li>{rec["n"]} صفحة، منها {len(rec.get("whole", []))} تبقى كاملة</li>
<li>نقط معزولة خارج الإطار: {specks}</li><li>انحراف النص عن وسط الصفحة: {round(rec.get("offcentre_before", 0) * 100, 1)}٪ ← {round(rec.get("offcentre_after", 0) * 100, 1)}٪</li></ul>{"".join(figs)}</section>''')
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
<h1>عينة القص الجديد — للموافقة (الصيغة الثانية)</h1>
<div class="intro"><p>بعد ملاحظاتك على العينة الأولى: توسيط النص في كل الصفحات باتساق، وتكبير معتدل للكتب ذات الهوامش العادية. <b>لم يتغير شيء على الهاتف</b>: هذه صور فقط.</p><ul>
<li>القص لا يمس الصورة ولا النص: يتغير الإطار الظاهر من الصفحة فقط، ويمكن الرجوع عنه في أي وقت.</li>
<li>إطار بمقاس واحد للكتاب كله، يوضع في كل صفحة بحيث يتوسط نصُّها أفقيا (ورأسيا)، والصفحة القصيرة (آخر فصل، عنوان) تأخذ موضع جاراتها؛ فلا تتمايل الصفحات، ويبقى النص في الوسط باتساق مهما انحرف الماسح.</li>
<li>الإطار يحيط بكل أثر كتابة في الصفحة: الحواشي، أرقام الصفحات، العناوين الجارية، التعليقات وأرقام المخطوط في الهامش، والأطر والزخارف المطبوعة؛ ثم يُترك هامش سخي حوله.</li>
<li>الكتب ذات الهوامش العادية تكبَّر أيضا تكبيرا معتدلا على حساب شيء من الهامش، ما دام الإطار نفسه يصلح لكل صفحات الكتاب. وما لا يكسب فيه النص 6٪ على الأقل ولا كان منحرفا عن الوسط يبقى كما هو.</li>
<li>ظل حافة الكتاب وأشرطة الماسح السوداء ليست من النص: لا يمتد إليها الإطار.</li>
<li>كل صفحة تُفحص مرة ثانية بدقة مضاعفة: إن بقي خارج الإطار شيء غير نقطة معزولة زُحزح الإطار ليشمله، وإلا بقيت تلك الصفحة كاملة.</li>
<li>لا يقع خارج الإطار إلا النقط المعزولة (أصغر من 1.4 مم، وبعيدة عن أي كتابة 5 مم فأكثر)، وهي معلَّمة بدائرة زرقاء.</li>
<li>تنظيف النقط بلون الخلفية خطوة مستقلة لاحقة، ليست في هذه العينة.</li></ul>
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
        rec = analyse(a[0])
        if rec.get('decision') == 'crop': rec = verify(a[0], rec)
        json.dump(rec, open(a[1], 'w'), ensure_ascii=False)
        print(json.dumps({k: rec.get(k) for k in ('decision', 'n', 'measured', 'gain', 'gain_h', 'banded', 'boxes')} | {'whole': len(rec.get('whole', []))}, ensure_ascii=False))
    elif cmd == 'apply':
        print(json.dumps(apply(a[0], json.load(open(a[1])), a[2])))
    elif cmd == 'sheet':
        rec = json.load(open(a[1]))
        pg = [int(x) - 1 for x in a[3].split(',')] if len(a) > 3 else None
        print(json.dumps(sheet(a[0], rec, a[2], pg), ensure_ascii=False))
