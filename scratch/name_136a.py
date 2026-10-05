"""One-off (2026-10-05): final names for queue 136a (top missing Waqfeya titles, first half), from the title pages read in the staged files
(sheets of pages 1-5 of each book) and, where the title page is silent, the Waqfeya record. Single-file books become
plain files in their section (§4); sets get numbered volume files. Writes data/queue/134-printers-final.tsv (file://)."""
import csv, os, re, collections, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = sys.argv[1]
BATCH = sys.argv[2]                           # stage batch name: downloads/stage-<BATCH>, data/queue/<BATCH>-final.tsv                              # the sheets folder with books.tsv (scratch/title_sheets.py)
A = 'الأمير شكيب أرسلان'
T = 'الدار التقدمية'
N = {0: ('علوم القرآن وأصول التفسير', 'إعراب القرآن الكريم وبيانه - محيي الدين الدرويش (ط دار اليمامة - دار ابن كثير)'), 1: ('كتب السنة', 'سلسلة الأحاديث الضعيفة والموضوعة - الألباني (ط مكتبة المعارف)'), 2: ('كتب السنة', 'سلسلة الأحاديث الصحيحة - الألباني (ط مكتبة المعارف)'), 3: ('الفقه الحنبلي', 'الشرح الممتع على زاد المستقنع - ابن عثيمين (ط دار ابن الجوزي)'), 4: ('الفقه العام', 'فقه السنة - السيد سابق (ط الفتح للإعلام العربي)'), 5: ('كتب عامة', 'مناهج البحث العلمي - عبد الرحمن بدوي (ط وكالة المطبوعات - الكويت)'), 6: ('علوم القرآن وأصول التفسير', 'الجدول في إعراب القرآن وصرفه وبيانه - محمود صافي (ط دار الرشيد - مؤسسة الإيمان)'), 7: ('شروح الحديث', 'الكوكب الوهاج والروض البهاج في شرح صحيح مسلم - محمد الأمين الهرري (ط دار المنهاج - دار طوق النجاة)'), 8: ('شروح الحديث', 'ذخيرة العقبى في شرح المجتبى - محمد بن علي آدم الإثيوبي (ط دار المعراج الدولية - دار آل بروم)'), 9: ('التفسير', 'روائع البيان تفسير آيات الأحكام - محمد علي الصابوني (ط مكتبة الغزالي - مؤسسة مناهل العرفان)'), 10: ('الفقه الشافعي', 'الفقه المنهجي على مذهب الإمام الشافعي - مصطفى الخن ومصطفى البغا وعلي الشربجي (ط دار القلم)'), 11: ('الغريب والمعاجم', 'المعجم المفصل في شواهد العربية - إميل بديع يعقوب (ط دار الكتب العلمية)'), 12: ('علوم القرآن وأصول التفسير', 'مباحث في علوم القرآن - مناع القطان (ط مكتبة وهبة)'), 13: ('الغريب والمعاجم', 'المعجم الوجيز (ط مجمع اللغة العربية بالقاهرة)'), 14: ('الفقه الحنبلي', 'الملخص الفقهي - صالح الفوزان (ط دار العاصمة)'), 15: ('التاريخ', 'تاريخ الدولة العثمانية - يلماز أوزتونا (ترجمة عدنان محمود سلمان - مؤسسة فيصل للتمويل - إستانبول)'), 16: ('النحو والصرف', 'معاني النحو - فاضل صالح السامرائي (ط دار الفكر)'), 17: ('العقيدة', 'شرح العقيدة الواسطية - ابن عثيمين (ت سعد فواز الصميل - دار ابن الجوزي)'), 18: ('أصول الفقه', 'معلمة زايد للقواعد الفقهية والأصولية (ط مؤسسة زايد بن سلطان آل نهيان - مجمع الفقه الإسلامي الدولي)'), 19: ('التاريخ', 'تاريخ الجزائر الثقافي - أبو القاسم سعد الله (ط دار الغرب الإسلامي)'), 20: ('التخريج والأطراف', 'إرواء الغليل في تخريج أحاديث منار السبيل - الألباني (ط المكتب الإسلامي)'), 21: ('أصول الفقه', 'أصول الفقه الذي لا يسع الفقيه جهله - عياض بن نامي السلمي (ط دار التدمرية)'), 22: ('كتب عامة', 'ماذا خسر العالم بانحطاط المسلمين؟ - أبو الحسن الندوي (ط مكتبة الإيمان)'), 23: ('السيرة النبوية', 'السيرة النبوية عرض وقائع وتحليل أحداث - علي محمد الصلابي (ط دار المعرفة)'), 24: ('كتب عامة', 'موسوعة اليهود واليهودية والصهيونية - عبد الوهاب المسيري (ط دار الشروق)'), 25: ('شروح الحديث', 'نزهة المتقين شرح رياض الصالحين - مصطفى سعيد الخن وآخرون (ط مؤسسة الرسالة)'), 26: ('كتب السنة', 'ضعيف الجامع الصغير وزيادته - الألباني (ط المكتب الإسلامي)'), 27: ('التفسير', 'معارج التفكر ودقائق التدبر - عبد الرحمن حسن حبنكة الميداني (ط دار القلم)'), 28: ('الفرق والردود', 'أصول مذهب الشيعة الإمامية الاثني عشرية - ناصر القفاري'), 29: ('السيرة النبوية', 'فقه السيرة - محمد الغزالي (تخريج الألباني - دار الكتب الحديثة)'), 30: ('التفسير', 'التفسير الوسيط للقرآن الكريم - مجمع البحوث الإسلامية بالأزهر (ط المطابع الأميرية)'), 31: ('التراجم والطبقات', 'معجم المؤلفين - عمر رضا كحالة (ط مؤسسة الرسالة)'), 32: ('الجوامع', 'آثار ابن باديس (ط الشركة الجزائرية)'), 33: ('أصول الفقه', 'إتحاف ذوي البصائر بشرح روضة الناظر - عبد الكريم النملة (ط دار العاصمة)'), 34: ('كتب السنة', 'صحيح الجامع الصغير وزيادته - الألباني (ط المكتب الإسلامي)'), 35: ('الغريب والمعاجم', 'الرائد - جبران مسعود (ط دار العلم للملايين)'), 36: ('التراجم والطبقات', 'نزهة الفضلاء تهذيب سير أعلام النبلاء - محمد موسى الشريف (ط دار الأندلس الخضراء)'), 37: ('علوم القرآن وأصول التفسير', 'الصحيح المسند من أسباب النزول - مقبل بن هادي الوادعي (ط مكتبة صنعاء الأثرية)'), 38: ('كتب اللغة', 'موسوعة علوم اللغة العربية - إميل بديع يعقوب (ط دار الكتب العلمية)'), 39: ('الفقه العام', 'تمام المنة في التعليق على فقه السنة - الألباني (ط دار الراية)'), 40: ('كتب السنة', 'صحيح سنن الترمذي وضعيف سنن الترمذي - الألباني (ط مكتبة المعارف)'), 41: ('شروح الحديث', 'فتح الملهم بشرح صحيح الإمام مسلم - شبير أحمد العثماني ومحمد تقي العثماني (ط دار إحياء التراث العربي)'), 42: ('شروح الحديث', 'عون الباري لحل أدلة البخاري - صديق حسن خان (ط دار الرشيد)'), 43: ('أصول الفقه', 'السنة ومكانتها في التشريع الإسلامي - مصطفى السباعي (ط دار الوراق - المكتب الإسلامي)'), 44: ('شروح الحديث', 'أوجز المسالك إلى موطأ مالك - محمد زكريا الكاندهلوي (ت تقي الدين الندوي - دار القلم)')}
SHORT = {}
ORD = {'الأول': 1, 'الثاني': 2, 'الثاتي': 2, 'الثالث': 3, 'الرابع': 4, 'الخامس': 5, 'السادس': 6, 'السابع': 7, 'الثامن': 8, 'التاسع': 9, 'العاشر': 10}
NOISE = re.compile(r'\s*-\s*(طبعة نادرة جداً|ملون|ط\.\s*\S+|مصورة من ط\.\s*\S+)(?=\s*[(.]|$)')

