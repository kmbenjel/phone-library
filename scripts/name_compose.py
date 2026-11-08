"""Book and volume names under the owner's rules of 2026-10-10 (AGENTS.md §4):
  * nothing is shortened when the whole name fits in 240 bytes: the full title, the author, the editor, the publisher —
    every piece of information we have («All the possible info should be present»);
  * no parentheses and no commas anywhere (owner: «avoid ()», «تبقي على الأقواس», «استغن عن الفواصل»):
    «<title> - <author> - ت <editor> - <publisher> <city> <year>» (no «ط», no «=»: «X أو Y»),
    «… - ط <publisher>»; a title's own «(مخطوط)», «(رسالة ماجستير)» go after the edition («… - مخطوط»), a one- or two-word
    «(الجد)» is written inline, a longer one («(شاعر الطبيعة والأندلس)») becomes a «، …» subtitle;
  * only when the name is too long, the combination that keeps the most information is chosen; what gives way, first to
    last: a subtitle that came from parentheses, the publisher (owner: «publisher first»), editors after the second, the
    words after the title's head («جمع الجوامع في كذا كذا ويليه همع الهوامع في كذا كذا» → «جمع الجوامع ويليه همع
    الهوامع»), the later joined titles («ويليه، ومعه، =»), the first editor; a title is never cut inside a word or a name;
  * a volume file is named like its folder: «NN - <title> - <label>.pdf» with the folder's full title, shortened the same
    way only when needed; no parentheses around the label.
compose(title, author, edition) → the name without «.pdf»; volume(nn, title, label) → the same for a volume."""
import re, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from textnorm import norm

LIMIT = 236                                   # + «.pdf» = 240 bytes: the phone's file system allows 255 bytes per
                                              # name (UTF-8, ≈ 125 Arabic letters); ~15 kept for temporary upload suffixes (owner
                                              # 2026-10-10: «whatever length, once useful and technically acceptable»)
JOIN = re.compile(r'\s+(ويليه|ويليها|ومعه|ومعها|وبهامشه|وبهامشها|وبذيله|وذيله|وفي آخره|=)\s+')
SUB = re.compile(r'\s*،\s*|\s+-\s+|\s+(?:المسمى|المسماة|الموسوم|الموسومة|وهو|وهي)\s+')
PARTICLES = {norm(w) for w in 'في من على عن إلى الى بين مع لما لمن لأهل لمعرفة لبيان لشرح بشرح شرح وهو أو'.split()}
WEAK_END = {norm(w) for w in 'بن ابن أبي أبو عبد ذي ذو أهل دار شيخ الإمام الشيخ لما ما لمن الذي التي و في من على عن إلى '
            'أكثر أقل بعض كل أهم نحو حول ضد غير سائر جميع بين مع'.split()}
EDITION_KIND = re.compile(r'^(مخطوط|مخطوطة|رسالة( علمية| جامعية| ماجستير| دكتوراه|)|أطروحة.*|بحث محكم|نسخة خطية)$')
B = lambda s: len(s.encode())

def tidy(s):
    s = re.sub(r'\s+', ' ', s).strip(' -،')
    s = re.sub(r'\(\s*\)', '', s)
    return s.strip()

def split_title(title):
    """the title's own parentheses → (title without them, edition words, subtitle)"""
    ed, sub = [], []
    def take(m):
        x = m.group(1).strip()
        if EDITION_KIND.match(x): ed.append(x); return ' '
        if len(x.split()) <= 2: return ' ' + x + ' '
        sub.append(x); return ' '
    t = tidy(re.sub(r'\(([^()]*)\)', take, title))
    return t, ed, sub

def head(seg):
    """a joined title's own head: up to its first particle from the third word on («جمع الجوامع في …» → «جمع الجوامع»)"""
    w = seg.split()
    for i in range(2, len(w)):
        if norm(w[i]) in PARTICLES:
            w = w[:i]; break
    while len(w) > 1 and norm(w[-1]) in WEAK_END: w.pop()
    return ' '.join(w)

DATEWORD = re.compile(r'^([\d٠-٩]+|هـ|ه|م|-|–)$')
UPTO = {norm(w) for w in 'إلى الى حتى'.split()}
SUFFIX = ('هما', 'هم', 'ها', 'ه')

