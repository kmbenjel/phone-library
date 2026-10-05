import csv

# Read existing plan
plan = list(csv.DictReader(open('plans/download_batch.tsv'), delimiter='\t'))

# Read Shamela matches
shamela_rows = list(csv.DictReader(open('data/compare/shamela-matches.tsv'), delimiter='\t'))
shamela_missing_pdf = [r for r in shamela_rows if r['match'] == '' and r['shamela_pdf'] == '1']

added = 0
for r in shamela_missing_pdf:
    try:
        death = int(r['death'] or 9999)
    except:
        continue
    
    if death <= 700:
        # Check if we already have it in the Waqfeya plan?
        # Actually, if we do, the downloader can handle duplicates, but let's just append it.
        # It's better to provide the Shamela link.
        plan.append({
            'waqfeya_id': f"shamela_{r['shamela_id']}",
            'title': r['title'],
            'author': r['author'],
            'category': r['category'],
            'century': f"القرن {str(death)[:2] if death >= 1000 else str(death)[0]} هـ",
            'visits': '',
            'size_mb': '',
            'url': f"https://shamela.ws/book/{r['shamela_id']}"
        })
        added += 1

with open('plans/download_batch.tsv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['waqfeya_id', 'title', 'author', 'category', 'century', 'visits', 'size_mb', 'url'], delimiter='\t')
    w.writeheader()
    w.writerows(plan)

print(f"Added {added} Shamela books to the plan. Total is now {len(plan)}.")
