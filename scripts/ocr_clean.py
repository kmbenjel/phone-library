"""Image-level cleaning + a searchable text layer, for chosen books (owner 2026-10-10: «ok for ocrmypdf and sample»).
LOSSY by design — used only on books that need it (photographed pages, grey or dirty scans, heavy colour scans of plain
text, scans without text); the lossless crop (book_crop.py) stays the default. Nothing here reaches the phone: the
originals are kept, the results wait for the owner's review.
Per book (data/improve/ocr/<n>/):
  1. orig.pdf — the phone file's bytes (the laptop's copy when its MD5 equals the phone's, else fetched under the lock);
  2. clean.pdf — bw_clean.py's method page by page (in parallel): the paper's light evened out, black and white (Otsu),
     levelled, the photo's junk out (border marks, bars, blots), one page size for the book, each page centred on its
     text; a picture page (more than 30 % ink once binarised: a cover, a plate) keeps its own grey image instead;
     black-and-white pages stored as CCITT Group 4 (lossless) by img2pdf, grey pages as JPEG;
  3. final.pdf — OCRmyPDF adds an invisible Arabic+English text layer (-l ara+eng, images untouched: --optimize 0);
  4. checks: the same number of pages; sizes; the OCR read of 6 pages spread over the book, original vs final (tesseract
     ara at 300 dpi: mean word confidence, Arabic words found) — a final copy must not read worse than its original.
→ data/improve/ocr/report.json (one record per book), read by scripts/ocr_review_page.py.
Usage: python3 scripts/ocr_clean.py LIST [--jobs 8]   (LIST: one phone path per line, under Books/)"""
import csv, hashlib, io, json, os, re, shutil, subprocess, sys, tempfile, time
from concurrent.futures import ProcessPoolExecutor
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
sys.path.insert(0, os.path.expanduser('~/.local/share/phone-library-tools/site'))   # PyMuPDF (as book_crop.py)
J = lambda *p: os.path.join(ROOT, *p)
OUT = J('data', 'improve', 'ocr')
UVPY = os.path.expanduser('~/.local/share/uv/tools/ocrmypdf/bin/python')
OCRMYPDF = os.path.expanduser('~/.local/bin/ocrmypdf')
DPI = 300

def fetch(path, dst):
    from crop_batch import Phone, md5_file, LOCAL_MAP
    if os.path.exists(dst): return
    with Phone() as ph: want = ph.md5(path)
    local = dict(l.rstrip('\n').split('\t')[:2] for l in open(LOCAL_MAP, encoding='utf-8')) if os.path.exists(LOCAL_MAP) else {}
    lp = local.get(path)
    if lp and os.path.exists(lp) and md5_file(lp) == want: shutil.copyfile(lp, dst); return
    with Phone() as ph: ph.get(path, dst + '.part')
    if md5_file(dst + '.part') != want: os.remove(dst + '.part'); raise RuntimeError('download differs from the phone file')
    os.rename(dst + '.part', dst)

def one_page(args):
    """worker: page i → (i, packed 1-bit image or grey JPEG bytes, kind, text box, angle)"""
    import numpy as np, cv2, pymupdf, bw_clean as b
    src, i = args
    doc = pymupdf.open(src); page = doc[i]
    v = b.page_gray(page, min(DPI / 72.0, 3300 / max(page.rect.width, page.rect.height)))
    bw = b.binarise(b.even_light(v))
    if (bw < 128).mean() > 0.30:                            # a picture page: its own grey image
        ok, jpg = cv2.imencode('.jpg', v, [cv2.IMWRITE_JPEG_QUALITY, 85])
        return i, ('grey', jpg.tobytes(), v.shape), None, 0.0
    bw, ang = b.level(bw)
    box = b.text_box(bw)
    return i, ('bw', np.packbits(bw < 128), bw.shape), box, ang