def one_member(w, i):
    """is the «و…» word w[i] a member that cannot be cut off (cuts)"""
    n = norm(w[i]); rest = [x for x in w[i + 1:] if not DATEWORD.match(x)]
    if not rest: return True
    nx = norm(rest[0])                                 # a new clause next («… والإمالة وما كان …»); another item of
    if nx in PARTICLES or nx in {'فيما', 'مما', 'عما', 'بما', 'لما', 'وما', 'ومن', 'وفي'}: return True   # a list may follow
    if n[1:].startswith(norm('إيا')): return True
    raw = lambda x: TASHKEEL.sub('', x)                 # (the raw word: norm folds «ة» into «ه», a pronoun's letter)
    sf = next((x for x in SUFFIX if raw(w[i]).endswith(x)), None)
    return bool(sf and len(raw(w[i])) > 4 and any(raw(x).endswith(sf) and len(raw(x)) > 3 for x in w[max(0, i - 3):i]))

def cuts(seg):
    """a title's natural breaks, longest prefix first: before a particle («في», «من», «فيما»), a «و…» or «لـ…» word,
    from the third word on — «الاستذكار الجامع لمذاهب فقهاء الأمصار…» → «الاستذكار الجامع», …; never inside a pair or a
    range (owner 2026-10-19: «لا يمكن أن تكون الجملة مقصوصة هكذا أبدا»): not before a «و…» member of one word — the
    title's last word, or one followed by a date, a particle or another «و…» («القضاء والفتيا», «إتيانه واجتنابه», «صلى
    الله عليه وسلم», «الرقي والصعود في أصول الفقه», «التفخيم والإمالة وما كان …»); not before «وإياه» (it belongs to its
    verb: «من نظمني وإياه الزمان») or a clause matching the one before it («قواها الألباني وضعفها الحويني»); nor before the
    «إلى» of a «من …» («من أوله إلى نهاية …», «من إعلان الدستور العثماني إلى الآن»). A member of two words may go: a
    rhymed title's second half («بداية المجتهد ونهاية المقتصد», «جمال القراء وكمال الإقراء»)"""
    w = seg.split(); out = []
    for i in range(len(w) - 1, 1, -1):
        n = norm(w[i])
        if n in PARTICLES or n in {'فيما', 'مما', 'عما', 'بما', 'لما', 'وما', 'ومن', 'وفي'} or (len(n) > 3 and (n.startswith('و') or n.startswith('لل')
                or n.startswith('لم') or n.startswith('لا'))):
            if n.startswith('و') and n not in PARTICLES and one_member(w, i): continue
            if n in UPTO and any(norm(x) == 'من' for x in w[max(0, i - 6):i]): continue
            k = w[:i]
            if len(k) > 2 and norm(k[-2]) in {'ما', 'مما', 'فيما', 'عما', 'بما', 'لما', 'وما'}: continue   # never «… وبيان ما ورد»
            # a «و…» word is not left hanging without its complement («وتفسير | لمسلم بن خالد»)
            if len(k) > 1 and n.startswith('ل') and norm(k[-1]).startswith('و') and len(norm(k[-1])) > 3: k.pop()
            while len(k) > 1 and norm(k[-1]) in WEAK_END: k.pop()
            k = whole_clause(k)
            if k and ' '.join(k) not in out: out.append(' '.join(k))
    return out

# a «و…» clause naming a relation or an effect needs what follows it (owner 2026-10-19 on «… شرح عمدة الأحكام وأثر ذلك»:
# «لا يمكن أن تكون الجملة مقصوصة هكذا أبدا»): such a clause is kept whole or dropped whole, never cut after its first words
RELATION = {norm(w) for w in 'أثر أثره أثرها أثرهم آثار آثاره آثارها دور دوره دورها دورهم موقف موقفه موقفها منهج منهجه منهجها '
            'جهود جهوده جهودها علاقة علاقته علاقتها صلة صلته صلتها أهمية أهميته أهميتها تطبيق تطبيقه تطبيقاته تطبيقاتها '
            'انعكاس انعكاسه انعكاساته مكانة مكانته مكانتها مدى'.split()}
