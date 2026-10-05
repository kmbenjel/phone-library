"""Read every phone file from the inside (one FTP connection, streamed: download → analyse → delete).
Per file → data/inspect/files.jsonl:
  md5 (computed locally), pdfinfo metadata (title/author/subject/keywords = Waqfeya/archive id), pages,
  page sizes (distinct sizes + counts: mixed sizes = cropping/scan problems, landscape = two-page spreads),
  images (count, median ppi, colour mix, encodings, 1-bit share), bytes per page, text layer (first pages and a
  middle page), first-pages text (2,500 chars), margins of 3 sample pages (content bounding box from a 20-dpi render,
  dark scanner borders), and for image-only files the first 4 pages rendered at 150 dpi for OCR
  (data/inspect/ocr-queue/, consumed by inspect_ocr.py) + a small thumbnail of page 1 (data/inspect/thumbs/).
Resumable (path+size already in files.jsonl is skipped). Order: PRIORITY file (one path per line) first.
Usage: python3 scripts/inspect_files.py [index.tsv] [priority.txt]"""
import csv, ftplib, hashlib, json, os, queue, re, statistics, subprocess, sys, threading, time
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from phone_host import HOST, PORT
from netpace import Pacer
sys.path.append(os.path.expanduser('~/.local/share/phone-library-tools/site'))
try:
    import pymupdf, fix_pdf                    # crop «recipes» while the file is here (no second download later)
except Exception:
    pymupdf = None
J = lambda *p: os.path.join(ROOT, *p)
IDX = sys.argv[1] if len(sys.argv) > 1 else J('data/phone/index-now.tsv')
PRI = sys.argv[2] if len(sys.argv) > 2 else None
OUT, TMP, OCRQ, THUMBS, CROPS = J('data/inspect/files.jsonl'), J('data/inspect/tmp'), J('data/inspect/ocr-queue'), J('data/inspect/thumbs'), J('data/inspect/crops')
for d in (TMP, OCRQ, THUMBS, CROPS): os.makedirs(d, exist_ok=True)
WORKERS, MAX_STAGED, OCR_CAP = 3, 4, 12000

def run(cmd, timeout=600):
    try:
        return subprocess.run(cmd, capture_output=True, timeout=timeout).stdout.decode('utf-8', 'replace')
    except subprocess.TimeoutExpired:
        return ''

def pgm(path):
    """Read a binary PGM written by pdftoppm -gray → (w, h, bytes)."""
    data = open(path, 'rb').read()
    parts, pos = [], 0
    while len(parts) < 4:
        m = re.compile(rb'\s*(#[^\n]*\n\s*)*(\S+)').match(data, pos)
        parts.append(m.group(2)); pos = m.end()
    w, h = int(parts[1]), int(parts[2])
    return w, h, data[pos + 1: pos + 1 + w * h]

