"""Report 04: what was changed on the phone (from data/changes/changes.tsv) + what still needs review."""
import csv, os, sys
from collections import Counter, defaultdict
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from report_lib import Report
J = lambda p: os.path.join(ROOT, p)
log = [r for r in csv.reader(open(J('data/changes/changes.tsv')), delimiter='\t') if r and 'test-' not in r[5]]
moves = [r for r in log if r[1] == 'move']
quar = [r for r in moves if r[3].startswith('Books-مكررات/')]
undone = {r[5][5:] for r in log if r[5].startswith('undo-')}
R = Report('سجل التغييرات', 'ما طُبّق على ملفات الهاتف، وما هو مقترح بانتظار الموافقة')
deleted = [r for r in log if r[1] == 'delete']
R.kpis([('عمليات نقل/تسمية', f'{len(moves):,}'), ('نسخ مكررة حُذفت بعد التحقق', f'{len(deleted):,}'),
        ('مجلدات فارغة أزيلت', f'{sum(1 for r in log if r[1] == "rmdir"):,}'), ('خطط مطبقة', f'{len({r[5] for r in log}):,}')])
R.note('المحذوف هو النسخ المكررة فقط، بعد التحقق من تطابقها: الحجم بالبايت نفسه، وتطابق عينات من 64 ك.ب في أول الملف وربعه ونصفه وثلاثة أرباعه وآخره، '
       'ومع بقاء النسخة المطابقة في المكتبة. كل نقل أو تسمية أخرى يمكن التراجع عنها: python3 scripts/apply_plan.py --undo <اسم الخطة>.')
R.h2('الخطط المطبقة')
by = defaultdict(list)
for r in log: by[r[5]].append(r)
R.table(['الخطة', 'التاريخ', 'نقل', 'إزالة مجلد فارغ', 'الأسباب'],
        [[p, rs[0][0], sum(1 for r in rs if r[1] == 'move'), sum(1 for r in rs if r[1] == 'rmdir'),
          '، '.join(f'{k} ({v})' for k, v in Counter(r[4].split(':')[0].split(' «')[0] for r in rs if r[1] == 'move').most_common(4))] for p, rs in by.items()],
        numeric=(2, 3))
import glob
applied = {r[5] for r in log}
pending = [f for f in sorted(glob.glob(J('plans/[0-9][0-9][0-9]-*.tsv'))) if os.path.basename(f)[:-4] not in applied]
if pending:
    R.h2('تغييرات مقترحة بانتظار الموافقة', 'pending')
    R.note('هذه الخطط جاهزة ولم تُطبَّق بعد. بعد الموافقة تُطبَّق بالترتيب، ويُسجَّل كل نقل هنا، ويمكن التراجع عن أي خطة.')
    for f in pending:
        rows = [l.rstrip('\n').split('\t') for l in open(f) if l.strip() and not l.startswith('#')]
        R.h3(f'{os.path.basename(f)[:-4]} — {len(rows):,} عملية')
        R.p('الأسباب: ' + '، '.join(f'{k} ({v:,})' for k, v in Counter(r[2].split(':')[0].split(' «')[0] for r in rows).most_common()))
        R.table(['من', 'إلى', 'السبب'], [[r[0].removeprefix('Books/'), r[1].removeprefix('Books/'), r[2]] for r in rows], fold=f'عرض العمليات ({len(rows):,})', md_limit=40)
import glob as _g
_idx = sorted(_g.glob(J('data/phone/index-2*.tsv')) + [J('data/phone/index-now.tsv')], key=os.path.getmtime)[-1]
sys.path.insert(0, J('scripts'))
from audit_numbering import audit as _audit
_a = _audit(_idx)
R.h2('فحص الترقيم: ما بقي', 'audit')
R.p('يُفحص كل مجلد آليًا بعد كل تعديل. المعدود هنا أخطاء فعلية؛ أما «NN - … (المقدمة)» بجانب المجلد نفسه، وأقسام المجلد الواحد (القسم الأول/الثاني)، و(أ)/(ب)، و(نسخة أخرى) فمقصودة.')
for _k, _lab in (('all files numbered 01', 'كل الملفات مرقمة 01'), ('repeated volume number', 'رقم مجلد مكرر'), ('99 for indexes', '99 للفهارس'), ('numbered and unnumbered mixed', 'ملفات مرقمة وأخرى غير مرقمة')):
    R.table(['المجلد'], [[f] for f in sorted(_a[_k])], fold=f'{_lab}: {len(_a[_k])}', md_limit=60)
rv = J('data/phone/rename-review.tsv')
if os.path.exists(rv):
    items = [l.rstrip('\n').split('\t') for l in open(rv) if l.strip()]
    R.h2(f'يحتاج مراجعة ({len(items):,})', 'review')
    R.p('حالات لم يكفِ الدليل لتصحيحها آليًا، فتُركت كما هي.')
    R.table(['المسار', 'السبب'], items, fold=f'{len(items):,} بندًا', md_limit=100)
for p, rs in by.items():
    mv = [r for r in rs if r[1] in ('move', 'delete')]
    if not mv: continue
    R.h2(f'تفاصيل: {p}')
    R.table(['من', 'إلى', 'السبب'], [[r[2].removeprefix('Books/'), r[3].removeprefix('Books/') or '— حُذف', r[4]] for r in mv], fold=f'{len(mv):,} عملية', md_limit=30)
print(R.write('04 - سجل التغييرات'))
