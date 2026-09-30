"""Report 03: expansion recommendations (run compare_shamela.py + compare_waqfeya.py first)."""
import csv, json, os, re, sys
from collections import defaultdict, Counter
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from report_lib import Report, pct
from textnorm import title_key, author_tokens, norm
J = lambda p: os.path.join(ROOT, p)

cat = json.load(open(J('data/catalog.json')))
W = list(csv.DictReader(open(J('data/compare/waqfeya-matches.tsv')), delimiter='\t'))
for r in W:
    for k in ('visits', 'volumes', 'volumes_on_phone'): r[k] = int(r[k] or 0)
    for k in ('size_mb', 'missing_mb'): r[k] = float(r[k] or 0)
S = list(csv.DictReader(open(J('data/compare/shamela-matches.tsv')), delimiter='\t'))
shamela_keys = {title_key(r['title']) for r in S}
scope = [r for r in W if r['phone_category']]

# Core reference works (a starting checklist; edit freely). (discipline, title, author hint)
CORE = [
 ('التفسير', 'جامع البيان عن تأويل آي القرآن', 'الطبري'), ('التفسير', 'تفسير القرآن العظيم', 'كثير'), ('التفسير', 'الجامع لأحكام القرآن', 'القرطبي'),
 ('التفسير', 'التحرير والتنوير|تفسير التحرير والتنوير', 'عاشور'), ('التفسير', 'المحرر الوجيز', 'عطية'), ('التفسير', 'أضواء البيان', 'الشنقيطي'), ('التفسير', 'الكشاف', 'الزمخشري'),
 ('علوم القرآن', 'الإتقان في علوم القرآن', 'السيوطي'), ('علوم القرآن', 'البرهان في علوم القرآن', 'الزركشي'), ('علوم القرآن', 'النشر في القراءات العشر', 'الجزري'),
 ('متون الحديث', 'صحيح البخاري|الجامع المسند الصحيح المختصر', ''), ('متون الحديث', 'صحيح مسلم|المسند الصحيح المختصر', 'مسلم'), ('متون الحديث', 'سنن أبي داود', ''), ('متون الحديث', 'سنن الترمذي|الجامع الكبير|الجامع الصحيح', 'الترمذي'),
 ('متون الحديث', 'سنن النسائي', ''), ('متون الحديث', 'سنن ابن ماجه', ''), ('متون الحديث', 'الموطأ|موطأ|موطأ الإمام مالك', 'مالك'), ('متون الحديث', 'المسند', 'حنبل'),
 ('متون الحديث', 'المصنف', 'الرزاق'), ('متون الحديث', 'المصنف', 'شيبة'), ('متون الحديث', 'السنن الكبرى', 'البيهقي'),
 ('شروح الحديث', 'فتح الباري', 'حجر'), ('شروح الحديث', 'المنهاج شرح صحيح مسلم', 'النووي'), ('شروح الحديث', 'التمهيد لما في الموطأ', 'البر'),
 ('شروح الحديث', 'الاستذكار', 'البر'), ('شروح الحديث', 'إكمال المعلم', 'عياض'), ('شروح الحديث', 'المنتقى شرح الموطأ|المنتقى شرح موطأ|المنتقى', 'الباجي'),
 ('علوم الحديث', 'مقدمة ابن الصلاح', ''), ('علوم الحديث', 'تدريب الراوي', 'السيوطي'), ('علوم الحديث', 'فتح المغيث', 'السخاوي'),
 ('الرجال', 'تهذيب الكمال', 'المزي'), ('الرجال', 'تهذيب التهذيب', 'حجر'), ('الرجال', 'ميزان الاعتدال', 'الذهبي'), ('الرجال', 'سير أعلام النبلاء', 'الذهبي'),
 ('أصول الفقه', 'الرسالة', 'الشافعي'), ('أصول الفقه', 'المستصفى', 'الغزالي'), ('أصول الفقه', 'الموافقات', 'الشاطبي'), ('أصول الفقه', 'البحر المحيط في أصول الفقه', 'الزركشي'),
 ('الفقه المالكي', 'المدونة', ''), ('الفقه المالكي', 'الرسالة', 'زيد'), ('الفقه المالكي', 'مختصر خليل|مختصر العلامة خليل|مختصر الشيخ خليل', ''), ('الفقه المالكي', 'مواهب الجليل', 'الحطاب'),
 ('الفقه المالكي', 'الخرشي على مختصر|شرح الخرشي|شرح مختصر خليل', 'الخرشي'), ('الفقه المالكي', 'حاشية الدسوقي', 'الدسوقي'), ('الفقه المالكي', 'الذخيرة', 'القرافي'),
 ('الفقه المالكي', 'البيان والتحصيل', 'رشد'), ('الفقه المالكي', 'النوادر والزيادات', 'زيد'), ('الفقه المالكي', 'المعيار المعرب', 'الونشريسي'),
 ('الفقه الحنفي', 'المبسوط', 'السرخسي'), ('الفقه الحنفي', 'بدائع الصنائع', 'الكاساني'), ('الفقه الحنفي', 'رد المحتار', 'عابدين'),
 ('الفقه الشافعي', 'الأم', 'الشافعي'), ('الفقه الشافعي', 'المجموع شرح المهذب', 'النووي'), ('الفقه الشافعي', 'روضة الطالبين', 'النووي'), ('الفقه الشافعي', 'نهاية المحتاج', 'الرملي'),
 ('الفقه الحنبلي', 'المغني', 'قدامة'), ('الفقه الحنبلي', 'كشاف القناع', 'البهوتي'), ('الفقه الحنبلي', 'الإنصاف', 'المرداوي'),
 ('الفقه المقارن', 'المحلى', 'حزم'), ('الفقه المقارن', 'بداية المجتهد', 'رشد'),
 ('السيرة', 'السيرة النبوية', 'هشام'), ('السيرة', 'زاد المعاد', 'القيم'), ('السيرة', 'الشفا بتعريف حقوق المصطفى', 'عياض'),
 ('التاريخ', 'تاريخ الرسل والملوك', 'الطبري'), ('التاريخ', 'البداية والنهاية', 'كثير'), ('التاريخ', 'الكامل في التاريخ', 'الأثير'),
 ('التاريخ', 'تاريخ ابن خلدون', ''), ('التاريخ', 'نفح الطيب', 'المقري'), ('التاريخ', 'الاستقصا لأخبار دول المغرب الأقصى', 'الناصري'),
 ('اللغة', 'لسان العرب', ''), ('اللغة', 'القاموس المحيط', ''), ('اللغة', 'تاج العروس', 'الزبيدي'), ('اللغة', 'الكتاب', 'سيبويه'),
 ('اللغة', 'مغني اللبيب', 'هشام'), ('اللغة', 'شرح ابن عقيل', ''),
 ('الأدب', 'الكامل في اللغة والأدب', 'المبرد'), ('الأدب', 'البيان والتبيين', 'الجاحظ'), ('الأدب', 'الأغاني', 'الأصفهاني'), ('الأدب', 'العقد الفريد', 'ربه'),
 ('الرقائق', 'إحياء علوم الدين', 'الغزالي'), ('الرقائق', 'رياض الصالحين', 'النووي'), ('الرقائق', 'الأذكار', 'النووي'), ('الرقائق', 'مدارج السالكين', 'القيم'),
]

