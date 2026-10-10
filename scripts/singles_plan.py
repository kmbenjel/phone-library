"""Single-volume books: a folder holding one PDF becomes a plain file in its section (AGENTS.md §4 «Single file»):
`<title> - <author> (<edition>).pdf` (the title is shortened only when the name would pass 200 bytes).

v2 (2026-10-10, owner: «single books in folders» first). v1 held back 1,055 of 1,178 folders, 946 of them only because
the folder name had no « - » before its author (Waqfeya's «<title> لفلان» form). Now:
  * the name comes from the folder name; old edition forms are normalised (« - ط. X» → «(ط X)», « - ت- X» → «(ت X)»);
  * an author written as «لفلان» at the end of the title is moved after « - » ONLY when the words after «ل» are a known
    author name (Shamela's common names, Waqfeya authors, the authors already in phone names) — and, when the file has an
    exact-size Waqfeya record, only when the record's author agrees. «شرح/حاشية/نظم … لفلان» (the «ل» may name the
    original's author) needs that record; else the title is kept whole (no guessing);
  * «01 - X» alone becomes a plain file only on evidence that it is the whole book: it was made by plan 066 from an
    uploader's gift number («الهدية (N)»), or its exact-size Waqfeya record has one volume and links one file; it stays a
    folder when the record or the PDF's embedded title names more volumes; otherwise it goes to the review list;
  * kept as folders: one volume of a larger set (file «NN - …» with NN > 1, «(جزء N)», the record's volumes), collections
    and series («مؤلفات/سلسلة/مجلة …»), folders with sub-folders; cut names («… - ال», «- ابن قي») wait for the title-page
    pass (data/review/name-fix-review.tsv); a name already taken by another file is listed, never overwritten.
Usage: python3 scripts/singles_plan.py index.tsv plans/NNN-singles.tsv [review.tsv] [--skip LIST]
       (--skip: phone paths not to touch now, e.g. a crop batch still running on them)"""
import collections, csv, json, os, re, sys, unicodedata
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from textnorm import norm
from special_dirs import NOT_BOOKS
from rename_plan import clean, deficient, redundant, author_short, researcher_short
from textnorm import title_key
import name_compose
J = lambda p: os.path.join(ROOT, p)
N = lambda s: unicodedata.normalize('NFC', s)

COLLECTION = re.compile(r'^(مؤلفات|سلسلة|مجلة)\s')
DERIVED = re.compile(r'^(شرح|حاشية|تعليق|تعليقات|التعليق|نظم|منظومة|مختصر|اختصار|تهذيب|تخريج|تقريرات|فتح|الشرح|الحاشية|المختصر|تحقيق|دراسة)\b')
CUT = re.compile(r'\s-\s*\S{1,2}$|\s-\s*(اب|ابن \S{1,2}|أبو \S{0,2}|عبد|محمد بن)$|\s(لل|ال|اب)$|\(\s*-\s*\S+\s*\)|\(\s*$')
COMMON_GIVEN = {norm(w) for w in 'محمد أحمد علي عبد الله عبد الرحمن عمر عثمان إبراهيم الإمام الشيخ الحافظ العلامة القاضي'.split()}

def known_authors():
    """normalised author names: Shamela common names, Waqfeya authors, the authors of phone names"""
    k = set()
    for l in open(J('data/shamela/authors.jsonl'), encoding='utf-8'):
        a = json.loads(l); k.add(norm(re.split(r'\s*\(', a['name'])[0]))
        for w in norm(a.get('full', '')).split():               # its nisbas («المعسكري»), as titles write «للمعسكري»
            if w.startswith('ال') and w.endswith('ي') and len(w) >= 6: k.add(w)
    for l in open(J('data/waqfeya/books.jsonl'), encoding='utf-8'):
        a = (json.loads(l).get('author') or {}).get('name') or ''
        if a and a != 'كتاب سماوي':
            k.add(norm(author_short(a)))
            last = norm(re.split(r'[،(]', a)[0]).split()[-1:]       # the nisba alone («الإفراني»), as the titles write it
            if last and last[0].startswith('ال') and len(last[0]) >= 5: k.add(last[0])
    seen = collections.defaultdict(set)                 # phone names: an author part counts only when it signs two titles
    for p, _ in csv.reader(open(J('data/phone/index-now.tsv'), encoding='utf-8'), delimiter='\t'):
        for part in p.split('/')[1:]:
            base = re.sub(r'\([^()]*\)', '', part.removesuffix('.pdf'))
            bits = [x.strip() for x in base.split(' - ')]
            if len(bits) >= 2 and not re.match(r'^\d+$', bits[0]): seen[norm(bits[-1])].add(norm(bits[0]))
    k |= {a for a, titles in seen.items() if len(titles) >= 2}
    return {a for a in k if a and len(a) > 3 and a not in COMMON_GIVEN}

