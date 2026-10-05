"""One-off: archive.org candidates for pre-700 Shamela books missing on the phone (data/compare/shamela-pre700-books-missing.tsv).
Same scoring as scripts/find_on_archive.py (title words, author, no whole-library bundles, PDFs present).
Writes data/expansion-candidates-shamela-pre700.json. Usage: python3 scratch/find_on_archive_titles.py [N=2]"""
import csv, json, os, re, sys, time, urllib.parse, urllib.request
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from textnorm import norm, title_key, author_tokens
BUNDLE = re.compile(r'htm|bok|word|وورد|zip|مضغوط|صيغة|islamic\s*\d|كتب إسلامية|shamela|الشاملة|موسوعة', re.I)
def get(url):
    for i in range(3):
        try: return json.load(urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'personal-library/1.0'}), timeout=60))
        except Exception: time.sleep(5)
    return {}
N = int(sys.argv[1]) if len(sys.argv) > 1 else 2
rows = list(csv.DictReader(open(os.path.join(ROOT, 'data/compare/shamela-pre700-books-missing.tsv'), encoding='utf-8'), delimiter='\t'))
out = {}
for n, r in enumerate(rows):
    title = re.sub(r'\s*[-_]\s*(ت|ط)\s.*$', '', r['title']); title = re.sub(r'_\d+$', '', title)
    tw = title_key(title).split()[:5]
    raw = [w for w in re.sub(r'[^؀-ۿ\s]', ' ', title).split() if w not in ('كتاب',)][:4]
    aw = author_tokens(r['author'])
    res = get('https://archive.org/advancedsearch.php?' + urllib.parse.urlencode({'q': f'title:({" ".join(raw)}) AND mediatype:texts', 'fl[]': ['identifier', 'title', 'item_size'], 'rows': 25, 'output': 'json'}, doseq=True))
    cands = []
    for x in (res.get('response') or {}).get('docs', []):
        t = str(x.get('title', ''))
        if BUNDLE.search(t) or BUNDLE.search(x['identifier']) or (x.get('item_size') or 0) > 2e9: continue
        nt = set(norm(t).split())
        s = sum(1 for w in tw if w in nt) / max(1, len(tw)) * 10 + (3 if aw & nt else 0)
        if s >= 8: cands.append((s, x['identifier'], t))
    cands.sort(reverse=True); best = []
    for s, ident, t in cands[:5]:
        m = get(f'https://archive.org/metadata/{ident}')
        if m.get('is_dark') or not m.get('files'): continue
        pdfs = [(f['name'], int(f.get('size') or 0)) for f in m['files'] if f['name'].lower().endswith('.pdf') and not f['name'].lower().endswith('_text.pdf')]
        if pdfs and len(pdfs) <= 40: best.append({'id': ident, 'title': t, 'score': round(s, 1), 'pdfs': pdfs, 'mb': round(sum(z for _, z in pdfs) / 1e6, 1)})
        if len(best) >= N: break
    out[r['title']] = {'author': r['author'], 'death': r['death'], 'category': r['category'], 'candidates': best}
    print(f'{n + 1}/{len(rows)} {r["title"][:50]} → {len(best)}', flush=True)
    if n % 25 == 0: json.dump(out, open(os.path.join(ROOT, 'data/expansion-candidates-shamela-pre700.json'), 'w'), ensure_ascii=False, indent=1)
json.dump(out, open(os.path.join(ROOT, 'data/expansion-candidates-shamela-pre700.json'), 'w'), ensure_ascii=False, indent=1)
