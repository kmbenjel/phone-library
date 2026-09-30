"""Fetch each Waqfeya book page's detail record (links, century, tags, series, size). -> data/waqfeya/details.jsonl (resumable)"""
import json, os, re, sys, time, urllib.request, urllib.parse
from concurrent.futures import ThreadPoolExecutor
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'data/waqfeya/details.jsonl')
def rsc_text(h):
    return ''.join(json.loads('"' + m.group(1) + '"') for m in re.finditer(r'self\.__next_f\.push\(\[1,"((?:[^"\\]|\\.)*)"\]\)', h, flags=re.S))
books = [json.loads(l) for l in open(os.path.join(ROOT, 'data/waqfeya/books.jsonl'))]
done = set()
if os.path.exists(OUT):
    for l in open(OUT):
        try: done.add(json.loads(l)['_id'])
        except Exception: pass
todo = [b for b in books if b['_id'] not in done]
print('todo', len(todo), flush=True)
def one(b):
    url = 'https://waqfeya.net/books/' + urllib.parse.quote(b['permalink'])
    for a in range(4):
        try:
            h = urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (personal library catalog)'}), timeout=60).read().decode()
            t = rsc_text(h); k = t.find('{"_id":"' + b['_id'] + '","name"')
            while k >= 0:
                o, _ = json.JSONDecoder().raw_decode(t, k)
                if 'links' in o or 'century' in o: time.sleep(0.4); return o
                k = t.find('{"_id":"' + b['_id'] + '","name"', k + 1)
            time.sleep(0.4); return {'_id': b['_id'], 'nodetail': True}
        except Exception:
            time.sleep(5 * (a + 1))
    return {'_id': b['_id'], 'error': True}
with ThreadPoolExecutor(3) as ex, open(OUT, 'a') as w:
    for n, r in enumerate(ex.map(one, todo), 1):
        w.write(json.dumps(r, ensure_ascii=False) + '\n')
        if n % 500 == 0: print(n, flush=True); w.flush()
print('done')