def lam_author(title, known, record_author=''):
    """«<title> لفلان» → (title, author) when the words after «ل» are a known author name; else (title, '')"""
    w = title.split()
    for i in range(len(w) - 1, 0, -1):
        x = w[i]
        if not x.startswith('ل') or len(x) < 3: continue
        if x.startswith('لل'): first = 'ال' + x[2:]
        elif x.startswith('لأبي'): first = 'أبو' + x[4:]
        elif x.startswith('لابن') or x.startswith('لإ') or x.startswith('لأ') or x.startswith('لعبد'): first = x[1:]
        else: first = x[1:]
        cand = ' '.join([first] + w[i + 1:])
        if norm(first) in {norm(x) for x in ('الإمام', 'الشيخ', 'الحافظ', 'العلامة', 'القاضي')} and len(w) > i + 1:
            cand = ' '.join(w[i + 1:])                 # «للإمام ابن حجر العسقلاني» → «ابن حجر العسقلاني»
        if len(norm(cand)) < 4: continue
        nc = norm(cand); ok = nc in known
        if not ok:                                   # «ابن عرفة الورغمي»: a known name followed by its nisba
            for j in range(len(cand.split()) - 1, 0, -1):
                pre = norm(' '.join(cand.split()[:j]))
                if pre in known and pre not in COMMON_GIVEN and len(pre.split()) + (pre.startswith('ابن') or pre.startswith('ابو')) >= 2: ok = True; break
                if pre in known and len(pre.split()) == 1 and len(pre) >= 6: ok = True; break
        if not ok: continue
        t = ' '.join(w[:i])
        if record_author:
            ra = {v.removeprefix('ال') for v in norm(record_author).split() if len(v) > 2} - {'ابن', 'ابو', 'ابي', 'عبد', 'الله'}
            ca = {v.removeprefix('ال') for v in nc.split() if len(v) > 2} - {'ابن', 'ابو', 'ابي', 'عبد', 'الله'}
            if not (ra & ca): return title, '', 'the «ل» name disagrees with the record\'s author'
        elif DERIVED.match(t):
            return title, '', 'a derived work («شرح/حاشية/نظم … لفلان») without a record: whose name?'
        return t, cand, ''
    return title, '', ''

PUBLISHER = {'صادر': 'دار صادر', 'العلمية': 'دار الكتب العلمية', 'القلم': 'دار القلم', 'بيروت': 'دار بيروت',
             'الكتاب العربي': 'دار الكتاب العربي'}       # the uploaders' short forms «ط. صادر» of these houses

