import csv, json, requests
from concurrent.futures import ThreadPoolExecutor

queries = {
    'أجاثا كريستي': ('الأدب المترجم', 'أجاثا كريستي'),
    'شيرلوك هولمز': ('الأدب المترجم', 'آرثر كونان دويل'),
    'أرسين لوبين': ('الأدب المترجم', 'موريس لوبلان'),
    'الزير سالم': ('تراث شعبي', 'قصص وروايات'),
    'عنترة بن شداد': ('تراث شعبي', 'قصص وروايات'),
    'بني هلال': ('تراث شعبي', 'قصص وروايات'),
    'ألف ليلة وليلة': ('تراث شعبي', 'قصص وروايات')
}

session = requests.Session()
new_books = []

def search_archive(query):
    url = f"https://archive.org/advancedsearch.php?q=title:({query})+AND+mediatype:texts&fl[]=identifier,title&rows=30&output=json"
    try:
        r = session.get(url, timeout=10).json()
        return r['response']['docs']
    except:
        return []

def get_pdf(doc, cat, author):
    id = doc['identifier']
    url = f"https://archive.org/metadata/{id}/files"
    try:
        files = session.get(url, timeout=10).json().get('result', [])
        for f in files:
            name = f['name']
            if name.endswith('.pdf') and not name.endswith('_text.pdf'):
                return {
                    'waqfeya_id': id,
                    'title': doc['title'].replace('/', '-'),
                    'author': author,
                    'category': cat,
                    'century': 'القرن 14 هـ',
                    'visits': '99999',
                    'size_mb': '0',
                    'url': f"https://archive.org/download/{id}/{name}"
                }
    except:
        pass
    return None

docs_to_process = []
for q, (cat, author) in queries.items():
    docs = search_archive(q)
    for d in docs:
        docs_to_process.append((d, cat, author))

print(f"Found {len(docs_to_process)} candidate documents. Fetching PDF links...")

with ThreadPoolExecutor(max_workers=10) as ex:
    results = ex.map(lambda x: get_pdf(x[0], x[1], x[2]), docs_to_process)
    
for r in results:
    if r: new_books.append(r)

# Deduplicate based on ID
seen = set()
unique_new = []
for b in new_books:
    if b['waqfeya_id'] not in seen:
        seen.add(b['waqfeya_id'])
        unique_new.append(b)

with open('plans/download_batch_large.tsv', 'a', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['waqfeya_id', 'title', 'author', 'category', 'century', 'visits', 'size_mb', 'url'], delimiter='\t')
    w.writerows(unique_new)

print(f"Successfully added {len(unique_new)} new literature books to the plan.")
