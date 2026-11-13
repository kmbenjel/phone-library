"""Author death years for books that did not match a Shamela book (owner 2026-11-08: the index is «by death year»;
1,797 books showed only Waqfeya's century, al-Shafi'i, al-Baji, al-'Izz among them).

A death year is given to a catalog author only on evidence, in this order:
  1. «phone»   — the same author name (normalised) already carries a Shamela death year on another phone book
                 (data/compare/shamela-matches.tsv), and all those years agree;
  2. «shamela» — Shamela's author table (master.db, read-only) has exactly one author of that short name whose death
                 falls in the book's Waqfeya century.
A name that two Shamela authors share (in the book's century, or anywhere when it has none) gets no year by either path.
Either way, when the book has a Waqfeya century the year must fall in it; a book without one gets a year only when every
book of that name on the phone lies in one century. Any disagreement is listed in the review table, not used.
Output: data/names/author-death.tsv (author_key, death, source, books, example) + author-death-review.tsv.
Used by edition_info.py (index card «death») and report_people.py (report 07).
  scripts/author_death.py            # rebuild the tables
"""
import collections, csv, json, os, re, sqlite3, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from textnorm import norm
J = lambda p: os.path.join(ROOT, p)
OUT, REVIEW = J('data/names/author-death.tsv'), J('data/names/author-death-review.tsv')
MASTER = os.path.expanduser('~/.local/share/shamela/database/master.db')
TITLES = re.compile(r'^(?:(?:الإمام|الامام|الحافظ|الشيخ|العلامة|العلامه|شيخ الإسلام|شيخ الاسلام|القاضي|الأستاذ|الدكتور|د)\.?\s+)+')
GOOD_MATCH = ('exact', 'prefix+author', 'smart-tokens', 'prefix')

def author_key(a):
    """The catalog author's first name form («الشاشي؛ إسحاق بن …» → «الشاشي»), titles dropped, normalised."""
    a = re.split(r'[؛;]', a or '')[0].strip()
    return norm(TITLES.sub('', a))

def century_of(c):
    m = re.search(r'(\d+)', c or ''); return int(m.group(1)) if m else None

def in_century(d, c):
    return c is None or (d - 1) // 100 + 1 == c

def build():
    cat = json.load(open(J('data/catalog.json'), encoding='utf-8'))
    books = {str(b['id']): b for b in cat['books']}
    matched = {}                                         # phone book id → Shamela death year of its matched work
    for r in csv.DictReader(open(J('data/compare/shamela-matches.tsv'), encoding='utf-8'), delimiter='\t'):
        if r['match'] not in GOOD_MATCH or not r['death'].isdigit() or not 0 < int(r['death']) < 1500: continue
        for i in (r['phone_book_ids'] or '').split(): matched.setdefault(i, int(r['death']))
    phone = collections.defaultdict(set)                 # author key → death years seen on matched phone books
    for i, d in matched.items():
        if i in books: phone[author_key(books[i].get('author'))].add(d)
    sham = collections.defaultdict(list)                 # Shamela short name → [(death, id)]
    db = sqlite3.connect(f'file:{MASTER}?mode=ro', uri=True)
    for aid, name, d in db.execute('select author_id, author_name, death_number from author'):
        if d and 0 < int(d) < 1500: sham[norm(TITLES.sub('', name or ''))].append((int(d), aid))
    res, review = {}, []
    allc = collections.defaultdict(set)                  # author key → every century its phone books show
    for i, b in books.items():
        k = author_key(b.get('author'))
        if i in matched: allc[k].add((matched[i] - 1) // 100 + 1)
        elif century_of(b.get('century')): allc[k].add(century_of(b.get('century')))
    todo = collections.defaultdict(list)                 # (author key, century or None) → books without a matched year
    for i, b in books.items():
        if i not in matched and b.get('author'): todo[(author_key(b['author']), century_of(b.get('century')))].append(b)
    for (k, c), bs in sorted(todo.items(), key=lambda kv: (kv[0][0], kv[0][1] or 0)):
        if not k or len(k) < 3: continue
        ex, cs = bs[0]['folder'], f'القرن {c}' if c else ''
        if c is None and len(allc[k]) > 1:               # no century of its own and the name spans several: no year
            review.append([k, '', 'no century; the name spans ' + ' '.join(map(str, sorted(allc[k]))), '', ex]); continue
        cc = c if c is not None else next(iter(allc[k]), None)
        got = None
        homs = {d for d, _ in sham.get(k, []) if in_century(d, cc)}   # Shamela authors who share this short name
        if len(homs) > 1:                                # «الشاشي» 335 and 325 …: the name alone cannot tell them apart
            review.append([k, ' '.join(map(str, sorted(homs))), 'several Shamela authors of that name', cs, ex]); continue
        ys = phone.get(k, set())
        fit = {d for d in ys if in_century(d, cc)}
        if len(fit) > 1:
            review.append([k, ' '.join(map(str, sorted(fit))), 'several years on the phone', cs, ex]); continue
        if fit:
            d = fit.pop()
            if homs and d not in homs:                   # Shamela's author of that name died in another year
                review.append([k, f'{d} / {" ".join(map(str, sorted(homs)))}', 'phone and Shamela author table disagree', cs, ex]); continue
            got = (d, 'phone')
        elif ys and c is not None:
            review.append([k, ' '.join(map(str, sorted(ys))), 'phone year outside the Waqfeya century', cs, ex]); continue
        if not got and cc is not None and len(homs) == 1:   # Shamela's author table needs a century as a second witness
            got = (homs.pop(), 'shamela')
        if got: res[(k, c)] = (got[0], got[1], len(bs), ex)
    with open(OUT, 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f, delimiter='\t', lineterminator='\n'); w.writerow(['author_key', 'century', 'death', 'source', 'books', 'example'])
        for k, c in sorted(res, key=lambda kc: (kc[0], kc[1] or 0)): w.writerow([k, c or '', *res[(k, c)]])
    with open(REVIEW, 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f, delimiter='\t', lineterminator='\n'); w.writerow(['author_key', 'years', 'why', 'century', 'example'])
        w.writerows(sorted(review, key=lambda r: r[0]))
    src = collections.Counter(v[1] for v in res.values())
    print(f'author-death: {len(res)} authors ({dict(src)}), {sum(v[2] for v in res.values())} books; review {len(review)}')

def load():
    """(author key, Waqfeya century or None) → death year; empty when the table was never built."""
    if not os.path.exists(OUT): return {}
    return {(r['author_key'], int(r['century']) if r['century'] else None): int(r['death'])
            for r in csv.DictReader(open(OUT, encoding='utf-8'), delimiter='\t')}

def death_of(table, b):
    """The table's year for a catalog book (author + its Waqfeya century), else None."""
    return table.get((author_key(b.get('author')), century_of(b.get('century'))))

if __name__ == '__main__':
    build()
