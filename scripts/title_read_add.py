"""Append title-page readings to data/names/title-read.tsv (used while reading the sheets of scripts/title_sheets.py).
Input on stdin: one reading per line, fields separated by « | »: n | verdict | title | author | editor | publisher | city |
year | kind | section | note   (the book is taken from data/names/sheets/books.tsv by n; empty fields allowed)."""
import csv, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J = lambda *p: os.path.join(ROOT, *p)
books = {l.split('\t')[0]: l.split('\t')[1] for l in open(J('data', 'names', 'sheets', 'books.tsv'), encoding='utf-8')}
VERDICTS = {'ok', 'other-book', 'other-edition', 'part', 'no-title-page', 'unreadable'}
out = open(J('data', 'names', 'title-read.tsv'), 'a', encoding='utf-8')
for line in sys.stdin:
    if not line.strip(): continue
    f = [x.strip() for x in line.rstrip('\n').split(' | ')]
    f += [''] * (11 - len(f))
    n, verdict = f[0], f[1]
    assert n in books, n; assert verdict in VERDICTS, verdict
    out.write('\t'.join([n, books[n], verdict] + f[2:11]) + '\n')
print('ok')
