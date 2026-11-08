"""Complete folder names that were cut (e.g. «الجوهر المكنون في صدف الثلاثة ال») by a unique prefix match against
Waqfeya titles, Shamela titles and the owner's poems catalog (data/mappings/mandumat_catalog.json). Ambiguous -> review.
Usage: python3 scripts/restore_cut_names.py index.tsv plans/NNN.tsv"""
import csv, json, os, re, sys
from collections import defaultdict, Counter
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from textnorm import norm
from rename_plan import clean, fit, author_short, redundant
J = lambda p: os.path.join(ROOT, p)

def sources():
    out = []                                                          # (title, author)
    for l in open(J('data/waqfeya/books.jsonl')):
        b = json.loads(l); t = re.split(r'\s+-\s+(?:ط|ت)[ .:]', b['name'])[0]
        out.append((t, author_short((b.get('author') or {}).get('name', ''))))
    for r in csv.DictReader(open(J('data/shamela/books.tsv')), delimiter='\t'): out.append((r['title'], r['author']))
    if os.path.exists(J('data/mappings/mandumat_catalog.json')):
        for m in json.load(open(J('data/mappings/mandumat_catalog.json'))): out.append((m.get('book_title', ''), m.get('author', '')))
    return [(clean(t), clean(a)) for t, a in out if t]

def main(index, out):
    src = sources(); by_first = defaultdict(list)
    for t, a in src:
        w = norm(t).split()
        if w: by_first[w[0]].append((w, t, a))
    files = defaultdict(list)
    for p, s in csv.reader(open(index), delimiter='\t'):
        if p.startswith('فهارس الويب/') or p.count('/') != 2: continue
        files[p.rsplit('/', 1)[0]].append(p.rsplit('/', 1)[1])
    existing = set(files); moves, review = [], []
    for folder, names in sorted(files.items()):
        sec, name = folder.split('/', 1)
        if not re.search(r'[\s-]\S{1,3}$|\.\.\.$', name): continue
        m = re.match(r'^(.*?)(\s*\([^()]*\))?$', name); core, tail_ed = m.group(1), (m.group(2) or '')
        parts = core.split(' - ')
        cut_in_author = len(parts) > 1 and re.search(r'\s\S{1,3}$', parts[-1]) and not re.search(r'\s\S{1,3}$', parts[0])
        title_cut = ' - '.join(parts[:-1]) if cut_in_author else core
        w = norm(title_cut.rstrip('. ')).split()
        if len(w) < 2: review.append((folder, 'too short to complete')); continue
        if cut_in_author:
            cands = {(t, a) for ww, t, a in by_first.get(w[0], []) if ww == w and a}
            frag = norm(parts[-1]).split()
            cands = {(t, a) for t, a in cands if norm(a).startswith(' '.join(frag[:-1])) and any(x.startswith(frag[-1]) for x in norm(a).split())}
        else:
            full, part = w[:-1], w[-1]
            cands = {(t, a) for ww, t, a in by_first.get(w[0], []) if len(ww) > len(full) and ww[:len(full)] == full and ww[len(full)].startswith(part)}
        titles = {norm(t) for t, a in cands}
        if len(titles) != 1:
            review.append((folder, f'{len(titles)} possible full titles' if titles else 'no full title found')); continue
        t, a = sorted(cands, key=lambda x: -len(x[1]))[0]
        a = author_short(a)
        new = t + (f' - {a}' if a and not redundant(a, t) else '')
        new = fit(new + tail_ed, 200)
        dest = f'{sec}/{new}'
        if dest in existing: review.append((folder, 'completed name already exists as a folder')); continue
        old_title = core if not cut_in_author else title_cut
        for n in names:
            nn = n.replace(old_title, t) if old_title in n else n
            moves.append((f'Books/{folder}/{n}', f'Books/{dest}/{nn}', 'complete a cut name (unique match in Waqfeya/Shamela/poems catalog)'))
    with open(out, 'w') as f:
        for a, b, r in moves: f.write(f'{a}\t{b}\t{r}\n')
    with open(J('data/phone/names-review.tsv'), 'w') as f:
        for x, why in review: f.write(f'{x}\t{why}\n')
    print('folders completed:', len({a.rsplit('/', 1)[0] for a, b, r in moves}), '| moves:', len(moves), '| review:', len(review), Counter(w.split(' ')[0] for x, w in review))
if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
