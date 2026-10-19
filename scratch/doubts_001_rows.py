"""One-off: the rows of data/review/doubts-001.tsv (owner 2026-10-20: «أرني ما بقي مشكلا في المتصفح»; «وأريد مراجعة مسألة
الطبري بيدي»): books named without a title page, the الطبري set, and the 141 files plan 331 named from Waqfeya labels.
Page images: data/inspect/pages (found through the change log, or rendered by front_pages.py), the الطبري ones rendered
from local copies (scratchpad, given as argv[1])."""
import csv, glob, hashlib, json, os, re, sys, unicodedata
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
TIMG, DHU = sys.argv[1], sys.argv[2]
N = lambda s: unicodedata.normalize('NFC', s)
idx = {N(l.split('\t')[0]): (l.split('\t')[0], l.rstrip('\n').split('\t')[1]) for l in open('data/phone/index-now.tsv', encoding='utf-8')}
mv, rev = {}, {}
for r in csv.reader(open('data/changes/changes.tsv', encoding='utf-8'), delimiter='\t'):
    if len(r) > 3 and r[1] == 'move':
        a, b = N(r[2].removeprefix('Books/')), N(r[3].removeprefix('Books/')); mv[a] = b; rev.setdefault(b, []).append(a)
def cur(p):
    p = N(p); s = 0
    while p in mv and s < 60: p = mv[p]; s += 1
    return p
keys = {}
for l in open('data/inspect/files.jsonl'):
    try: d = json.loads(l)
    except ValueError: continue
    if d.get('key'): keys.setdefault(N(d['path']), []).append(d['key'])
def images(p):
    raw, size = idx[p]
    ks = [hashlib.md5(f'{raw}\t{size}'.encode()).hexdigest()[:16]]
    todo, seen = [p], {p}
    while todo:
        x = todo.pop(); ks += keys.get(x, [])
        for a in rev.get(x, []):
            if a not in seen: seen.add(a); todo.append(a)
    for k in ks:
        fs = sorted(glob.glob(f'data/inspect/pages/{k}-*.jpg'), key=lambda f: int(re.search(r'-(\d+)\.jpg$', f).group(1)))
        if fs: return ','.join(fs[:3])
    return ''

out = ['#S\tA\tكتب سُمّيت بلا صفحة عنوان فيها (الاسم من مصدر آخر)', '#S\tB\tتاريخ الطبري: المجموعة بعد إصلاحها (لمراجعتك بيدك)',
       '#S\tC\tالخطة 331: ملفات سُمّيت من وسم الوقفية لا من صفحة عنوانها']
A = [('أصول الفقه/شرح الفصول في علم الجدل - برهان الدين النسفي - ت شريفة بنت علي بن سليمان الحوشاني - جامعة الملك سعود.pdf',
      'لا صفحة عنوان في الملف (يبدأ بدراسة المحققة)؛ المحققة والناشر من سجل الوقفية الذي نُزّل منه الملف'),
     ('البلاغة/الجامع الكبير في صناعة المنظوم من الكلام والمنثور - ضياء الدين ابن الأثير - مطبعة المجمع العلمي.pdf',
      'لا صفحة عنوان (يبدأ بالنص وينتهي بجدول الخطأ والصواب)؛ المطبعة من سجل الوقفية'),
     ('الشعر ودواوينه/ديوان الأمير شكيب أرسلان - مطبعة المنار مصر.pdf', 'لا صفحة عنوان (يبدأ بمقدمة الشاعر)؛ الناشر من سجل الوقفية'),
     ('الفقه الحنبلي/تيسير فقه العمدة في الفقه الحنبلي - محمد بن حامد الديماني.pdf',
      'يبدأ الملف من الصفحة 5 بلا صفحة عنوان؛ العنوان من اسم المجلد القديم، والناظم من تقريظ محمد سالم بن عبد الودود'),
     ('فهارس الكتب والأدلة/معجم المؤلفات الأصولية المالكية المبثوثة في كشف الظنون وإيضاح المكنون وهدية العارفين - ترحيب بن ربيعان الدوسري.pdf',
      '27 صفحة بلا صفحة إصدار: قد يكون بحثا مستلا من مجلة، واسمه لا يقول ذلك')]
for p, why in A: out.append(f'A\t{p}\t{why}\t{images(N(p))}')
TF = N('التاريخ/تاريخ الطبري تاريخ الرسل والملوك - ابن جرير الطبري - ت محمد أبو الفضل إبراهيم - دار المعارف بمصر/')
for p in sorted(x for x in idx if x.startswith(TF)):
    fn = p[len(TF):]
    if fn.startswith('11 - '):
        why, im = 'المجلد الحادي عشر من دار المعارف نفسها: «ذيول تاريخ الطبري» (الصلة لعريب، التكملة للهمذاني، المنتخب من ذيل المذيل) — جُلب اليوم مكان نسخة سويدان', ','.join(sorted(glob.glob(f'{DHU}/c-*.png'))[:3])
    elif fn.endswith('الواجهة.pdf'): why, im = 'الواجهة: ذخائر العرب 30، الطبعة الثانية، دار المعارف بمصر', ','.join(sorted(glob.glob(f'{TIMG}/t00w-*.jpg')))
    elif fn.endswith('المقدمة.pdf'): why, im = 'مقدمة التحقيق مع صفحة عنوان الجزء الأول', ','.join(sorted(glob.glob(f'{TIMG}/t00m-*.jpg')))
    else: why, im = f'الجزء {int(fn[:2])}: غلافه ذخائر العرب 30، دار المعارف بمصر', ','.join(sorted(glob.glob(f'{TIMG}/t{fn[:2]}-*.jpg')))
    out.append(f'B\t{idx[p][0]}\t{why}\t{im}')
SW = [x for x in idx if x.startswith(N('نسخ مستبعدة/التاريخ/تاريخ الطبري'))]
for p in SW: out.append(f'B\t{idx[p][0]}\tنسخة دار سويدان بيروت من المجلد 11 («روائع التراث العربي — تاريخ الأمم والملوك — الجزء الحادي عشر»): وُضعت جانبا؛ قل «احذف» أو «أبق»\t{",".join(sorted(glob.glob(f"{TIMG}/t11-*.jpg")))}')
for l in open('plans/331-raw-archive-names.tsv', encoding='utf-8'):
    a, b, why = l.rstrip('\n').split('\t')[:3]
    p = cur(b.removeprefix('Books/'))
    if p not in idx: continue
    m = re.search(r'Waqfeya label «([^»]*)»', why)
    note = f'الاسم من وسم الوقفية «{m.group(1)}» لهذا الملف: أصفحاته هي ما يقوله الاسم؟' if m else 'الاسم من نمط أسماء الملفات في المادة (لم يوجد وسم في الوقفية)'
    out.append(f'C\t{idx[p][0]}\t{note}\t{images(p)}')
open('data/review/doubts-001.tsv', 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print(sum(1 for x in out if not x.startswith('#')), 'rows;', sum(1 for x in out if not x.startswith('#') and not x.split('\t')[3]), 'without images')
