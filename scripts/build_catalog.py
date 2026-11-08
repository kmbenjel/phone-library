"""Build the machine-readable catalog (data/catalog.json + catalog.tsv) from the phone index + provenance + sources.
Usage: python3 scripts/build_catalog.py data/phone/index-<date>.tsv"""
import json, csv, os, re, sys, time
from collections import defaultdict, OrderedDict
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J = lambda p: os.path.join(ROOT, p)
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from special_dirs import NOT_BOOKS
INDEX_DIR = 'فهارس الويب'

from textnorm import title_key, norm
# generic words never make two titles alike (normalised like title_key's output: «رسالة» → «رساله»; 2026-10-09 «ديوان
# عنترة» gave its author to «ديوان كشاجم» through the one word «ديوان»)
STOP0 = {norm(w) for w in ('كتاب', 'رسالة', 'جزء', 'شرح', 'مختصر', 'في', 'على', 'من', 'الى', 'إلى', 'عن', 'ومعه', 'ويليه', 'ط', 'ت',
                           'ديوان', 'مجموعة', 'مجموع', 'مؤلفات', 'رسائل', 'أعمال', 'الشيخ', 'الإمام', 'تحقيق', 'ودراسة', 'دراسة')}
def _w(t):
    return {w for w in title_key(t).split() if len(w) > 2 and w not in STOP0}

EDITION_HEAD = re.compile(r'^(ت|ط|ترجمة|تنسيق|تقديم|إعداد|جمع|اعتنى|اعتناء|عني|صحح|صححه|قدم|قرأ|نسخه|ضبط|شرح|راجع|أعده|خرج|وقف على|'
                          r'دار|مكتبة|المكتبة|مطبعة|المطبعة|مؤسسة|منشورات|وزارة|جامعة|مركز|المجمع|مجمع|الهيئة|المجلس|الدار|'
                          r'مخطوط|رسالة|أطروحة|مستل|\d)\b')

def split_folder(name):
    """'Title - Author (edition)' -> (title, author, edition). Separators inside brackets are ignored.
    The names of 2026-10-10 have no parentheses: «Title - Author - ت Editor - Publisher City» → the author is the
    second part unless it opens an edition («ت»، a printed role, a publisher, «مخطوط»…)."""
    if '/' in name:
        _, name = name.rsplit('/', 1)
    if '(' not in name and ' - ' in name:
        segs = name.split(' - ')
        title, rest = segs[0], segs[1:]
        author = rest.pop(0) if rest and not EDITION_HEAD.match(rest[0]) else ''
        return title.strip(), author.strip(), ' - '.join(rest).strip()
    depth, cut = 0, -1
    for i, ch in enumerate(name):
        depth += ch == '('; depth -= ch == ')'
        if depth == 0 and name.startswith(' - ', i): cut = i; break
    title, rest = (name[:cut], name[cut + 3:]) if cut >= 0 else (name, '')
    m = re.match(r'^(.*?)\s*\((.*)\)\s*$', rest)
    author, edition = (m.group(1), m.group(2)) if m else (rest, '')
    if re.match(r'^(ط|ت)[ .]', author): author, edition = '', (author + (' - ' + edition if edition else ''))
    if not rest:
        m = re.match(r'^(.*?)\s*\(([^()]*)\)\s*$', title)
        if m: title, edition = m.group(1), m.group(2)
    return title.strip(), author.strip(), edition.strip()

def count_titles(books, prov):
    """Distinct works: 1 per book folder; collections/bucket folders count each work inside;
    periodicals/series count as 1 title + their issues. ('books' in stats = folders.)"""
    from rename_plan import COLLECTION
    titles = issues = 0
    for b in books:
        ps = [f'{b["cat"]}/{b["folder"]}/{f}' for f, _ in b['files']]
        src = {prov[p]['waqfeya_id'] for p in ps if p in prov and prov[p]['waqfeya_id']}
        front = lambda p: re.search(r'\((الواجهة|المقدمة)\)|^00 - ', p.rsplit('/', 1)[1])
        if re.match(r'^(مجلة|سلسلة)', b['folder']) or b['cat'] == 'المجلات والدوريات والسلاسل الكبرى':
            titles += 1; issues += len([p for p in ps if not front(p)])
        elif COLLECTION.match(b['folder']) or len(src) >= 3:
            titles += len(src) + len([p for p in ps if not (p in prov and prov[p]['waqfeya_id']) and not front(p)])
        else:
            titles += 1
    return titles, issues

