"""Report 01: the phone library vs the locally installed Shamela (run compare_shamela.py first)."""
import csv, json, os, sys
from collections import defaultdict, Counter
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from report_lib import Report, pct
from textnorm import title_key
import shamela_cards as SC
J = lambda p: os.path.join(ROOT, p)
CARDS = SC.load()
ed = lambda r: SC.ed_line(CARDS.get(int(r['shamela_id'])))

cat = json.load(open(J('data/catalog.json')))
books = {b['id']: b for b in cat['books']}
rows = list(csv.DictReader(open(J('data/compare/shamela-matches.tsv')), delimiter='\t'))
smap = {}
for l in open(J('data/mappings/shamela-to-phone.tsv')):
    if l.startswith('#') or not l.strip(): continue
    k, _, v = l.rstrip('\n').partition('\t'); smap[k] = v
order = list(smap)                     # Shamela's own section order (mapping file follows category_order)
for r in rows:
    if r['category'] not in order: order.append(r['category'])
order = [c for c in order if any(r['category'] == c for r in rows)]
wq = {}
for w in csv.DictReader(open(J('data/compare/waqfeya-matches.tsv')), delimiter='\t'):
    k = title_key(w['name'])
    if k and (k not in wq or int(w['visits'] or 0) > int(wq[k]['visits'] or 0)): wq[k] = w
waq_of = lambda r: wq.get(title_key(r['title']))
total = len(rows); present = [r for r in rows if r['phone_book_ids']]
matched_phone = {int(i) for r in present for i in r['phone_book_ids'].split()}
not_in_shamela = [b for b in cat['books'] if b['id'] not in matched_phone]

R = Report('مقارنة المكتبة بالمكتبة الشاملة',
           f'الشاملة المثبتة على الحاسوب ({total:,} كتابًا في {len(order)} قسمًا) مقابل كتب PDF على الهاتف (نحو {cat["stats"]["titles"]:,} عنوانًا في {cat["stats"]["files"]:,} ملفًا)')
same = {r['shamela_id']: max((SC.same_edition(CARDS.get(int(r['shamela_id'])), books[int(i)]['folder']) for i in r['phone_book_ids'].split()),
                             key=['', 'other', 'publisher', 'same'].index) for r in present}
R.kpis([('كتب الشاملة', f'{total:,}'), ('لها نسخة PDF على الهاتف', f'{len(present):,}'), ('نسبة التغطية', pct(len(present), total)),
        ('منها بطبعة الشاملة نفسها', f"{sum(1 for v in same.values() if v == 'same'):,}"),
        ('كتب الهاتف غير الموجودة في الشاملة', f'{len(not_in_shamela):,}')])
R.note('يُعدّ الكتاب موجودًا إذا كان العمل نفسه على الهاتف، بأي طبعة (2026-10-08). الأدلة، وكلها مع اتفاق المؤلف: العنوان بعد توحيد الرسم، '
       'أو كلماته المميِّزة كلها؛ أو عنوانه المطبوع واسم مؤلفه الكامل من بطاقة الكتاب في الشاملة المثبتة على الحاسوب؛ '
       'أو أنه مطبوع داخل مجموع أو مع كتاب آخر على الهاتف («ويليه»، «ضمن آثار المعلمي»). '
       'ولا يُعدّ موجودًا ما كان مختصرًا لكتاب على الهاتف أو شرحًا له أو منتقًى منه أو جزءًا آخر منه أو رواية أخرى له. '
       '«طبعة الشاملة» من بطاقة الكتاب فيها، و«الطبعة على الهاتف» تقارن محققها وناشرها باسم الملف على الهاتف. '
       'الشاملة نصوص مدخلة، والهاتف كتب مصوّرة؛ فالمقارنة تبيّن أي نصوص الشاملة لها أصل مصوّر عندك.')

R.h2('التغطية حسب أقسام الشاملة', 'cats')
trs = []
for c in order:
    rs = [r for r in rows if r['category'] == c]; p = sum(1 for r in rs if r['phone_book_ids'])
    trs.append([c, smap.get(c) or '— لا مقابل', len(rs), p, pct(p, len(rs))])
R.table(['قسم الشاملة', 'القسم المقابل على الهاتف', 'كتب الشاملة', 'على الهاتف', 'النسبة'], trs, numeric=(2, 3, 4))

R.h2('التغطية حسب قرن وفاة المؤلف', 'era')
by_c = defaultdict(lambda: [0, 0])
for r in rows:
    d = int(r['death']) if r['death'].isdigit() and 0 < int(r['death']) < 1500 else None
    k = f'القرن {(d - 1) // 100 + 1}' if d else 'غير محدد / معاصر'
    by_c[k][0] += 1; by_c[k][1] += 1 if r['phone_book_ids'] else 0
