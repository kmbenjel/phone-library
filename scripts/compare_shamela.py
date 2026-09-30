"""Compare the phone library with the locally installed Shamela: which Shamela books have a PDF on the phone.
Output: data/compare/shamela-matches.tsv"""
import csv, json, os, sys
from collections import defaultdict
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from textnorm import title_key, author_tokens, norm
J = lambda p: os.path.join(ROOT, p)
cat = json.load(open(J('data/catalog.json')))
# every title a phone book is known by: folder title, Waqfeya names, per-file bracketed titles (bucket folders)
keys = defaultdict(set)   # title key -> set(book id)
auth = {}
for b in cat['books']:
    ts = {b['title']} | {w['name'] for w in b.get('waqfeya', [])}
    for t in ts:
        k = title_key(t)
        if k: keys[k].add(b['id'])
    auth[b['id']] = author_tokens(b.get('author', ''))
by_first = defaultdict(list)
for k in keys: by_first[k.split()[0]].append(k)
rows = []
for r in csv.DictReader(open(J('data/shamela/books.tsv')), delimiter='\t'):
    k = title_key(r['title']); at = author_tokens(r['author'])
    hit, how = set(), ''
    if k in keys: hit, how = set(keys[k]), 'exact'
    else:
        kw = k.split()
        for pk in by_first.get(kw[0] if kw else '', []):
            if pk.startswith(k + ' ') or k.startswith(pk + ' '):
                if len(kw) >= 3 and len(pk.split()) >= 3: hit |= keys[pk]; how = 'prefix'
                elif at:                                   # short title: only with a matching author
                    ok = {h for h in keys[pk] if auth[h] & at}
                    if ok: hit |= ok; how = 'prefix+author'
    if hit and len(k.split()) <= 2 and at:        # short titles are ambiguous: reject a *different* known author
        hit = {h for h in hit if not auth[h] or auth[h] & at}; how = '' if not hit else how
    rows.append([r['book_id'], r['title'], r['author'], r['death'], r['category'], r['has_pdf'], how, ' '.join(map(str, sorted(hit)))])
with open(J('data/compare/shamela-matches.tsv'), 'w') as f:
    w = csv.writer(f, delimiter='\t'); w.writerow(['shamela_id', 'title', 'author', 'death', 'category', 'shamela_pdf', 'match', 'phone_book_ids']); w.writerows(rows)
found = sum(1 for r in rows if r[7])
print(f'shamela books: {len(rows)}  on phone: {found} ({found*100/len(rows):.1f}%)')
