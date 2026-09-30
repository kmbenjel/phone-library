"""Fetch archive.org item metadata (title, creator, file names + exact sizes) for identifiers listed in files.
Usage: python3 scripts/fetch_archive_meta.py data/archive/ids-*.txt   -> data/archive/items.jsonl (resumable)"""
import json, sys, os, time, urllib.request, urllib.parse
from concurrent.futures import ThreadPoolExecutor
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'data/archive/items.jsonl')
ids = list(dict.fromkeys(l.strip() for f in sys.argv[1:] for l in open(f) if l.strip()))
done = set()
if os.path.exists(OUT):
    for l in open(OUT):
        try: done.add(json.loads(l)['id'])
        except Exception: pass
todo = [i for i in ids if i not in done]
print('ids', len(ids), 'todo', len(todo), flush=True)
def one(i):
    url = 'https://archive.org/metadata/' + urllib.parse.quote(i)
    for a in range(4):
        try:
            d = json.load(urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'personal-library-catalog/1.0'}), timeout=60))
            md = d.get('metadata', {})
            files = [{'name': f['name'], 'size': int(f.get('size', 0) or 0), 'format': f.get('format', '')}
                     for f in d.get('files', []) if f.get('source') == 'original' or f['name'].lower().endswith('.pdf')]
            return {'id': i, 'title': md.get('title'), 'creator': md.get('creator'), 'uploader': md.get('uploader'),
                    'collection': md.get('collection'), 'date': md.get('date'), 'files': files, 'missing': not d}
        except Exception as e:
            time.sleep(3 * (a + 1))
    return {'id': i, 'error': True}
with ThreadPoolExecutor(14) as ex, open(OUT, 'a') as w:
    for n, r in enumerate(ex.map(one, todo), 1):
        w.write(json.dumps(r, ensure_ascii=False) + '\n')
        if n % 100 == 0: print(n, flush=True); w.flush()
print('done')
