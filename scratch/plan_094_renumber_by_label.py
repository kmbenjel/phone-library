"""One-off (094): renumber sets whose file numbers contradict the volume named in their own labels
(«(المجلد الثالث عشر …)», «(الجزء الواحد والخمسون …)»): earlier passes numbered several sets in reverse and gave real
volumes the number 99. New number = the ordinal of the label. Two steps (temporary names) because numbers are swapped."""
import csv, re, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UNITS = {'الأول': 1, 'الحادي': 1, 'الواحد': 1, 'الثاني': 2, 'الثالث': 3, 'الرابع': 4, 'الخامس': 5, 'السادس': 6, 'السابع': 7,
         'الثامن': 8, 'التاسع': 9}
TENS = {'العشرون': 20, 'الثلاثون': 30, 'الأربعون': 40, 'الخمسون': 50, 'الستون': 60, 'السبعون': 70, 'الثمانون': 80}
U = '|'.join(UNITS); T = '|'.join(TENS)
ORD = re.compile(rf'\((?:المجلد|الجزء)\s+(?:(?P<u>{U})\s+و(?P<t>{T})|(?P<u2>{U})\s+عشر|(?P<t2>{T})|(?P<ten>العاشر)|(?P<u3>{U}))(?=\s|\)|-)')
def ordinal(f):
    m = ORD.search(f)
    if not m: return None
    g = m.groupdict()
    if g['u']: return UNITS[g['u']] + TENS[g['t']]
    if g['u2']: return 10 + UNITS[g['u2']]
    if g['t2']: return TENS[g['t2']]
    if g['ten']: return 10
    return UNITS[g['u3']]
SETS = ['التاريخ/تاريخ مدينة دمشق - تاريخ دمشق - ابن عساكر (ت عمر بن غرامة العمروي - دار الفكر)',
        'كتب السنة/كتاب السنن المعروف بالسنن الكبرى - النسائي (ت مركز البحوث وتقنية المعلومات - دار التأصيل)',
        'علوم أخرى/موسوعة الإمام ابن أبي الدنيا - ابن أبي الدنيا']
idx = [p for p, s in csv.reader(open(os.path.join(ROOT, 'data/phone/index-now.tsv'), encoding='utf-8'), delimiter='\t')]
for pre in ('الأنساب/الأنساب - ط. العثمانية - السمعاني (ت عبد', 'كتب السنة/السنن الكبرى وفي ذيله الجوهر النقي - البيهقي (مطبعة مجلس دائرة المعارف العث',
            'كتب السنة/الموطأ برواية أبي مصعب', 'فهارس الكتب والأدلة/الفهرست - ط. الفرقان',
            'الفقه الحنفي/شرح فتح القدير على الهداية شرح بداية المبتدي - ابن الهمام (ت عبد الرزاق'):
    SETS.append(sorted({p.rsplit('/', 1)[0] for p in idx if p.startswith(pre)})[0])
step1, step2, review = [], [], []
for d in SETS:
    files = sorted(p.rsplit('/', 1)[1] for p in idx if p.rsplit('/', 1)[0] == d)
    width = max(2, len(str(len(files))))
    moves = []
    for f in files:
        m = re.match(r'^(\d+) - (.*)$', f)
        if not m: continue
        o = ordinal(f)
        if o is None or int(m.group(1)) == 0 and 'مقدمة التحقيق' not in f: continue
        new = f'{o:0{width}d} - {m.group(2)}'
        if new != f: moves.append((f, new))
    targets = [n for _, n in moves]
    keep = set(files) - {f for f, _ in moves}
    if len(set(targets)) != len(targets) or set(targets) & keep:
        review.append(d); continue
    for i, (f, n) in enumerate(moves):
        tmp = f'__renumber_{i:04d}.pdf'
        step1.append((f'Books/{d}/{f}', f'Books/{d}/{tmp}', 'step 1 of renumbering by the volume named in the label'))
        step2.append((f'Books/{d}/{tmp}', f'Books/{d}/{n}', f'number = the volume of its own label (was «{f.split(" - ")[0]}»: set numbered in reverse / 99)'))
for name, rows in (('094a-renumber-by-label-step1', step1), ('094b-renumber-by-label', step2)):
    with open(os.path.join(ROOT, 'plans', name + '.tsv'), 'w', encoding='utf-8') as w:
        for r in rows: w.write('\t'.join(r) + '\n')
print(len(step1), 'files in', len(SETS) - len(review), 'sets; review:', review)
for a, b, c in step2: print(c.split('«')[1].split('»')[0], '→', b.rsplit('/', 1)[1][:90])
