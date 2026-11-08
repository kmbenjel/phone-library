"""Report 02: the phone library vs the whole Waqfeya catalog (run compare_waqfeya.py first)."""
import csv, json, os, re, sys
from collections import defaultdict, Counter
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from report_lib import Report, pct
J = lambda p: os.path.join(ROOT, p)

cat = json.load(open(J('data/catalog.json')))
rows = list(csv.DictReader(open(J('data/compare/waqfeya-matches.tsv')), delimiter='\t'))
for r in rows:
    for k in ('visits', 'volumes', 'volumes_on_phone'): r[k] = int(r[k] or 0)
    for k in ('size_mb', 'missing_mb'): r[k] = float(r[k] or 0)
scope = [r for r in rows if r['phone_category']]
st = Counter(r['status'] for r in scope)
on = lambda r: r['status'] in ('complete', 'partial', 'other-copy')
from_waqfeya = {(b['cat'], b['folder']) for b in cat['books'] if b.get('waqfeya')}
other_src = [b for b in cat['books'] if not b.get('waqfeya')]
url = lambda r: r['url']

R = Report('مقارنة المكتبة بالمكتبة الوقفية',
           f'فهرس الوقفية كاملًا ({len(rows):,} مادة في {len({r["waqfeya_category"] for r in rows})} قسمًا) مقابل الهاتف (نحو {cat["stats"]["titles"]:,} عنوانًا في {cat["stats"]["files"]:,} ملفًا)')
R.kpis([('مواد الوقفية', f'{len(rows):,}'), ('ضمن أقسام مكتبتك', f'{len(scope):,}'),
        ('كاملة على الهاتف', f'{st["complete"]:,}'), ('ناقصة بعض المجلدات', f'{st["partial"]:,}'),
        ('نسخة أخرى على الهاتف', f'{st["other-copy"]:,}'), ('غير موجودة', f'{st["missing"]:,}'),
        ('نسبة التغطية', pct(st['complete'] + st['partial'] + st['other-copy'], len(scope))),
        ('حجم الناقص كله', f'{sum(r["missing_mb"] for r in scope) / 1024:,.0f} GB')])
R.note('الطريقة: كل ملف على الهاتف طوبق بحجمه الدقيق بالبايت مع ملفات أرشيف archive.org التي تحيل إليها الوقفية؛ '
       'فـ«كاملة» و«ناقصة» حكمان يقينيان على الملفات نفسها (المجلدات الأصلية دون ملف الواجهة والمقدمة). '
       '«نسخة أخرى» تعني أن على الهاتف كتابًا بالعنوان نفسه من مصدر آخر أو طبعة أخرى. '
       '«ضمن أقسام مكتبتك» يستبعد أقسام الوقفية التي لا مقابل لها عندك (اللغات الأجنبية، الصوتيات، البرامج، الأخبار، علوم الحاسب…).')

R.h2('التغطية حسب أقسام الهاتف', 'phone-cats')
by = defaultdict(Counter)
for r in scope: by[r['phone_category']][r['status']] += 1
trs = []
for c in sorted(by, key=lambda c: -sum(by[c].values())):
    t = sum(by[c].values()); o = by[c]['complete'] + by[c]['partial'] + by[c]['other-copy']
    trs.append([c, t, by[c]['complete'], by[c]['partial'], by[c]['other-copy'], by[c]['missing'], pct(o, t)])
R.table(['قسم الهاتف', 'في الوقفية', 'كاملة', 'ناقصة', 'نسخة أخرى', 'غير موجودة', 'التغطية'], trs, numeric=(1, 2, 3, 4, 5, 6))

R.h2('التغطية حسب أقسام الوقفية (كلها)', 'waq-cats')
byw = defaultdict(Counter); pc = {}
for r in rows: byw[r['waqfeya_category']][r['status']] += 1; pc[r['waqfeya_category']] = r['phone_category']
trs = []
for c in sorted(byw, key=lambda c: -sum(byw[c].values())):
    t = sum(byw[c].values()); o = byw[c]['complete'] + byw[c]['partial'] + byw[c]['other-copy']
    trs.append([c, pc[c] or '— خارج النطاق', t, o, pct(o, t)])
R.table(['قسم الوقفية', 'يقابله على الهاتف', 'المواد', 'على الهاتف', 'النسبة'], trs, numeric=(2, 3, 4),
        fold=f'{len(byw)} قسمًا', md_limit=None)

