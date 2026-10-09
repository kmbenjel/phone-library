"""One-off (2026-10-09, owner: «Complete them» — the Waqfeya books whose edition is on the phone with volumes missing).
Writes plans/277-complete-sets-moves.tsv (the lone files already on the phone go into their book's folder) and
data/queue/277-complete-sets.tsv (only the files each Waqfeya record links that the phone lacks; exact sizes from
archive.org). Names per AGENTS.md §4, volume labels from the Waqfeya records. Refuses to run twice (the plan is the record).
Not here: التنبيه والإيقاظ (the phone copy holds every page of the Waqfeya file + a front page: complete), الروض الأنف ت الوكيل
(compared with the complete set of the same edition first), الأموال لأبي عبيد (the record links إمتاع الأسماع), الأمثال والحكم
للماوردي (item dark)."""
import csv, os, sys, urllib.parse
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLAN = os.path.join(ROOT, 'plans/277-complete-sets-moves.tsv')
QUEUE = os.path.join(ROOT, 'data/queue/277-complete-sets.tsv')
if os.path.exists(PLAN) or os.path.exists(QUEUE): sys.exit('already written — never rerun a one-off')

moves, q = [], []
def mv(a, b, why): moves.append(['Books/' + a, 'Books/' + b, why])
def get(item, fn, size, to, rec):
    q.append([f'https://archive.org/download/{item}/{urllib.parse.quote(fn)}', size, 'Books/' + to,
              f'«{rec}»: https://archive.org/download/{item}/{fn}'])

# النحو الوافي — FP42543 (nawa1 = the phone's single file)
R = 'النحو الوافي مع ربطه بالأساليب الرفيعة والحياة اللغوية المتجددة - ط 4'
F = 'النحو والصرف/النحو الوافي مع ربطه بالأساليب الرفيعة والحياة اللغوية المتجددة - عباس حسن (ط دار المعارف)'
mv('النحو والصرف/النحو الوافي مع ربطه بالأساليب الرفيعة والحياة اللغوية المتجددة - ط 4.pdf', F + '/01 - النحو الوافي.pdf',
   'the phone file is nawa1.pdf (exact size) = المجلد الأول of the 4; folder for the set (owner 2026-10-09: complete)')
get('FP42543', 'nawa0.pdf', 643081, F + '/00 - النحو الوافي (الواجهة).pdf', R)
for n, z in ((2, 12562947), (3, 14173463), (4, 17057994)):
    get('FP42543', f'nawa{n}.pdf', z, F + f'/{n:02d} - النحو الوافي.pdf', R)

# التفسير البياني — tbqkwaq (tbqk1 = the phone's single file)
R = 'التفسير البياني للقرآن الكريم'
F = 'التفسير/التفسير البياني للقرآن الكريم - بنت الشاطئ (ط دار المعارف)'
mv('التفسير/التفسير البياني للقرآن الكريم - بنت الشاطئ (ط دار المعارف).pdf', F + '/01 - التفسير البياني للقرآن الكريم.pdf',
   'the phone file is tbqk1.pdf (exact size) = مجلد 1 of 2; folder for the set (owner 2026-10-09: complete)')
get('tbqkwaq', 'tbqk2.pdf', 2735840, F + '/02 - التفسير البياني للقرآن الكريم.pdf', R)

# شرح الزركشي ت ابن جبرين — FP33813 (shrwrkshyfkh0 = the phone's lone cover)
R = 'شرح الزركشي على مختصر الخرقي - ت: ابن جبرين'
F = 'الفقه الحنبلي/شرح الزركشي على مختصر الخرقي (ت عبد الله بن جبرين)'
S = 'شرح الزركشي على مختصر الخرقي'
mv('الفقه الحنبلي/شرح الزركشي على مختصر الخرقي - ت- ابن جبرين.pdf', F + f'/00 - {S} (الواجهة).pdf',
   'the phone file is shrwrkshyfkh0.pdf (exact size) = الواجهة; folder for the 7 volumes (owner 2026-10-09: complete)')
for n, z, lab in ((1, 12061876, 'الطهارة - الصلاة'), (2, 11975945, 'تابع الصلاة - الصيام'), (3, 13545656, 'الاعتكاف - البيوع'),
                  (4, 11299675, 'السلم - قسم الفيء والغنيمة والصدقة'), (5, 12001654, 'النكاح - الرضاع'),
                  (6, 13284802, 'النفقات - الصيد والذبائح'), (7, 11751244, 'الأضاحي - العتق')):
    get('FP33813', f'shrwrkshyfkh{n}.pdf', z, F + f'/{n:02d} - {S} ({lab}).pdf', R)

# فهارس مسند أحمد ط بيت الأفكار — waq39009 (39009.pdf = the phone's المسند)
R = 'فهارس مسند الإمام أحمد بن حنبل - ط. بيت الأفكار'
F = 'كتب السنة/مسند الإمام أحمد بن حنبل (ط بيت الأفكار الدولية)'
mv('كتب السنة/مسند الإمام الحافظ أبي عبد الله أحمد بن حنبل - ط. بيت الأفكار.pdf', F + '/01 - مسند الإمام أحمد بن حنبل.pdf',
   'the phone file is waq39009/39009.pdf (exact size) = the مسند; its فهارس join it in one folder (owner 2026-10-09: complete)')
get('waq39009', '15936.pdf', 49647251, F + '/02 - مسند الإمام أحمد بن حنبل (الفهارس).pdf', R)

