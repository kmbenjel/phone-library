"""Find Waqfeya replacements for books whose files were deleted (not real PDFs).
A book = a folder that lost files. Match: archive.org id found in the deleted page -> Waqfeya record; else title (+author) match.
Only unambiguous matches with downloadable PDFs are kept. Output: data/phone/replacements.json"""
import csv, json, os, re, sys, glob
from collections import defaultdict
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from textnorm import title_key, author_tokens, norm
from build_catalog import split_folder
from rename_plan import vol_from_orig
J = lambda p: os.path.join(ROOT, p)
books = {}
for fn in ('data/waqfeya/books.jsonl', 'data/waqfeya/details.jsonl', 'data/waqfeya/details2.jsonl'):
    for l in open(J(fn)):
        d = json.loads(l); books[d['_id']] = {**books.get(d['_id'], {}), **d}
items = {}
for fn in ['data/archive/items.jsonl'] + glob.glob(J('data/archive/files*.jsonl')):
    for l in open(fn):
        d = json.loads(l)
        if not d.get('error'): items[d['id']] = d
ids_of = lambda b: sorted(set(re.findall(r'archive\.org/(?:details|download)/([^/"?#\s]+)', json.dumps([b.get('thumbnail'), b.get('links'), b.get('archiveLink')], ensure_ascii=False))))
by_item = defaultdict(set); by_key = defaultdict(set)
for wid, b in books.items():
    for i in ids_of(b): by_item[i].add(wid)
    by_key[title_key(b['name'].split(' - ')[0])].add(wid)
def pdfs(wid):
    out = []
    for i in ids_of(books[wid]):
        it = items.get(i)
        if not it or it.get('http'): continue
        for f in it.get('files', []):
            n = f['name']
            if n.lower().endswith('.pdf') and not n.lower().endswith('_text.pdf') and f.get('format') != 'Text PDF' and f['size'] > 0:
                out.append({'item': i, 'name': n, 'size': f['size']})
    return out
deleted = json.load(open(J('data/phone/non-pdf-files.json')))
now = {p for p, s in csv.reader(open(sys.argv[1]), delimiter='\t')}
folders = defaultdict(list)
for d in deleted: folders[d['path'].rsplit('/', 1)[0]].append(d)
res = []
for folder, ds in sorted(folders.items()):
    remaining = [p for p in now if p.startswith(folder + '/')]
    sec, name = folder.split('/', 1)
    title, author, ed = split_folder(name)
    cand = set()
    for d in ds:
        for i in d['archive_ids']: cand |= by_item.get(i, set())
    how = 'archive id' if cand else ''
    if not cand:
        cand = set(by_key.get(title_key(title), set()))
        at = author_tokens(author)
        if at: cand = {w for w in cand if author_tokens((books[w].get('author') or {}).get('name', '')) & at} or cand
        how = 'title'
    cand = {w for w in cand if pdfs(w)}
    entry = {'folder': folder, 'deleted': len(ds), 'remaining': len(remaining), 'how': how}
    if len(cand) == 1:
        w = cand.pop(); fs = pdfs(w)
        entry.update({'waqfeya_id': w, 'waqfeya_name': books[w]['name'], 'url': 'https://waqfeya.net/books/' + books[w].get('permalink', ''),
                      'files': fs, 'mb': round(sum(f['size'] for f in fs) / 2**20, 1)})
    else:
        entry['waqfeya_id'] = None; entry['candidates'] = len(cand)
    res.append(entry)
json.dump(res, open(J('data/phone/replacements.json'), 'w'), ensure_ascii=False, indent=1)
m = [r for r in res if r.get('waqfeya_id')]
print(f'folders that lost files: {len(res)} (now empty: {sum(1 for r in res if r["remaining"] == 0)})')
print(f'  unique Waqfeya match with PDFs: {len(m)}  ({sum(r["mb"] for r in m):,.0f} MB)  | ambiguous: {sum(1 for r in res if not r.get("waqfeya_id") and r.get("candidates"))} | not in Waqfeya: {sum(1 for r in res if not r.get("waqfeya_id") and not r.get("candidates"))}')
print(f'  of the now-empty folders: matched {sum(1 for r in m if r["remaining"] == 0)}')
