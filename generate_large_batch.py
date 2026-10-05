import csv

rows = list(csv.DictReader(open('data/compare/waqfeya-matches.tsv'), delimiter='\t'))
plan = []

giants = ['ابن تيمية', 'ابن قيم', 'ابن حجر', 'السيوطي', 'الذهبي', 'الشوكاني', 'السخاوي', 'السبكي', 'ابن كثير', 'ابن رجب', 'الزركشي', 'الصنعاني']

for r in rows:
    if r['status'] != 'missing': continue
    c = r['century']
    if 'القرن' not in c: continue
    
    try:
        num = int(c.replace('القرن ', '').replace(' هـ', ''))
    except:
        continue
        
    if num >= 8 and num <= 14:
        # Condition 1: High visits (Top tier Nafaes)
        is_popular = int(r['visits'] or 0) >= 20000
        
        # Condition 2: Hawashi
        is_hawashi = 'حاشي' in r['name'] or 'حواش' in r['name']
        
        # Condition 3: Giant scholars (Nafaes)
        is_giant = any(g in r['author'] for g in giants) if r['author'] else False
        
        if is_popular or is_hawashi or is_giant:
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

# Sort by century, then visits
plan.sort(key=lambda x: (x['century'], -int(x['visits'] or 0)))

with open('plans/download_batch_large.tsv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['waqfeya_id', 'title', 'author', 'category', 'century', 'visits', 'size_mb', 'url'], delimiter='\t')
    w.writeheader()
    w.writerows(plan)

print(f"Generated large download plan with {len(plan)} books.")