# المغني ط المنار — waq16678 (00, 01, 12 on the phone as improved copies)
R = 'المغني ويليه الشرح الكبير - ط. المنار'
F = 'الفقه الحنبلي/المغني ويليه الشرح الكبير - ابن قدامة (ت محمد رشيد رضا - مطبعة المنار ومكتبتها)'
get('waq16678', '01_16678p.pdf', 808352, F + '/01 - المغني (المقدمة).pdf', R)
for n, fn, z, lab in ((2, '02_16679.pdf', 24047806, 'تابع الصلاة - الزكاة'), (3, '03_16680.pdf', 29366162, 'الصيام - الحج والمناسك'),
                      (4, '04_16681.pdf', 20435508, 'البيوع - المفلس'), (5, '05_16682.pdf', 20280645, 'الصلح - المساقاة'),
                      (6, '06_16683.pdf', 21617325, 'الإجارات - الوصايا'), (7, '07_16684.pdf', 21676470, 'الفرائض - النكاح'),
                      (8, '08_16685.pdf', 22605270, 'الصداق - الظهار'), (9, '09_16686.pdf', 23254936, 'اللعان - الديات'),
                      (10, '10_16687.pdf', 21201853, 'تابع الديات - الجهاد'), (11, '11_16688.pdf', 17368045, 'الصيد والذبائح - القسمة')):
    get('waq16678', fn, z, F + f'/{n:02d} - المغني ({lab}).pdf', R)

# البحر المحيط ت المهدي — fp61684_202503 (01p, 01–04 on the phone)
R = 'تفسير البحر المحيط - ت: المهدي'
F = 'التفسير/البحر المحيط - أبو حيان الأندلسي (ت عبد الرزاق المهدي - دار إحياء التراث العربي)'
get('fp61684_202503', '00_61684.pdf', 1020637, F + '/00 - البحر المحيط (الواجهة).pdf', R)
for n, fn, z, lab in ((5, '05_61688.pdf', 25185477, 'التوبة - النحل'), (6, '06_61689.pdf', 21855684, 'الإسراء - الفرقان'),
                      (7, '07_61690.pdf', 25193856, 'الشعراء - الشورى'), (8, '08_61691.pdf', 26124989, 'الزخرف - الناس')):
    get('fp61684_202503', fn, z, F + f'/{n:02d} - البحر المحيط ({lab}).pdf', R)

# صحيح البخاري ط بيت السنة — sahbukdaisunFP (the phone's lone file is the cover, improved copy of 00_sahbukdaisun.pdf)
R = 'الجامع المسند الصحيح المختصر = صحيح البخاري - ط. بيت السنة'
F = 'كتب السنة/صحيح البخاري (ط بيت السنة)'
S = 'صحيح البخاري'
mv('كتب السنة/الجامع المسند الصحيح المختصر = صحيح البخاري - ط. بيت السنة.pdf', F + f'/00 - {S} (الواجهة).pdf',
   'the phone file is the cover (00_sahbukdaisun.pdf, improved copy); folder for the set (owner 2026-10-09: complete)')
get('sahbukdaisunFP', '01_sahbukdaisunM.pdf', 21662483, F + f'/00 - {S} (المدخل إلى الجامع المسند الصحيح والنسخة اليونينية).pdf', R)
get('sahbukdaisunFP', '01_sahbukdaisunMp.pdf', 950681, F + f'/00 - {S} (كلمات في الإمام البخاري).pdf', R)
get('sahbukdaisunFP', '01_sahbukdaisunp.pdf', 499989, F + f'/01 - {S} (المقدمة).pdf', R)
for n, z, lab in ((1, 15865183, 'بدء الوحي - الجنائز'), (2, 13492328, 'الزكاة - الوصايا'), (3, 16402370, 'الجهاد والسير - المغازي'),
                  (4, 12489871, 'التفسير - النفقات'), (5, 10941912, 'الأطعمة - الرقاق'), (6, 12370740, 'القدر - التوحيد'),
                  (7, 8545394, 'الفهارس')):
    get('sahbukdaisunFP', f'{n:02d}_sahbukdaisun.pdf', z, F + f'/{n:02d} - {S} ({lab}).pdf', R)

# شرح علل الترمذي ت عتر — FPsetset (set.pdf = the phone's single file, improved copy)
R = 'شرح علل الترمذي لابن رجب'
F = 'علوم الحديث/شرح علل الترمذي - ابن رجب (ت نور الدين عتر - دار الملاح)'
mv('علوم الحديث/شرح علل الترمذي - ابن رجب (ت نور الدين عتر - دار الملاح).pdf', F + '/01 - شرح علل الترمذي.pdf',
   'the phone file is set.pdf (improved copy) = the book; its مقدمة التحقيق joins it (owner 2026-10-09: complete)')
get('FPsetset', 'setp.pdf', 826155, F + '/00 - شرح علل الترمذي (مقدمة التحقيق).pdf', R)

for r in moves + q:
    assert all(len(p.encode()) <= 200 for p in r[2 if r in q else 1].split('/')[1:]), r
with open(PLAN, 'w', encoding='utf-8', newline='') as f: csv.writer(f, delimiter='\t').writerows(moves)
with open(QUEUE, 'w', encoding='utf-8', newline='') as f: csv.writer(f, delimiter='\t').writerows(q)
print(len(moves), 'moves →', PLAN); print(len(q), 'files,', round(sum(r[1] for r in q) / 1e6), 'MB →', QUEUE)