keys = sorted([k for k in by_c if k.startswith('القرن')], key=lambda k: int(k.split()[1])) + ['غير محدد / معاصر']
R.table(['القرن الهجري', 'كتب الشاملة', 'على الهاتف', 'النسبة'], [[k, *by_c[k], pct(by_c[k][1], by_c[k][0])] for k in keys if k in by_c], numeric=(1, 2, 3))
early = [r for r in rows if r['death'].isdigit() and 0 < int(r['death']) <= 700]
R.p(f'كتب المتقدمين (وفاة المؤلف حتى 700هـ): {len(early):,} في الشاملة، منها {sum(1 for r in early if r["phone_book_ids"]):,} على الهاتف ({pct(sum(1 for r in early if r["phone_book_ids"]), len(early))}).')

early_missing = [r for r in early if not r['phone_book_ids']]
early_missing.sort(key=lambda r: (int(r['death']) if r['death'].isdigit() and int(r['death']) > 0 else 9999, r['title']))
R.h2(f'نواقص ما قبل 700 هـ من الشاملة ({len(early_missing):,} كتابًا مفقودًا)', 'missing-pre700')
R.p('كتب التراث المتقدمة في الشاملة حتى سنة 700 هـ التي ليس لها مقابل مصور على الهاتف حتى الآن، مرتبة بسنة وفاة المؤلف.')
R.table(['#', 'الكتاب', 'المؤلف', 'الوفاة', 'قسم الشاملة', 'طبعة الشاملة', 'في الوقفية'],
        [[i, r['title'], r['author'], r['death'] or '', r['category'], ed(r), 'نعم' if waq_of(r) else ''] for i, r in enumerate(early_missing, 1)],
        numeric=(0, 3), links={6: [waq_of(r)['url'] if waq_of(r) else None for r in early_missing]},
        fold=f'نواقص الشاملة حتى 700 هـ ({len(early_missing):,} كتابًا)', md_limit=50,
        pick=[(f"s:{r['shamela_id']}", r['title']) for r in early_missing])

R.h2('كتب على الهاتف ليست في الشاملة', 'extra')
R.p('عناوين لم يُعثر لها على مقابل في الشاملة: غالبها كتب معاصرة ودوريات وسلاسل، أو طبعات عناوينها مختلفة عن عنوان الشاملة.')
cc = Counter(b['cat'] for b in not_in_shamela); tc = Counter(b['cat'] for b in cat['books'])
R.table(['قسم الهاتف', 'كتب القسم', 'ليست في الشاملة', 'النسبة'], [[c, tc[c], n, pct(n, tc[c])] for c, n in sorted(cc.items(), key=lambda x: -x[1])], numeric=(1, 2, 3))

R.h2('تفصيل: كتب الشاملة غير الموجودة على الهاتف', 'missing')
R.p('مرتبة داخل كل قسم بسنة وفاة المؤلف (الأقدم أولًا). «في الوقفية» يعني أن له نسخة مصوّرة (PDF) في الوقفية بالعنوان نفسه، فيمكن تحميله؛ وما ليس في الوقفية قد يوجد مصوّرًا في مكان آخر. القائمة الكاملة في data/shamela-matches.tsv.')
for c in order:
    miss = [r for r in rows if r['category'] == c and not r['phone_book_ids']]
    if not miss: continue
    miss.sort(key=lambda r: (int(r['death']) if r['death'].isdigit() and int(r['death']) > 0 else 9999, r['title']))
    R.table(['#', 'الكتاب', 'المؤلف', 'الوفاة', 'طبعة الشاملة', 'في الوقفية'], [[i, r['title'], r['author'], r['death'] or '', ed(r), 'نعم' if waq_of(r) else ''] for i, r in enumerate(miss, 1)],
            numeric=(0, 3), links={5: [waq_of(r)['url'] if waq_of(r) else None for r in miss]},
            fold=f'{c} — {len(miss):,} غير موجود من {sum(1 for r in rows if r["category"] == c):,} (منها {sum(1 for r in miss if waq_of(r)):,} في الوقفية)', md_limit=40,
            pick=[(f"s:{r['shamela_id']}", r['title']) for r in miss])

R.h2('تفصيل: كتب الشاملة الموجودة على الهاتف', 'present')
R.p('«وجه المطابقة» دليل الحكم بوجوده، و«الطبعة على الهاتف» تقول هل النسخة المصوّرة عندك هي طبعة الشاملة نفسها (بمحققها أو ناشرها).')
R.table(['الكتاب', 'المؤلف', 'قسم الشاملة', 'طبعة الشاملة', 'مكانه على الهاتف', 'الطبعة على الهاتف', 'وجه المطابقة'],
        [[r['title'], r['author'], r['category'], ed(r), ' | '.join(books[int(i)]['cat'] + ' / ' + books[int(i)]['folder'] for i in r['phone_book_ids'].split()[:2]),
          SC.SAME[same[r['shamela_id']]], SC.how_ar(r['match'])] for r in sorted(present, key=lambda r: (order.index(r['category']), r['title']))],
        fold=f'{len(present):,} كتابًا', md_limit=60)
print(R.write('01 - مقارنة بالشاملة'))