R.h2('التغطية حسب القرن (قرن المؤلف في الوقفية)', 'century')
byc = defaultdict(Counter)
for r in scope: byc[r['century'] or 'غير مذكور'][on(r)] += 1
def ck(k):
    m = re.search(r'(\d+)', k); return (0, int(m.group(1))) if m else (1, k)
R.table(['القرن', 'في الوقفية', 'على الهاتف', 'النسبة'], [[k, sum(v.values()), v[True], pct(v[True], sum(v.values()))] for k, v in sorted(byc.items(), key=lambda x: ck(x[0]))], numeric=(1, 2, 3))

part = sorted([r for r in scope if r['status'] == 'partial'], key=lambda r: (-(r['volumes'] - r['volumes_on_phone']), -r['visits']))
R.h2(f'كتب ناقصة المجلدات على الهاتف ({len(part):,})', 'partial')
R.p(f'إكمالها يحتاج نحو {sum(r["missing_mb"] for r in part) / 1024:,.1f} GB. الرابط يفتح صفحة الكتاب في الوقفية.')
R.table(['الكتاب', 'المؤلف', 'قسم الهاتف', 'على الهاتف', 'المجلدات', 'الناقص (MB)', 'مكانه'],
        [[r['name'], r['author'].split('؛')[0], r['phone_category'], r['volumes_on_phone'], r['volumes'], round(r['missing_mb']), r['phone_folders'].split(' | ')[0].split('/', 1)[-1]] for r in part],
        numeric=(3, 4, 5), links={0: [r['url'] for r in part]}, pick=[(f"w:{r['waqfeya_id']}", r['name'] + ' (إكمال)') for r in part])

R.h2(f'كتب الهاتف التي ليست من الوقفية ({len(other_src):,})', 'other-sources')
R.p('كتب لم تُطابق ملفاتها أي ملف في الوقفية: مصدرها رفوع أخرى على archive.org أو مواقع أخرى، أو طبعات بأحجام مختلفة.')
oc = Counter(b['cat'] for b in other_src); tc = Counter(b['cat'] for b in cat['books'])
R.table(['قسم الهاتف', 'كتب القسم', 'ليست من الوقفية', 'النسبة'], [[c, tc[c], n, pct(n, tc[c])] for c, n in oc.most_common()], numeric=(1, 2, 3))

R.h2('تفصيل: كتب الوقفية غير الموجودة، لكل قسم', 'missing')
R.p('مرتبة بعدد الزيارات في الوقفية (الأشهر أولًا). الحجم من ملفات الأرشيف. القائمة الكاملة في data/waqfeya-matches.tsv.')
for c in [t[0] for t in sorted(((c, sum(by[c].values())) for c in by), key=lambda x: -x[1])]:
    miss = sorted([r for r in scope if r['phone_category'] == c and r['status'] == 'missing'], key=lambda r: -r['visits'])
    if not miss: continue
    R.table(['#', 'الكتاب', 'المؤلف', 'القرن', 'مج', 'MB', 'زيارات'],
            [[i, r['name'], r['author'].split('؛')[0], r['century'].replace('القرن ', ''), r['volumes'], round(r['size_mb']), r['visits']] for i, r in enumerate(miss, 1)],
            numeric=(0, 4, 5, 6), links={1: [r['url'] for r in miss]}, fold=f'{c} — {len(miss):,} غير موجود', md_limit=30,
            pick=[(f"w:{r['waqfeya_id']}", r['name']) for r in miss])

R.h2('تفصيل: كتب الوقفية الموجودة على الهاتف', 'present')
pres = sorted([r for r in scope if on(r)], key=lambda r: (r['phone_category'], r['name']))
R.table(['الكتاب', 'الحالة', 'مكانه على الهاتف'],
        [[r['name'], {'complete': 'كاملة', 'partial': f'ناقصة {r["volumes_on_phone"]}/{r["volumes"]}', 'other-copy': 'نسخة أخرى'}[r['status']], r['phone_folders'].split(' | ')[0]] for r in pres],
        links={0: [r['url'] for r in pres]}, fold=f'{len(pres):,} كتابًا', md_limit=60)
print(R.write('02 - مقارنة بالوقفية'))