POINTER = {norm(w) for w in 'ذلك ذلكم هذا هذه هذين تلك عليه عليها فيه فيها منه منها به بها له لها'.split()}

def whole_clause(k):
    for j in range(len(k) - 1, max(0, len(k) - 4), -1):
        t = norm(k[j])
        if t.startswith('و') and t[1:] in RELATION:
            return k[:j]
    if len(k) > 2 and norm(k[-1]) in POINTER:                  # «… وأثر ذلك», «… وما يتعلق به»: back to the last «و…»
        for j in range(len(k) - 2, max(0, len(k) - 5), -1):
            if norm(k[j]).startswith('و') and len(norm(k[j])) > 2: return k[:j]
    return k

def editors_short(ed):
    """«ت أ و ب و ج - الناشر» → editors cut to the first two"""
    m = re.match(r'^ت\s+(.*?)(\s+-\s+.*)?$', ed)
    if not m: return ed
    names = [x.strip() for x in re.split(r'\s*[،؛]\s*|\s+و(?=\S{3,})', m.group(1)) if x.strip()]
    return 'ت ' + ' و'.join(names[:2]) + (m.group(2) or '') if len(names) > 2 else ed

def without_publisher(ed):
    if ed.startswith('ط '): return ''
    return re.split(r'\s+-\s+', ed)[0]

def build(title_parts, joins, sub, author, ed, kinds=()):
    t = title_parts[0]
    for j, p in zip(joins, title_parts[1:]): t += f" {'أو' if j == '=' else j} {p}"     # owner: no «=» — «X أو Y»
    if sub: t += '، ' + '، '.join(sub)
    s = t
    if author: s += f' - {author}'
    kinds = [k for k in kinds if not (ed and norm(k) in norm(ed))]   # (a lithograph whose printer is «طبعة حجرية فاس»)
    ed = ' - '.join([e for e in [ed] + list(kinds) if e])          # «مخطوط», «رسالة ماجستير» stay to the end
    if ed: s += f' - {ed}'                                         # owner 2026-10-10: no parentheses at all
    s = re.sub(r'\s*[،,]\s*', ' ', s)                             # and no commas: «مكتبة المعارف الرباط 1985»
    return tidy(safe(s))

def safe(s):
    """AGENTS §4 characters: none of \\ / : * ? " < > | (FAT/Windows; «/» is a folder on the phone — plan 315 failed on
    «1276 هـ / 1860» and «ديوان …: …»): «/» and «:» → a space, «?» → «؟», «"…"» → «…», the rest dropped"""
    s = s.translate(str.maketrans('یکۀ', 'يكة'))                    # Persian letters typed for Arabic ones
    s = re.sub(r'\s*\((?:\?|؟)\)', '', s)                         # a reader's «(?)» never reaches a name
    s = s.replace('(', '').replace(')', '')                           # owner: no parentheses anywhere
    s = re.sub(r'\s*[/\\:|]\s*', ' ', s).replace('?', '؟').replace('*', '')
    s = re.sub(r'"([^"]*)"', r'«\1»', s).replace('"', '').replace('<', '').replace('>', '')
    return re.sub(r'\s+', ' ', s)

def one_name(x):
    """Shamela's «short؛ full» form of a name → the full name when it contains the short one, else the short one"""
    if '؛' not in x: return x
    a, b = [y.strip() for y in x.split('؛', 1)]
    b = re.split(r'،', b)[0].strip()
    return b if set(norm(a).split()) <= set(norm(b).split()) else a

TASHKEEL = re.compile(r'[\u064B-\u0652\u0670]')
PUBLISHER_WORD = re.compile(r'^(دار|مكتبة|مكتبه|مؤسسة|مطبعة|المطبعة|المكتب|وزارة|مجمع|جامعة|مركز|الهيئة|المجلس|عالم|إدارة|الأمانة|بيت|شركة|منشورات|معهد|الجمعية|جمعية|مجلة|الدار|مطابع|المطبعه|\d)')