def margins(pdf, page, key):
    """Content box of one page at 20 dpi: margins as fractions + dark border bands (scanner edges)."""
    base = os.path.join(TMP, f'{key}-m{page}')
    run(['pdftoppm', '-gray', '-r', '20', '-f', str(page), '-l', str(page), '-singlefile', pdf, base], 120)
    f = base + '.pgm'
    if not os.path.exists(f): return None
    try:
        w, h, px = pgm(f)
    finally:
        os.remove(f)
    if w < 10 or h < 10: return None
    dark = lambda v: v < 150
    rows = [sum(1 for x in range(w) if dark(px[y * w + x])) / w for y in range(h)]
    cols = [sum(1 for y in range(h) if dark(px[y * w + x])) / h for x in range(w)]
    ink = lambda a: [i for i, v in enumerate(a) if 0.01 < v < 0.9]          # rows/cols with text, not solid borders
    r, c = ink(rows), ink(cols)
    if not r or not c: return {'p': page, 'blank': True}
    band = lambda a: round(max(statistics.mean(a[:max(1, len(a) // 30)]), statistics.mean(a[-max(1, len(a) // 30):])), 2)
    return {'p': page, 'l': round(c[0] / w, 3), 'r': round(1 - (c[-1] + 1) / w, 3), 't': round(r[0] / h, 3),
            'b': round(1 - (r[-1] + 1) / h, 3), 'edge_dark_rows': band(rows), 'edge_dark_cols': band(cols)}

def analyse(pdf, path, size, md5, key):
    rec = {'path': path, 'size': size, 'md5': md5, 'magic': open(pdf, 'rb').read(5).decode('latin-1')}
    if not rec['magic'].startswith('%PDF'):
        return rec
    info = run(['pdfinfo', '-isodates', pdf], 120)
    meta = dict(re.findall(r'^([A-Za-z ]+):\s*(.*)$', info, re.M))
    rec['meta'] = {k.lower(): meta[k] for k in ('Title', 'Author', 'Subject', 'Keywords', 'Creator', 'Producer', 'CreationDate') if meta.get(k)}
    pages = int(meta.get('Pages', '0') or 0); rec['pages'] = pages
    if not pages: rec['error'] = 'no pages'; return rec
    sizes = {}
    for w, h, rot in re.findall(r'^Page\s+\d+ size:\s+([\d.]+) x ([\d.]+) pts.*\n^Page\s+\d+ rot:\s+(\d+)', run(['pdfinfo', '-f', '1', '-l', str(pages), pdf], 300), re.M):
        k = f'{5 * round(float(w) / 5)}x{5 * round(float(h) / 5)}' + (f'r{rot}' if rot != '0' else '')   # 5-pt buckets: scanner jitter is not a problem
        sizes[k] = sizes.get(k, 0) + 1
    rec['page_sizes'] = dict(sorted(sizes.items(), key=lambda kv: -kv[1])[:12]); rec['n_page_sizes'] = len(sizes)
    imgs = [l.split() for l in run(['pdfimages', '-list', pdf], 300).splitlines()[2:]]
    imgs = [x for x in imgs if len(x) >= 14 and x[2] in ('image', 'smask', 'mask')]
    img = [x for x in imgs if x[2] == 'image']
    if img:
        ppi = sorted(int(x[12]) for x in img if x[12].isdigit())
        col, enc = {}, {}
        for x in img:
            col[x[5]] = col.get(x[5], 0) + 1; enc[x[8]] = enc.get(x[8], 0) + 1
        rec['images'] = {'n': len(img), 'per_page': round(len(img) / pages, 2), 'ppi_median': ppi[len(ppi) // 2] if ppi else None,
                         'ppi_min': ppi[0] if ppi else None, 'color': col, 'enc': enc,
                         'bpc1_share': round(sum(1 for x in img if x[7] == '1') / len(img), 3),
                         'px_median': sorted(int(x[3]) * int(x[4]) for x in img)[len(img) // 2]}
    rec['bytes_per_page'] = size // pages
    first = run(['pdftotext', '-f', '1', '-l', str(min(6, pages)), '-layout', pdf, '-'], 120)
    mid = run(['pdftotext', '-f', str(max(1, pages // 2)), '-l', str(max(1, pages // 2)), pdf, '-'], 60)
    rec['text_first_chars'] = len(re.sub(r'\s', '', first)); rec['text_mid_chars'] = len(re.sub(r'\s', '', mid))
    rec['text_first'] = re.sub(r'[ \t]+', ' ', first).strip()[:2500]
    samples = sorted({min(pages, p) for p in (max(1, pages // 4), max(1, pages // 2), max(1, 3 * pages // 4))})
    rec['margins'] = [m for m in (margins(pdf, p, key) for p in samples) if m]
    mm = [m for m in rec['margins'] if not m.get('blank')]
    if pymupdf and mm and (statistics.median(m['l'] + m['r'] for m in mm) > 0.30 or max(max(m['l'], m['r']) for m in mm) > 0.20
                           or max(max(m.get('edge_dark_rows', 0), m.get('edge_dark_cols', 0)) for m in mm) >= 0.35):
        try:
            boxes = fix_pdf.crop_boxes(pymupdf.open(pdf))
            json.dump({'path': path, 'size': size, 'md5': md5, 'boxes': boxes}, open(os.path.join(CROPS, key + '.json'), 'w'))
            rec['crop_recipe'] = True
        except Exception as e:
            rec['crop_error'] = repr(e)[:200]
    run(['pdftoppm', '-gray', '-jpeg', '-jpegopt', 'quality=60', '-r', '18', '-f', '1', '-l', '1', '-singlefile', pdf, os.path.join(THUMBS, key)], 120)
    if rec['text_first_chars'] < 300:            # image-only front matter: queue the first 4 pages for OCR
        while len(os.listdir(OCRQ)) > OCR_CAP: time.sleep(30)     # OCR is slower than the download: cap the backlog
        run(['pdftoppm', '-gray', '-jpeg', '-jpegopt', 'quality=85', '-r', '150', '-f', '1', '-l', str(min(4, pages)), pdf, os.path.join(OCRQ, key)], 300)
        rec['ocr_queued'] = True
    return rec

def key_of(path, size):
    return hashlib.md5(f'{path}\t{size}'.encode()).hexdigest()[:16]

def main():
    rows = [(p, int(s)) for p, s in csv.reader(open(IDX, encoding='utf-8'), delimiter='\t') if s.isdigit()]
    rows = [r for r in rows if not r[0].startswith('فهارس الويب/')]
    done = set()
    if os.path.exists(OUT):
        for l in open(OUT, encoding='utf-8'):
            try: d = json.loads(l); done.add((d['path'], d['size']))
            except Exception: pass
    pri = {}
    if PRI:
        for i, l in enumerate(open(PRI, encoding='utf-8')): pri.setdefault(l.rstrip('\n'), i)
    todo = sorted((r for r in rows if r not in done), key=lambda r: (pri.get(r[0], 10 ** 9), r[0]))
    print('to inspect:', len(todo), 'GB', round(sum(s for _, s in todo) / 1e9, 1), flush=True)
    q, lock, out = queue.Queue(MAX_STAGED), threading.Lock(), open(OUT, 'a', encoding='utf-8')
    def worker():
        while True:
            item = q.get()
            if item is None: return
            pdf, path, size, md5, key = item
            try:
                rec = analyse(pdf, path, size, md5, key)
            except Exception as e:
                rec = {'path': path, 'size': size, 'md5': md5, 'error': repr(e)[:300]}
            rec['key'] = key; rec['t'] = time.strftime('%F %T')
            with lock:
                out.write(json.dumps(rec, ensure_ascii=False) + '\n'); out.flush()
            os.remove(pdf)
    ths = [threading.Thread(target=worker, daemon=True) for _ in range(WORKERS)]
    for t in ths: t.start()
    def connect():
        f = ftplib.FTP(); f.encoding = 'utf-8'; f.connect(HOST, PORT, timeout=300); f.login(); return f
    f, t0, nbytes = connect(), time.time(), 0
    pacer = Pacer()                      # Wi-Fi is shared (games, calls): back off when the router's latency rises
    for i, (path, size) in enumerate(todo):
        key = key_of(path, size); dst = os.path.join(TMP, key + '.pdf')
        for attempt in range(4):
            try:
                h = hashlib.md5()
                with open(dst, 'wb') as o:
                    def cb(b):
                        o.write(b); h.update(b); pacer.wait(len(b))
                    f.retrbinary('RETR /Books/' + path, cb, blocksize=1 << 16)
                if os.path.getsize(dst) != size: raise OSError(f'short read {os.path.getsize(dst)} != {size}')
                q.put((dst, path, size, h.hexdigest(), key)); nbytes += size; break
            except ftplib.error_perm as e:
                print('FAIL', path, e, flush=True); break
            except (ftplib.error_temp, OSError, EOFError) as e:
                print('retry', path, e, flush=True); time.sleep(5 * (attempt + 1))
                try: f = connect()
                except Exception: pass
        if i % 50 == 0:
            el = time.time() - t0
            print(f'{i}/{len(todo)}  {nbytes / 1e9:.1f} GB  {nbytes / 1e6 / max(el, 1):.1f} MB/s  {el / 60:.0f} min  {pacer.status()}', flush=True)
    for _ in ths: q.put(None)
    for t in ths: t.join()
    print('done', flush=True)

if __name__ == '__main__':
    main()
