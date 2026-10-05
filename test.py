import csv
for r in csv.DictReader(open('data/compare/shamela-matches.tsv'), delimiter='\t'):
    if r['match'] == 'in-collection':
        print(r['title'], '-->', r['phone_book_ids'])
