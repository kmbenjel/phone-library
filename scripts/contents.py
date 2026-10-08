"""Works contained in one phone book (owner, 2026-10-07): a volume or folder that holds several books stays as it is — it is
never split — but what it contains is known, counted as present in the Shamela comparison and shown in the index.
Covers collections (series such as «لقاء العشر الأواخر», مجموع / مؤلفات / رسائل / آثار / الأعمال), books printed with another
(«ويليه», «ومعه», «وبهامشه» …) and a book kept with a related one (a poem and its commentary in one folder).
Sources, each item tagged with where it was read:
  name     the book's title split at its joiners (ويليه / ويليها / ومعه / ومعها / وبهامشه / وبهامشها / وبذيله / وفي آخره / وعليه)
  files    in a collection, or a folder whose files carry their own titles (not volume numbers): each file's own title;
           «=» separates several works printed in one file; a trailing «- name» is the author
  waqfeya  the Waqfeya records linked to the book: per-file link titles of a collection record, and the «- …» lines that
           list the contents in a record's description
Each item is matched to the local Shamela catalog (same normalised title, or a ≥ 3-word prefix; a known author must agree;
a title of ≤ 2 words needs the author). The book's own title is not an item (compare_shamela.py matches it already).
→ data/editions/contents.json {book key: [{"t": title, "a": author, "s": source, "sh": [shamela ids]}]}
Usage: python3 scripts/contents.py"""
import collections, csv, json, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from textnorm import title_key, author_tokens
J = lambda p: os.path.join(ROOT, p)
JOIN = re.compile(r'[،,]?\s+(?:ويليه|ويليها|ويليهما|ومعه|ومعها|ومعهما|وبهامشه|وبهامشها|وبذيله|وبذيلها|ويذيله|ويذيلها|وفي آخره|وفي آخرها|وعليه|وعليها|ويتلوه|وتليه|وتليها)\s+')
COLL = re.compile(r'^(?:سلسلة|مؤلفات|مجموع|مجموعة|رسائل|الرسائل|آثار|الأعمال|موسوعة|جوامع|جامع الرسائل|ثلاث رسائل|أربع رسائل|رسالتان)')
SKIP = re.compile(r'الواجهة|المقدمة|مقدمة|الفهارس|فهارس|الغلاف|تحميل|^ج\s*\d|^الجزء|^المجلد|^مجلد|^القسم|^نسخة|صور المخطوط|^\d+$')

def split_author(s):
    """«title - author» → (title, author) when the tail looks like a name (≤ 5 words)"""
    s = re.sub(r'\s*\([^()]*\)\s*$', '', s).strip()
    if ' - ' in s:
        t, a = s.rsplit(' - ', 1)
        if 0 < len(a.split()) <= 5 and len(t.split()) >= 1: return t.strip(), a.strip()
    return s, ''

def file_items(fname):
    base = re.sub(r'\.pdf$', '', fname, flags=re.I)
    base = re.sub(r'^\d+\s*-\s*', '', base)                     # issue / item number
    out = []
    for part in re.split(r'\s+=\s+', base):
        t, a = split_author(part)
        if t and not SKIP.search(t): out.append((t, a))
    return out

def shamela_index():
    by_key, by_first = collections.defaultdict(list), collections.defaultdict(list)
    for r in csv.DictReader(open(J('data/shamela/books.tsv'), encoding='utf-8'), delimiter='\t'):
        k = title_key(r['title'])
        if not k: continue
        by_key[k].append((int(r['book_id']), author_tokens(r['author'])))
        by_first[k.split()[0]].append(k)
    return by_key, by_first

def match(t, a, by_key, by_first):
    k = title_key(t); at = author_tokens(a)
    if not k: return []
    cands = list(by_key.get(k, []))
    if not cands and len(k.split()) >= 3:
        for pk in by_first.get(k.split()[0], []):
            if len(pk.split()) >= 3 and (pk.startswith(k + ' ') or k.startswith(pk + ' ')): cands += by_key[pk]
    if len(k.split()) <= 2: cands = [c for c in cands if at and c[1] & at]         # short titles: only with the author
    elif at: cands = [c for c in cands if not c[1] or c[1] & at]
    return sorted({c[0] for c in cands})

def main():
    cat = json.load(open(J('data/catalog.json'), encoding='utf-8'))
    waq = {}
    for l in open(J('data/waqfeya/details.jsonl'), encoding='utf-8'):
        d = json.loads(l); waq[d.get('_id') or d.get('id')] = d
    by_key, by_first = shamela_index()
    out, stats = {}, collections.Counter()
    for b in cat['books']:
        key = f"{b['cat']}/{b['folder']}"
        own = title_key(b['title'])
        items = []
        parts = JOIN.split(b['title'])
        if len(parts) > 1:
            for p in parts[1:]: items.append((*split_author(p), 'name'))
        coll = bool(COLL.match(b['folder'])) or b['cat'] == 'الجوامع'
        names = [f for f, s in b['files']]
        if coll or (len(names) > 1 and len({title_key(file_items(f)[0][0]) for f in names if file_items(f)}) > max(2, len(names) // 2)):
            for f in names:
                for t, a in file_items(f): items.append((t, a or '', 'files'))
        for w in b.get('waqfeya') or []:
            d = waq.get(w['id']) or {}
            nm = d.get('name') or w.get('name') or ''
            for p in JOIN.split(nm)[1:]: items.append((*split_author(p), 'waqfeya'))
            if coll or COLL.match(nm) or 'لقاء العشر' in nm:
                for x in d.get('links') or []:
                    tt = (x.get('title') or '').strip()
                    tt = re.sub(r'^\d+\s*-\s*', '', tt)
                    t, a = split_author(tt)
                    if t and not SKIP.search(t): items.append((t, a, 'waqfeya'))
            lines = [re.sub(r'<[^>]+>', '', x).strip() for x in re.split(r'<br\s*/?>|\n', d.get('description') or '')]
            listed = [x[1:].strip() for x in lines if x.startswith('-') and 3 <= len(x) < 160]
            if len(listed) >= 2:
                for x in listed: items.append((*split_author(x), 'waqfeya'))
        seen, rows = set(), []
        for t, a, s in items:
            k = title_key(t)
            if not k or k == own or k in seen or len(k) < 4: continue
            seen.add(k)
            rows.append({'t': t, 'a': a, 's': s, 'sh': match(t, a, by_key, by_first)})
        keys = [title_key(r['t']) for r in rows]                 # «X» and «X للبيضاوي»: keep the fuller one
        rows = [r for r, k in zip(rows, keys) if not any(o != k and o.startswith(k + ' ') for o in keys)]
        if rows:
            out[key] = rows; stats['books'] += 1; stats['items'] += len(rows); stats['in shamela'] += sum(1 for r in rows if r['sh'])
    os.makedirs(J('data/editions'), exist_ok=True)
    json.dump(out, open(J('data/editions/contents.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    print(dict(stats))

if __name__ == '__main__':
    main()