def clean(src, dst, jobs):
    import numpy as np, cv2, pymupdf
    n = pymupdf.open(src).page_count
    with ProcessPoolExecutor(jobs) as ex: res = sorted(ex.map(one_page, [(src, i) for i in range(n)], chunksize=2))
    boxes = [r[2] for r in res if r[2]]
    q = lambda v, f: sorted(v)[min(len(v) - 1, int(f * (len(v) - 1)))]
    if boxes:
        ws = [b_[2] - b_[0] for b_ in boxes]; hs = [b_[3] - b_[1] for b_ in boxes]
        W = q([x for x in ws if x <= 1.25 * q(ws, .5)] or ws, .95); H = q([x for x in hs if x <= 1.15 * q(hs, .5)] or hs, .98)
    else:
        W, H = 2000, 3000
    mg = int(0.06 * W); W, H = W + 2 * mg, H + 2 * mg            # 6 % margins (owner's rule, 2026-10-09)
    tmp = tempfile.mkdtemp(dir=os.path.dirname(dst)); files = []
    for i, (kind, data, shape), box, ang in res:
        f = os.path.join(tmp, f'{i:04d}')
        if kind == 'grey':
            g = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_GRAYSCALE)
            s = min(W / g.shape[1], H / g.shape[0]); g = cv2.resize(g, (max(1, int(g.shape[1] * s)), max(1, int(g.shape[0] * s))), interpolation=cv2.INTER_AREA)
            canvas = np.full((H, W), 255, np.uint8); y0, x0 = (H - g.shape[0]) // 2, (W - g.shape[1]) // 2
            canvas[y0:y0 + g.shape[0], x0:x0 + g.shape[1]] = g
            cv2.imwrite(f + '.jpg', canvas, [cv2.IMWRITE_JPEG_QUALITY, 85]); files.append(f + '.jpg'); continue
        ink = np.unpackbits(data)[:shape[0] * shape[1]].reshape(shape).astype(bool)
        bw = np.where(ink, 0, 255).astype(np.uint8)
        if not box: box = [0, 0, shape[1], shape[0]]
        cx, cy = (box[0] + box[2]) // 2, (box[1] + box[3]) // 2
        bw_, bh_ = max(W, box[2] - box[0] + 2 * mg), max(H, box[3] - box[1] + 2 * mg)
        x0, y0 = cx - bw_ // 2, cy - bh_ // 2
        canvas = np.full((bh_, bw_), 255, np.uint8)
        sx0, sy0, sx1, sy1 = max(0, x0), max(0, y0), min(shape[1], x0 + bw_), min(shape[0], y0 + bh_)
        canvas[sy0 - y0:sy1 - y0, sx0 - x0:sx1 - x0] = bw[sy0:sy1, sx0:sx1]
        t = mg // 2                                             # outside the text block: the photo's surroundings
        tx0, ty0, tx1, ty1 = box[0] - x0 - t, box[1] - y0 - t, box[2] - x0 + t, box[3] - y0 + t
        canvas[:max(0, ty0)] = 255; canvas[max(0, ty1):] = 255; canvas[:, :max(0, tx0)] = 255; canvas[:, max(0, tx1):] = 255
        if (bw_, bh_) != (W, H): canvas = cv2.resize(canvas, (W, H), interpolation=cv2.INTER_AREA)
        from PIL import Image
        Image.fromarray(canvas > 127).save(f + '.tif', compression='group4', dpi=(DPI, DPI)); files.append(f + '.tif')
    code = ("import img2pdf, sys\nfiles = sys.argv[2:]\nlay = img2pdf.get_fixed_dpi_layout_fun((%d, %d))\n"
            "open(sys.argv[1], 'wb').write(img2pdf.convert(files, layout_fun=lay))" % (DPI, DPI))
    subprocess.run([UVPY, '-c', code, dst] + files, check=True)
    shutil.rmtree(tmp)
    return {'pages': n, 'size_px': [W, H], 'turned': sum(1 for r in res if r[3]), 'grey_pages': sum(1 for r in res if r[1][0] == 'grey')}

