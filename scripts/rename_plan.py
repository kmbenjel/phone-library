"""Plan folder/file renames from provenance evidence (see AGENTS.md §4 for the conventions).

Usage: python3 scripts/rename_plan.py data/phone/index-<date>.tsv plans/NNN-renames.tsv
Writes the plan (from, to, reason) and data/phone/rename-review.tsv (cases left for a human).
Run AFTER duplicates are quarantined and the index refreshed, so merges don't collide."""
import csv, json, os, re, sys
from collections import defaultdict, Counter
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from textnorm import norm, title_key, author_tokens
def redundant(author, title):
    at = {w.removeprefix('ال') for w in author_tokens(author)}
    tt = {w.removeprefix('ال') for w in norm(title).split()}
    return bool(at) and at <= tt
J = lambda p: os.path.join(ROOT, p)
INDEX_DIR = 'فهارس الويب'
MAXB = 200                                   # max bytes per name component
COLLECTION = re.compile(r'^(مؤلفات|سلسلة|مجلة|موسوعة|مجموع|آثار|أعمال|رسائل|فتاوى|دواوين|الأعمال)')
PARTICLES = {'في', 'من', 'على', 'عن', 'الى', 'إلى', 'بين', 'مع', 'ويليه', 'ومعه', 'وبهامشه', 'وبذيله', 'وذيله', 'المسمى', 'المسماة', 'وهو', 'او', 'أو'}

# ---------- text helpers ----------
def clean(s):
    s = s.replace('‏', '').replace('‎', '')
    s = re.sub(r'\bت_\s*', 'ت ', s)
    s = re.sub(r'بـ\s*[:_]\s*', 'بـ', s)
    s = re.sub(r'\(\(+', '(', s); s = re.sub(r'\)\)+', ')', s)
    s = re.sub(r'(\d)(?=[\u0621-\u064A])', r'\1 ', s)
    s = re.sub(r'_alt\b', '', s)
    s = re.sub(r'\s*_\s*', ' - ', s)
    s = s.replace(':', ' -').replace('?', '؟').replace('"', '').replace('*', '').replace('|', '-').replace('\\', '-').replace('/', '-').replace('<', '').replace('>', '')
    s = re.sub(r'\.{2,}|…', '', s)
    s = balance(s)
    s = re.sub(r'\(\s*\)', '', s)
    s = re.sub(r'\s+', ' ', s).strip(' -.،')
    s = re.sub(r'\s+-\s*-\s+', ' - ', s)
    return s

def balance(s):
    out, depth = [], 0
    for ch in s:
        if ch == '(':
            depth += 1; out.append(ch)
        elif ch == ')':
            if depth: depth -= 1; out.append(ch)
        else: out.append(ch)
    s = ''.join(out)
    return s + ')' * depth

def fit(s, limit=MAXB):
    if len(s.encode()) <= limit: return s
    w = s.split()
    while w and len(' '.join(w).encode()) > limit: w.pop()
    while w and norm(w[-1]) in PARTICLES | {'و', 'ب', 'ل'}: w.pop()
    return balance(' '.join(w)).strip(' -')

def author_short(a):
    a = (a or '').strip()
    if not a or a in ('مجموعة من المؤلفين', 'كتاب سماوي'): return '' if a != 'مجموعة من المؤلفين' else a
    a = re.split(r'[؛;]', a)[0]
    if '،' in a and len(a) > 25: a = a.split('،')[0]
    return a.strip()

def publisher_short(p):
    p = (p or '').strip()
    return re.split(r'\s+-\s+', p)[0].strip() if p else ''

def researcher_short(r):
    r = (r or '').strip()
    if not r: return ''
    parts = [x.strip() for x in re.split(r'\s+-\s+|،\s*|\s+و(?=[^\s]{3,})', r) if x.strip()]
    return ' و'.join(parts[:2]) if len(parts) > 1 and len(r) > 30 else r

EDITION_RE = re.compile(r'\s+-\s+((?:ط|ت)[ .:].*|ج\s*\d.*|الجزء.*|المجلد.*|من\s.*|قطعة.*|السفر.*|القسم.*)$')
PART_RE = re.compile(r'^(ج\s*\d|الجزء|المجلد|من\s|قطعة|السفر|القسم)')

def split_wname(name):
    """Waqfeya book name -> (title, edition-part-from-name)."""
    m = EDITION_RE.search(name)
    if m: return name[:m.start()].strip(), m.group(1).strip()
    return name.strip(), ''

