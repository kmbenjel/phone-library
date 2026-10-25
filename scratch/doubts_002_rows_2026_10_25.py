"""One-off: data/review/doubts-002.tsv (owner 2026-10-20 on doubts-001: «حلّ الأمر ثم اعرض ما يتجدد من الإشكالات»): what is
still unresolved after his comments, and what was changed on them today (2026-10-25) for him to check — with first pages
(rendered from the local joined copies in argv[1])."""
import csv, glob, hashlib, json, os, re, subprocess, sys, unicodedata
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(ROOT)
S = sys.argv[1]; IMG = f'{S}/d2img'; os.makedirs(IMG, exist_ok=True)
N = lambda s: unicodedata.normalize('NFC', s)
idx = {N(l.split('\t')[0]): (l.split('\t')[0], l.rstrip('\n').split('\t')[1]) for l in open('data/phone/index-now.tsv', encoding='utf-8')}
rev = {}
for r in csv.reader(open('data/changes/changes.tsv', encoding='utf-8'), delimiter='\t'):
    if len(r) > 3 and r[1] == 'move': rev.setdefault(N(r[3].removeprefix('Books/')), []).append(N(r[2].removeprefix('Books/')))
keys = {}
for l in open('data/inspect/files.jsonl'):
    try: d = json.loads(l)
    except ValueError: continue
    if d.get('key'): keys.setdefault(N(d['path']), []).append(d['key'])
def stored(p):
    raw, size = idx[p]; ks = [hashlib.md5(f'{raw}\t{size}'.encode()).hexdigest()[:16]]; todo = [p]; seen = {p}
    while todo:
        x = todo.pop(); ks += keys.get(x, [])
        for a in rev.get(x, []):
            if a not in seen: seen.add(a); todo.append(a)
    for k in ks:
        fs = sorted(glob.glob(f'data/inspect/pages/{k}-*.jpg'), key=lambda f: int(re.search(r'-(\d+)\.jpg$', f).group(1)))
        if fs: return fs[:3]
    return []
def render(pdf, tag, pages=(1, 2, 3)):
    out = []
    for p in pages:
        pre = f'{IMG}/{tag}_{p}'
        if not os.path.exists(pre + '.png'):
            subprocess.run(['pdftoppm', '-cropbox', '-gray', '-png', '-r', '45', '-f', str(p), '-l', str(p), '-singlefile', pdf, pre], capture_output=True)
        if os.path.exists(pre + '.png'): out.append(pre + '.png')
    return out
def find(prefix, contains=''):
    m = sorted(p for p in idx if p.startswith(N(prefix)) and N(contains) in p)
    return m[0] if m else None
out = ['#S\tA\tما بقي بلا حل: لا يوجد في أي رفع ما ينقص', '#S\tB\tما عملته اليوم بناء على ملاحظاتك — للمراجعة',
       '#S\tC\tمسألة لقرارك']
T7 = find('التاريخ/تاريخ الطبري تاريخ الرسل والملوك - ابن جرير الطبري - ت محمد أبو الفضل إبراهيم - دار المعارف بمصر/07 - ')
out.append(f"A\t{idx[T7][0]}\tالجزء السابع: صور المخطوطات في أوله هي من نسخه فعلا — «بيان» المحقق بعدها يقول «ومن النسخ التي حصلت عليها لتحقيق هذا الجزء…» ويصفها، والنص يبدأ بسنة 104 أول سنوات هذا الجزء. الناقص صفحة العنوان وحدها: كل رفع لهذا المسح (الوقفية trm07 ورفعان في أرشيف الإنترنت) هو الملف نفسه بلا صفحة عنوان\t{','.join(stored(T7))}")
F1 = find('أصول الفقه/شرح الفصول في علم الجدل')
out.append(f"A\t{idx[F1][0]}\tبدأ هكذا عند رفعه: الملف في الوقفية (shfselgd) والرفع الآخر في أرشيف الإنترنت ملف واحد بالحجم نفسه 10,361,172 بايتا يبدأ بدراسة المحققة؛ لم يحذف منه شيء عندنا\t{','.join(stored(F1))}")
F4 = find('الفقه الحنبلي/تيسير فقه العمدة')
out.append(f"A\t{idx[F4][0]}\tالسبب: النسخة التي وصلتنا (من مكتبة الحاسوب المحلية، بلا مصدر معروف) تبدأ من الصفحة 5؛ لا يوجد في أرشيف الإنترنت رفع آخر لهذه الطبعة (الموجود «نظم تيسير فقه العمدة» ملف وورد مختلف، وتسجيل صوتي)\t{','.join(stored(F4))}")
pf = json.load(open(f'{S}/pf/match.json')); tg = {x['i']: x for x in json.load(open(f'{S}/pf/targets.json'))}
for x in pf:
    j = f"{S}/pf/joined/{x['i']}.pdf"            # uploaded copies are deleted by fetch_queue: then no image, x opens it
    if N(x['volume']) not in idx: continue
    out.append(f"B\t{idx[N(x['volume'])][0]}\tضُمّ إليه جزؤه الأول «{tg[x['i']]['file']}» (صفحة العنوان والتقديم/الدراسة/صور المخطوطات) الذي فصلته الوقفية ولم يصل إلى الهاتف — والأصل محفوظ في «نسخ مستبعدة»\t{','.join(render(j, 'pf' + str(x['i'])) if os.path.exists(j) else [])}")
