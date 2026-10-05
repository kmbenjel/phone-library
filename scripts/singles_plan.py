"""Single-volume books: a folder holding one PDF becomes a plain file in its section (AGENTS.md §4 «Single file»):
`<short title> - <author> (<edition>).pdf`. Title/author/edition come from the folder name (already evidence-checked)
or, when the folder name is deficient, from the Waqfeya record the file matches byte-for-byte.
Kept as a folder: one volume of a multi-volume work (the record lists more volumes, or the file is «NN - …» /
«(جزء N)» / «المجلد» with N > 1), collections/series, sub-sections (الأدب/أدب عالمي/…), and anything that would
collide with an existing name.
Usage: python3 scripts/singles_plan.py index.tsv plans/NNN-singles.tsv"""
import collections, csv, json, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from textnorm import norm, title_key
from rename_plan import clean, fit, deficient, canonical_folder, split_wname, author_short, redundant
from names_plan import short, BAD_FOLDER
J = lambda p: os.path.join(ROOT, p)

def parse_folder(name):
    """«title - author (edition)» → (title, author, edition)."""
    m = re.match(r'^(.*?)\s*\(([^()]*)\)\s*$', name)
    ed = m.group(2).strip() if m else ''
    base = m.group(1) if m else name
    parts = [x.strip() for x in base.split(' - ')]
    title, author = parts[0], (parts[-1] if len(parts) > 1 else '')
    if re.match(r'^(ت|ط)\b', author): ed, author = ed or author, ''
    return title, author, ed

def main(index, out):
    idx = [p for p, s in csv.reader(open(index, encoding='utf-8'), delimiter='\t')]
    prov = {r['path']: r for r in csv.DictReader(open(J('data/phone/provenance.tsv'), encoding='utf-8'), delimiter='\t')}
    books = {}
    for fn in ('data/waqfeya/details.jsonl', 'data/waqfeya/details2.jsonl'):
        if os.path.exists(J(fn)):
            for l in open(J(fn), encoding='utf-8'):
                d = json.loads(l); books[d['_id']] = d
    folders = collections.defaultdict(list)
    plain = collections.defaultdict(set)
    for p in idx:
        parts = p.split('/')
        if len(parts) == 3: folders['/'.join(parts[:2])].append(p)
        elif len(parts) == 2: plain[parts[0]].add(parts[1])
    rows, stats = [], collections.Counter()
    for folder, ps in sorted(folders.items()):
        if len(ps) != 1: continue
        cat, name = folder.split('/', 1)
        fn = ps[0].rsplit('/', 1)[1]
        if not fn.lower().endswith('.pdf') or cat == 'فهارس الويب': continue
        if re.match(r'^(مؤلفات|سلسلة|مجلة|موسوعة|مجموع|أدب)', name): stats['keep: collection'] += 1; continue
        r = prov.get(ps[0]) or {}
        b = books.get(r.get('waqfeya_id')) if r.get('waqfeya_id') else None
        nvol = re.sub(r'\D', '', str((b or {}).get('numberOfVolumes') or ''))
        vm = re.match(r'^(\d{1,3}) - ', fn) or re.search(r'\((?:جزء|الجزء|المجلد|مجلد)\s*(\d+)\)', fn)
        if (nvol and int(nvol) > 1) or (vm and int(vm.group(1)) > 1) or re.search(r'الجزء (الثاني|الثالث|الرابع)', fn):
            stats['keep: part of a multi-volume work'] += 1; continue
        if b and (BAD_FOLDER.search(name) or deficient(name) or ' - ' not in name):
            canon, title, a = canonical_folder(b)
            t, au, ed = parse_folder(canon)
        else:
            t, au, ed = parse_folder(name)
        t, au, ed = clean(t), clean(au), clean(ed)
        if not t: stats['skip: no title'] += 1; continue
        st = short(t, au)
        cand = st + (f' - {au}' if au and ' - ' not in st and not redundant(au, st) else '') + (f' ({ed})' if ed else '')
        if len(cand.encode()) > 196:
            cand = st + (f' - {au}' if au and ' - ' not in st and not redundant(au, st) else '')
        new = fit(cand, 196) + '.pdf'
        if new in plain[cat]: stats['skip: name taken'] += 1; continue
        plain[cat].add(new)
        rows.append((f'Books/{ps[0]}', f'Books/{cat}/{new}', 'single-volume book: plain file in its section (§4)'))
        stats['to plain file'] += 1
    with open(out, 'w', encoding='utf-8') as w:
        for r in rows: w.write('\t'.join(r) + '\n')
    print(dict(stats))

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