def parse_folder(name):
    """«title - author (edition)» → (title, author, edition); old forms «- ط. X», «- ت- X» read as the edition"""
    name = re.sub(r'\s*-\s*ط\.\s*(.+)$', r' (ط \1)', name) if not name.endswith(')') else name
    name = re.sub(r'\s*-\s*ت-\s*(.+)$', r' (ت \1)', name) if not name.endswith(')') else name
    name = re.sub(r'\s-\s*ت\s*-\s*([^()]+)$', r' (ت \1)', name) if not name.endswith(')') else name
    name = re.sub(r'\(ط\.\s*', '(ط ', name)
    m = re.match(r'^(.*?)\s*\(([^()]*)\)\s*$', name)
    ed = m.group(2).strip() if m else ''
    base = m.group(1) if m else name
    if ed and not re.match(r'^(ت|ط|رسالة|دار|مكتبة|مؤسسة|المكتب|مطبعة)', ed): base, ed = name, ''   # «(رسالة علمية)», «(الجد)» belong to the title
    parts = [x.strip() for x in base.split(' - ')]
    title, author = (' - '.join(parts[:-1]), parts[-1]) if len(parts) > 1 else (parts[0], '')
    author = re.split(r'\s*؛', author)[0].strip()
    if re.match(r'^(من\s|ج\s*\d|الجزء|المجلد|قطعة|السفر|القسم|سورة\s)', author):    # a part described, not an author
        title, author = f'{title}، {author}', ''
    if re.match(r'^(ت|ط)\s', author): ed, author = ed or author, ''
    m = re.match(r'^ط\s+(.+)$', ed)
    if m and m.group(1) in PUBLISHER: ed = 'ط ' + PUBLISHER[m.group(1)]
    return title, author, ed

JUNK = re.compile(r'كتاب اقرا اونلاين|اقرا اونلاين|نسخة مفهرسة وقابلة للبحث|مفهرس[ةه]?|كاملا|ألوان|\bpdf\b|\b\d+\b|book\d*|[A-Za-z_]+')

def file_info(fn, folder_title, known=frozenset()):
    """what the file name adds to the folder name: (author, extra words not explained)"""
    stem = re.sub(r'^0*1\s*-\s*', '', fn.removesuffix('.pdf'))
    stem = re.sub(r'الهدية\s*\(\s*\d+\s*\)', '', stem)
    stem = JUNK.sub(' ', stem)
    base = re.sub(r'\([^()]*\)', ' ', stem)
    parts = [x.strip() for x in base.split(' - ') if x.strip()]
    au = parts[-1] if len(parts) > 1 and not re.match(r'^(ط|ت)\.?\s', parts[-1]) else ''
    au = re.split(r'\s*[؛،]', au)[0].strip()
    if au and norm(au) not in known and not any(norm(' '.join(au.split()[:j])) in known for j in range(2, len(au.split()))):
        au = ''                                        # «العصر الجاهلي لشوقي ضيف» is not an author: its words stay «extra»
    extra = {w for w in norm(stem).split() if len(w) > 2} - set(norm(folder_title).split())
    expl = {w for w in norm(au).split()} | {'ط', 'ت', 'تحقيق'}
    return au, {w for w in extra if w not in expl and w.removeprefix('ال') not in {x.removeprefix('ال') for x in expl}}

def same_book(t, b):
    """a Waqfeya record lends its author/editor only when its title is this book (a bundle's record names another)"""
    rt = {w for w in title_key(b.get('name', '')).split() if len(w) > 2}; tt = {w for w in norm(t).split() if len(w) > 2}
    return bool(rt) and len(rt & tt) / max(1, min(len(rt), len(tt))) >= 0.6

def enrich(au, ed, b):
    """the author, editor and publisher the name lacks, from the exact-size record of the same book"""
    why = []
    v = lambda x: '' if (x or '').strip() in ('', '-', 'بدون', 'دون', 'لا يوجد', 'غير معروف') else x.strip()
    if not au:
        a = author_short((b.get('author') or {}).get('name', ''))
        if a and a not in ('كتاب سماوي', 'مجموعة من المؤلفين'): au = a; why.append('author')
    r, pub = researcher_short(v(b.get('researcher'))), v(b.get('publisher')).replace(' - ', '، ')
    if r and not ed.startswith('ت ') and norm(r) not in norm(ed):
        p0 = ed[2:].strip() if ed.startswith('ط ') else ''
        ed = f'ت {r}' + (f' - {p0 or pub}' if (p0 or pub) else ''); why.append('editor')
    elif pub and not ed:
        ed = f'ط {pub}'; why.append('publisher')
    elif pub and ed.startswith('ت ') and ' - ' not in ed and norm(pub) not in norm(ed):
        ed = f'{ed} - {pub}'; why.append('publisher')
    return au, ed, why