def main(index):
    prov = {}
    if os.path.exists(J('data/phone/provenance.tsv')):
        for r in csv.DictReader(open(J('data/phone/provenance.tsv')), delimiter='\t'): prov[r['path']] = r
    wq = {}
    for fn in ('data/waqfeya/books.jsonl', 'data/waqfeya/details.jsonl', 'data/waqfeya/details2.jsonl'):
        if os.path.exists(J(fn)):
            for l in open(J(fn)):
                d = json.loads(l); wq[d['_id']] = {**wq.get(d['_id'], {}), **d}
    books = OrderedDict()
    for path, size in csv.reader(open(index), delimiter='\t'):
        parts = path.split('/')
        if parts[0] in NOT_BOOKS or len(parts) < 2: continue
        if len(parts) == 2:
            cat, folder, fname = parts[0], parts[1][:-4] if parts[1].lower().endswith('.pdf') else parts[1], parts[1]
        else:
            cat, folder, fname = parts[0], '/'.join(parts[1:-1]), parts[-1]
        b = books.setdefault((cat, folder), {'cat': cat, 'folder': folder, 'files': [], 'bytes': 0, 'waqfeya': set(), 'archive': set()})
        b['files'].append([fname, int(size)]); b['bytes'] += int(size)
        p = prov.get(path)
        if p and p['match'] != 'none':
            b['archive'].add(p['archive_id'])
            if p['waqfeya_id']: b['waqfeya'].add(p['waqfeya_id'])
    out = []
    for n, b in enumerate(sorted(books.values(), key=lambda x: (x['cat'], x['folder'])), 1):
        t, a, e = split_folder(b['folder'])
        b['files'].sort()
        rec = {'id': n, 'cat': b['cat'], 'folder': b['folder'], 'title': t, 'author': a, 'edition': e,
               'files': b['files'], 'bytes': b['bytes'], 'archive': sorted(b['archive'])}
        ws = [wq[i] for i in sorted(b['waqfeya']) if i in wq]
        if ws:
            rec['waqfeya'] = [{'id': x['_id'], 'name': x.get('name'), 'url': 'https://waqfeya.net/books/' + x.get('permalink', '')} for x in ws]
        # author, century and edition only from a record whose title resembles the book: a Waqfeya record may link another
        # book's file (صيام الصالحين → «مقاصد الصوم»; 2026-10-09 the catalog showed its author for the wrong book)
        own = _w(t + ' ' + b['folder'])
        ws = [x for x in ws if len(_w(x.get('name', '')) & own) >= max(1, 0.5 * min(len(_w(x.get('name', ''))), len(own) or 1))]
        if ws:
            w = ws[0]
            rec['century'] = (w.get('century') or {}).get('name', '')
            if not rec['author']: rec['author'] = (w.get('author') or {}).get('name', '')
            for k in ('researcher', 'publisher', 'numberOfVolumes', 'yearOfPublish'):
                if w.get(k): rec[k] = w[k]
        out.append(rec)
    cats = defaultdict(lambda: {'books': 0, 'files': 0, 'bytes': 0})
    for r in out:
        c = cats[r['cat']]; c['books'] += 1; c['files'] += len(r['files']); c['bytes'] += r['bytes']
    titles, issues = count_titles(out, prov)
    cat = {'generated': time.strftime('%Y-%m-%d %H:%M'), 'root': 'Books',
           'stats': {'categories': len(cats), 'books': len(out), 'titles': titles, 'issues': issues,
                     'files': sum(len(r['files']) for r in out), 'bytes': sum(r['bytes'] for r in out)},
           'categories': [{'name': k, **v} for k, v in sorted(cats.items())], 'books': out}
    json.dump(cat, open(J('data/catalog.json'), 'w'), ensure_ascii=False, separators=(',', ':'))
    with open(J('data/catalog.tsv'), 'w') as f:
        w = csv.writer(f, delimiter='\t'); w.writerow(['id', 'category', 'folder', 'title', 'author', 'edition', 'files', 'bytes', 'century', 'waqfeya_url', 'archive_ids'])
        for r in out:
            w.writerow([r['id'], r['cat'], r['folder'], r['title'], r['author'], r['edition'], len(r['files']), r['bytes'], r.get('century', ''),
                        (r.get('waqfeya') or [{}])[0].get('url', ''), ' '.join(r['archive'])])
    print('catalog:', cat['stats'])

if __name__ == '__main__':
    main(sys.argv[1])
