"""Find other archive.org copies of books whose Waqfeya items went dark (FPnnnn items withdrawn in 2025).
For each Waqfeya id: search archive.org by title (and author), keep items that hold real PDFs (not «Htm/Bok/Word/zip»
bundles of whole libraries), score them (title words, author, an edition named in the title, number of PDFs close to
the record's volumes) and write the best candidates with their PDF files and exact sizes for review.
Usage: python3 scripts/find_on_archive.py ids.txt out.json [N=3]"""
import json, os, re, sys, time, urllib.parse, urllib.request
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from textnorm import norm, title_key, author_tokens
J = lambda p: os.path.join(ROOT, p)
BUNDLE = re.compile(r'htm|bok|word|وورد|zip|مضغوط|صيغة|islamic\s*\d|كتب إسلامية|shamela', re.I)

def get(url):
    for i in range(3):
        try: return json.load(urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'personal-library/1.0'}), timeout=60))
        except Exception: time.sleep(5)
    return {}

def main():
    ids = [l.strip() for l in open(sys.argv[1], encoding='utf-8') if l.strip()]
    N = int(sys.argv[3]) if len(sys.argv) > 3 else 3
    recs = {}
    for fn in ('data/waqfeya/details.jsonl', 'data/waqfeya/details2.jsonl'):
        for l in open(J(fn), encoding='utf-8'):
            d = json.loads(l)
            if d['_id'] in ids: recs[d['_id']] = d
    out = {}
    for n, i in enumerate(ids):
        d = recs.get(i)
        if not d: continue
        title = re.split(r'\s+-\s+(?:ط|ت)[\s.:]', d['name'])[0]
        tw = title_key(title).split()[:5]
        raw = [w for w in re.sub(r'[^\u0600-\u06FF\s]', ' ', title).split() if w not in ('كتاب',)][:4]   # archive.org search needs the real spelling (hamza)
        au = (d.get('author') or {}).get('name', '') if isinstance(d.get('author'), dict) else ''
        aw = author_tokens(re.split(r'[؛;]', au)[0])
        q = ' '.join(raw)
        res = get('https://archive.org/advancedsearch.php?' + urllib.parse.urlencode({'q': f'title:({q}) AND mediatype:texts', 'fl[]': ['identifier', 'title', 'item_size'], 'rows': 25, 'output': 'json'}, doseq=True))
        cands = []
        for x in (res.get('response') or {}).get('docs', []):
            t = str(x.get('title', ''))
            if BUNDLE.search(t) or BUNDLE.search(x['identifier']) or (x.get('item_size') or 0) > 3e9: continue
            nt = set(norm(t).split())
            s = sum(1 for w in tw if w in nt) / max(1, len(tw)) * 10 + (3 if aw & nt else 0) + (1 if re.search(r'(^|\s)(ت|تحقيق|ط)[\s:]', t) else 0)
            if s < 6: continue
            cands.append((s, x['identifier'], t))
        cands.sort(reverse=True)
        best = []
        for s, ident, t in cands[:6]:
            m = get(f'https://archive.org/metadata/{ident}')
            if m.get('is_dark') or not m.get('files'): continue
            pdfs = [(f['name'], int(f.get('size') or 0)) for f in m['files'] if f['name'].lower().endswith('.pdf') and not f['name'].lower().endswith('_text.pdf')]
            if not pdfs: continue
            best.append({'id': ident, 'title': t, 'score': round(s, 1), 'pdfs': pdfs[:40], 'mb': round(sum(z for _, z in pdfs) / 1e6, 1)})
            if len(best) >= N: break
        out[i] = {'waqfeya': d['name'], 'author': au, 'volumes': d.get('numberOfVolumes'), 'candidates': best}
        print(f'{n + 1}/{len(ids)} {d["name"][:60]} → {len(best)} candidates', flush=True)
    json.dump(out, open(sys.argv[2], 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

if __name__ == '__main__':
    main()