def parse_edition(ed):
    """«ت أ وب - الناشر، المدينة» / «ت أ - ب - الناشر» / «ط الناشر» → (editors, publisher, city, other)"""
    ed = TASHKEEL.sub('', tidy(ed))
    if not ed: return [], '', '', ''
    m = re.match(r'^(ت|ط)\s+(.*)$', ed)
    kind, rest = (m.group(1), m.group(2)) if m else ('', ed)
    if not kind and PUBLISHER_WORD.match(ed) and not re.match(r'^\d', ed): kind, rest = 'ط', ed     # «(مطبعة السعادة)»
    segs = [one_name(x.strip()) for x in re.split(r'\s+-\s+', rest) if x.strip()]
    if kind == 'ت':
        eds = [segs[0]] + [x for x in segs[1:-1] if not PUBLISHER_WORD.match(x)] if segs else []
        pubs = [x for x in segs[1:-1] if PUBLISHER_WORD.match(x)] + segs[-1:] if len(segs) > 1 else []
        pub = ' و'.join(pubs)
        names = [y.strip() for x in eds for y in re.split(r'\s*[،؛]\s*|\s+و(?=[^\s]{3,}\s)', x) if y.strip()]
    elif kind == 'ط':
        names, pub = [], ' - '.join(segs)
    else:
        return [], '', '', ed                              # an unknown form is kept whole
    city = ''
    if '،' in pub: pub, city = [x.strip() for x in pub.split('،', 1)]
    return names, pub, city, ''

def with_place(pub, city):
    """the publisher as printed, then the city with a space only («مكتبة المعارف الرباط»; owner 2026-10-11: «مطبعة حجازي
    بالقاهرة» is kept because the cover prints it so — the city is not joined with «بـ» as a rule); a city the
    publisher's name already holds is not repeated; a city without a publisher stands alone"""
    cs = [c.strip() for c in re.split(r'\s*[،,/]\s*', city or '') if c.strip() and norm(c.strip()) not in norm(pub or '')]
    return ' '.join(x for x in [pub] + cs if x)

def edition_text(names, pub, city, other, year='', role='ت', more=()):
    """«ت أ وب - الناشر بالمدينة» / «الناشر بالمدينة 1341 هـ» / «ت أ»; the role as printed when it is not tahqiq
    («صححه وعلق عليه فلان», «تنسيق فلان» — owner 2026-10-10 night); `more`: the other contributors as printed, after the
    editor («راجعه وقدم له فلان», «إشراف وتحرير فلان»)"""
    if other: return other + (f' {year}' if year else '')
    p = ' '.join(x for x in (with_place(pub, city), year) if x)
    if names or more:
        ed = ' - '.join(([f'{role or "ت"} ' + ' و'.join(names)] if names else []) + list(more))
        return ed + (f' - {p}' if p else '')
    return p                                                          # owner: no «ط» — the publisher speaks for itself

# A PERSON'S NAME, SHORTENED ONLY FOR A LONG TITLE (owner 2026-10-10, plan 313: «يمكن ذكر الاسم كاملا للمؤلف أو بالكنية
# أو اللقب على حسب الشهير والمعروف، نجنح للاقتصار عند الاضطرار لوجود معلومات ضرورية كعنوان طويل»): the names and printed
# roles get shorter after the publisher has gone and before the title loses a word (2026-10-25: «مراقي السعود لمبتغي
# الرقي», «شمس الآفاق بنور» were cut while a nasab of six words stayed whole) — see compose's order
HONOR = {norm(x) for x in 'الحافظ الإمام الشيخ العلامة سيدي المحدث الفقيه الأستاذ الدكتور المؤرخ الأديب الشريف المقرئ المسند الحاج الرئيس'.split()}
KUNYA = {norm(x) for x in 'أبو أبي أبا أم'.split()}
LINK = {norm(x) for x in 'بن بنت ولد'.split()}

