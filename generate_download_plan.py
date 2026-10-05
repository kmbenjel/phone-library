import csv

rows = list(csv.DictReader(open('data/compare/waqfeya-matches.tsv'), delimiter='\t'))
plan = []

for r in rows:
    if r['status'] != 'missing': continue
    c = r['century']
    if 'القرن' not in c: continue
    
    try:
        num = int(c.replace('القرن ', '').replace(' هـ', ''))
    except:
        continue
        
    is_pre700 = (num <= 7)
    is_important_post700 = (num > 7 and num <= 14 and int(r['visits'] or 0) > 50000)
    
    if is_pre700 or is_important_post700:
        # Generate the target path
        cat = r['waqfeya_category'] or 'كتب عامة'
        title = r['name'].replace('/', '-')
        # Some waqfeya names have ' - ط. كذا' which we can keep.
        plan.append({
            'title': r['name'],
            'author': r['author'],
            'category': cat,
            'century': r['century'],
            'visits': r['visits'],
            'size_mb': r['size_mb'],
            'url': r['url'],
            'waqfeya_id': r['waqfeya_id']
        })

# Sort by century, then visits
plan.sort(key=lambda x: (x['century'], -int(x['visits'] or 0)))

with open('plans/download_batch.tsv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['waqfeya_id', 'title', 'author', 'category', 'century', 'visits', 'size_mb', 'url'], delimiter='\t')
    w.writeheader()
    w.writerows(plan)

print(f"Generated download plan with {len(plan)} books.")