def short_title(t, author=''):
    t = re.split(r'\s+=\s+|\s+-\s+|\s+ويليه\s|\s+ومعه\s|\s+وبهامشه\s|\s+وبذيله\s|\s+المسمى\s|\s+المسماة\s|\s+الموسوم\s|\s+الموسومة\s|،\s*', t)[0].strip()
    w = t.split()
    if len(w) > 5:
        for i in range(2, len(w)):
            if norm(w[i]) in PARTICLES: w = w[:i]; break
        w = w[:6]
    s = ' '.join(w)
    if len(w) == 1 and author and not redundant(author, s): s = f'{s} - {author}'
    return balance(s)

# ---------- volume labels ----------
def vol_from_orig(orig):
    """archive.org Waqfeya naming: 00_xxxx = front, NN_xxxx = vol NN, NN_xxxxp = front of vol NN."""
    b = orig.rsplit('/', 1)[-1]
    m = re.match(r'^(\d{1,3})_\d+(p?)(?:_\d+)?\.pdf$', b, re.I) or re.match(r'^(\d{1,3})(p?)\.pdf$', b, re.I)
    if not m: return None
    n = int(m.group(1)); p = bool(m.group(2))
    return (0, 'front') if n == 0 else ((n, 'front') if p else (n, 'vol'))

def label_from_link(title):
    t = re.sub(r'^تحميل\s+', '', (title or '').strip())
    if re.search(r'واجهة|الغلاف', t): return 'الواجهة'
    if re.fullmatch(r'ال?مقدمة.*', t): return 'المقدمة'
    if ':' in t: return t.split(':', 1)[1].strip()
    m = re.search(r'\(([^)]+)\)', t)
    if m: return m.group(1).strip()
    if re.fullmatch(r'ال?فهارس.*', t): return 'الفهارس'
    return ''

# ---------- load ----------
def load():
    books = {}
    for fn in ('data/waqfeya/books.jsonl', 'data/waqfeya/details.jsonl', 'data/waqfeya/details2.jsonl'):
        if os.path.exists(J(fn)):
            for l in open(J(fn)):
                d = json.loads(l); books[d['_id']] = {**books.get(d['_id'], {}), **d}
    link_label = {}
    for b in books.values():
        for x in b.get('links') or []:
            m = re.search(r'archive\.org/download/([^/]+)/(.+?)\s*$', x.get('url', ''))
            if m: link_label[(m.group(1), m.group(2))] = x.get('title', '')
    prov = {r['path']: r for r in csv.DictReader(open(J('data/phone/provenance.tsv')), delimiter='\t')}
    return books, link_label, prov

def canonical_folder(b):
    title, ed_in_name = split_wname(b['name'])
    a = author_short((b.get('author') or {}).get('name', ''))
    if a and redundant(a, title): a = ''
    r, p = researcher_short(b.get('researcher')), publisher_short(b.get('publisher'))
    if r and p: ed = f'ت {r} - {p}'
    elif r: ed = f'ت {r}'
    elif p: ed = f'ط {p}'
    else: ed = re.sub(r'^([تط])[.:]?\s*', r'\1 ', ed_in_name) if ed_in_name and not PART_RE.match(ed_in_name) else ''
    name = clean(title)
    if a: name += f' - {clean(a)}'
    base = name
    if ed: name += f' ({clean(ed)})'
    if len(name.encode()) > MAXB: name = fit(base)
    return name, clean(title), clean(a)

def deficient(name):
    return bool(re.search(r'\.\.\.|…|_|\s-\S{1,2}$|\s\S$|\(\s*$', name)) or name.count('(') != name.count(')')

