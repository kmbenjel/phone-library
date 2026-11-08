"""Fetch the full Waqfeya catalog (books list API) into data/waqfeya/books.jsonl.
Usage: python3 scripts/fetch_waqfeya.py   (polite: 1 request/second, resumable)"""
import json, time, urllib.request, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'data/waqfeya/pages')
os.makedirs(OUT, exist_ok=True)
API = 'https://waqfeya.net/books/books-api?page={}&pageSize=100&sortBy=latest'
def get(url):
    for attempt in range(5):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (personal library catalog)'})
            return json.load(urllib.request.urlopen(req, timeout=60))
        except Exception as e:
            print('retry', url, e, file=sys.stderr); time.sleep(5 * (attempt + 1))
    raise SystemExit('failed ' + url)
page, total_pages = 1, None
while total_pages is None or page <= total_pages:
    f = os.path.join(OUT, f'{page:04d}.json')
    if not os.path.exists(f):
        d = get(API.format(page)); json.dump(d, open(f, 'w'), ensure_ascii=False); time.sleep(1)
    else:
        d = json.load(open(f))
    total_pages = d['pagination']['totalPages']; page += 1
seen = {}
for fn in sorted(os.listdir(OUT)):
    for b in json.load(open(os.path.join(OUT, fn)))['data']: seen[b['_id']] = b
with open(os.path.join(ROOT, 'data/waqfeya/books.jsonl'), 'w') as w:
    for b in seen.values(): w.write(json.dumps(b, ensure_ascii=False) + '\n')
print('books:', len(seen))
