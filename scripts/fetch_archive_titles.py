"""Bulk-fetch archive.org titles/creators for identifiers (advancedsearch, 100 ids per query).
Usage: python3 scripts/fetch_archive_titles.py ids.txt -> data/archive/titles.jsonl"""
import json, sys, os, urllib.request, urllib.parse, time
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'data/archive/titles.jsonl')
ids = [l.strip() for l in open(sys.argv[1]) if l.strip()]
have = set()
if os.path.exists(OUT): have = {json.loads(l)['identifier'] for l in open(OUT)}
ids = [i for i in ids if i not in have]
with open(OUT, 'a') as w:
    for k in range(0, len(ids), 40):
        chunk = ids[k:k + 40]
        q = 'identifier:(' + ' OR '.join(f'"{i}"' for i in chunk) + ')'
        url = 'https://archive.org/advancedsearch.php?' + urllib.parse.urlencode(
            [('q', q), ('rows', '200'), ('output', 'json')] + [('fl[]', f) for f in ('identifier', 'title', 'creator', 'uploader', 'date', 'collection')])
        d = json.load(urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'personal-library-catalog/1.0'}), timeout=120))
        if 'response' not in d: print('ERR', str(d)[:300]); continue
        for doc in d['response']['docs']: w.write(json.dumps(doc, ensure_ascii=False) + '\n')
        time.sleep(1)
print('titles:', sum(1 for _ in open(OUT)))