def units(w):
    """the words of a name grouped: «عبد X», «أبو X» / «أبو عبد X», «X الدين» (a laqab), «ابن X» — a family or famous
    name, never a link of the nasab (written «ابن» inside a name: «إسماعيل بن يوسف ابن الأحمر»)"""
    out, i = [], 0
    while i < len(w):
        n = norm(w[i])
        if n in KUNYA and i + 1 < len(w):
            j = 3 if norm(w[i + 1]) == norm('عبد') and i + 2 < len(w) else 2
            out.append(w[i:i + j]); i += j; continue
        if n in (norm('عبد'), norm('ابن')) and i + 1 < len(w):
            j = 3 if n == norm('ابن') and norm(w[i + 1]) in (norm('عبد'), norm('أبي')) and i + 2 < len(w) else 2
            out.append(w[i:i + j]); i += j; continue
        if i + 1 < len(w) and norm(w[i + 1]) in (norm('الدين'), norm('الله')):   # a laqab; «غرم الله», «حبيب الله»
            out.append(w[i:i + 2]); i += 2; continue
        out.append([w[i]]); i += 1
    return out

def name_forms(x):
    """a person's name, then its shorter forms, each of ≥ 2 words, longest first: without the honorifics in front
    («الحافظ», «الشيخ»), without a «أبو …» at its end, a nasab of three links or more kept to its first and last
    («علي بن حسن بن علي بن عبد الحميد» → «علي بن حسن بن عبد الحميد»), of three nisbas or more the first and the last
    (the famous one is either: «السنوسي … الجزائري», «المقدسي … الحنبلي»), or the kunya or the laqab with the nisbas
    («أبو علي المالكي البغدادي», «زين الدين العراقي»)"""
    w = x.split()
    if len(w) <= 2: return [x]
    U = units(w)
    tok = lambda us: [t for u in us for t in u]
    kind = lambda u: ('honor' if len(u) == 1 and norm(u[0]) in HONOR else 'kunya' if norm(u[0]) in KUNYA
                      else 'link' if len(u) == 1 and norm(u[0]) in LINK else 'laqab' if len(u) == 2 and norm(u[1]) == norm('الدين') and not u[0].startswith('و')
                      else 'nisba' if (len(u) == 1 and u[0].startswith('ال')) or norm(u[0]) == norm('ابن') else 'ism')
    forms = [U]
    a = U[:]
    while a and kind(a[0]) == 'honor' and len(tok(a[1:])) >= 3: a = a[1:]
    forms.append(a)
    if len(a) > 1 and norm(a[-1][0]) == norm('أبو') and len(tok(a[:-1])) >= 3: a = a[:-1]; forms.append(a)
    K = [kind(u) for u in a]
    # the nasab: a name followed by «بن X» links («الحسن بن محمد»: an ism may begin with «ال»); after it its tail
    s = next((i for i in range(len(a) - 2) if K[i] in ('ism', 'kunya', 'nisba') and K[i + 1] == 'link'), None)
    if s is not None:
        e = s
        while e + 2 < len(a) and K[e + 1] == 'link': e += 2
        head, chain, tail = a[:s], a[s:e + 1], a[e + 1:]
        # of three links or more the first and the last (the last is often the family: «بن مانع», «بن عبد الهادي» —
        # «محمد بن عبد العزيز بن مانع» keeps both of its two links)
        c1 = chain[:3] + chain[-2:] if len(chain) > 5 else chain
        if c1 is not chain: forms.append(head + c1 + tail)
        nis = [u for u in tail if kind(u) == 'nisba']
        if len(nis) >= 3:
            forms.append(head + c1 + [u for u in tail if kind(u) != 'nisba' or u is nis[0] or u is nis[-1]])
        if len(nis) >= 2:                                       # of two, the first («الجكني الشنقيطي», «السنوسي الجزائري»)
            forms.append(head + c1 + [u for u in tail if kind(u) != 'nisba' or u is nis[0]])
        kun = [u for u in head if kind(u) == 'kunya']
        if kun and nis: forms.append(kun[-1:] + tail)          # «أبو علي المالكي البغدادي»
        laq = [u for u in head if kind(u) == 'laqab']
        if laq and nis: forms.append(laq[-1:] + nis[-1:])      # «زين الدين العراقي»
    out = []
    for f in forms:
        t = ' '.join(tok(f))
        if len(t.split()) >= 2 and t not in out: out.append(t)
    return sorted(out, key=lambda t: -len(t.split())) or [x]

