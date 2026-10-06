"""Sheets of imprint pages to READ BY EYE (owner, 2026-10-06: accuracy above all). Imprint lines are often set in
calligraphy that tesseract cannot read («الطبعة الثالثة ١٤٠٧هـ - ١٩٨٧م» came out as «الطعست الا لتر»), but a 60-dpi
render is clearly legible to a reader. For every book still without a year (data/editions/edition-info.json):
  its first content file is copied from the phone; pages 1-8 are scored for imprint words (text layer, else a quick
  150-dpi tesseract pass): حقوق، محفوظة، الطبعة، الناشر، رقم الإيداع، الترقيم، هاتف، ص.ب، ISBN …; the title page and the
  best imprint page are rendered (60 dpi, trimmed) → data/editions/imprint-sheets/sNNNN.png, 6 books per sheet, each
  book labelled with its number; data/editions/imprint-sheets/books.tsv maps number → book key, file, pages shown.
The reading is written by hand to data/editions/imprint-read.tsv (n, hijri, gregorian, edition, note) and used by
scripts/edition_info.py (source «صفحة الحقوق»). Resumable; N workers; phone copies under the shared lock.
Usage: python3 scripts/imprint_sheets.py [--workers 4] [--limit N]"""
import argparse, csv, json, os, re, subprocess, tempfile, threading
from concurrent.futures import ThreadPoolExecutor
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J = lambda p: os.path.join(ROOT, p)
OUT = J('data/editions/imprint-sheets')
TMP = J('data/imprint-tmp')
KEY = re.compile(r'حقوق|محفوظ|الطبع|طبعة|الناشر|الإيداع|الايداع|الترقيم|هاتف|تلفون|فاكس|ص\.\s*ب|ISBN|بيروت|القاهرة|الرياض|دمشق|الكويت|عمان', re.I)
lock = threading.Lock()
PER = 6                                     # books per sheet (3 × 2 grid, imprint page at 85 dpi)

def score(local, page, d):
    t = subprocess.run(['pdftotext', '-f', str(page), '-l', str(page), local, '-'], capture_output=True, text=True).stdout
    if len(re.sub(r'\s', '', t)) < 30:
        png = os.path.join(d, f's{page}')
        subprocess.run(['pdftoppm', '-r', '110', '-gray', '-f', str(page), '-l', str(page), '-singlefile', '-png', local, png], capture_output=True, timeout=300)
        if not os.path.exists(png + '.png'): return 0, 0
        t = subprocess.run(['tesseract', png + '.png', '-', '-l', 'ara+eng', '--psm', '6'], capture_output=True, text=True,
                           env={**os.environ, 'OMP_THREAD_LIMIT': '1'}, timeout=300).stdout
        os.remove(png + '.png')
    else:
        auto = text_read(t)
        if auto: return 99, auto                     # a clean edition line in the PDF's own text layer
    words = len(t.split())
    return len(KEY.findall(t)), words

