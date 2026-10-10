"""Which books have already been checked against their own pages? (owner 2026-10-10: «راجع ما فعلته سابقا وقاعدة البيانات
التي عندك لتعلم هل تم التحقق من ذلك من قبل في حق هذا الكتاب أم لا»)

Evidence of an earlier reading, each carried forward along the logged moves to today's path:
  sheet    — the imprint sheets (data/editions/imprint-sheets/books.tsv): book n was READ when imprint-read.tsv has row n,
             imprint-misfiled.tsv lists it, or a plan's reason cites «book n»; a sheet made but never read is «sheet only»;
  rename   — a logged move whose reason cites the file's own pages (title page, imprint, «read», the PDF titles inside…);
  text     — the imprint taken from the text layer (data/editions/imprint-text.tsv);
  titles   — the PDF's embedded title checked by verify_names.py (data/phone/name-checks.tsv lists only the disagreements).
→ data/names/read-status.tsv: book (cat/folder or cat/file), status (read / sheet only / never), sources, what was read.
Usage: python3 scripts/read_status.py"""
import csv, json, os, re, unicodedata, collections
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J = lambda *p: os.path.join(ROOT, *p)
N = lambda s: unicodedata.normalize('NFC', s)
READ = re.compile(r'title page|title-page|imprint|صفحة العنوان|الغلاف|by eye|pages? read|read:|\(read|PDF titles inside|من داخل', re.I)

def forward():
    fwd = {}
    for r in csv.reader(open(J('data', 'changes', 'changes.tsv'), encoding='utf-8'), delimiter='\t'):
        if len(r) > 3 and r[1] == 'move' and r[2] and r[3]:
            fwd[N(r[2].removeprefix('Books/'))] = N(r[3].removeprefix('Books/'))
    return fwd

def follow(p, fwd):
    seen = set()
    while p in fwd and p not in seen: seen.add(p); p = fwd[p]
    return p

def book_of(path):
    parts = path.split('/')
    return '/'.join(parts[:2]) if len(parts) >= 3 else path.removesuffix('.pdf')

def main():
    idx = [N(l.split('\t', 1)[0]) for l in open(J('data', 'phone', 'index-now.tsv'), encoding='utf-8') if l.strip()]
    books_now = {book_of(p) for p in idx}
    fwd = forward()
    st = collections.defaultdict(lambda: {'src': set(), 'what': []})
    # imprint sheets
    read_n = {}
    for r in csv.DictReader(open(J('data', 'editions', 'imprint-read.tsv'), encoding='utf-8'), delimiter='\t'):
        read_n[r['n']] = ' '.join(x for x in (r.get('note'), r.get('hijri'), r.get('gregorian')) if x)
    for l in open(J('data', 'editions', 'imprint-misfiled.tsv'), encoding='utf-8'):
        b = l.rstrip('\n').split('\t')
        if b and b[0].isdigit(): read_n[b[0]] = 'MISFILED: ' + (b[2] if len(b) > 2 else '')
    for r in csv.reader(open(J('data', 'changes', 'changes.tsv'), encoding='utf-8'), delimiter='\t'):
        if len(r) > 4:
            for n in re.findall(r'book (\d+)\)', r[4]): read_n.setdefault(n, 'read (see plan ' + r[5].strip() + ')')
    for l in open(J('data', 'editions', 'imprint-sheets', 'books.tsv'), encoding='utf-8'):
        b = l.rstrip('\n').split('\t')
        if len(b) < 3: continue
        n, book, fn = b[0], N(b[1]), N(b[2])
        cat = book.split('/')[0]
        path = f'{book}/{fn}' if not book.endswith(fn.removesuffix('.pdf')) else f'{cat}/{fn}'
        now = book_of(follow(path, fwd))
        if n in read_n: st[now]['src'].add('sheet'); st[now]['what'].append(f'sheet book {n}: {read_n[n][:120]}')
        else: st[now]['src'].add('sheet only')
    # renames citing the file's own pages
    for r in csv.reader(open(J('data', 'changes', 'changes.tsv'), encoding='utf-8'), delimiter='\t'):
        if len(r) > 5 and r[1] == 'move' and READ.search(r[4]):
            now = book_of(follow(N(r[3].removeprefix('Books/')), fwd))
            st[now]['src'].add('rename'); st[now]['what'].append(f'{r[5].strip()}: {r[4][:120]}')
    # imprint text layer
    if os.path.exists(J('data', 'editions', 'imprint-text.tsv')):
        for l in open(J('data', 'editions', 'imprint-text.tsv'), encoding='utf-8'):
            b = l.rstrip('\n').split('\t')
            if b and b[0]: st[book_of(follow(N(b[0]) + '/x', fwd)) if '/' in b[0] else b[0]]['src'].add('text')
    os.makedirs(J('data', 'names'), exist_ok=True)
    c = collections.Counter()
    with open(J('data', 'names', 'read-status.tsv'), 'w', encoding='utf-8') as w:
        w.write('book\tstatus\tsources\twhat was read\n')
        for b in sorted(books_now):
            s = st.get(b)
            src = s['src'] if s else set()
            status = 'read' if src & {'sheet', 'rename', 'text'} else ('sheet only' if 'sheet only' in src else 'never')
            c[status] += 1
            w.write(f"{b}\t{status}\t{','.join(sorted(src))}\t{' | '.join(dict.fromkeys(s['what'])) if s else ''}\n")
    print(dict(c), 'of', len(books_now), 'books → data/names/read-status.tsv')

if __name__ == '__main__':
    main()
