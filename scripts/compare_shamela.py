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

# Additional inverted index on clean title tokens for fallback matching
word_to_books = defaultdict(set)
# Additional inverted index on clean title tokens for fallback matching
word_to_books = defaultdict(set)
phone_books = {}
phone_full_tks = {}
phone_folder_words = {}
phone_authors = {}
for b in cat['books']:
    phone_books[b['id']] = b
    tk = title_key(b['title'])
    fk = title_key(b['folder'])
    phone_folder_words[b['id']] = set(fk.split())
    phone_authors[b['id']] = auth[b['id']] | author_tokens(b['folder'])
    
    ts = {b['title']} | {w['name'] for w in b.get('waqfeya', [])}
    phone_full_tks[b['id']] = [title_key(t) for t in ts if t]
    
    all_words = set(tk.split()) | set(fk.split())
    for w in all_words:
        if len(w) > 2 and w not in ('كتاب', 'رسالة', 'جزء', 'شرح', 'مختصر'):
            word_to_books[w].add(b['id'])

# works contained in a phone book (scripts/contents.py; owner 2026-10-07: count them as present, never split the volume)
contained = defaultdict(set)
_CF = J('data/editions/contents.json')
if os.path.exists(_CF):
    _ids = {f"{b['cat']}/{b['folder']}": b['id'] for b in cat['books']}
    for _k, _items in json.load(open(_CF, encoding='utf-8')).items():
        for _it in _items:
            for _sid in _it.get('sh') or []:
                if _k in _ids: contained[_sid].add(_ids[_k])

rows = []
col_keywords = {'مجموع', 'مؤلفات', 'رسائل', 'أعمال', 'فتاوى', 'تراث', 'موسوعة', 'جامع', 'الجامع'}

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
    if not hit:
        # Smart fallback: token matching + author verification
        kw = [w for w in k.split() if len(w) > 2 and w not in ('كتاب', 'رسالة', 'جزء', 'شرح', 'مختصر')]
        if len(kw) >= 2:
            candidates = word_to_books[kw[0]]
            for w in kw[1:]:
                candidates = candidates & word_to_books[w]
                if not candidates: break
            if candidates:
                valid = set()
                for cid in candidates:
                    cb_at = phone_authors[cid]
                    if not at or not cb_at or (at & cb_at):
                        valid.add(cid)
                if valid:
                    hit, how = valid, 'smart-tokens'
                    
    if not hit and at:
        # Check strictly for attached books by the same author
        valid = set()
        for cid, cb in phone_books.items():
            cb_at = phone_authors[cid]
            if cb_at and (at & cb_at):
                # Rule A: Attached books (exact phrase match within full Waqfeya names)
                tk_list = phone_full_tks[cid]
                kw = k.split()
                # Ensure the missing title is not just a single common word, or check if it matches as a whole phrase
                if len(kw) >= 2 or len(k) >= 5:
                    if any(f" {k} " in f" {t} " for t in tk_list):
                        valid.add(cid)
        if valid:
            hit, how = valid, 'in-collection'
            
    if not hit and int(r['book_id']) in contained:          # printed inside a phone book (collection, «ويليه», commentary kept with its text)
        hit, how = contained[int(r['book_id'])], 'contained'
    rows.append([r['book_id'], r['title'], r['author'], r['death'], r['category'], r['has_pdf'], how, ' '.join(map(str, sorted(hit)))])
with open(J('data/compare/shamela-matches.tsv'), 'w') as f:
    w = csv.writer(f, delimiter='\t'); w.writerow(['shamela_id', 'title', 'author', 'death', 'category', 'shamela_pdf', 'match', 'phone_book_ids']); w.writerows(rows)
found = sum(1 for r in rows if r[7])
print(f'shamela books: {len(rows)}  on phone: {found} ({found*100/len(rows):.1f}%)')