DIG = str.maketrans('٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹', '01234567890123456789')
ORD = 'الأولى الاولى الثانية الثالثة الرابعة الخامسة السادسة السابعة الثامنة التاسعة العاشرة'.split()
def text_read(t):
    """edition + year from a TEXT LAYER (not OCR) — only when the page has exactly one edition line carrying a year,
    the year is hijri+gregorian that agree, or one year marked هـ / م; anything else goes to the eye"""
    lines = [l.strip() for l in t.translate(DIG).splitlines() if l.strip()]
    hits = []
    for i, l in enumerate(lines):
        if not re.search(r'الطبع[ةه]|طبعة', l): continue
        ctx = ' '.join(lines[i:i + 2])
        hs = [int(y) for y in re.findall(r'(?<!\d)(1[23]\d\d|14[0-4]\d)(?!\d)', ctx)]
        gs = [int(y) for y in re.findall(r'(?<!\d)(18[3-9]\d|19\d\d|20[0-2]\d)(?!\d)', ctx)]
        pair = [(h, g) for h in hs for g in gs if abs(g - (0.970229 * h + 621.57)) <= 2]
        marked_h = re.findall(r'(?<!\d)(1[23]\d\d|14[0-4]\d)\s*(?:هـ|ه)', ctx)
        marked_g = re.findall(r'(?<!\d)(18[3-9]\d|19\d\d|20[0-2]\d)\s*م(?![ا-ي])', ctx)
        ed = next((w for w in ORD if w in ctx), '')
        if len(set(pair)) > 1 or (len(set(marked_h)) > 1 and not pair): return None      # several editions/years: the eye decides
        if len(set(pair)) == 1: hits.append((pair[0][0], pair[0][1], ed, ctx))
        elif not pair and len(set(marked_h)) == 1 and not gs: hits.append((int(marked_h[0]), None, ed, ctx))
        elif not pair and len(set(marked_g)) == 1 and not hs: hits.append((None, int(marked_g[0]), ed, ctx))
    years = {(h, g) for h, g, e, c in hits}
    return hits[0] if len(years) == 1 else None

def first_file(b):
    fs = [f for f, s in sorted(b['files']) if not re.search(r'الواجهة|الفهارس|صور المخطوط', f)] or [f for f, s in sorted(b['files'])]
    nums = [f for f in fs if re.match(r'0*1 - ', f)]
    return (nums or fs)[0]

def prepare(tag, b):
    key = f"{b['cat']}/{b['folder']}"
    f = first_file(b)
    rel = f"{b['cat']}/{f}" if len(b['files']) == 1 and f == b['folder'] + '.pdf' else f"{b['cat']}/{b['folder']}/{f}"
    if dict(b['files'])[f] > 300e6: return None
    d = tempfile.mkdtemp(dir=TMP); local = os.path.join(d, 'b.pdf')
    try:
        r = subprocess.run(['flock', '/tmp/phone-ftp.lock', 'rclone', 'copyto', 'phone:Books/' + rel, local, '-q', '--retries', '3'],
                           capture_output=True, timeout=1800)
        if r.returncode or not os.path.exists(local): return None
        info = subprocess.run(['pdfinfo', local], capture_output=True, text=True).stdout
        pages = int(re.search(r'Pages:\s*(\d+)', info).group(1)) if 'Pages:' in info else 1
        cands = []
        for p in [x for x in (2, 4, 3, 1, 5, 6) if x <= pages]:      # where imprints usually are; stop at a clear one
            sc = score(local, p, d)
            if sc[0] == 99:                                         # read from the text layer: no sheet needed
                h, g, ed, line = sc[1]
                return {'key': key, 'file': f, 'auto': True, 'page': p, 'hijri': h, 'gregorian': g, 'edition': ed, 'line': line[:200]}
            cands.append((sc, p))
            if sc[0] >= 3: break
        best = max(cands, key=lambda x: x[0][0])
        show = [best[1]] if best[0][0] else sorted({1, min(2, pages)})    # the imprint page; else title + verso
        imgs = []
        for p in show:
            png = os.path.join(OUT, f'tmp-{tag}-p{p}')
            subprocess.run(['pdftoppm', '-r', '85' if len(show) == 1 else '60', '-gray', '-f', str(p), '-l', str(p), '-singlefile', '-png', local, png],
                           capture_output=True, timeout=300)
            if os.path.exists(png + '.png'):
                subprocess.run(['convert', png + '.png', '-trim', '+repage', '-resize', '640x900>', png + '.png'], capture_output=True)
                imgs.append(png + '.png')
        return {'key': key, 'file': f, 'pages': show, 'imgs': imgs, 'score': best[0][0]} if imgs else None
    except (subprocess.TimeoutExpired, AttributeError):
        return None
    finally:
        subprocess.run(['rm', '-rf', d])

