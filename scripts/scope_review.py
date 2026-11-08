"""Books outside the library's scope (owner, 2026-10-08: «رسائل دعوية موجهة للعموم الأوسع أو رسائل جامعية غير ذات قيمة
علمية خاصة.. لا أهتم بها وحمّلت بالغلط، والكتب في القرن الحالي لا ينبغي أن يكون عندي منها الكثير، نعم من الجيد العظيم
والوفير من القرن السابق لا بأس به»). Lists CANDIDATES for the owner to tick — nothing is removed by this script.

Three groups, each row with its evidence:
  thesis  a university thesis («رسالة ماجستير / دكتوراه، أطروحة، بحث مقدم لنيل…» in the name, the record or the first
          pages' text / OCR) by a modern author. A thesis that edits a classical work (author died before 1300 AH) is the
          classical work itself and is not listed.
  tract   a short popular da'wa tract: modern author (died 1400 AH or later, or unknown with a print year ≥ 1980),
          ≤ 100 pages, in a religious section.
  recent  printed 2000 or later (1421 AH), modern author, not a classical text — the owner keeps «not many» of these.
Never listed: classical authors (died before 1300 AH); what the owner chose himself — هنداوي «مقدمات قصيرة جدًّا»,
OpenStax, Siyavula, Hesperian, Strang, world literature (الأدب/أدب عالمي), سلسلة عالم المعرفة, the works of علي العمران and
عبد الهادي حميتو; periodicals (مجلة …).
Output: data/review/scope-candidates.json (+ .tsv); `page` also writes the owner's review page
selection/مراجعة-نطاق-المكتبة.html (published as a claude.ai artifact with a db: the ticks are read back with ArtifactData
get decisions/current → {remove: [catalog paths]}). Usage: python3 scripts/scope_review.py [page]"""
import csv, json, os, re, sys, collections
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J = lambda p: os.path.join(ROOT, p)

THESIS = re.compile(r'رسالة\s+(?:ال)?(?:ماجستير|ماجيستير|دكتوراه|دكتوراة|الدكتوراه|علمية|جامعية)|أطروحة|اطروحة')   # in the name / record
TITLEPAGE = re.compile(r'(?:رسالة|بحث|أطروحة|اطروحة|مذكرة)\s+(?:مقدمة?|تكميلي)\s+(?:لنيل|استكمالا|ل?استكمال)|'
                       r'لنيل\s+(?:درجة|شهادة)\s+(?:ال)?(?:ماجستير|ماجيستير|دكتوراه|دكتوراة|عالمية|الدكتوراه|الماجستير)')  # a thesis title page
KEEP_PATHS = ('علوم أخرى/مقدمات قصيرة', 'هنداوي', 'OpenStax', 'Siyavula', 'Hesperian', 'Strang', 'الأدب/أدب عالمي',
              'عالم المعرفة', 'العمران', 'حميتو')
RELIGIOUS = {'العقيدة', 'الرقائق والآداب والأذكار', 'الفقه العام', 'مسائل فقهية', 'السياسة الشرعية والقضاء', 'كتب عامة',
             'الفرق والردود', 'علوم القرآن وأصول التفسير', 'التفسير', 'كتب السنة', 'شروح الحديث', 'علوم الحديث',
             'الفقه الحنفي', 'الفقه المالكي', 'الفقه الشافعي', 'الفقه الحنبلي', 'أصول الفقه', 'علوم الفقه والقواعد الفقهية',
             'السيرة النبوية', 'الفتاوى', 'التراجم والطبقات', 'الجوامع', 'الأدعية والأذكار'}

AR = str.maketrans('٠١٢٣٤٥٦٧٨٩', '0123456789')

def norm(s):
    s = re.sub(r'[\u064B-\u0652\u0640]', '', s or '')
    s = s.translate(str.maketrans('أإآىة', 'اااي ه'.replace(' ', '')))
    return re.sub(r'\s+', ' ', re.sub(r'^(?:ال)', '', s.strip()))

def death_signals():
    """classical or modern, from three independent sources: the Shamela books matched to phone books (their author's death),
    the Shamela authors list (name → death), and the Shamela books list (author → death)"""
    by_id = {}
    for r in csv.DictReader(open(J('data/compare/shamela-matches.tsv'), encoding='utf-8'), delimiter='\t'):
        if r.get('death', '').isdigit():
            for i in (r.get('phone_book_ids') or '').replace(';', ',').split(','):
                if i.strip().isdigit(): by_id.setdefault(int(i), []).append(int(r['death']))
    names = {}
    for l in open(J('data/shamela/authors.jsonl'), encoding='utf-8'):
        d = json.loads(l); m = re.match(r'(.*?)\s*\((.*?)\)', d['name'])
        if m:
            nums = re.findall(r'\d+', m.group(2).translate(AR))
            if nums and int(nums[-1]) > 0: names.setdefault(norm(m.group(1)), set()).add(int(nums[-1]))
    for r in csv.DictReader(open(J('data/shamela/books.tsv'), encoding='utf-8'), delimiter='\t'):
        if r.get('death', '').isdigit() and int(r['death']) > 0: names.setdefault(norm(r['author']), set()).add(int(r['death']))
    return by_id, names

