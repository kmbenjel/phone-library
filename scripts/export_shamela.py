"""Export the locally installed Shamela catalog (master.db) to data/shamela/books.tsv (read-only)."""
import sqlite3, csv, os, json
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.expanduser('~/.local/share/shamela/database/master.db')
c = sqlite3.connect(f'file:{DB}?mode=ro', uri=True)
cats = dict(c.execute('select category_id, category_name from category'))
auth = {a: (n, d) for a, n, d in c.execute('select author_id, author_name, death_number from author')}
w = csv.writer(open(os.path.join(ROOT, 'data/shamela/books.tsv'), 'w'), delimiter='\t')
w.writerow(['book_id', 'title', 'category', 'author', 'death', 'printed', 'has_pdf', 'pdf_size', 'author_id'])
n = 0
for bid, name, cat, main, printed, pdf in c.execute('select book_id, book_name, book_category, main_author, printed, pdf_links from book order by book_id'):
    a, d = auth.get(main, ('', ''))
    size = ''
    if pdf:
        try: size = json.loads(pdf).get('size', '')
        except Exception: pass
    w.writerow([bid, name, cats.get(cat, cat), a, d if d and d < 99999 else '', printed, 1 if pdf else 0, size, main or '']); n += 1
print('shamela books:', n)
