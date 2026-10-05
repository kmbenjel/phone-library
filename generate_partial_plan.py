import csv

rows = list(csv.DictReader(open('data/compare/waqfeya-matches.tsv'), delimiter='\t'))
plan = []

for r in rows:
    if r['status'] == 'partial':
        cat = r['waqfeya_category'] or 'كتب عامة'
        title = r['name'].replace('/', '-')
        plan.append({
            'waqfeya_id': r['waqfeya_id'],
            'title': r['name'],
            'author': r['author'],
            'category': cat,
            'century': r['century'],
            'visits': r['visits'],
            'size_mb': r['size_mb'],
            'url': r['url']
        })

with open('plans/download_partial.tsv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['waqfeya_id', 'title', 'author', 'category', 'century', 'visits', 'size_mb', 'url'], delimiter='\t')
    w.writeheader()
    w.writerows(plan)

print(f"Generated partial download plan with {len(plan)} books.")
