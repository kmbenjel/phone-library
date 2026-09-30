"""Fetch archive.org file lists (name, exact size, format) via <id>_files.xml (fast path; no title).
Usage: python3 scripts/fetch_archive_files.py data/archive/ids-ordered.txt -> data/archive/files.jsonl (resumable)
Titles for non-Waqfeya items come from scripts/fetch_archive_titles.py (advancedsearch, bulk)."""
import json, sys, os, time, urllib.request, urllib.parse, xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, os.environ.get('OUT', 'data/archive/files.jsonl'))
ids = list(dict.fromkeys(l.strip() for f in sys.argv[1:] for l in open(f) if l.strip()))
done = set()
for src in __import__('glob').glob(os.path.join(ROOT, 'data/archive/files*.jsonl')) + [os.path.join(ROOT, 'data/archive/items.jsonl')]:
    if os.path.exists(src):
        for l in open(src):
            try:
                d = json.loads(l)
                if not d.get('error'): done.add(d['id'])
            except Exception: pass
todo = [i for i in ids if i not in done]
if os.environ.get('REVERSE'): todo.reverse()
print('ids', len(ids), 'todo', len(todo), flush=True)
def one(i):
    url = f'https://archive.org/download/{urllib.parse.quote(i)}/{urllib.parse.quote(i)}_files.xml'
    for a in range(4):
        try:
            x = urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'personal-library-catalog/1.0'}), timeout=60).read()
            files = []
            for f in ET.fromstring(x).findall('file'):
                name = f.get('name'); size = f.findtext('size'); fmt = f.findtext('format') or ''
                if f.get('source') == 'original' or name.lower().endswith('.pdf'):
                    files.append({'name': name, 'size': int(size or 0), 'format': fmt})
            return {'id': i, 'files': files}
        except urllib.error.HTTPError as e:
            if e.code in (403, 404): return {'id': i, 'files': [], 'http': e.code}
            time.sleep(3 * (a + 1))
        except Exception:
            time.sleep(3 * (a + 1))
    return {'id': i, 'error': True}
with ThreadPoolExecutor(8) as ex, open(OUT, 'a') as w:
    for n, r in enumerate(ex.map(one, todo), 1):
        w.write(json.dumps(r, ensure_ascii=False) + '\n')
        if n % 100 == 0: print(n, flush=True); w.flush()
print('done')