PERSONS = re.compile(r'\s+و(?=(?:محمد|أحمد|عبد|علي|صالح|عمر|عثمان|إبراهيم|يوسف|حسن|حسين|أبو|أبي|ابن|إسماعيل|خالد|سعيد|مصطفى|عامر|نبيل)\b|\S+\sالدين\b)')

def people_options(x):
    """(text, people kept, words kept) of an author line: one person — each form of the name; several («X ومحمد Y وصالح
    Z») — all, the first two, the first, each whole or in its shortest form"""
    if not x: return [('', 0, 0)]
    ps = [p.strip() for p in PERSONS.split(x) if p.strip()]
    if len(ps) == 1:                                   # an author line that still holds a « و…» may be two people: whole
        fs = [x] if re.search(r'\sو\S{2,}', x) else name_forms(x)
        return [(f, 1, len(f.split())) for f in fs]
    out = []
    for k in sorted({len(ps), 2, 1}, reverse=True):
        for ns in (ps[:k], [name_forms(p)[-1] for p in ps[:k]]):
            out.append((' و'.join(ns), k, sum(len(n.split()) for n in ns)))
    return list(dict.fromkeys(out))

def title_options(seg):
    """(text, words kept) of a joined title's part: whole, without its subtitle, then cut at each natural break"""
    out = [seg]
    ns = SUB.split(seg)[0].strip()
    if ns and ns != seg: out.append(ns)
    out += [c for c in cuts(ns) if c not in out]
    return out

def wscore(text, seg):
    """a title part's worth: its head (up to the first natural break, «جمع الجوامع») counts fully, the words after it
    («في كذا كذا») little — they are the first to give way, as the owner's example shows"""
    cs = cuts(SUB.split(seg)[0].strip())
    hn = len((cs[-1] if cs else seg).split())
    n = len(text.split())
    return 10 * min(n, 2) + 2 * max(0, min(n, hn) - 2) + 0.6 * max(0, n - max(hn, 2))

# an author's dates in brackets — «(1413 هـ)», «(بعد 666 هـ)», «(ت 717 هـ)», «(840 - 909 هـ)», «(المتوفى 717 هـ)»: not an
# edition word (2026-10-19: readings that kept them put «- 1413 هـ» at the end of names, as if the print's year)
DEATH = re.compile(r'^(?:ت\.?|المتوفى|المتوفي|توفي)?\s*(?:بعد|قبل|نحو|حوالي)?\s*\d{1,4}(?:\s*[-–]\s*\d{1,4})?\s*(?:هـ|ه)?'
                   r'(?:\s*/\s*\d{3,4}\s*م?)?$')