UNITS = {'الأول': 1, 'الحادي': 1, 'الثاني': 2, 'الثاتي': 2, 'الثالث': 3, 'الرابع': 4, 'الخامس': 5, 'السادس': 6, 'السابع': 7,
         'الثامن': 8, 'التاسع': 9, 'العاشر': 10}
TENS = {'عشر': 10, 'العشرون': 20, 'الثلاثون': 30, 'الأربعون': 40, 'الأريعون': 40, 'الخمسون': 50}

def ordinal(words):
    """«الحادي عشر» 11, «الحادي والثلاثون» 31, «الأربعون» 40 → the first number named"""
    n = 0
    for w in words:
        w2 = w[1:] if w.startswith('و') and w[1:] in TENS else w
        if w2 in TENS and (n or w2 != 'عشر'): n += TENS[w2]
        elif w in UNITS and not n: n = UNITS[w]
        else: break
    return n or None

def vol(fname):
    """→ (number or None, kind) from a waq_queue file name"""
    m = re.match(r'^(\d+) - ', fname)
    if m: return int(m.group(1)), 'nn'
    if '(الواجهة)' in fname: return 0, 'cover'
    m = re.search(r'\((?:مجلد|المجلد|المجلدات|الجزء) (\d+)', fname)
    if m: return int(m.group(1)), 'mj'
    m = re.search(r'\((?:الجزء|المجلد|الجزءان|المجلدان) ([^-()]+)', fname)
    if m:
        v = ordinal(m.group(1).split())
        if v: return v, 'juz'
    if '(مقدمة التحقيق)' in fname: return None, 'pref'
    return None, 'main'