def auth_ok(hint, *texts):
    if not hint: return True
    h = norm(hint).removeprefix('ال')
    return any(h in norm(t) for t in texts)

def on_phone(title, hint):
    for t in title.split('|'):
        b = _on_phone(t, hint)
        if b: return b
    return None

def _on_phone(title, hint):
    k = title_key(title)
    for b in cat['books']:
        bk = title_key(b['title']); wk = {title_key(w['name']) for w in b.get('waqfeya', [])}
        if any(x == k or x.startswith(k + ' ') for x in {bk} | wk) and auth_ok(hint, b['folder'], b.get('author', ''), ' '.join(w['name'] for w in b.get('waqfeya', []))):
            return b
    return None

def best_waqfeya(title, hint):
    c = [x for t in title.split('|') for x in _best(t, hint)]
    return max(c, key=lambda r: r['visits']) if c else None

def _best(title, hint):
    k = title_key(title)
    return [r for r in W if (title_key(r['name']) == k or title_key(r['name']).startswith(k + ' ')) and auth_ok(hint, r['author'], r['name'])]

R = Report('توصيات لتوسعة المكتبة', 'مبنية على المقارنة بالشاملة والوقفية وعلى حالة ملفات الهاتف')
part = sorted([r for r in scope if r['status'] == 'partial'], key=lambda r: (-(r['visits']), -r['volumes']))
core_rows = []
for d, t, h in CORE:
    b = on_phone(t, h)
    if b: core_rows.append([d, t.split('|')[0], 'موجود', f"{b['cat']} / {b['folder']}", '', '', None]); continue
    w = best_waqfeya(t, h)
    core_rows.append([d, t.split('|')[0], 'غير موجود', w['name'] if w else '— لم يوجد في الوقفية', round(w['size_mb']) if w else '', w['url'] if w else '', (f"w:{w['waqfeya_id']}", w['name']) if w else None])