for k, lab in (('A', 'الواجهة (صفحة عنوان دار المعارف وفهرس الجزء الأول) وُضعت بعد الغلاف الخارجي'), ('B', 'المقدمة (247 صفحة) قبل الطهارة'),
               ('C', 'المقدمة قبل الجزء الأول، دون تكرار صفحة العنوان'), ('D', 'المقدمة قبل الجزء الأول، دون تكرار صفحة العنوان'), ('E', 'مجلد المقدمة (279 صفحة) قبل الجزء الأول')):
    pass
v1 = {'A': 'الأدب/تاريخ الأدب العربي - بروكلمان', 'B': 'التخريج والأطراف/تنقيح التحقيق في أحاديث التعليق - ابن عبد الهادي/01 - ',
      'C': 'الفقه الحنبلي/شرح منتهى الإرادات - البهوتي', 'D': 'شروح الحديث/السنن الكبرى = سنن البيهقي الكبرى - ط. العلمية/01 - ',
      'E': 'كتب السنة/جامع المسانيد والسنن - ابن كثير'}
lab = {'A': 'الواجهة (صفحة عنوان دار المعارف وفهرس الجزء الأول) وُضعت فيه بعد الغلاف الخارجي — والأجزاء 1–3 في أغلفة طبعة الهيئة المصرية التي جمعت أجزاء دار المعارف أقساما', 'B': 'المقدمة (247 صفحة) وُضعت قبل كتاب الطهارة في الجزء الأول',
       'C': 'المقدمة وُضعت قبل الجزء الأول دون تكرار صفحة العنوان', 'D': 'المقدمة وُضعت قبل الجزء الأول دون تكرار صفحة العنوان', 'E': 'مجلد المقدمة (279 صفحة) وُضع قبل الجزء الأول'}
for k, pre in v1.items():
    p = find(pre, '/01 - ') if not pre.endswith('/01 - ') else find(pre)
    out.append(f"B\t{idx[p][0]}\t{lab[k]} (ملاحظتك على الطبري: «ولم ليست المقدمة مع الجزء الأول»)\t{','.join(render(f'{S}/v1f/{k}joined.pdf', 'v1' + k))}")
M = find('الأدب/شرح المشكل من شعر المتنبي - ابن سيده - ت مصطفى السقا')
out.append(f"B\t{idx[M][0]}\tالملف القديم بهذا الاسم كان نسخة مطابقة بايتا ببايت للجزء الأول من «المحكم» لابن سيده: حُذف، وجُلب الكتاب نفسه من أرشيف الإنترنت (hmmt00011) ومعه ملحقه، وقُرئت صفحتا العنوان\t{','.join(render(f'{S}/mushkil/001.pdf', 'mk'))}")
for p in sorted(x for x in idx if x.startswith(N('الأدب/جمهرة رسائل العرب في عصور العربية الزاهرة - أحمد زكي صفوت - المكتبة العلمية بيروت/'))):
    out.append(f"B\t{idx[p][0]}\tسُمّي بجزئه كما طُبع على صفحة عنوانه؛ وحُذفت النسخة الأخرى من الطبعة نفسها (رفع الوقفية، ثلاثة أجزاء بلا الرابع ولا نص)\t{','.join(stored(p))}")
out.append("C\tنسخ مستبعدة/__المستبدل\tفي 665 مجموعة تبقى المقدمة (أو الدراسة، أو صفحة العنوان مع التقديم) ملفا منفصلا عن الجزء الأول: 756 ملفا (89 منها من صفحة إلى 3، و354 من 4 إلى 40 صفحة، و308 أطول). أضمّها كلها إلى أجزائها الأولى كما فعلت في الطبري وهذه الأربعة والثلاثين؟ يحتاج ذلك نقل الجزء الأول لكل منها من الهاتف وإليه (بضع غيغابايتات، ساعات)، والأصول تحفظ في «نسخ مستبعدة». اكتب: «ضمّ الكل» أو «القصيرة فقط» أو «اتركها»\t")
open('data/review/doubts-002.tsv', 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print(sum(1 for l in out if not l.startswith('#')), 'rows')