def moved_from():
    """later path → every earlier path it was moved from (all of them: an undo moves a file back into its old name, and
    the name before that must still be reachable — plan 310's undo hid plan 066's «الهدية» names)"""
    back = collections.defaultdict(list)
    for r in csv.reader(open(J('data/changes/changes.tsv'), encoding='utf-8'), delimiter='\t'):
        if len(r) > 3 and r[1] == 'move' and r[2] and r[3]: back[N(r[3])].append(N(r[2]))
    return back

def history(path, back):
    out, todo, seen = [], [N('Books/' + path)], set()
    while todo and len(out) < 60:
        p = todo.pop()
        for q in back.get(p, ()):
            if q not in seen: seen.add(q); out.append(q); todo.append(q)
    return out

def main(index, out, review_out=None, skip=()):
    idx = [(N(p), int(s or 0)) for p, s in csv.reader(open(index, encoding='utf-8'), delimiter='\t')]
    rawof = {N(p): p for p, _ in csv.reader(open(index, encoding='utf-8'), delimiter='\t')}   # the phone's own bytes: a
    # non-NFC name moved by its NFC form leaves its folder behind (plan 310: 4 folders), so «from» is always the raw path
    prov = {N(r['path']): r for r in csv.DictReader(open(J('data/phone/provenance.tsv'), encoding='utf-8'), delimiter='\t')}
    books = {}
    for fn in ('data/waqfeya/details.jsonl', 'data/waqfeya/details2.jsonl'):
        if os.path.exists(J(fn)):
            for l in open(J(fn), encoding='utf-8'):
                d = json.loads(l); books[d['_id']] = d
    meta = {}
    for l in open(J('data/inspect/files.jsonl'), encoding='utf-8'):
        d = json.loads(l)
        try: meta[N(d['path'])] = (eval(d['meta']) if isinstance(d.get('meta'), str) else (d.get('meta') or {})).get('title', '') or ''
        except Exception: pass
    known, back = known_authors(), moved_from()
    cutrev = {N(r['book']) for r in csv.DictReader(open(J('data/review/name-fix-review.tsv'), encoding='utf-8'), delimiter='\t')
              if 'cut' in r['defect']}
    under = collections.defaultdict(list); deep = set(); plain = collections.defaultdict(set)
    for p, s in idx:
        parts = p.split('/')
        if len(parts) >= 3: under['/'.join(parts[:2])].append((p, s))
        if len(parts) > 3: deep.add('/'.join(parts[:2]))
        if len(parts) == 2: plain[parts[0]].add(norm(parts[1].removesuffix('.pdf')))
    rows, review, stats = [], [], collections.Counter()
    def hold(why, folder, extra=''):
        stats[why] += 1; review.append((folder, why, extra))
    for folder, ps in sorted(under.items()):
        if len(ps) != 1: continue
        cat, name = folder.split('/', 1)
        path, size = ps[0]; fn = path.rsplit('/', 1)[1]
        if path in skip: stats['later: busy (--skip)'] += 1; continue
        if cat in NOT_BOOKS or not fn.lower().endswith('.pdf'): continue
        if folder in deep: stats['keep: has sub-folders'] += 1; continue
        if COLLECTION.match(name): stats['keep: collection or series'] += 1; continue
        r = prov.get(path) or {}
        b = books.get(r.get('waqfeya_id')) if r.get('match') in ('unique', 'substituted-unique') else None   # one record by exact size
        nvol = int(re.sub(r'\D', '', str((b or {}).get('numberOfVolumes') or '')) or 0)
        nlinks = len([x for x in (b or {}).get('links') or [] if 'archive.org/download' in x.get('url', '') and x.get('url', '').lower().endswith('.pdf')])
        mt = meta.get(path, '')
        vm = re.match(r'^0*(\d{1,3}) - ', fn) or re.search(r'\((?:جزء|الجزء|المجلد|مجلد)\s*(\d+)\)', fn) or re.search(r'(?:^|\s)ج\s*(\d{1,2})(?:\s|$)', fn)
        vol_meta = re.search(r'(?:^|\s)-\s*ج\s*(\d+)', mt)
        if (vm and int(vm.group(1)) > 1) or re.search(r'الجزء (الثاني|الثالث|الرابع|الخامس)|المجلد (الثاني|الثالث)', fn) \
           or (vol_meta and int(vol_meta.group(1)) > 1):
            stats['keep: one volume of a larger set'] += 1; continue
        gift = any('الهدية' in h for h in history(path, back))
        one = re.match(r'^0*1 - ', fn) or re.search(r'\((?:جزء|الجزء|المجلد|مجلد)\s*1\)', fn)
        if b and (nvol > 1 or nlinks > 1) and not gift:
            stats['keep: the record has more volumes (incomplete set)'] += 1; continue
        if one:
            if gift: why1 = 'was «الهدية (N)» (plan 066 made it «01 -»)'
            elif b and nvol <= 1 and nlinks <= 1: why1 = 'its exact-size Waqfeya record: one volume, one file'
            elif vol_meta: stats['keep: «01 -», the PDF title says «ج 1»'] += 1; continue
            else: hold('wait: «01 -» alone, no evidence it is the whole book', folder, fn); continue
        if re.search(r'\((الواجهة|المقدمة|الفهارس|الفهرس|الغلاف)\)|^0*0 - ', fn):
            stats['keep: a cover, preface or index alone (part of a set)'] += 1; continue
        if CUT.search(name) or deficient(name) or folder in cutrev:
            hold('wait: cut name (title-page pass)', folder, fn); continue
        t, au, ed = parse_folder(name)
        au = re.sub(r'\s+ط\s+\S+$', '', au)
        how = 'folder name'
        fau, extra = file_info(fn, name, known)
        if extra:
            hold('wait: the file name says more than the folder name (read it)', folder, fn); continue
        if fau and not au and norm(fau) not in norm(t):
            au, how = fau, 'folder name + the author in the file name'
        if not au:
            t2, au2, doubt = lam_author(t, known, author_short((b or {}).get('author', {}).get('name', '') if b else ''))
            if au2: t, au, how = t2, au2, 'author from «لفلان» in the title'
            elif doubt: stats['note: «ل» name not used — ' + doubt] += 1
        if gift: how += '; ' + why1
        elif one: how += '; ' + why1
        if b and same_book(t, b):
            au, ed, got = enrich(au, ed, b)
            if got: how += '; from the exact-size Waqfeya record: ' + ', '.join(got)
        t, au, ed = clean(t), clean(au), clean(ed)
        if not t: hold('skip: no title', folder, fn); continue
        new = name_compose.compose(t, au if au and not redundant(au, t) else '', ed) + '.pdf'
        if norm(new.removesuffix('.pdf')) in plain[cat]:
            hold('wait: the plain name is taken in the section', folder, new); continue
        plain[cat].add(norm(new.removesuffix('.pdf')))
        rows.append((f'Books/{rawof[path]}', f'Books/{cat}/{new}', f'single-volume book: plain file in its section (§4); {how}'))
        stats['to plain file' + (' (author from «ل»)' if 'لفلان' in how else '') + (' (was «01 -»)' if one else '')] += 1
    with open(out, 'w', encoding='utf-8') as w:
        for r in rows: w.write('\t'.join(r) + '\n')
    if review_out:
        with open(review_out, 'w', encoding='utf-8') as w:
            w.write('folder\twhy\tfile\n')
            for r in review: w.write('\t'.join(r) + '\n')
    for k, v in sorted(stats.items(), key=lambda x: -x[1]): print(f'{v:6}  {k}')

if __name__ == '__main__':
    a = sys.argv[1:]; skip = set()
    if '--skip' in a:
        k = a.index('--skip'); lst = a[k + 1]; del a[k:k + 2]
        done = {N(l.split('\t')[0]) for l in open(J('data/crop/done.tsv'), encoding='utf-8')} if os.path.exists(J('data/crop/done.tsv')) else set()
        skip = {N(l.strip().removeprefix('Books/')) for l in open(lst, encoding='utf-8') if l.strip()} - done
    main(*a[:3], skip=skip)
