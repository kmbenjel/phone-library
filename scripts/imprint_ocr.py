"""Read the edition line (الطبعة … سنة) from the imprint / title pages of each phone book that still lacks a year
(owner, 2026-10-06: accuracy above all; tesseract allowed). For each book: its first content file (volume 1 or the
single file) is copied from the phone, pages 1-8 are read — the PDF's own text layer when it has one, else tesseract
(ara+eng) on a 300-dpi render, page 2 first — and a year is accepted ONLY when it is read cleanly:
  * a hijri year (1250-1447) and a gregorian year (1830-2026) on the same edition line that agree (g ≈ 0.97h + 622 ± 2), or
  * one year with its own marker (هـ / م) on a line that names the edition (الطبعة / طبعة / سنة الطبع).
The edition number (الأولى، الثانية… or a numeral) is taken from the same line. Everything read is kept with its
page and line → data/editions/imprint-ocr.jsonl {key, file, page, line, hijri, gregorian, edition_no, ok}.
Resumable; N parallel workers (phone copies under the shared lock); the copied file is deleted after reading.
Usage: python3 scripts/imprint_ocr.py [--workers 5] [--all] [--sample N]
  --all: also books that already have a year (to measure agreement); --sample N: only N books (random, fixed seed)"""
import argparse, csv, json, os, random, re, subprocess, sys, tempfile, threading
from concurrent.futures import ThreadPoolExecutor
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J = lambda p: os.path.join(ROOT, p)
OUT = J('data/editions/imprint-ocr.jsonl')
TMP = J('data/imprint-tmp')
DIG = str.maketrans('٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹', '01234567890123456789')
ORD = 'الأولى الاولى الثانية الثالثة الرابعة الخامسة السادسة السابعة الثامنة التاسعة العاشرة الحادية'.split()
EDLINE = re.compile(r'الطبع[ةه]|طبع[ةه]|سنة الطبع|الطبع\s|تاريخ الطبع')
lock = threading.Lock()

def parse(text):
    """→ (hijri, gregorian, edition_no, line) or None; only clean reads"""
    lines = [l.strip() for l in text.translate(DIG).splitlines() if l.strip()]
    for i, l in enumerate(lines):
        if not EDLINE.search(l): continue
        ctx = ' '.join(lines[i:i + 2])                     # the year is often on the next line
        hs = [int(y) for y in re.findall(r'\b(1[23]\d\d|14[0-4]\d)\s*(?:هـ|ه|ھ|هجري)', ctx)]
        gs = [int(y) for y in re.findall(r'\b(18[3-9]\d|19\d\d|20[0-2]\d)\s*(?:م|ميلادي)?(?!\d)', ctx)]
        hs_any = [int(y) for y in re.findall(r'\b(1[23]\d\d|14[0-4]\d)\b', ctx)]
        pair = next(((h, g) for h in hs_any for g in gs if abs(g - (0.970229 * h + 621.57)) <= 2), None)
        ed = next((w for w in ORD if w in ctx), None)
        m = re.search(r'الطبعة\s*[:\-]?\s*\(?(\d{1,2})\)?(?!\d)', ctx)
        if not ed and m: ed = m.group(1)
        if pair: return pair[0], pair[1], ed, ctx
        gm = [int(y) for y in re.findall(r'\b(18[3-9]\d|19\d\d|20[0-2]\d)\s*م\b', ctx)]
        if len(set(hs)) == 1 and not gs: return hs[0], None, ed, ctx
        if len(set(gm)) == 1 and not hs_any: return None, gm[0], ed, ctx
        own = [int(y) for y in re.findall(r'(?<!\d)(\d{4})(?!\d)', l)]          # one lone year on the edition line itself
        if len(own) == 1 and re.search(r'الطبع', l):
            y = own[0]
            if 1250 <= y <= 1447: return y, None, ed, l
            if 1830 <= y <= 2026: return None, y, ed, l
    return None

def first_file(b):
    fs = [f for f, s in sorted(b['files']) if not re.search(r'الواجهة|الفهارس|صور المخطوط', f)] or [f for f, s in sorted(b['files'])]
    nums = [f for f in fs if re.match(r'0*1 - ', f)]
    return (nums or fs)[0]

