"""Open or collect the pages a book cites — on the desktop (Brave tabs at the right page) or on the phone (one small
PDF of all the cited pages, with a bookmark per citation, dropped into the phone's Download/مقتطفات/ for Acrobat).

Citations file (UTF-8, one per line):   book words | volume | pages        e.g.
    سير أعلام النبلاء | 1 | 366-372
    الطبقات الكبرى ابن سعد | 7 | 396
    البداية والنهاية | 9 | 125, 130
  book words: any words of the title/author/edition as written in the library names (local ~/Books first, then phone)
  volume: the NN of «NN - …» volume files (leave empty for one-file books)
  pages: printed page numbers (as in the book's references); add «p» for PDF page numbers instead (e.g. p412)
Printed → PDF page: the PDF's own page labels if present; else the page number read from the page (text layer, or
OCR of the top/bottom strip near the expected place); learned offsets are cached in data/excerpts/offsets.json.

Usage: PYTHONPATH=~/.local/share/phone-library-tools/site /usr/bin/python3 scripts/excerpt.py citations.txt NAME
           [--open] [--phone] [--pad 0]
  --open   open every cited page in Brave tabs, one after another (desktop)
  --phone  upload data/excerpts/NAME.pdf to the phone: Download/مقتطفات/NAME.pdf
  --pad N  also take N pages after each cited page (a quotation often runs over)"""
import csv, ftplib, json, os, re, subprocess, sys, unicodedata
import pymupdf
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
import phone_host
from textnorm import norm
from phone_host import HOST, PORT
J = lambda *p: os.path.join(ROOT, *p)
LB = os.path.expanduser('~/Books')
OUT = J('data/excerpts'); CACHE = os.path.expanduser('~/.cache/phone-library/books')
os.makedirs(OUT, exist_ok=True); os.makedirs(CACHE, exist_ok=True)
OFFS = J('data/excerpts/offsets.json')
offsets = json.load(open(OFFS)) if os.path.exists(OFFS) else {}
AR_DIGITS = str.maketrans('٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹', '01234567890123456789')

def find_book(words, vol):
    """→ (location, path): location 'local' (~/Books) or 'phone'."""
    keys = norm(words).split()
    cands = []
    for loc, paths in (('local', local_paths()), ('phone', phone_paths())):
        for p in paths:
            n = norm(p)
            if all(k in n for k in keys):
                fn = p.rsplit('/', 1)[-1]
                m = re.match(r'^0*(\d+) - ', fn)
                if vol:
                    if m and int(m.group(1)) == int(vol): cands.append((loc, p))
                elif not m or p.count('/') == 1: cands.append((loc, p))
        if cands: break
    if not cands: raise SystemExit(f'not found: «{words}» vol {vol or "-"}')
    cands.sort(key=lambda c: len(c[1]))
    return cands[0]

def local_paths():
    out = []
    for root, d, fs in os.walk(LB):
        for f in fs:
            if f.lower().endswith('.pdf'): out.append(os.path.relpath(os.path.join(root, f), LB))
    return out

def phone_paths():
    return [p for p, s in csv.reader(open(J('data/phone/index-now.tsv'), encoding='utf-8'), delimiter='\t') if p.lower().endswith('.pdf')]

def fetch(loc, p):
    if loc == 'local': return os.path.join(LB, p)
    dst = os.path.join(CACHE, p.replace('/', '__'))
    if not os.path.exists(dst):
        f = ftplib.FTP(); f.encoding = 'utf-8'; f.connect(HOST, PORT, timeout=300); phone_host.login(f)
        with open(dst + '.part', 'wb') as o: f.retrbinary('RETR /Books/' + p, o.write, blocksize=1 << 16)
        f.quit(); os.replace(dst + '.part', dst)
    return dst