core_missing = [r for r in core_rows if r[2] != 'موجود']
# classical works: missing on phone, present in Waqfeya and Shamela, early authors
def century_n(c):
    m = re.search(r'(\d+)', c or ''); return int(m.group(1)) if m else 99
classics = [r for r in scope if r['status'] == 'missing' and title_key(r['name']) in shamela_keys and century_n(r['century']) <= 9]
classics.sort(key=lambda r: -r['visits'])
local = [l.rstrip('\n').split('\t') for l in open(J('data/phone/local-Books.tsv'))] if os.path.exists(J('data/phone/local-Books.tsv')) else []
phone_sizes = {f[1] for b in cat['books'] for f in b['files']}
local_new = [(int(s), p) for s, p in local if p.lower().endswith('.pdf') and int(s) not in phone_sizes]

R.kpis([('كتب ناقصة المجلدات', f'{len(part):,}'), ('حجم إكمالها', f'{sum(r["missing_mb"] for r in part) / 1024:,.1f} GB'),
        ('من قائمة الأمهات: غير موجود', f'{len(core_missing)} من {len(core_rows)}'),
        ('كتب المتقدمين المقترحة', f'{len(classics):,}'), ('ملفات على الحاسوب ليست في الهاتف', f'{len(local_new)}')])

R.h2('1. أولًا: إتمام ما بدأ', 'finish')
R.ul(['تم: حذف 841 نسخة مكررة (8 GB) بعد التحقق من تطابقها، وتصحيح أسماء نحو 5,500 ملف، ونقل 238 كتابًا إلى أقسامها الصحيحة (انظر «04 - سجل التغييرات»).',
      'مراجعة البنود المتبقية في «04 - سجل التغييرات» (قسم: يحتاج مراجعة) — أسماء لم يكفِ الدليل لتصحيحها آليًا.',
      'إكمال الكتب الناقصة (البند 2) قبل إضافة عناوين جديدة: كتاب ناقص الأجزاء أقل نفعًا من كتاب واحد كامل.'])

R.h2(f'2. إكمال الكتب الناقصة ({len(part):,})', 'partial')
R.p('مرتبة بشهرة الكتاب في الوقفية. التحميل من صفحة الكتاب في الوقفية (أو من archive.org مباشرة)، ثم وضع المجلدات في مجلد الكتاب نفسه بالترقيم المعتمد (انظر AGENTS.md).')
R.table(['الكتاب', 'قسم الهاتف', 'على الهاتف', 'المجلدات', 'الناقص (MB)', 'مكانه'],
        [[r['name'], r['phone_category'], r['volumes_on_phone'], r['volumes'], round(r['missing_mb']), r['phone_folders'].split(' | ')[0].split('/', 1)[-1]] for r in part],
        numeric=(2, 3, 4), links={0: [r['url'] for r in part]}, md_limit=50, pick=[(f"w:{r['waqfeya_id']}", r['name'] + ' (إكمال)') for r in part])

R.h2('3. قائمة الأمهات والمراجع الأساسية', 'core')
R.p('قائمة مقترحة قابلة للتعديل (في scripts/report_recommend.py → CORE). «غير موجود» يعني أنه لم يُعثر على عنوانه في المكتبة؛ والرابط لأشهر طبعة له في الوقفية.')
R.table(['الفن', 'الكتاب', 'الحالة', 'على الهاتف / المقترح من الوقفية', 'MB'],
        [r[:5] for r in core_rows], numeric=(4,), links={3: [r[5] or None for r in core_rows]}, pick=[r[6] for r in core_rows])

R.h2(f'4. كتب المتقدمين الناقصة (حتى القرن 9هـ، موجودة في الشاملة والوقفية) — {len(classics):,}', 'classics')
R.p(f'الحجم الكلي نحو {sum(r["size_mb"] for r in classics) / 1024:,.0f} GB. مقسمة على أقسام الهاتف، الأشهر أولًا.')
by = defaultdict(list)
for r in classics: by[r['phone_category']].append(r)
for c in sorted(by, key=lambda c: -len(by[c])):
    xs = by[c]
    R.table(['#', 'الكتاب', 'المؤلف', 'القرن', 'مج', 'MB', 'زيارات'],
            [[i, r['name'], r['author'].split('؛')[0], r['century'].replace('القرن ', ''), r['volumes'], round(r['size_mb']), r['visits']] for i, r in enumerate(xs, 1)],
            numeric=(0, 4, 5, 6), links={1: [r['url'] for r in xs]}, fold=f'{c} — {len(xs):,} كتابًا، {sum(r["size_mb"] for r in xs) / 1024:,.1f} GB', md_limit=15,
            pick=[(f"w:{r['waqfeya_id']}", r['name']) for r in xs])