def ocr_quality(pdf, pages):
    """mean tesseract word confidence and Arabic words found, on the given pages (300 dpi grey)"""
    conf, words = [], 0
    with tempfile.TemporaryDirectory() as d:
        for p in pages:
            base = os.path.join(d, f'p{p}')
            subprocess.run(['pdftoppm', '-gray', '-r', '300', '-cropbox', '-f', str(p), '-l', str(p), '-png', '-singlefile', pdf, base],
                           check=True, stderr=subprocess.DEVNULL)
            r = subprocess.run(['tesseract', base + '.png', '-', '-l', 'ara', '--psm', '3', 'tsv'], capture_output=True, text=True)
            for row in csv.reader(io.StringIO(r.stdout), delimiter='\t', quoting=csv.QUOTE_NONE):
                if len(row) == 12 and row[0] == '5' and row[11].strip():
                    try: c = float(row[10])
                    except ValueError: continue
                    if c >= 0: conf.append(c)
                    if re.fullmatch(r'[ء-ي٠-٩]{3,}', row[11].strip()) and c >= 60: words += 1
    return {'conf': round(sum(conf) / len(conf), 1) if conf else 0.0, 'good_words': words}

def main(lst, jobs=8):
    os.makedirs(OUT, exist_ok=True)
    paths = [l.strip().removeprefix('Books/') for l in open(lst, encoding='utf-8') if l.strip()]
    rep_path = os.path.join(OUT, 'report.json')
    report = json.load(open(rep_path, encoding='utf-8')) if os.path.exists(rep_path) else {}
    for n, path in enumerate(paths, 1):
        key = hashlib.md5(path.encode()).hexdigest()[:10]
        if key in report and report[key].get('done'): continue
        d = os.path.join(OUT, key); os.makedirs(d, exist_ok=True)
        o, c, f = (os.path.join(d, x) for x in ('orig.pdf', 'clean.pdf', 'final.pdf'))
        t0 = time.time(); r = {'path': path}
        try:
            fetch(path, o)
            r.update(clean(o, c, jobs)); t1 = time.time()
            subprocess.run([OCRMYPDF, '-l', 'ara+eng', '--output-type', 'pdf', '--optimize', '0', '--jobs', str(jobs),
                            '--tesseract-timeout', '300', '--quiet', c, f], check=True)
            t2 = time.time()
            import pymupdf
            n_o, n_f = pymupdf.open(o).page_count, pymupdf.open(f).page_count
            pick = sorted({max(1, round(n_o * k / 7)) for k in range(1, 7)})
            r.update(same_pages=n_o == n_f, size_orig=os.path.getsize(o), size_final=os.path.getsize(f),
                     ocr_orig=ocr_quality(o, pick), ocr_final=ocr_quality(f, pick), sample_pages=pick,
                     sec_clean=round(t1 - t0), sec_ocr=round(t2 - t1), done=True)
            os.remove(c)
        except Exception as e:
            r['error'] = repr(e)[:300]
        report[key] = r
        json.dump(report, open(rep_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        q0, q1 = r.get('ocr_orig', {}), r.get('ocr_final', {})
        print(f"[{n}/{len(paths)}] {path[:70]} | {r.get('pages')} p | {r.get('size_orig', 0) // 1000} → {r.get('size_final', 0) // 1000} KB"
              f" | OCR conf {q0.get('conf')} → {q1.get('conf')}, words {q0.get('good_words')} → {q1.get('good_words')}"
              f" | {r.get('sec_clean')}+{r.get('sec_ocr')} s {r.get('error', '')}", flush=True)

if __name__ == '__main__':
    a = sys.argv[1:]
    main(a[0], int(a[a.index('--jobs') + 1]) if '--jobs' in a else 8)