def make_sheet(group):
    no = group[0]['n'] // PER
    tiles = []
    for g in group:
        t = os.path.join(OUT, f"t{g['n']:05d}.png")
        subprocess.run(['montage', *g['imgs'], '-tile', f"{len(g['imgs'])}x1", '-geometry', '+3+3', '-title', str(g['n']), t], capture_output=True)
        tiles.append(t)
    subprocess.run(['montage', *tiles, '-tile', '3x', '-geometry', '+6+6', '-background', '#bbb', os.path.join(OUT, f's{no:04d}.png')], capture_output=True)
    for g in group:
        for p in g['imgs']:
            if os.path.exists(p): os.remove(p)
    for t in tiles: os.remove(t)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--workers', type=int, default=4); ap.add_argument('--limit', type=int, default=0)
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True); os.makedirs(TMP, exist_ok=True)
    cat = json.load(open(J('data/catalog.json'), encoding='utf-8'))
    info = json.load(open(J('data/editions/edition-info.json'), encoding='utf-8'))
    mapf = os.path.join(OUT, 'books.tsv')
    if os.path.exists(mapf):                    # a stopped run: books prepared but never laid on a sheet go back to the queue
        rows = [r for r in csv.reader(open(mapf, encoding='utf-8'), delimiter='\t') if r]
        keep = [r for r in rows if os.path.exists(os.path.join(OUT, f's{int(r[0]) // PER:04d}.png'))]
        if len(keep) < len(rows):
            with open(mapf, 'w', encoding='utf-8') as w:
                for r in keep: w.write('\t'.join(r) + '\n')
        for f in os.listdir(OUT):
            if f.startswith(('tmp-', 't0')): os.remove(os.path.join(OUT, f))
    done = {r[1] for r in csv.reader(open(mapf, encoding='utf-8'), delimiter='\t')} if os.path.exists(mapf) else set()
    if os.path.exists(J('data/editions/imprint-text.tsv')):
        done |= {r[0] for r in csv.reader(open(J('data/editions/imprint-text.tsv'), encoding='utf-8'), delimiter='\t') if r}
    start = sum(1 for _ in open(mapf, encoding='utf-8')) if os.path.exists(mapf) else 0
    start = (start + PER - 1) // PER * PER                                  # a new run starts on a fresh sheet
    todo = [b for b in cat['books'] if f"{b['cat']}/{b['folder']}" not in done
            and not ({'hijri', 'gregorian'} & set(info.get(f"{b['cat']}/{b['folder']}", {})))
            and b['cat'] not in ('علوم أخرى',) and not re.search(r'^مجلة|^سلسلة|^أدب عالمي', b['folder'])]   # no Arabic imprint page
    if a.limit: todo = todo[:a.limit]
    print(len(todo), 'books to prepare', flush=True)
    pending, nxt = [], [start]
    from concurrent.futures import as_completed
    with ThreadPoolExecutor(a.workers) as ex:
        futs = [ex.submit(prepare, abs(hash(b['folder'])), b) for b in todo]
        for fu in as_completed(futs):                              # as they finish: one slow book does not hold the rest
            res = fu.result()
            if not res: continue
            if res.get('auto'):                                    # text layer read cleanly → data/editions/imprint-text.tsv
                with open(J('data/editions/imprint-text.tsv'), 'a', encoding='utf-8') as w:
                    w.write('\t'.join(str(res[k] or '') for k in ('key', 'file', 'page', 'hijri', 'gregorian', 'edition', 'line')) + '\n')
                continue
            res['n'] = nxt[0]; nxt[0] += 1                     # numbers only for prepared books: sheets without gaps
            with open(mapf, 'a', encoding='utf-8') as w:
                w.write(f"{res['n']}\t{res['key']}\t{res['file']}\t{','.join(map(str, res['pages']))}\t{res['score']}\n")
            pending.append(res)
            if len(pending) == PER: make_sheet(pending); pending = []
    if pending: make_sheet(pending)
    print('done', flush=True)

if __name__ == '__main__':
    main()