def read_book(b, size_cap=250e6):
    key = f"{b['cat']}/{b['folder']}"
    f = first_file(b)
    size = dict(b['files'])[f]
    rec = {'key': key, 'file': f, 'ok': False}
    if size > size_cap: rec['why'] = 'too big'; return rec
    rel = f"{b['cat']}/{f}" if len(b['files']) == 1 and f == b['folder'] + '.pdf' else f"{b['cat']}/{b['folder']}/{f}"
    d = tempfile.mkdtemp(dir=TMP); local = os.path.join(d, 'b.pdf')
    try:
        r = subprocess.run(['flock', '/tmp/phone-ftp.lock', 'rclone', 'copyto', 'phone:Books/' + rel, local, '-q', '--retries', '3'],
                           capture_output=True, timeout=1800)
        if r.returncode or not os.path.exists(local): rec['why'] = 'copy failed'; return rec
        for page in (2, 1, 3, 4, 5, 6, 7, 8):
            t = subprocess.run(['pdftotext', '-f', str(page), '-l', str(page), '-layout', local, '-'], capture_output=True, text=True).stdout
            src = 'text'
            if len(re.sub(r'\s', '', t)) < 30:                     # no text layer: OCR a 300-dpi render
                png = os.path.join(d, f'p{page}')
                subprocess.run(['pdftoppm', '-r', '300', '-gray', '-f', str(page), '-l', str(page), '-singlefile', '-png', local, png],
                               capture_output=True, timeout=600)
                if not os.path.exists(png + '.png'): continue
                t = subprocess.run(['tesseract', png + '.png', '-', '-l', 'ara+eng', '--psm', '6'], capture_output=True, text=True,
                                   env={**os.environ, 'OMP_THREAD_LIMIT': '1'}, timeout=600).stdout
                os.remove(png + '.png'); src = 'ocr'
            p = parse(t)
            if p:
                rec.update({'ok': True, 'page': page, 'src': src, 'hijri': p[0], 'gregorian': p[1], 'edition_no': p[2], 'line': p[3][:200]})
                return rec
        rec['why'] = 'no clean edition line'
        return rec
    except subprocess.TimeoutExpired:
        rec['why'] = 'timeout'; return rec
    finally:
        subprocess.run(['rm', '-rf', d])

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--workers', type=int, default=5); ap.add_argument('--all', action='store_true')
    ap.add_argument('--sample', type=int, default=0); a = ap.parse_args()
    os.makedirs(TMP, exist_ok=True); os.makedirs(os.path.dirname(OUT), exist_ok=True)
    cat = json.load(open(J('data/catalog.json'), encoding='utf-8'))
    info = json.load(open(J('data/editions/edition-info.json'), encoding='utf-8')) if os.path.exists(J('data/editions/edition-info.json')) else {}
    done = set()
    if os.path.exists(OUT):
        for l in open(OUT, encoding='utf-8'):
            try: done.add(json.loads(l)['key'])
            except ValueError: pass
    todo = [b for b in cat['books'] if f"{b['cat']}/{b['folder']}" not in done
            and (a.all or not ({'hijri', 'gregorian'} & set(info.get(f"{b['cat']}/{b['folder']}", {}))))]
    if a.sample:
        random.Random(7).shuffle(todo); todo = todo[:a.sample]
    print(len(todo), 'books to read', flush=True)
    n = [0, 0]
    def work(b):
        rec = read_book(b)
        with lock:
            with open(OUT, 'a', encoding='utf-8') as w: w.write(json.dumps(rec, ensure_ascii=False) + '\n')
            n[0] += 1; n[1] += rec['ok']
            if n[0] % 25 == 0: print(f'{n[0]}/{len(todo)} read, {n[1]} with a clean edition line', flush=True)
    with ThreadPoolExecutor(a.workers) as ex: list(ex.map(work, todo))
    print('done', n, flush=True)

if __name__ == '__main__':
    main()