# ---------- plan ----------
def main(index, out):
    books, link_label, prov = load()
    files = defaultdict(list)
    for p, s in csv.reader(open(index), delimiter='\t'):
        if p.startswith(INDEX_DIR + '/'): continue
        files[p.rsplit('/', 1)[0]].append(p)
    moves, review = [], []
    target_of_book = {}     # waqfeya id -> (category, folder) already chosen (merge destination)
    used = set(files)       # folder names already taken
    def add(a, b, why):
        if a != b: moves.append((a, b, why))

    for folder in sorted(files, key=lambda f: -len(files[f])):
        cat, name = folder.split('/', 1)
        ps = files[folder]
        src = Counter(prov[p]['waqfeya_id'] for p in ps if p in prov and prov[p]['waqfeya_id'])
        bases = {title_key(books[w]['name'].split(' - ')[0]) for w in src}
        if len(src) > 1 and len(bases) == 1 and not COLLECTION.match(name):
            multi_record(folder, cat, name, ps, prov, books, src, add, used, target_of_book); continue
        matched = sum(src.values())
        kinds = len(src)
        if kinds == 0:
            # no Waqfeya evidence: mechanical fixes only
            nf = clean(name) if deficient(name) or '_' in name else name
            nf = nf or name
            dest = f'{cat}/{nf}'
            if dest != folder and dest in used: dest = folder; review.append((folder, 'fixed name collides with an existing folder'))
            used.add(dest)
            for p in ps:
                fn = p.rsplit('/', 1)[1]
                nfn = mech_file(fn)
                add(f'Books/{p}', f'Books/{dest}/{nfn}', 'mechanical fix' if nfn != fn or dest != folder else '')
            continue
        top, topn = src.most_common(1)[0]
        is_collection = bool(COLLECTION.match(name))
        if kinds == 1 or (topn >= 0.8 * matched and not is_collection):
            b = books[top]
            canon, title, a = canonical_folder(b)
            if top in target_of_book:
                dest = target_of_book[top]; why = 'merge copies of the same book'
            else:
                cur_ok = not deficient(name) and title_key(name) and title_key(b['name']).startswith(title_key(name)) and len(norm(name).split()) >= len(norm(title).split())
                dest_name = name if cur_ok and ' - ' in name else canon
                dest = f'{cat}/{dest_name}'
                if dest != folder and dest in used and dest not in target_of_book.values():
                    dest = f'{cat}/{canon}' if f'{cat}/{canon}' not in used else folder
                target_of_book[top] = dest; used.add(dest)
                why = 'restore full name from Waqfeya record' if dest != folder else ''
            plan_files(ps, prov, link_label, b, dest, why, add, review)
            if kinds > 1: review.append((folder, f'{kinds} Waqfeya sources; minority files kept in folder'))
        elif is_collection:
            for p in ps:
                r = prov.get(p); fn = p.rsplit('/', 1)[1]
                if r and r['waqfeya_id'] and len([q for q in ps if prov.get(q, {}).get('waqfeya_id') == r['waqfeya_id']]) == 1:
                    wb = books[r['waqfeya_id']]; t, _ = split_wname(wb['name'])
                    a = author_short((wb.get('author') or {}).get('name', ''))
                    nfn = fit(clean(t) + (f' - {clean(a)}' if a and not redundant(a, name + ' ' + t) else '')) + '.pdf'
                    add(f'Books/{p}', f'Books/{folder}/{nfn}', 'collection item named from Waqfeya record')
                else:
                    add(f'Books/{p}', f'Books/{folder}/{mech_file(fn)}', 'mechanical fix')
        else:
            # bucket folder: give every source book its own folder
            by = defaultdict(list)
            for p in ps: by[prov.get(p, {}).get('waqfeya_id') or ''].append(p)
            for wid, group in by.items():
                if not wid:
                    for p in group: review.append((p, 'unidentified file in a mixed (bucket) folder'))
                    continue
                b = books[wid]; canon, title, a = canonical_folder(b)
                dest = target_of_book.get(wid) or f'{cat}/{canon}'
                target_of_book.setdefault(wid, dest); used.add(dest)
                plan_files(group, prov, link_label, b, dest, f'split mixed folder «{name}»', add, review)
    # final: a destination used twice blocks every source folder involved (never split a book across folders)
    dest_src = defaultdict(list)
    for a, b, why in moves: dest_src[b].append(a)
    existing = {f'Books/{p}' for f in files for p in files[f]}
    moving = {a for a, b, w in moves if a != b}
    blocked = set()
    for b, srcs in dest_src.items():
        if len(srcs) > 1 or (b in existing and b not in moving and srcs[0] != b):
            for a in srcs: blocked.add(a.rsplit('/', 1)[0])
    final = []
    for a, b, why in moves:
        if a.rsplit('/', 1)[0] in blocked:
            continue
        final.append((a, b, why))
    for f in sorted(blocked): review.append((f[6:], 'name clash inside the planned folder: left unchanged (resolve duplicates first)'))
    with open(out, 'w') as f:
        for a, b, why in final:
            if a != b: f.write(f'{a}\t{b}\t{why}\n')
    with open(J('data/phone/rename-review.tsv'), 'w') as f:
        for x, why in review: f.write(f'{x}\t{why}\n')
    c = Counter(w.split(' «')[0] for a, b, w in final if a != b)
    print('planned moves:', sum(c.values()), dict(c)); print('review items:', len(review))

