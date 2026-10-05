"""Reports 07 and 08 — reaching books through people.
07 «فهرس المؤلفين حسب سنة الوفاة»: every author on the phone, by century of death (Shamela's death year when the book
   matches Shamela, else Waqfeya's century), with his books, sections and sizes. Serves the expansion strategy
   (authors who died before 700 AH) and quick finding.
08 «فهرس المحققين»: every editor (محقق) with the editions of his on the phone (Waqfeya record of the exact files,
   else the «(ت …)» of the name), so edition decisions can be made editor by editor."""
import collections, csv, json, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from report_lib import Report, RawHTML, gb
from textnorm import norm
J = lambda p: os.path.join(ROOT, p)
CENT = ['الأول', 'الثاني', 'الثالث', 'الرابع', 'الخامس', 'السادس', 'السابع', 'الثامن', 'التاسع', 'العاشر', 'الحادي عشر',
        'الثاني عشر', 'الثالث عشر', 'الرابع عشر', 'الخامس عشر']
SKIP = ('فهارس الويب', 'نسخ محسنة للاستبدال', 'نسخ مستبعدة')

def load():
    cat = json.load(open(J('data/catalog.json'), encoding='utf-8'))
    death, sh_author = {}, {}
    for r in csv.DictReader(open(J('data/compare/shamela-matches.tsv'), encoding='utf-8'), delimiter='\t'):
        if not r['phone_book_ids']: continue
        for i in r['phone_book_ids'].split():
            if r['death'].isdigit() and int(r['death']) < 1500:
                death.setdefault(i, int(r['death'])); sh_author.setdefault(i, r['author'])
    return [b for b in cat['books'] if b['cat'] not in SKIP], death, sh_author

def edition_of(b):
    """The editor as the book's own name gives it («(ت X - publisher)», «- ت X»); the catalog's researcher field
    is not used: it is sometimes copied from a Waqfeya page that collects several books."""
    m = re.search(r'\(ت\s+([^()]+?)(?:\s+-\s+[^()]+)?\)\s*$', b['folder']) or re.search(r'\s-\s+ت[\s\-]+([^-()]+)', b['folder'])
    if m: return m.group(1).strip()
    return ''                                    # the catalog's researcher field can come from a collective Waqfeya page

def report_authors(B, death, sh_author):
    R = Report('07 - فهرس المؤلفين حسب سنة الوفاة', 'كل مؤلف على الهاتف مع كتبه، مرتبًا على قرن وفاته — للوصول السريع ولخطة التوسعة (من توفي قبل 700)')
    by = collections.defaultdict(list)
    for b in B:
        i = str(b['id'])
        d = death.get(i)
        c = None
        if d: c = (d - 1) // 100 + 1
        elif b.get('century'):
            m = re.search(r'(\d+)', b['century']); c = int(m.group(1)) if m else None
        a = sh_author.get(i) or b.get('author') or '—'
        a = re.split(r'[؛;]', a)[0].strip()
        by[(c, a)].append((d, b))
    cents = collections.defaultdict(list)
    for (c, a), v in by.items(): cents[c].append((min([d for d, _ in v if d] or [99999]), a, v))
    known = sum(len(v) for (c, a), v in by.items() if c)
    pre700 = sum(len(v) for (c, a), v in by.items() if c and c <= 7)
    R.kpis([('المؤلفون', len(by)), ('الكتب المعروفة سنة وفاة مؤلفها أو قرنه', known), ('كتب من توفي قبل 700 هـ', pre700),
            ('كتب بلا معلومة وفاة', sum(len(v) for (c, a), v in by.items() if not c))])
    R.note('سنة الوفاة من الشاملة إذا طابق الكتابُ كتابًا فيها، وإلا القرن من سجل الوقفية. المؤلفون بلا معلومة في آخر الصفحة.')
    R.table(['القرن', 'المؤلفون', 'الكتب', 'الحجم'],
            [[f'القرن {CENT[c - 1]}' if c and c <= 15 else 'غير معروف', len(cents[c]), sum(len(v) for _, _, v in cents[c]),
              gb(sum(b['bytes'] for _, _, v in cents[c] for _, b in v))] for c in sorted(cents, key=lambda c: c or 99)], numeric=(1, 2))
    for c in sorted(cents, key=lambda c: c or 99):
        rows = []
        for d, a, v in sorted(cents[c], key=lambda x: (x[0], x[1])):
            titles = RawHTML('<br>'.join(f'{b["folder"]} <span class="sub">({b["cat"]}، {len(b["files"])} م)</span>' for _, b in sorted(v, key=lambda x: x[1]['folder'])))
            rows.append([a, d if d != 99999 else '—', len(v), titles])
        R.table(['المؤلف', 'الوفاة', 'الكتب', 'الكتب على الهاتف'], rows, numeric=(1, 2),
                fold=(f'القرن {CENT[c - 1]} — {len(cents[c])} مؤلفًا' if c and c <= 15 else f'بلا معلومة وفاة — {len(cents[c])} اسمًا'))
    print(R.write('07 - فهرس المؤلفين حسب سنة الوفاة'), '| authors', len(by), 'known', known, 'pre700', pre700)

def report_editors(B):
    R = Report('08 - فهرس المحققين', 'المحققون وطبعاتهم على الهاتف — لاختيار الطبعات محققًا محققًا')
    by = collections.defaultdict(list)
    for b in B:
        e = edition_of(b)
        if not e or len(e) < 3: continue
        for one in re.split(r'\s+و(?=[^\s]{3,})|،\s*|\s+-\s+', e)[:3]:
            one = one.strip()
            if len(one) < 3 or re.match(r'^(دار|مكتبة|مؤسسة|مطبعة|ط\b|مجموعة|وزارة|جامعة|مركز)', one): continue
            key = ' '.join(norm(one).split())
            by[key].append((one, b))
    for key in [k for k in by if len(k.split()) == 1]:            # «التركي» → «عبد الله بن عبد المحسن التركي» if unique
        full = [k for k in by if len(k.split()) > 1 and k.split()[-1] == key]
        if len(full) == 1: by[full[0]] += by.pop(key)
    rows = []
    for key, v in sorted(by.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        name = collections.Counter(n for n, _ in v).most_common(1)[0][0]
        works = RawHTML('<br>'.join(f'{b["folder"]} <span class="sub">({b["cat"]})</span>' for _, b in sorted(v, key=lambda x: x[1]['folder'])))
        rows.append([name, len(v), works])
    R.kpis([('المحققون', len(rows)), ('طبعات منسوبة إلى محقق', sum(r[1] for r in rows))])
    R.note('المحقق كما يرد بعد «ت» في اسم الكتاب على الهاتف (والأسماء تُصحَّح من صفحات العنوان تباعًا). قد يرد المحقق الواحد بصيغ مختلفة.')
    R.table(['المحقق', 'طبعاته على الهاتف', 'الكتب'], rows[:400], numeric=(1,))
    if len(rows) > 400:
        R.table(['المحقق', 'طبعاته على الهاتف', 'الكتب'], rows[400:], numeric=(1,), fold=f'محققون آخرون ({len(rows) - 400})')
    print(R.write('08 - فهرس المحققين'), '| editors', len(rows))

if __name__ == '__main__':
    B, death, sh_author = load()
    report_authors(B, death, sh_author)
    report_editors(B)
