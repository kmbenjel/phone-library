"""Report 04: what was changed on the phone (from data/changes/changes.tsv) + what still needs review."""
import csv, os, sys
from collections import Counter, defaultdict
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from report_lib import Report
J = lambda p: os.path.join(ROOT, p)
log = [r for r in csv.reader(open(J('data/changes/changes.tsv')), delimiter='\t') if r]
moves = [r for r in log if r[1] == 'move']
quar = [r for r in moves if r[3].startswith('Books-مكررات/')]
undone = {r[5][5:] for r in log if r[5].startswith('undo-')}
R = Report('سجل التغييرات', 'ما طُبّق على ملفات الهاتف، وما هو مقترح بانتظار الموافقة')
R.kpis([('عمليات نقل/تسمية', f'{len(moves):,}'), ('نسخ مكررة نُقلت إلى Books-مكررات', f'{len(quar):,}'),
        ('مجلدات فارغة أزيلت', f'{sum(1 for r in log if r[1] == "rmdir"):,}'), ('خطط مطبقة', f'{len({r[5] for r in log}):,}')])
R.note('لم يُحذف أي ملف. النسخ المكررة (متطابقة بالحجم وبصمة أول وآخر 64 ك.ب) نُقلت إلى مجلد «Books-مكررات» في ذاكرة الهاتف بالمسار نفسه؛ '
       'راجعه ثم احذفه يدويًا. كل خطة يمكن التراجع عنها: python3 scripts/apply_plan.py --undo <اسم الخطة>.')
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
rv = J('data/phone/rename-review.tsv')
if os.path.exists(rv):
    items = [l.rstrip('\n').split('\t') for l in open(rv) if l.strip()]
    R.h2(f'يحتاج مراجعة ({len(items):,})', 'review')
    R.p('حالات لم يكفِ الدليل لتصحيحها آليًا، فتُركت كما هي.')
    R.table(['المسار', 'السبب'], items, fold=f'{len(items):,} بندًا', md_limit=100)
for p, rs in by.items():
    mv = [r for r in rs if r[1] == 'move']
    if not mv: continue
    R.h2(f'تفاصيل: {p}')
    R.table(['من', 'إلى', 'السبب'], [[r[2].removeprefix('Books/'), r[3].removeprefix('Books/'), r[4]] for r in mv], fold=f'{len(mv):,} عملية', md_limit=30)
print(R.write('04 - سجل التغييرات'))