def mech_file(fn):
    stem = fn[:-4] if fn.lower().endswith('.pdf') else fn
    ext = fn[len(stem):]
    s = clean(stem)
    return (s or stem) + ext.lower()

def old_label(fn, title):
    m = re.match(r'^(?:\d+ - )?.*?\((.+)\)(?:_alt)?\.pdf$', fn)
    if not m: return ''
    lab = clean(m.group(1))
    if not lab or re.match(r'^(ط|ت)[ .]', lab) or lab in ('المقدمة', 'الواجهة'): return lab if lab in ('المقدمة', 'الواجهة') else ''
    lw = norm(lab).split(); tw = norm(title).split()
    if lw and all(w in tw for w in lw[:-1]) and any(t.startswith(lw[-1]) for t in tw): return ''   # remnant of the cut title
    return lab

def repair_file(fn, title, short):
    m = re.match(r'^(\d+) - (.*?)(?:\s*\((.+)\))?(?:_alt)?\.pdf$', fn)
    if m and norm(title).startswith(norm(clean(m.group(2)))):
        lab = old_label(fn, title)
        return f'{m.group(1)} - {short}' + (f' ({lab})' if lab else '') + '.pdf'
    return mech_file(fn)

def multi_record(folder, cat, name, ps, prov, books, src, add, used, target_of_book):
    """One book published on Waqfeya as several records (one per part): keep one folder, keep numbering."""
    w0 = books[src.most_common(1)[0][0]]
    base = clean(w0['name'].split(' - ')[0])
    a = author_short((w0.get('author') or {}).get('name', ''))
    canon = fit(base + (f' - {clean(a)}' if a and not redundant(a, base) else ''))
    key = ('multi', title_key(base))
    dest = target_of_book.get(key) or (folder if not deficient(name) and title_key(name).startswith(title_key(base)) else f'{cat}/{canon}')
    target_of_book[key] = dest; used.add(dest)
    short = clean(short_title(base, a))
    for p in ps:
        fn = p.rsplit('/', 1)[1]
        add(f'Books/{p}', f'Books/{dest}/{repair_file(fn, base, short)}', 'restore full name (multi-record book)')

def plan_files(ps, prov, link_label, b, dest, why, add, review):
    title, part = split_wname(b['name'])
    part = clean(part) if PART_RE.match(part or '') else ''
    a = author_short((b.get('author') or {}).get('name', ''))
    short = clean(short_title(title, a))
    info = []
    for p in ps:
        r = prov.get(p); fn = p.rsplit('/', 1)[1]
        if not r or r['waqfeya_id'] != b['_id']:
            info.append((p, None, None, fn)); continue
        v = vol_from_orig(r['orig_name'])
        lab = label_from_link(link_label.get((r['archive_id'], r['orig_name']), ''))
        info.append((p, v, lab, fn))
    vols = [v for p, v, lab, fn in info if v and v[1] == 'vol']
    nvol = len(vols); width = max(2, len(str(max([v[0] for v in vols], default=1))))
    names = Counter()
    for p, v, lab, fn in info:
        if v is not None and not lab: lab = old_label(fn, title)
        if v is None:
            new = repair_file(fn, title, short)
        elif nvol <= 1:
            base = fit(clean(title), MAXB - 30)
            new = f'{base} ({lab or "الواجهة"}).pdf' if v[1] == 'front' else f'{base}.pdf'
            if v[1] == 'vol' and (lab or part) and lab not in ('الواجهة', 'المقدمة'): new = f'{base} ({fit(clean(lab or part), 80)}).pdf'
        else:
            n = str(v[0]).zfill(width) if v[1] == 'vol' else ('0' * width if v[0] == 0 else str(v[0]).zfill(width))
            lab = lab if v[1] == 'vol' else (lab or ('الواجهة' if v[0] == 0 else 'المقدمة'))
            if v[1] == 'front' and lab not in ('الواجهة', 'المقدمة') and v[0] > 0: lab = 'المقدمة'
            new = f'{n} - {short}' + (f' ({fit(clean(lab), 90)})' if lab else '') + '.pdf'
        names[new] += 1
        add(f'Books/{p}', f'Books/{dest}/{new}', why or ('volume names from Waqfeya record' if v else 'mechanical fix'))
    for n, k in names.items():
        if k > 1: review.append((f'{dest}/{n}', f'{k} files would get the same name'))

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
