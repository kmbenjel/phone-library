"""Title-page reading sheets (owner 2026-10-10: a name comes from what the book itself prints; whatever the book's source,
look for its Shamela card AND its Waqfeya record; when anything is missing or doubtful, read the file — and watch for
books whose name is another book or another edition).

For each book not yet read (data/names/read-status.tsv), one row: its first pages (data/inspect/pages/<key>-1..3.jpg,
rendered by inspect_files.py), numbered. A sidecar text per sheet gives, for each book: its current name and the
candidates found BY TITLE in both catalogues — the Shamela cards (data/shamela/cards.jsonl: printed title, author,
editor, publisher, edition) and the Waqfeya records (data/waqfeya/details*.jsonl: author, researcher, publisher, year) —
so the reader confirms or rejects them against the page. What is read goes to data/names/title-read.tsv (one row per
book: n, book, verdict, title, author, editor, publisher, city, year, kind, section, note); verdict = ok | other-book |
other-edition | no-title-page | unreadable; section = the Shamela section the book belongs to when it is filed elsewhere
(owner: «في غاية التنظيم والدقة وحسن التصنيف»).
Usage: python3 scripts/title_sheets.py LIST [--per 2]   (LIST: one book per line, «cat/folder» or «cat/file-stem»)
       → data/names/sheets/sNNNN.jpg + sNNNN.txt, data/names/sheets/books.tsv (n, book, path, key)"""
import csv, hashlib, json, os, re, sys, unicodedata, collections
from PIL import Image, ImageDraw, ImageFont, ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True              # a page cut short by an interrupted render still shows its top
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from textnorm import norm, title_key
J = lambda *p: os.path.join(ROOT, *p)
N = lambda s: unicodedata.normalize('NFC', s)
OUT = J('data', 'names', 'sheets')
H = 640                                           # page height on the sheet (px)

def catalogues():
    sh, wq = [], []
    for l in open(J('data', 'shamela', 'cards.jsonl'), encoding='utf-8'):
        d = json.loads(l); sh.append((set(title_key(d.get('title', '')).split()), d))
    for fn in ('details.jsonl', 'details2.jsonl'):
        p = J('data', 'waqfeya', fn)
        if os.path.exists(p):
            for l in open(p, encoding='utf-8'):
                d = json.loads(l)
                if (d.get('category') or {}).get('name') == 'صوتيات': continue
                wq.append((set(title_key(d.get('name', '')).split()), d))
    inv = collections.defaultdict(list)
    for kind, L in (('sh', sh), ('wq', wq)):
        for i, (ks, d) in enumerate(L):
            for w in ks:
                if len(w) > 3: inv[(kind, w)].append(i)
    return sh, wq, inv

def candidates(title, sh, wq, inv, k=2):
    tk = {w for w in title_key(title).split() if len(w) > 2}
    out = []
    for kind, L in (('sh', sh), ('wq', wq)):
        score = collections.Counter()
        for w in tk:
            for i in inv.get((kind, w), ())[:4000]: score[i] += 1
        best = []
        for i, n in score.most_common(40):
            ks = {w for w in L[i][0] if len(w) > 2}
            if not ks: continue
            r = len(tk & ks) / max(len(tk), len(ks))
            first = title_key(title).split()[:2]
            if r >= 0.6 and all(w in ks for w in first if len(w) > 2): best.append((r, L[i][1]))   # the same opening words
        best.sort(key=lambda x: -x[0])
        for r, d in best[:k]:
            if kind == 'sh':
                out.append(f"  الشاملة #{d.get('id')}: {d.get('title','')} | المؤلف: {d.get('author','')} | المحقق: {d.get('editor','')} | الناشر: {d.get('publisher','')} | الطبعة: {d.get('edition','')}")
            else:
                a = (d.get('author') or {}).get('name', '') if isinstance(d.get('author'), dict) else d.get('author', '')
                out.append(f"  الوقفية: {d.get('name','')} | المؤلف: {a} | المحقق: {d.get('researcher','')} | الناشر: {d.get('publisher','')} | السنة: {d.get('yearOfPublish','')}")
    return out

