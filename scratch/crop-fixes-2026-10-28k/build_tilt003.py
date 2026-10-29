"""build_tilt003.py — the owner's review page crop-tilt-003 (data/review/crop-tilt-003.tsv → scripts/doubts_page.py): the 83
pages regression 27l leaves as scanned for their two angles, each with its two pictures (twoang_page.py, /tmp/claude-1000/twoang)
and the verdict of the look by eye (verdict-*.jsonl; mine.jsonl overrides: my own look at every page questioned). Pages
questioned first, then the rest by book. The evidence (rows.jsonl, verdict-*.jsonl, mine.jsonl) lives in tilt003/; the
pictures stay in /tmp/claude-1000/twoang (twoang_page.py makes them again). A row the owner settled stays in its place,
marked done (verdict DONE: comments are kept by row number — moving rows would put his words under another page)."""
import json, glob, os, subprocess
T = '/tmp/claude-1000/twoang'; ROOT = '/home/k/projects/phone-library'
E = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tilt003')
PATH = {'00597fea27cf': 'الأدب/خزانة الأدب للبغدادي/01 - خزانة الأدب للبغدادي.pdf',
 '29b9db6c6baa': 'الأدب/صبح الأعشى في كتابة الإنشا - القلقشندي (ط دار الكتب المصرية)/05 - صبح الأعشى في كتابة الإنشا (تابع المقالة الثانية - المقالة الثالثة).pdf',
 '8ec1fd8095ad': 'البلاغة/دلائل الإعجاز - عبد القاهر الجرجاني (ت محمود شاكر - مكتبة الخانجي).pdf',
 '2b47002d18ab': 'التاريخ/الموسوعة الشاملة في تاريخ الحروب الصليبية - سهيل زكار/الموسوعة الشاملة (38).pdf',
 'f134344a7421': 'التراجم والطبقات/تذكرة الحفاظ - شمس الدين الذهبي (دار الكتب العلمية)/التنبيه والإيقاظ لما في ذيول تذكرة الحفاظ.pdf',
 '3103a9db389b': 'السياسة الشرعية والقضاء/رسوم دار الخلافة - هلال الصابئ (ت ميخائيل عواد - دار الرائد العربي).pdf',
 'c63a21351cba': 'العلل والسؤلات الحديثية/اللآلئ المصنوعة في الأحاديث الموضوعة - الجلال السيوطي (ط دار المعرفة)/01 - اللآلئ المصنوعة في الأحاديث الموضوعة (التوحيد - مناقب البلدان والأيام).pdf',
 '435bf8357444': 'العلل والسؤلات الحديثية/اللآلئ المصنوعة في الأحاديث الموضوعة - الجلال السيوطي (ط دار المعرفة)/02 - اللآلئ المصنوعة في الأحاديث الموضوعة (الطهارة - فوائد متفرقة).pdf',
 '0c32c1a4815b': 'العلل والسؤلات الحديثية/سؤالات أبي داود للإمام أحمد بن حنبل في جرح الرواة وتعديلهم (ت أبو عمر محمد بن علي الأزهري - الفاروق الحديثة).pdf',
 '83dfc7786870': 'الفقه المالكي/روضة المستبين - ابن بزيزة.pdf',
 '51cfa6854fda': 'الفقه المالكي/روضة المستبين في شرح كتاب التلقين لابن بزيزة/1 - روضة المستبين في شرح كتاب التلقين لابن بزيزة.pdf',
 '5b214426d112': 'شروح الحديث/إرشاد الساري لشرح صحيح البخاري وبهامشه صحيح مسلم بشرح النووي - القسطلاني (ط المطبعة الأميرية)/10 - إرشاد الساري لشرح صحيح البخاري (تابع 86 الحدود680297 التوحيد7563=تابع45 البر والصلة).pdf',
 'acb87508dd15': 'فهارس الكتب والأدلة/فهرسة ابن خير الإشبيلي/1 - فهرسة ابن خير الإشبيلي.pdf',
 'eb8673fd16b1': 'كتب اللغة/المثلث - ابن السيد البطليوسي (ت صلاح مهدي الفرطوسي)/1 - المثلَّث للبطليوسي.pdf',
 '9da5c530d977': 'كتب اللغة/معجم تيمور الكبير في الألفاظ العامية - أحمد تيمور باشا/02 - معجم تيمور الكبير (الألف - التاء).pdf',
 '4b80602ae0e8': 'الأدب/الفوائد المحصورة في شرح المقصورة - محمد بن أحمد بن هشام اللخمي - ت أحمد عبد الغفور عطار - منشورات دار مكتبة الحياة بيروت.pdf',
 '55d35c02e3e0': 'التراجم والطبقات/مختصر تاريخ دمشق لابن عساكر/27 - مختصر تاريخ دمشق لابن عساكر (هارون الرشيد - يزيد بن القعقاع).pdf'}
