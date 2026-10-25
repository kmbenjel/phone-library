"""One-off (owner 2026-10-20 «ولم ليست المقدمة مع الجزء الأول», read in plan 331's check 2026-10-25): sets whose vol. 1 front
(title page, imprint, introduction) is a separate file. Mode «sheet»: fetch each front + its volume, sheet of their first pages
(argv[2]/pairs.png). Mode «join»: join them with the specs below (scripts/join_parts.py), write plans/375-… (originals aside)
and data/queue/376-… (the joined file under the volume's own name)."""
import json, os, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(ROOT)
from PIL import Image, ImageDraw
mode, S = sys.argv[1], sys.argv[2]; os.makedirs(S, exist_ok=True)
PAIRS = [
 ('A', 'الأدب/تاريخ الأدب العربي - بروكلمان (ت عبد الحليم النجار ورمضان عبد التواب - دار المعارف)/00 - تاريخ الأدب العربي (الواجهة).pdf',
       'الأدب/تاريخ الأدب العربي - بروكلمان (ت عبد الحليم النجار ورمضان عبد التواب - دار المعارف)/01 - تاريخ الأدب العربي.pdf'),
 ('B', 'التخريج والأطراف/تنقيح التحقيق في أحاديث التعليق - ابن عبد الهادي/01 - تنقيح التحقيق في أحاديث التعليق (المقدمة).pdf',
       'التخريج والأطراف/تنقيح التحقيق في أحاديث التعليق - ابن عبد الهادي/01 - تنقيح التحقيق في أحاديث التعليق (الطهارة).pdf'),
 ('C', 'الفقه الحنبلي/شرح منتهى الإرادات - البهوتي (ت عبد الله بن عبد المحسن التركي)/00 - شرح منتهى الإرادات (المقدمة).pdf',
       'الفقه الحنبلي/شرح منتهى الإرادات - البهوتي (ت عبد الله بن عبد المحسن التركي)/01 - شرح منتهى الإرادات.pdf'),
 ('D', 'شروح الحديث/السنن الكبرى = سنن البيهقي الكبرى - ط. العلمية/00 - السنن الكبرى (المقدمة).pdf',
       'شروح الحديث/السنن الكبرى = سنن البيهقي الكبرى - ط. العلمية/01 - السنن الكبرى (الطهارة - الصلاة 1 - 2188).pdf'),
 ('E', 'كتب السنة/جامع المسانيد والسنن - ابن كثير (ت عبد المعطي أمين قلعجي - دار الفكر)/00 - جامع المسانيد والسنن (المقدمة).pdf',
       'كتب السنة/جامع المسانيد والسنن - ابن كثير (ت عبد المعطي أمين قلعجي - دار الفكر)/01 - جامع المسانيد والسنن.pdf')]
SPEC = json.loads(os.environ.get('SPEC', '{}'))                    # {"A": ["F", "V:1-z"], …}
def local(k, which): return f'{S}/{k}{which}.pdf'
def npages(f): return int(next(l.split()[-1] for l in subprocess.run(['pdfinfo', f], capture_output=True, text=True).stdout.splitlines() if l.startswith('Pages')))
for k, f, v in PAIRS:
    for which, p in (('F', f), ('V', v)):
        if not os.path.exists(local(k, which)):
            subprocess.run(['flock', '/tmp/phone-ftp.lock', 'rclone', 'copyto', '--bwlimit', '6M', '--retries', '3', 'phone:Books/' + p, local(k, which)], check=True)
if mode == 'sheet':
    W, H = 118, 165
    sheet = Image.new('L', (30 + 11 * (W + 4) + 10, len(PAIRS) * (H + 20)), 255); d = ImageDraw.Draw(sheet)
    for r, (k, f, v) in enumerate(PAIRS):
        y = r * (H + 20); nf = npages(local(k, 'F')); d.text((2, y + H // 2), f'{k} F{nf}', fill=0)
        items = [('f', p) for p in range(1, min(6, nf) + 1)] + [('v', p) for p in range(1, 6)]
        for c, (w, p) in enumerate(items):
            pre = f'{S}/t_{k}{w}{p}'
            subprocess.run(['pdftoppm', '-cropbox', '-gray', '-png', '-r', '30', '-f', str(p), '-l', str(p), '-singlefile', local(k, w.upper()), pre], capture_output=True)
            X = 30 + (c if w == 'f' else 6 + p - 1) * (W + 4) + (10 if w == 'v' else 0)
            if os.path.exists(pre + '.png'):
                im = Image.open(pre + '.png').convert('L'); im.thumbnail((W, H)); sheet.paste(im, (X, y + 14))
            d.text((X + 2, y + 1), f'{w}{p}', fill=0)
    sheet.save(f'{S}/pairs.png'); print('sheet', f'{S}/pairs.png')
else:
    aside, queue = [], []
    for k, f, v in PAIRS:
        spec = SPEC[k]; out = f'{S}/{k}joined.pdf'
        args = [local(k, 'F') + ':1-z' if s == 'F' else local(k, 'V') + ':' + s.split(':')[1] for s in spec]
        r = subprocess.run(['python3', 'scripts/join_parts.py', out] + args, capture_output=True, text=True, check=True)
        print(k, r.stdout.strip().split(': ', 1)[1])
        why = (f"owner 2026-10-20 («ولم ليست المقدمة مع الجزء الأول»; plan 331 read 2026-10-25): vol. 1's front «{f.split('/')[-1]}» "
               f"joined in front of the volume ({' + '.join(spec)}; scripts/join_parts.py, image streams unchanged)")
        aside += [f'Books/{p}\tBooks/نسخ مستبعدة/__المستبدل/{p}\t{why} — set aside' for p in (f, v)]
        queue.append(f'file://{out}\t{os.path.getsize(out)}\tBooks/{v}\t{why}')
    open('plans/375-vol1-fronts-originals-aside.tsv', 'w', encoding='utf-8').write('\n'.join(aside) + '\n')
    open('data/queue/376-vol1-fronts-joined.tsv', 'w', encoding='utf-8').write('\n'.join(queue) + '\n')