absent = json.load(open(J('data/phone/absent-books.json'))) if os.path.exists(J('data/phone/absent-books.json')) else []
if absent:
    R.h2(f'4ب. كتب لم تكن على الهاتف إلا صفحات ويب ({len(absent)})', 'absent')
    R.p('كانت ملفاتها صفحات ويب محفوظة باسم .pdf (من الشاملة أو الرق المنشور أو archive.org) فحُذفت، ولم يوجد لها في الوقفية بديل مطابق بلا لبس. إن أردتها فابحث عنها بعنوانها.')
    R.table(['القسم', 'الكتاب'], [[a.split('/')[0], a.split('/', 1)[1]] for a in absent], fold=f'{len(absent)} كتابًا')

R.h2('5. بنية الأقسام', 'structure')
tiny = [c for c in cat['categories'] if c['books'] <= 6]
R.ul([f'أقسام صغيرة جدًا: ' + '، '.join(f'«{c["name"]}» ({c["books"]} كتب)' for c in tiny) + ' — يُقترح نقل كتبها إلى الأقسام الموضوعية (مثل «الإتقان في علوم القرآن» إلى علوم القرآن) أو إبقاؤها إن كانت نواة لقسم ستتوسع فيه.',
      'أقسام في الشاملة لا مقابل لها على الهاتف: المنطق، الطب، الجوامع، فهارس الكتب والأدلة، كتب عامة، علوم أخرى. يُنشأ قسم لها عند الحاجة فقط.',
      'في الوقفية أقسام واسعة تُصنَّف الآن داخل أقسام أعم على الهاتف: الفتاوى، السياسة الشرعية، الفرائض (داخل «الفقه المقارن والعام»)، الأنساب (داخل «التراجم»)، الفرق والردود (داخل «العقيدة»). إن كبرت هذه المجموعات فالأنفع فصلها في أقسام مستقلة.',
      '«كتب ابن تيمية وابن القيم» قسم بحسب المؤلف لا الموضوع؛ يحسن الإبقاء عليه لأنه متعارف، مع تذكّر أن كتبهما قد تظهر أيضًا في أقسامها الموضوعية.'])

R.h2(f'6. ملفات على الحاسوب ليست على الهاتف ({len(local_new)})', 'local')
R.p('في مجلد ~/Books على الحاسوب (نسخة قديمة جزئية من المكتبة). يمكن رفعها إلى الهاتف بعد تسميتها وفق القواعد.')
R.table(['الملف', 'MB'], [[p, round(s / 2**20)] for s, p in sorted(local_new, key=lambda x: x[1])], numeric=(1,), fold=f'{len(local_new)} ملفًا — {sum(s for s, _ in local_new) / 2**30:.1f} GB')

R.h2('7. طريقة التوسعة بالذكاء الاصطناعي بكفاءة', 'howto')
R.ul(['ابدأ كل جلسة بقراءة AGENTS.md في هذا المجلد: فيه مكان كل شيء وقواعد التسمية وطريقة الاتصال بالهاتف.',
      'catalog.json / catalog.tsv: فهرس المكتبة كاملًا (القسم، المجلد، العنوان، المؤلف، الطبعة، الملفات بأحجامها، مصدر الوقفية/الأرشيف).',
      'waqfeya-matches.tsv و shamela-matches.tsv: حالة كل كتاب في الوقفية والشاملة (موجود/ناقص/غير موجود) مع الروابط والأحجام — تكفي لاختيار الكتب دون تصفح المواقع.',
      'قبل الإضافة: تحقّق من عدم وجود الكتاب بالعنوان المطبّع وبالحجم الدقيق؛ بعد الإضافة: أعد الفهرسة وبناء الفهارس (الخطوات في AGENTS.md).',
      'كل نقل أو تسمية يمر عبر ملف خطة ويُسجَّل في سجل التغييرات، ويمكن التراجع عنه.'])
print(R.write('03 - توصيات التوسعة'))