STUDY = re.compile(r'منهج|عقيدته|موقف|جهود|اثر|دراسه|اراء|اختيارات|ومنهجه|عند (?:ال)?امام|في ضوء|مقارنه|حياته|عصره|فكر')
CLASSIC_NAMES = {}

def classify_age(b, e, by_id, names):
    """(oldest death found, how) — a book is classical if ANY source puts its author before 1300 AH"""
    sig = []
    sig += [(d, 'شاملة') for d in by_id.get(b['id'], [])]
    m = re.search(r'(\d+)', b.get('century') or '')
    if m: sig.append((int(m.group(1)) * 100 - 50, 'قرن الوقفية'))
    a = norm(b.get('author') or '')
    if a and len(a) > 3:
        if a in names and len(names[a]) == 1: sig.append((next(iter(names[a])), 'مؤلفو الشاملة'))
        else:                                       # a well-known short name («السيوطي») inside one full name of the list
            ds = {d for n, v in names.items() if re.search(r'(?:^|\s)(?:ال)?' + re.escape(a) + r'(?:$|\s)', n) for d in v}
            if ds and (max(ds) < 1300 or min(ds) >= 1300) and len(ds) <= 3: sig.append((min(ds), 'مؤلفو الشاملة'))
    d = (e.get('death') or {}).get('v')
    if d and str(d).isdigit(): sig.append((int(d), 'وفاة'))
    # a classical author named in the title of a book whose own author is unknown or only placed by a century: the
    # classical text itself (an edition, a commentary) — unless the title reads as a modern study of that author
    if not any(h in ('شاملة', 'مؤلفو الشاملة', 'وفاة') for _, h in sig):
        t = norm(b.get('title') or b['folder'])
        if not STUDY.search(t):
            hit = [d for n, d in CLASSIC_NAMES.items() if n in t]
            if hit: sig.append((min(hit), 'اسم في العنوان'))
            elif not sig and re.match(r'(?:شرح|حاشيه|ديوان|نظم|مختصر|تفسير|التوضيح شرح|التبيان شرح)\b|.* شرح ', t):
                sig.append((1299, 'عنوان متن أو شرح'))   # an unknown author's «شرح / ديوان / نظم …»: a classical text
    if not sig: return None, None, []
    lo = min(sig); return lo[0], lo[1], sig

def majors():
    p = J('data/mappings/major-modern-scholars.txt')
    return [norm(l.strip()) for l in open(p, encoding='utf-8') if l.strip() and not l.startswith('#')] if os.path.exists(p) else []