PARTS = {32}                                   # books whose «ج a - b» means volume a, part b (آثار ابن باديس)

def embedded(path, n, title):
    """the PDF's own title «… - ج N: label» (Waqfeya uploads) → (first volume number, label, companion?) — better evidence
    than the record's labels (AGENTS §3: labels lie sometimes)"""
    t = subprocess.run(['pdfinfo', path], capture_output=True, text=True).stdout
    m = re.search(r'^Title:\s*(.+)$', t, re.M)
    m = m and re.search(r'^(.*?)-\s*ج\s*([\d\s\-]+?)\s*:\s*(.*)$', m.group(1))
    if not m: return None
    work, nums = m.group(1).strip(' -'), [int(x) for x in re.findall(r'\d+', m.group(2))]
    lab = re.sub(r'(?<=[\u0621-\u064a])(?=\d)|(?<=\d)(?=[\u0621-\u064a])', ' ', m.group(3)).strip(' -')
    if len(nums) > 1 and n in PARTS: lab = f'الجزء {nums[0]} - القسم {nums[1]}' + (f' - {lab}' if lab else '')
    elif len(nums) > 1: lab = f'الأجزاء {nums[0]}-{nums[-1]}' + (f' - {lab}' if lab else '')
    if work.startswith('تكملة') and not title.startswith('تكملة'): lab = f'{work} ج {nums[0]} - {lab}'
    companion = bool(re.match(r'(استدراك|ملحق|ذيل)', lab))
    if companion: lab = f'{lab} على الجزء {nums[0]}'
    return nums[0], lab, companion