PAT = {'warped': 'صفحة ملتوية: يزيد الميل سطرا بعد سطر', 'two_blocks': 'كتلتان من السطور على زاويتين',
       'fan': 'سطور منفرجة لا يجمعها ميل واحد', 'other': 'سطور على أكثر من زاوية'}
cnt = lambda n: 'سطر واحد' if n == 1 else 'سطران' if n == 2 else f"{n} {'أسطر' if n <= 10 else 'سطرا'}"
f = lambda x: f'{abs(x):.2f}'.rstrip('0').rstrip('.')

def why(r, v):
    L = r['L']; b = [abs(x[1]) for x in L]; w = [abs(x[2]) for x in L if abs(x[2]) > 0.35 + 1e-6 and abs(x[2]) >= abs(x[1]) + 0.25 - 1e-6]
    s = (f"ص {r['page']} من الملف: كان المنهج سيديرها {f(r['turn'])}° فتركها كما مُسحت. كما مُسحت: {len(L)} {'أسطر' if len(L) <= 10 else 'سطرا'} ميلها من "
         f"{f(min(b))}° إلى {f(max(b))}°؛ لو أُديرت لمال {cnt(len(w))} منها أكثر مما هي الآن (حتى {f(max(w)) if w else '0'}°).")
    if v.get('ar'): return s + ' ' + v['ar']
    if v['verdict'] == 'RIGHT': return s + f" رأيي: {PAT.get(v['pattern'], PAT['other'])}، فتركها صواب."
    return s + ' رأيي: لم أقطع فيها، انظرها.'

if __name__ == '__main__':
    R = {(r['pdf'], r['page']): r for r in map(json.loads, open(f'{E}/rows.jsonl'))}
    V = {}
    for fn in sorted(glob.glob(f'{E}/verdict-*.jsonl')) + ([f'{E}/mine.jsonl'] if os.path.exists(f'{E}/mine.jsonl') else []):
        for v in map(json.loads, open(fn)): V[(v['pdf'], int(v['page']))] = v
    miss = [k for k in R if k not in V]
    assert not miss, f'no verdict for {miss}'
    bad = sorted([k for k in R if V[k]['verdict'] not in ('RIGHT', 'DONE')], key=lambda k: (PATH[k[0]], k[1]))
    done = sorted([k for k in R if V[k]['verdict'] == 'DONE'], key=lambda k: (PATH[k[0]], k[1]))
    ok = sorted([k for k in R if V[k]['verdict'] == 'RIGHT'], key=lambda k: (PATH[k[0]], k[1]))
    out = ['#T\tصفحات تُركت كما مُسحت: سطورها على زاويتين\t'
           f'{len(R) - len(done)} صفحة من كتب الاختبار الـ31، يتركها المنهج الآن بلا تدوير بقاعدتك (2026-10-27 «اتركها كما مُسحت»): '
           'تدوير واحد يسوي بعض سطورها ويميل غيرها. لكل صفحة صورتان: الأولى كما مُسحت، والثانية لو أُديرت بالزاوية التي '
           'كان المنهج سيديرها بها. على كل سطر خط بميله الذي قيس: أخضر = مستو (0.35° فأقل)، أحمر = مائل، والرقم ميله بالدرجات. '
           'فُحصت كل صفحة بالعين وبقياس مستقل للميل، ورأيي مكتوب تحت اسمها. اكتب رأيك إن خالفته، أو «أدرها» لتُدار.',
           '#S\tD\tتم بأمرك', '#S\tQ\tما أرى رفض تدويره خطأ: سطوره على ميل واحد', '#S\tOK\tما أرى تركه صوابا']
    for sec, ks in (('D', done), ('Q', bad), ('OK', ok)):
        for k in ks:
            out.append('\t'.join([sec, PATH[k[0]], why(R[k], V[k]), f'{T}/{k[0]}-{k[1]}-1.jpg,{T}/{k[0]}-{k[1]}-2.jpg']))
    open(f'{ROOT}/data/review/crop-tilt-003.tsv', 'w', encoding='utf-8').write('\n'.join(out) + '\n')
    subprocess.run(['python3', f'{ROOT}/scripts/doubts_page.py', 'crop-tilt-003'], check=True)
    print(len(done), 'done,', len(bad), 'questioned,', len(ok), 'right')