def main(lst, per=2):
    os.makedirs(OUT, exist_ok=True)
    books = [N(l.strip()) for l in open(lst, encoding='utf-8') if l.strip()]
    idx = [N(l.split('\t', 1)[0]) for l in open(J('data', 'phone', 'index-now.tsv'), encoding='utf-8') if l.strip()]
    raw = {N(a): (a, b) for a, b in (l.rstrip('\n').split('\t')[:2] for l in open(J('data', 'phone', 'index-now.tsv'), encoding='utf-8') if l.strip())}
    files_of = collections.defaultdict(list)
    for p in idx:
        parts = p.split('/')
        files_of['/'.join(parts[:2]) if len(parts) >= 3 else p.removesuffix('.pdf')].append(p)
    key = {}
    for l in open(J('data', 'inspect', 'files.jsonl'), encoding='utf-8'):
        d = json.loads(l); key[N(d['path'])] = d.get('key')
    pages = collections.defaultdict(list)
    for f in os.listdir(J('data', 'inspect', 'pages')):
        m = re.match(r'^([0-9a-f]+)-(\d+)\.jpg$', f)
        if m: pages[m.group(1)].append(int(m.group(2)))
    sh, wq, inv = catalogues()
    reg = J(OUT, 'books.tsv')
    n0 = sum(1 for _ in open(reg, encoding='utf-8')) if os.path.exists(reg) else 0
    done_books = {l.split('\t')[1] for l in open(reg, encoding='utf-8')} if os.path.exists(reg) else set()
    todo, missing = [], []
    first = 1 + max([int(m.group(1)) for f in os.listdir(OUT) for m in [re.match(r'^s(\d{4})\.jpg$', f)] if m] or [-1])
    for b in books:
        if b in done_books: continue
        fs = sorted(files_of.get(b, []))
        f = next((x for x in fs if re.search(r'/0*1 - |/[^/]*\(الواجهة\)', x)), fs[0] if fs else None)
        k = key.get(f) if f else None
        if f and not pages.get(k):                  # renamed since inspection: front_pages.py keys by the current path
            k = hashlib.md5('\t'.join(raw.get(f, (f, ''))).encode()).hexdigest()[:16]   # the phone's own bytes
        if not k or not pages.get(k): missing.append(b); continue
        todo.append((b, f, k))
    font = ImageFont.load_default()
    try: font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 40)
    except OSError: pass
    with open(reg, 'a', encoding='utf-8') as R:
        for s in range(0, len(todo), per):
            group = todo[s:s + per]; rows, txt = [], []
            # after the last sheet already written: (n0 + s) // per reused it when a batch ended on an odd book and
            # overwrote it (2026-10-19: s0642, books 1283–1284, replaced by 1285–1286)
            sheet_no = first + s // per
            for j, (b, f, k) in enumerate(group):
                n = n0 + s + j
                ims = []
                for pg in sorted(pages[k])[:3]:
                    im = Image.open(J('data', 'inspect', 'pages', f'{k}-{pg}.jpg')).convert('L')
                    ims.append(im.resize((max(1, int(im.width * H / im.height)), H)))
                w = sum(i.width for i in ims) + 10 * len(ims) + 90
                row = Image.new('L', (w, H + 10), 255)
                d = ImageDraw.Draw(row); d.text((8, 10), str(n), fill=0, font=font)
                x = 90
                for i in ims: row.paste(i, (x, 5)); x += i.width + 10
                rows.append(row)
                R.write(f'{n}\t{b}\t{f}\t{k}\n')
                txt.append(f'[{n}] {b}\n  file: {f.rsplit("/", 1)[-1]}')
                title = re.sub(r'\s+-\s+.*$|\([^()]*\)', '', b.split('/', 1)[1]).strip()
                txt += candidates(title, sh, wq, inv) or ['  (no candidate by title)']
            W = max(r.width for r in rows); sheet = Image.new('L', (W, sum(r.height for r in rows) + 6 * len(rows)), 128)
            y = 0
            for r in rows: sheet.paste(r, (0, y)); y += r.height + 6
            sheet.save(J(OUT, f's{sheet_no:04d}.jpg'), quality=85)
            open(J(OUT, f's{sheet_no:04d}.txt'), 'w', encoding='utf-8').write('\n'.join(txt) + '\n')
    if missing:
        with open(J(OUT, 'no-pages.tsv'), 'a', encoding='utf-8') as w:
            for b in missing: w.write(b + '\n')
    print(f'{len(todo)} books on {-(-len(todo) // per)} sheets; {len(missing)} without page images (no-pages.tsv)')

if __name__ == '__main__':
    a = sys.argv[1:]
    per = int(a[a.index('--per') + 1]) if '--per' in a else 2
    main(a[0], per)
