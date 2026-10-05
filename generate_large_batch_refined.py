import csv

rows = list(csv.DictReader(open('data/compare/waqfeya-matches.tsv'), delimiter='\t'))
plan = []

# Expanded Giants (Added crucial 8th-14th century scholars, especially Azharite/Mazaheb pillars)
giants = [
    'ابن تيمية', 'ابن قيم', 'ابن حجر', 'السيوطي', 'الذهبي', 'الشوكاني', 'السخاوي', 'السبكي', 
    'ابن كثير', 'ابن رجب', 'الزركشي', 'الصنعاني',
    'التفتازاني', 'العراقي', 'العيني', 'المحلي', 'الأنصاري', 'الشربيني', 'الهيتمي', 'الرملي',
    'علي القاري', 'البهوتي', 'الزرقاني', 'ابن عابدين', 'الآلوسي', 'البجيرمي', 'الدسوقي', 'الباجوري', 'الدردير'
]

# Core Azharite Sciences Categories (Keywords in category)
azhar_sciences = ['أصول الفقه', 'العقيدة', 'النحو', 'الصرف', 'المنطق', 'البلاغة', 'اللغة']

for r in rows:
    if r['status'] != 'missing': continue
    c = r['century']
    if 'القرن' not in c: continue
    
    try:
        num = int(c.replace('القرن ', '').replace(' هـ', ''))
    except:
        continue
        
    if num >= 8 and num <= 14:
        # Base Popularity
        visits = int(r['visits'] or 0)
        is_popular = visits >= 20000
        
        # 1. Hawashi & Academic Notes
        name = r['name']
        is_hawashi = any(k in name for k in ['حاشي', 'حواش', 'تقريرات', 'تعليقات'])
        
        # 2. Giants of the Era
        author = r['author'] or ''
        is_giant = any(g in author for g in giants)
        
        # 3. Core Azharite Sciences (Lower threshold to 10k to ensure we capture Usul, Nahw, Mantiq)
        cat = r['waqfeya_category'] or 'كتب عامة'
        is_azhar_science = any(s in cat for s in azhar_sciences) and visits >= 10000
        
        if is_popular or is_hawashi or is_giant or is_azhar_science:
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

# Deduplicate just in case
seen = set()
unique_plan = []
for p in plan:
    if p['waqfeya_id'] not in seen:
        seen.add(p['waqfeya_id'])
        unique_plan.append(p)

unique_plan.sort(key=lambda x: (x['century'], -int(x['visits'] or 0)))

with open('plans/download_batch_large_v2.tsv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['waqfeya_id', 'title', 'author', 'category', 'century', 'visits', 'size_mb', 'url'], delimiter='\t')
    w.writeheader()
    w.writerows(unique_plan)

print(f"Refined large download plan with {len(unique_plan)} books.")