def compose(title, author='', edition='', limit=LIMIT, year='', kinds_extra=(), role='ت', more=()):
    """the name that carries the most information within `limit` bytes: every combination of the title's cut, its joined
    titles («ويليه، ومعه، =»), its subtitle, the author's and the editor's names (whole or shorter), the printed role, the
    other contributors (`more`, as printed: «راجعه وقدم له فلان»), the editors and the publisher is weighed; nothing is cut
    when all fits"""
    import itertools
    t, kinds, sub = split_title(tidy(title))
    kinds = kinds + [k for k in kinds_extra if k]                  # «رسالة ماجستير», «مخطوط» given apart from the title
    names, pub, city, other = parse_edition(edition)
    author = TASHKEEL.sub('', one_name(author))
    for x in re.findall(r'\(([^()]*)\)', author):        # «اليوسي (مخطوط)», «David Werner (Hesperian 2025)»: edition words
        x = tidy(x)
        if DEATH.match(x): continue                       # «التويجري (1413 هـ)»: his death year, never the print's
        if x and norm(x) not in norm(edition): kinds.append(x)
    author = tidy(re.sub(r'\([^()]*\)', ' ', author))
    more = [tidy(m) for m in more if tidy(m)]
    parts = JOIN.split(t)
    segs, joins = parts[0::2], parts[1::2]
    full = build(segs, joins, sub, author, edition_text(names, pub, city, other, year, role, more), kinds)
    if B(full) <= limit: return full
    # WHAT GIVES WAY, FIRST TO LAST (owner 2026-10-10, AGENTS.md §4): first everything else — year, city, subtitle,
    # publisher, editors after the first, other contributors, the authors after the second, and the names and printed role
    # at their full length (shortened only for a long title: plan 313) — weighed among themselves as since 2026-10-11; then
    # the words after the titles' heads (only at natural breaks — cuts), the second author (2026-10-26: «الروضة الغنية» lost
    # its own author, «تاج الدين الفركاح», to three words of its title), the heads of the titles, the later joined titles,
    # the first editor. A candidate is scored by a tuple in the reverse of that order and compared tuple to tuple: nothing
    # of a lesser rank outweighs one word of the title (2026-10-26: a role of seven words had outweighed five words of the
    # title, a nasab of six words «مراقي السعود لمبتغي الرقي»); among equals the longer name
    seg_opts = [title_options(sg)[:10] for sg in segs]
    hns = []
    for sg in segs:
        cs = cuts(SUB.split(sg)[0].strip()); hns.append(max(len((cs[-1] if cs else sg).split()), 2))
    au_opts = people_options(author)
    ed_opts = []
    for k in sorted({len(names), min(2, len(names)), min(1, len(names)), 0}, reverse=True):
        for pp, cc, yy in ((pub, city, year), (pub, city, ''), (pub, '', year), (pub, '', ''), ('', '', year), ('', '', '')):
            if pub and yy and not pp: continue           # a print's year belongs to its printer: never alone once the
                                                         # publisher has gone
            generic = re.match(r'^(وزارة|المجلس|الهيئة|جامعة|مجمع|مركز|الأمانة|دار المعارف|المكتب)', pp or '')
            # a long printed role («اعتنى به وأشرف على طباعته») is cut at its «و» joints before the editor goes
            # (2026-10-19); a role that includes the tahqiq becomes «ت», never its first part («قدم له وحققه وعلق عليه»
            # → «قدم له» would hide the tahqiq)
            role0 = role or 'ت'; rparts = role0.split(' و')
            ropts = [role0]
            if len(rparts) > 1:
                ropts += ['ت'] if re.search(r'حقق|تحقيق', role0) else [' و'.join(rparts[:j]) for j in range(len(rparts) - 1, 0, -1)]
            for rl in ropts:
                for f in (name_forms(names[0])[:4] if k >= 1 else ['']):
                    nk = ([f] + names[1:k]) if k >= 1 else []
                    for j in range(len(more), -1, -1):  # the other contributors, as printed
                        e = edition_text(nk, pp, cc, other, yy, rl, more[:j])
                        # (below the title: the weights in use since 2026-10-11 — the second editor 2.5, each later one
                        # 0.3, the publisher 0.5, its city 0.1/0.2, a kept year 0.3, the printed role whole 3 — and a
                        # name's word 1.05: more than publisher, city and year together, so a name is shortened only to
                        # keep the title, never for a publisher)
                        rest = (2.5 * (k >= 2) + 0.3 * max(0, k - 2) + 0.5 * bool(pp) + (0.2 if generic else 0.1) * bool(cc)
                                + 0.3 * bool(yy) + 3 * (rl == role0) + 1.05 * (len(f.split()) if k >= 1 else 0) + 0.3 * j)
                        ed_opts.append(((int(k >= 1), round(rest, 4)), e))
    ed_opts = sorted(dict.fromkeys(ed_opts), key=lambda x: x[0], reverse=True)
    def total(n, heads, tails, sw, au, eo):
        k1, rest = eo
        return (k1, n, heads, min(au[1], 2), tails, round(rest + 1.05 * au[2] + 1.0 * max(0, au[1] - 2) + 0.3 * sw, 4))
    best = None
    for n in range(len(segs), 0, -1):                       # the first n joined titles
        for combo in itertools.product(*seg_opts[:n]):
            heads = sum(min(len(c.split()), h) for c, h in zip(combo, hns))
            tails = sum(max(0, len(c.split()) - h) for c, h in zip(combo, hns))
            for ss in ((sub, len(' '.join(sub).split())), ([], 0)):
                if ss[0] and not sub: continue
                for au in au_opts:
                    if best is not None and ed_opts and total(n, heads, tails, ss[1], au, ed_opts[0][0]) < best[0]: continue
                    for eo, e in ed_opts:               # best first: the first that fits is this candidate's best (among
                        sc = total(n, heads, tails, ss[1], au, eo)   # equal ones, the longest)
                        if best is not None and sc < best[0]: break
                        nm = build(list(combo), joins[:n - 1], ss[0], au[0], e, kinds)
                        if B(nm) > limit: continue
                        if best is None or sc > best[0] or (sc == best[0] and B(nm) > B(best[1])): best = (sc, nm)
    if best: return best[1]
    w = segs[0].split()                                    # last resort: whole words off the title's end, no edition
    au = min(au_opts, key=lambda o: B(o[0]))[0] if au_opts else author
    while len(w) > 2 and B(build([' '.join(w)], [], [], au, '', kinds)) > limit: w.pop()
    while len(w) > 1 and norm(w[-1]) in WEAK_END: w.pop()
    n = build([' '.join(w)], [], [], au, '', kinds)
    return n if B(n) <= limit else build([' '.join(w)], [], [], '', '', kinds)