def page_number_on(page):
    """The printed page number shown on a page (top or bottom strip): text layer first, OCR otherwise."""
    r = page.rect
    for strip in (pymupdf.Rect(r.x0, r.y0, r.x1, r.y0 + r.height * 0.12), pymupdf.Rect(r.x0, r.y1 - r.height * 0.10, r.x1, r.y1)):
        t = page.get_text('text', clip=strip).translate(AR_DIGITS)
        nums = [int(x) for x in re.findall(r'(?<!\d)(\d{1,4})(?!\d)', t)]
        if nums: return nums
    nums = []
    for strip in (pymupdf.Rect(r.x0, r.y0, r.x1, r.y0 + r.height * 0.12), pymupdf.Rect(r.x0, r.y1 - r.height * 0.10, r.x1, r.y1)):
        pix = page.get_pixmap(dpi=200, clip=strip, colorspace=pymupdf.csGRAY)
        png = os.path.join(CACHE, 'strip.png'); pix.save(png)
        t = subprocess.run(['tesseract', png, '-', '-l', 'ara+eng', '--psm', '6'], capture_output=True, text=True).stdout.translate(AR_DIGITS)
        nums += [int(x) for x in re.findall(r'(?<!\d)(\d{1,4})(?!\d)', t)]
    return nums

def pdf_index(doc, key, printed):
    """Printed page → 0-based PDF page index."""
    labels = [doc[i].get_label() for i in range(min(len(doc), 2000))] if doc.page_count else []
    if any(labels):
        for i, l in enumerate(labels):
            if l and l.translate(AR_DIGITS).strip() == str(printed): return i
    if key in offsets: return max(0, min(len(doc) - 1, printed + offsets[key]))
    guesses = [printed + d for d in (0, 1, 2, 3, 4, -1, 5, 6, 8, 10, 12, 15, 20, 25, 30)]
    for g in guesses:
        if not 0 <= g < len(doc): continue
        for i in (g, g - 1, g + 1):
            if 0 <= i < len(doc) and printed in page_number_on(doc[i]):
                offsets[key] = i - printed; json.dump(offsets, open(OFFS, 'w'), ensure_ascii=False, indent=0)
                return i
    print(f'  page {printed}: number not found on the pages, using PDF page {printed} (add «p» to give PDF pages)')
    return max(0, min(len(doc) - 1, printed - 1))

def main():
    a = sys.argv[1:]; cfile, name = a[0], a[1]
    pad = int(a[a.index('--pad') + 1]) if '--pad' in a else 0
    out = pymupdf.open(); toc = []; tabs = []
    for line in open(cfile, encoding='utf-8'):
        if not line.strip() or line.startswith('#'): continue
        words, vol, pages = [x.strip() for x in (line.split('|') + ['', ''])[:3]]
        loc, p = find_book(words, vol)
        path = fetch(loc, p); doc = pymupdf.open(path)
        for part in re.split(r'[,،]\s*', pages):
            if not part: continue
            pdf_mode = part.startswith('p'); part = part.lstrip('p')
            lo, _, hi = part.partition('-'); lo, hi = int(lo), int(hi or lo)
            i0 = (lo - 1) if pdf_mode else pdf_index(doc, p, lo)
            i1 = (hi - 1) if pdf_mode else (i0 + (hi - lo))
            i1 = min(len(doc) - 1, i1 + pad)
            toc.append([1, f'{p.split("/")[1] if "/" in p else p} — ج {vol or "-"} ص {part}', len(out) + 1])
            out.insert_pdf(doc, from_page=i0, to_page=i1)
            tabs.append(f'file://{path}#page={i0 + 1}')
            print(f'  {words} ج{vol or "-"} ص{part} → {p} (PDF pages {i0 + 1}–{i1 + 1})')
    out.set_toc(toc)
    dst = os.path.join(OUT, name + '.pdf'); out.save(dst, garbage=3, deflate=True)
    print('excerpt:', dst, len(out), 'pages')
    if '--open' in a:
        for t in tabs: subprocess.Popen(['brave-browser', t], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if '--phone' in a:
        f = ftplib.FTP(); f.encoding = 'utf-8'; f.connect(HOST, PORT, timeout=300); phone_host.login(f)
        try: f.mkd('/Download/مقتطفات')
        except ftplib.error_perm: pass
        with open(dst, 'rb') as i: f.storbinary(f'STOR /Download/مقتطفات/{name}.pdf', i)
        f.quit(); print('on the phone: Download/مقتطفات/' + name + '.pdf (open it in Acrobat)')

if __name__ == '__main__':
    main()