def main():
    books = [l.rstrip('\n').split('\t') for l in open(os.path.join(S, 'books.tsv'), encoding='utf-8')]
    rows = list(csv.reader(open(os.path.join(ROOT, f'downloads/stage-{BATCH}/manifest.tsv'), encoding='utf-8'), delimiter='\t'))
    by = collections.defaultdict(list)
    for r in rows: by[os.path.dirname(r[2])].append(r)
    out, seen = [], set()
    for n, folder, cnt, first in books:
        cat, name = N[int(n)]
        fs = by[folder]
        assert len(name.encode()) <= 200, name
        if len(fs) == 1:
            tgt = [(fs[0], f'Books/{cat}/{name}.pdf')]
        else:
            short = re.sub(r'\s*\(.*$', '', name).split(' - ')[0]
            short = re.split(r'\s+(?:وبهامشه|وبهامشها|ويليه|ومعه)\s', short)[0]
            w = short.split()                                  # §4: cut at the first particle after two words
            cut = next((i for i in range(2, len(w)) if w[i] in ('في', 'على', 'من', 'عن', 'إلى')), None)
            short = ' '.join(w[:cut]) if cut else short
            short = SHORT.get(int(n), short)
            kinds = [vol(os.path.basename(r[2])) for r in fs]
            numbered = any(k[0] for k in kinds)
            tgt = []
            for r, (v, kind) in zip(fs, kinds):
                fn = os.path.basename(r[2])
                lab = re.search(r'\(([^()]*)\)\.pdf$', fn); lab = lab.group(1) if lab else ''
                e = embedded(r[4], int(n), name) if kind not in ('cover', 'pref') and 'مقدم' not in lab else None
                if e and e[2]:                       # an addendum: a companion, no volume number (§4)
                    tgt.append((r, f'Books/{cat}/{name}/{short} ({e[1]}).pdf')); continue
                if e and e[0]: v, lab = (v if kind == 'nn' else e[0]), e[1]; kind = 'emb'
                lab = lab.replace('الثاتي', 'الثاني')
                if kind == 'pref':
                    npref = sum(1 for t in tgt if '(المقدمة' in t[1]) + 1
                    lab = 'المقدمة' + (f' {npref}' if npref > 1 else '')
                    fn2 = f'{short} ({lab}).pdf' if not numbered else f'00 - {short} ({lab}).pdf'
                elif kind == 'main' and not numbered:
                    fn2 = f'{short} ({lab}).pdf' if lab and lab not in ('الكتاب',) and lab != short else f'{short}.pdf'
                elif kind == 'cover': fn2 = f'00 - {short} (الواجهة).pdf'
                else:
                    if re.match(r'مقدمة', lab): lab = 'المقدمة'
                    if re.fullmatch(r'مجلد \d+|المجلد \d+', lab): lab = ''
                    lab = re.sub(r'^مجلد (\d+) ، (\d+)$', r'المجلدان \1-\2', lab)
                    lab = re.sub(r'\s*:\s*', ' - ', lab); lab = re.sub(r'[\\/*?"<>|]', '', lab); lab = re.sub(r'\s+', ' ', lab).strip()
                    while lab and len(f'{v:02d} - {short} ({lab}).pdf'.encode()) > 200:      # §4: ≤ 200 bytes, cut at a word
                        lab = lab.rsplit(' ', 1)[0].rstrip(' -،') if ' ' in lab else ''
                    fn2 = f'{v:02d} - {short}' + (f' ({lab})' if lab else '') + '.pdf'
                tgt.append((r, f'Books/{cat}/{name}/{fn2}'))
        for r, t in tgt:
            assert t not in seen, t
            assert all(len(p.encode()) <= 200 for p in t.split('/')), t
            seen.add(t)
            out.append([f'file://{r[4]}', r[1], t, r[3]])
    with open(os.path.join(ROOT, f'data/queue/{BATCH}-final.tsv'), 'w', encoding='utf-8') as w:
        for x in out: w.write('\t'.join(x) + '\n')
    print(len(out), 'files')

if __name__ == '__main__':
    main()
