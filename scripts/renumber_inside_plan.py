"""Rename whole folders from the files themselves, for folders whose current names contradict their PDFs
(listed in data/phone/renumber-from-inside.txt): e.g. a set numbered in reverse (01 = ج 15), two numberings mixed,
or a folder named after another book (the «ابن بطال» folder that holds ابن عثيمين).
Each file's PDF title «<title> - ج N[ - القسم …][: label]» gives its place; front matter (مقدمة/تقديم/الواجهة) → 00;
indexes (الفهارس) → after the last volume. Volumes split in sections are numbered in reading order, the printed
part kept in the label (numbers never repeat). Folder name = «<title> - <author>» from the PDFs (most common), with
the folder's existing edition «(…)» kept unless the folder name was about another book.
A folder is renamed only when every file has a usable PDF title; otherwise it is listed for review.
Usage: python3 scripts/renumber_inside_plan.py index.tsv plans/NNN-renumber-inside.tsv review.tsv"""
import collections, csv, json, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from textnorm import norm, title_key, author_tokens
from rename_plan import clean, fit
from names_plan import short
J = lambda p: os.path.join(ROOT, p)
ORD = {norm(w): i for i, w in enumerate('الأول الثاني الثالث الرابع الخامس السادس السابع الثامن التاسع العاشر'.split(), 1)}

def place(t):
    """PDF title → (base title, sort key, kind, label)."""
    t = re.sub(r'\s+', ' ', t).strip()
    m = re.match(r'^(.*?)\s*-\s*ج\s*(\d+)(.*)$', t)
    if m:
        base, n, rest = m.group(1), int(m.group(2)), m.group(3)
        sec = re.search(r'القسم\s+(\S+)', rest)
        s = ORD.get(norm(sec.group(1)), 0) if sec else 0
        lab = re.sub(r'^\s*[-:،]\s*', '', rest).strip()
        if re.search(r'مقدم|تقديم', rest) and not re.search(r'\d', lab.replace(str(n), '')): return base, (n, s, -1), 'pref', lab or 'المقدمة'
        return base, (n, s, 0), 'vol', lab
    base, _, rest = t.partition(' - ')
    if re.search(r'الفهارس|فهارس', t): return base, (10 ** 4, 0, 0), 'index', clean(rest or 'الفهارس')
    if not rest: return base, (0, 0, 0), 'front?', ''              # bare title: a front-matter file (decided by pages)
    if re.search(r'مقدم|تقديم|الواجهة|المدخل', rest or t): return base, (0, 0, 0), 'front', clean(rest or 'المقدمة')
    return base, None, None, ''

def main(index, out, review_out):
    want = [l.strip() for l in open(J('data/phone/renumber-from-inside.txt'), encoding='utf-8') if l.strip()]
    idx = [p for p, s in csv.reader(open(index, encoding='utf-8'), delimiter='\t')]
    meta = {}
    global PAGES
    PAGES = {}
    for l in open(J('data/inspect/files.jsonl'), encoding='utf-8'):
        d = json.loads(l)
        if d.get('pages'): meta[d['path']] = d.get('meta') or {}; PAGES[d['path']] = d['pages']
    files = collections.defaultdict(list)
    for p in idx:
        if p.count('/') == 2: files[p.rsplit('/', 1)[0]].append(p)
    rows, review = [], []
    for folder in want:
        ps = files.get(folder)
        if not ps: review.append((folder, 'folder not found (renamed or emptied)')); continue
        missing = [p for p in ps if not meta.get(p, {}).get('title')]
        if missing:
            review.append((folder, f'{len(missing)} of {len(ps)} files have no PDF title (not inspected yet or none): ' + ', '.join(m.rsplit('/', 1)[1] for m in missing[:4]))); continue
        info = {p: place(meta[p]['title']) for p in ps}
        for p, v in list(info.items()):                                   # a bare title is front matter only if short
            if v[2] == 'front?':
                info[p] = (v[0], (0, 0, 0), 'front', 'الواجهة') if (PAGES.get(p) or 999) <= 60 else (v[0], None, None, '')
        bases = collections.Counter(title_key(v[0]) for v in info.values() if v[1])
        if not bases: review.append((folder, 'no «ج N» titles')); continue
        base_key = bases.most_common(1)[0][0]
        base = next(v[0] for v in info.values() if title_key(v[0]) == base_key)
        auths = collections.Counter(clean(re.split(r'[؛،,]', meta[p].get('author', ''))[0]) for p in ps if meta[p].get('author'))
        author = auths.most_common(1)[0][0] if auths else ''
        if len(author.split()) > 4: author = ' '.join(author.split()[:4])
        cat, name = folder.split('/', 1)
        if title_key(name)[:10] != title_key(base)[:10] and any(title_key(name)[:10] in title_key(v[3]) for v in info.values()):
            review.append((folder, f'the files are volumes of the series «{base}»; the folder is the book in it — left as is')); continue
        ed = re.search(r'\(([^()]*)\)\s*$', name)
        same_book = title_key(name)[:10] == title_key(base)[:10] and (not author or not author_tokens(name) or author_tokens(name) & author_tokens(author))
        new_folder_name = clean(base) + (f' - {author}' if author and norm(author) not in norm(base) else '') + (f' ({ed.group(1)})' if ed and same_book else '')
        new_folder = f'{cat}/{fit(new_folder_name, 196)}'
        order = sorted((v[1], p) for p, v in info.items() if v[1] is not None)
        unplaced = [p for p, v in info.items() if v[1] is None]
        if unplaced:
            review.append((folder, 'files without a place in the set: ' + ', '.join(u.rsplit('/', 1)[1] for u in unplaced[:4]))); continue
        st = short(clean(base), author)
        seq, names, n_vol = 0, {}, 0
        keys = sorted({k[:2] for k, _ in order if k[0] not in (0, 10 ** 4)})
        sequential = any(k[1] for k in keys) or len({k[0] for k in keys}) != len(keys)
        width = max(2, len(str(len(keys) + 1)))
        num_of = {k: (i + 1 if sequential else k[0]) for i, k in enumerate(keys)}
        last = max(num_of.values(), default=0)
        for k, p in order:
            kind, lab = info[p][2], clean(info[p][3])
            if kind in ('front',) or k[0] == 0: n = 0
            elif kind == 'index': n = last + 1
            else: n = num_of[k[:2]]
            lab = re.sub(r'^\s*\*\s*', '', lab).replace(' * ', ' ').strip(' -')
            if kind == 'pref': lab = lab if 'مقدم' in lab else f'مقدمة - {lab}' if lab else 'المقدمة'
            if sequential and kind == 'vol': lab = f'ج {k[0]}' + (f' ق {k[1]}' if k[1] else '') + (f' - {lab}' if lab else '')
            nm = f'{n:0{width}d} - {st}' + (f' ({fit(lab, 90)})' if lab else '') + '.pdf'
            names[p] = nm
        if len(set(names.values())) != len(names):
            review.append((folder, 'name clash after renumbering')); continue
        for p, nm in names.items():
            dst = f'{new_folder}/{nm}'
            if dst != p: rows.append((f'Books/{p}', f'Books/{dst}', 'renamed from the PDF titles inside the files (folder numbering/name contradicted them)'))
    with open(out, 'w', encoding='utf-8') as w:
        for r in rows: w.write('\t'.join(r) + '\n')
    with open(review_out, 'w', encoding='utf-8') as w:
        for r in review: w.write('\t'.join(r) + '\n')
    print('moves', len(rows), 'review', len(review))

if __name__ == '__main__':
    main(*sys.argv[1:4])