def volume(nn, title, label='', limit=LIMIT, author='', edition='', year=''):
    """«NN - <title> - <author> - ت <editor> - <publisher> <city> <year> - <label>»: everything the folder says, then the
    volume's label (owner 2026-10-10: the volume files carry all the information too), shortened only when needed"""
    label = tidy(re.sub(r'^\((.*)\)$', r'\1', label or ''))
    pre, post = f'{nn} - ', f' - {label}' if label else ''
    return pre + compose(title, author, edition, limit - B(pre) - B(post), year=year) + post

FUNCTION = re.compile(r'^(الواجهة|الغلاف|المقدمة|مقدمة التحقيق|مقدمة المحقق|الدراسة|قسم الدراسة|الفهارس|فهارس|الفهرس|الفهارس العامة|'
                      r'الفهارس العلمية|ملحق|ملاحق|الملحق|صور المخطوطات?|المستدرك|الاستدراك|التكملة|الذيل)\b')

def keep_label(label):
    """a volume's label is kept only when it says what the file IS (cover, introduction, indexes, appendix, manuscript
    images) — not a range of its contents («إحياء الموات - أمهات الأولاد»: owner 2026-10-10 «I don't feel like to keep
    these»); a part with its own printed title is passed by the caller as part of the title"""
    lb = tidy(re.sub(r'^\((.*)\)$', r'\1', label or ''))
    m = FUNCTION.match(lb)
    return re.sub(r'\s*\d+$', lambda x: x.group(0) if 'فهارس' in lb or 'ملحق' in lb else '', lb) if m else ''

def volumes(title, items, author='', edition='', year='', limit=LIMIT):
    """the files of one set: ONE shared part (title, author, editor, publisher…) for every volume, sized for the longest
    «NN - … - <label>», so that no volume says less than another; items = [(nn, label)] → names (without «.pdf»)"""
    clean = [(nn, keep_label(lb)) for nn, lb in items]
    room = min(limit - B(f'{nn} - ') - (B(f' - {lb}') if lb else 0) for nn, lb in clean)
    core = compose(title, author, edition, room, year=year)
    return [f'{nn} - {core}' + (f' - {lb}' if lb else '') for nn, lb in clean]

if __name__ == '__main__':
    for t in ('جمع الجوامع في أصول الفقه وقواعده الكلية ويليه همع الهوامع في شرح جمع الجوامع في علم العربية وفنونها كلها',
              'ديوان ابن خفاجة الأندلسي (شاعر الطبيعة والأندلس)', 'مسائل أبي الوليد ابن رشد (الجد)',
              'ابن أبي زيد القيرواني عقيدته وموقفه من الفرق (رسالة ماجستير)'):
        print(compose(t, 'السيوطي', 'ت عبد الحميد هنداوي ومحمد عبد الله وأحمد شاكر - دار الكتب العلمية'))
        print(compose(t, 'السيوطي', 'ت عبد الحميد هنداوي - دار الكتب العلمية', limit=120))
    print(volume('03', 'الجامع لأحكام القرآن والمبين لما تضمنه من السنة وآي الفرقان = تفسير القرطبي', 'سورة البقرة 1 - 141'))
