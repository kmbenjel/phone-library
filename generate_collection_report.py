import csv, json
from collections import defaultdict

cat = json.load(open('data/catalog.json'))
phone_books = {str(b['id']): b for b in cat['books']}

shamela_in_collection = defaultdict(list)
for r in csv.DictReader(open('data/compare/shamela-matches.tsv'), delimiter='\t'):
    if r['match'] == 'in-collection':
        pids = r['phone_book_ids'].split()
        if not pids: continue
        pid = pids[0]
        if pid in phone_books:
            shamela_in_collection[pid].append((r['title'], r['author']))

with open('/home/k/.gemini/antigravity/brain/1b35a0c8-c742-48f8-ac5a-f72a17ccbd20/collections_report.md', 'w') as f:
    f.write("# بيان الكتب الملحقة والمطوية ضمن الجوامع (الشاملة)\n\n")
    f.write("هذا التقرير يوضح بالتفصيل الكتب (والرسائل) التي كانت تُعتبر مفقودة في الشاملة، وكيف استطاع النظام التعرف على أماكن وجودها داخل الجوامع أو كملحقات للكتب الموجودة على هاتفك.\n\n")
    
    # Sort phone books by category, then title
    sorted_pids = sorted(shamela_in_collection.keys(), key=lambda x: (phone_books[x]['cat'], phone_books[x]['title']))
    
    for pid in sorted_pids:
        pb = phone_books[pid]
        f.write(f"### 📂 {pb['cat']} / {pb['title']}\n")
        f.write(f"**المؤلف:** {pb.get('author', 'غير محدد')}\n\n")
        f.write("**الكتب والرسائل المطوية داخله:**\n")
        for title, author in shamela_in_collection[pid]:
            f.write(f"- {title}\n")
        f.write("\n---\n\n")
print("Done")
