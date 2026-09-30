"""Match every phone PDF to its source archive.org file by exact byte size, then to the Waqfeya book.
Inputs: data/phone/index-*.tsv, data/archive/{files,items}.jsonl, data/archive/titles.jsonl,
        data/waqfeya/books.jsonl, data/waqfeya/details.jsonl
Output: data/phone/provenance.tsv"""
import json, csv, re, os, sys
from collections import defaultdict, Counter
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J = lambda p: os.path.join(ROOT, p)

def norm(s):
    s = re.sub(r'[ً-ْـ]', '', s or '')
    for a, b in (('أ', 'ا'), ('إ', 'ا'), ('آ', 'ا'), ('ة', 'ه'), ('ى', 'ي'), ('ؤ', 'و'), ('ئ', 'ي')): s = s.replace(a, b)
    return re.sub(r'[^ء-ي0-9 ]', ' ', s).split()

def sim(a, b):
    A, B = set(norm(a)), set(norm(b))
    return len(A & B) / max(1, min(len(A), len(B)))

def load_items():
    files = {}
    for fn in ['data/archive/items.jsonl'] + sorted(os.path.relpath(p, ROOT) for p in __import__('glob').glob(os.path.join(ROOT, 'data/archive/files*.jsonl'))):
        if os.path.exists(J(fn)):
            for l in open(J(fn)):
                d = json.loads(l)
                if not d.get('error'): files[d['id']] = d.get('files', [])
    return files

def load_waqfeya():
    books = {}; by_item = defaultdict(list)
    for l in open(J('data/waqfeya/books.jsonl')):
        b = json.loads(l); books[b['_id']] = b
    for fn in ('data/waqfeya/details.jsonl', 'data/waqfeya/details2.jsonl'):
        if os.path.exists(J(fn)):
            for l in open(J(fn)):
                d = json.loads(l)
                if 'links' in d: books[d['_id']] = {**books.get(d['_id'], {}), **d}
    for bid, b in books.items():
        ids = set(re.findall(r'archive\.org/(?:details|download)/([^/"?#\s]+)', json.dumps([b.get('thumbnail'), b.get('links'), b.get('archiveLink')], ensure_ascii=False)))
        for i in ids: by_item[i].append(bid)
    return books, by_item

if __name__ == '__main__':
    index = sys.argv[1]
    items = load_items(); books, wq_by_item = load_waqfeya()
    titles = {}
    if os.path.exists(J('data/archive/titles.jsonl')):
        for l in open(J('data/archive/titles.jsonl')):
            d = json.loads(l); titles[d['identifier']] = d.get('title')
    by_size = defaultdict(list)
    for i, fs in items.items():
        for f in fs:
            if f['name'].lower().endswith('.pdf') and f['size'] > 0: by_size[f['size']].append((i, f['name']))
    rows = list(csv.reader(open(index), delimiter='\t'))
    reject = set()   # (path, archive id, file) proven different by scripts/verify_provenance.py
    vf = J('data/phone/provenance-verified.tsv')
    if os.path.exists(vf):
        reject = {(r[0], r[1], r[2]) for r in csv.reader(open(vf), delimiter='\t') if r[3] == 'different'}
    folder_items = defaultdict(Counter)
    for p, s in rows:
        c = by_size.get(int(s), [])
        if len(c) == 1: folder_items[p.rsplit('/', 1)[0]][c[0][0]] += 1
    out = csv.writer(open(J('data/phone/provenance.tsv'), 'w'), delimiter='\t')
    out.writerow(['path', 'size', 'match', 'archive_id', 'orig_name', 'waqfeya_id', 'waqfeya_name', 'waqfeya_author', 'waqfeya_category', 'archive_title'])
    stats = Counter()
    for p, s in rows:
        folder = p.rsplit('/', 1)[0]; c = [x for x in by_size.get(int(s), []) if (p, x[0], x[1]) not in reject]
        if not c: stats['none'] += 1; out.writerow([p, s, 'none'] + [''] * 7); continue
        if len(c) == 1: pick, kind = c[0], 'unique'
        else:
            fav = folder_items[folder]
            pick = max(c, key=lambda x: (fav.get(x[0], 0), sim(folder, (books.get((wq_by_item.get(x[0]) or [''])[0], {}) or {}).get('name', '') or titles.get(x[0], '') or x[1])))
            kind = 'ambiguous-%d' % len(c)
        wid = (wq_by_item.get(pick[0]) or [''])[0]; b = books.get(wid, {})
        stats['waqfeya' if wid else 'archive-only'] += 1; stats[kind.split('-')[0]] += 1
        out.writerow([p, s, kind, pick[0], pick[1], wid, b.get('name', ''), (b.get('author') or {}).get('name', ''),
                      (b.get('category') or {}).get('name', ''), titles.get(pick[0], '')])
    print(dict(stats), 'of', len(rows))