def main():
    books = json.load(open(J('data/catalog.json'), encoding='utf-8'))['books']
    ei = json.load(open(J('data/editions/edition-info.json'), encoding='utf-8'))
    text = {}                                          # first pages' text (pdf text layer, else OCR), per phone file
    for l in open(J('data/inspect/files.jsonl'), encoding='utf-8'):
        d = json.loads(l); text[d['path']] = (d.get('key'), d.get('text_first') or '', d.get('pages'))
    ocr = collections.defaultdict(str)
    if os.path.exists(J('data/inspect/ocr.jsonl')):
        for l in open(J('data/inspect/ocr.jsonl'), encoding='utf-8'):
            d = json.loads(l); ocr[d['key']] += ' ' + d.get('text', '')
    by_id, names = death_signals(); major = majors()
    for n, v in names.items():                       # classical names of two words or more, never shared with a modern author
        if len(n.split()) >= 2 and len(n) >= 8 and max(v) < 1300: CLASSIC_NAMES[n] = min(v)
    out = []
    for b in books:
        path = b['cat'] + '/' + b['folder']
        if any(k in path for k in KEEP_PATHS) or b['folder'].startswith('مجلة') or b['folder'].startswith('سلسلة'): continue
        e = ei.get(path, {})
        died, how, sig = classify_age(b, e, by_id, names)
        if died is not None and died < 1300: continue          # a classical work (in any edition) is in scope
        g = (e.get('gregorian') or {}).get('v'); h = (e.get('hijri') or {}).get('v')
        year = int(g) if g else (int(h) + 579 if h else None)
        pages = 0
        files = [f for f, _ in b['files']]
        ftexts = []
        for f in files:
            p = path + '/' + f if not path.endswith('.pdf') else path
            t = text.get(p) or text.get(b['cat'] + '/' + f)
            if t:
                ftexts.append(t[1] + ' ' + ocr.get(t[0], ''))
                pages += t[2] or 0                     # the files' own page counts
        strong = ' '.join([b['folder'], b.get('edition') or ''] + ftexts)          # the name, the edition, the first pages
        weak = json.dumps(e.get('note', ''), ensure_ascii=False)                  # a record's note: often a classical text
        name = ' '.join([b['folder'], b.get('edition') or ''])
        m = THESIS.search(name); src = name                                      # edited in a thesis
        if not m: m = TITLEPAGE.search(' '.join(ftexts)); src = ' '.join(ftexts)
        if not m and died is not None and died >= 1300: m = THESIS.search(weak); src = weak
        if m and re.search(r'تحقيق|حقق|تحقيقا', src[max(0, m.start() - 150): m.end() + 150]): m = None   # an edition of a text
        row = {'path': path, 'cat': b['cat'], 'title': b.get('title') or b['folder'], 'author': b.get('author') or '',
               'died': died, 'died_how': how, 'signals': sig, 'year': year, 'pages': pages, 'mb': round(b['bytes'] / 1e6, 1), 'files': len(files),
               'publisher': (e.get('publisher') or {}).get('v') or '', 'editor': b.get('researcher') or (e.get('editor') or {}).get('v') or ''}
        modern = died is not None and died >= 1400            # a known modern author (unknown authors are not listed)
        au = b.get('author') or ''
        if '،' in au: au = ' '.join(x.strip() for x in reversed(au.split('،', 1)))   # «الأسد، ناصر الدين» → «ناصر الدين الأسد»
        fo = b['folder']
        mrev = re.search(r' - ([^()]+?)، ([^()]+?)(?: \(|$)', fo)
        if mrev: fo += ' ' + mrev.group(2) + ' ' + mrev.group(1)
        an = norm(au) + ' ' + norm(fo)
        row['major'] = next((mj for mj in major if mj and re.search(r'(?:^|\s)' + re.escape(mj) + r'(?:$|\s|\))', an)), '')
        if m and (died is None or died >= 1300):
            i = m.start(); row.update(group='thesis', evidence=src[max(0, i - 60): i + 80].replace('\n', ' ')); out.append(row); continue
        if modern and b['cat'] in RELIGIOUS and 0 < pages <= 100:
            row.update(group='tract', evidence=f'{pages} صفحة'); out.append(row); continue
        if modern and year and year >= 2000:
            row.update(group='recent', evidence=f'طبع {year}'); out.append(row); continue
    os.makedirs(J('data/review'), exist_ok=True)
    json.dump(out, open(J('data/review/scope-candidates.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    with open(J('data/review/scope-candidates.tsv'), 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f, delimiter='\t'); w.writerow(['group', 'path', 'author', 'died', 'year', 'pages', 'mb', 'evidence'])
        for r in out: w.writerow([r['group'], r['path'], r['author'], r['died'], r['year'], r['pages'], r['mb'], r['evidence']])
    c = collections.Counter(r['group'] for r in out)
    print(dict(c), 'of', len(books), 'books;', round(sum(r['mb'] for r in out) / 1000, 1), 'GB')

PAGE = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scope_review_page.html'), encoding='utf-8').read() \
    if os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scope_review_page.html')) else ''

def page():
    rows = json.load(open(J('data/review/scope-candidates.json'), encoding='utf-8'))
    def ev(r):
        e = r.get('evidence') or ''
        m = re.match(r'\{"v": "(.*?)", "s": "(.*?)"\}', e.strip())
        if m: e = f'{m.group(1)} ({m.group(2)})'
        e = re.sub(r'[\u200e\u200f\u202a-\u202e]', '', e); e = re.sub(r'\s+', ' ', e).strip()
        return e[:140] + ('…' if len(e) > 140 else '')
    def who(r):
        d, h = r.get('died'), r.get('died_how') or ''
        if d is None: return ''
        if h == 'قرن الوقفية': return f'القرن {(d // 100) + 1} هـ'
        return f'ت {d} هـ' if d < 1446 else 'معاصر'
    data = [{'p': r['path'], 'g': r['group'], 't': r['path'].rsplit('/', 1)[-1].removesuffix('.pdf'), 'c': r['cat'],
             'a': r.get('author') or '', 'w': who(r), 'y': r.get('year') or '', 'n': r.get('pages') or 0, 'mb': r.get('mb') or 0,
             'e': ev(r) if r['group'] == 'thesis' else '', 'm': bool(r.get('major'))} for r in rows]
    order = {'thesis': 0, 'tract': 1, 'recent': 2}
    data.sort(key=lambda x: (order[x['g']], x['m'], x['c'], x['t']))
    html = PAGE.replace('/*DATA*/[]', json.dumps(data, ensure_ascii=False))
    os.makedirs(J('selection'), exist_ok=True)
    out = J('selection/مراجعة-نطاق-المكتبة.html'); open(out, 'w', encoding='utf-8').write(html); print(out, len(data), 'rows')

if __name__ == '__main__':
    main()
    if 'page' in sys.argv[1:]: page()
