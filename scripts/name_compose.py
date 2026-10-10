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

def cuts(seg):
    """a title's natural breaks, longest prefix first: before a particle («في», «من», «فيما»), a «و…» or «لـ…» word,
    from the third word on — «الاستذكار الجامع لمذاهب فقهاء الأمصار…» → «الاستذكار الجامع», …"""
    w = seg.split(); out = []
    for i in range(len(w) - 1, 1, -1):
        n = norm(w[i])
        if n in PARTICLES or n in {'فيما', 'مما', 'عما', 'بما', 'لما', 'وما', 'ومن', 'وفي'} or (len(n) > 3 and (n.startswith('و') or n.startswith('لل')
                or n.startswith('لم') or n.startswith('لا'))):
            k = w[:i]
            # a «و…» word is not left hanging without its complement («وتفسير | لمسلم بن خالد»)
            if len(k) > 1 and n.startswith('ل') and norm(k[-1]).startswith('و') and len(norm(k[-1])) > 3: k.pop()
            while len(k) > 1 and norm(k[-1]) in WEAK_END: k.pop()
            if k and ' '.join(k) not in out: out.append(' '.join(k))
    return out

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
    ed = ' - '.join([e for e in [ed] + list(kinds) if e])          # «مخطوط», «رسالة ماجستير» stay to the end
    if ed: s += f' - {ed}'                                         # owner 2026-10-10: no parentheses at all
    s = re.sub(r'\s*[،,]\s*', ' ', s)                             # and no commas: «مكتبة المعارف الرباط 1985»
    return tidy(s)

def one_name(x):
    """Shamela's «short؛ full» form of a name → the full name when it contains the short one, else the short one"""
    if '؛' not in x: return x
    a, b = [y.strip() for y in x.split('؛', 1)]
    b = re.split(r'،', b)[0].strip()
    return b if set(norm(a).split()) <= set(norm(b).split()) else a

TASHKEEL = re.compile(r'[\u064B-\u0652\u0670]')
PUBLISHER_WORD = re.compile(r'^(دار|مكتبة|مكتبه|مؤسسة|مطبعة|المطبعة|المكتب|وزارة|مجمع|جامعة|مركز|الهيئة|المجلس|عالم|إدارة|الأمانة|بيت|شركة|منشورات|معهد|الجمعية|مجلة|الدار|مطابع|المطبعه|\d)')

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

def edition_text(names, pub, city, other, year=''):
    """«ت أ وب - الناشر، المدينة، السنة» / «ط الناشر، السنة» / «ت أ - السنة»"""
    if other: return other + (f'، {year}' if year else '')
    if city and norm(city) in norm(pub): city = ''               # «الجامعة الأميركية في بيروت» already says where
    p = ' '.join(x for x in (pub, city if pub else '', year) if x)
    if names: return 'ت ' + ' و'.join(names) + (f' - {p}' if p else '')
    return p                                                          # owner: no «ط» — the publisher speaks for itself

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

def compose(title, author='', edition='', limit=LIMIT, year='', kinds_extra=()):
    """the name that carries the most information within `limit` bytes: every combination of the title's cut, its joined
    titles («ويليه، ومعه، =»), its subtitle, the editors and the publisher is weighed; nothing is cut when all fits"""
    import itertools
    t, kinds, sub = split_title(tidy(title))
    kinds = kinds + [k for k in kinds_extra if k]                  # «رسالة ماجستير», «مخطوط» given apart from the title
    names, pub, city, other = parse_edition(edition)
    author = TASHKEEL.sub('', one_name(author))
    for x in re.findall(r'\(([^()]*)\)', author):        # «اليوسي (مخطوط)», «David Werner (Hesperian 2025)»: edition words
        x = tidy(x)
        if x and norm(x) not in norm(edition): kinds.append(x)
    author = tidy(re.sub(r'\([^()]*\)', ' ', author))
    parts = JOIN.split(t)
    segs, joins = parts[0::2], parts[1::2]
    full = build(segs, joins, sub, author, edition_text(names, pub, city, other, year), kinds)
    if B(full) <= limit: return full
    seg_opts = [title_options(sg)[:10] for sg in segs]
    ed_opts = []
    for k in sorted({len(names), min(2, len(names)), min(1, len(names)), 0}, reverse=True):
        for pp, cc, yy in ((pub, city, year), (pub, city, ''), (pub, '', year), (pub, '', ''), ('', '', year), ('', '', '')):
            generic = re.match(r'^(وزارة|المجلس|الهيئة|جامعة|مجمع|مركز|الأمانة|دار المعارف|المكتب)', pp or '')
            # owner 2026-10-10: when the whole title and the publisher cannot both fit, the publisher goes first; the
            # (first) editor stays — so a publisher weighs less than any word of the title, an editor more
            sc = (8 if k >= 1 else 0) + (2.5 if k >= 2 else 0) + 0.3 * max(0, k - 2) + (0.5 if pp else 0) + ((0.2 if generic else 0.1) if cc else 0)
            sc += 0.3 if yy else 0                       # the year gives way first
            e = edition_text(names[:k], pp, cc, other, yy)
            ed_opts.append((sc + (6 if other else 0), e))
    ed_opts = list(dict.fromkeys(ed_opts))
    best = None
    for n in range(len(segs), 0, -1):                       # the first n joined titles
        for combo in itertools.product(*seg_opts[:n]):
            ts = wscore(combo[0], segs[0]) + sum(4 + wscore(c, sg) for c, sg in zip(combo[1:], segs[1:]))
            for ss in ((sub, 0.3 * len(' '.join(sub).split())), ([], 0)):
                if ss[0] and not sub: continue
                for esc, e in ed_opts:
                    nm = build(list(combo), joins[:n - 1], ss[0], author, e, kinds)
                    if B(nm) > limit: continue
                    sc = ts + ss[1] + esc
                    if best is None or sc > best[0] or (sc == best[0] and B(nm) > B(best[1])): best = (sc, nm)
    if best: return best[1]
    w = segs[0].split()                                    # last resort: whole words off the title's end, no edition
    while len(w) > 2 and B(build([' '.join(w)], [], [], author, '', kinds)) > limit: w.pop()
    while len(w) > 1 and norm(w[-1]) in WEAK_END: w.pop()
    n = build([' '.join(w)], [], [], author, '', kinds)
    return n if B(n) <= limit else build([' '.join(w)], [], [], '', '', kinds)

def volume(nn, title, label='', limit=LIMIT, author='', edition='', year=''):
    """«NN - <title> - <author> - ت <editor> - <publisher> <city> <year> - <label>»: everything the folder says, then the
    volume's label (owner 2026-10-10: the volume files carry all the information too), shortened only when needed"""
    label = tidy(re.sub(r'^\((.*)\)$', r'\1', label or ''))
    pre, post = f'{nn} - ', f' - {label}' if label else ''
    return pre + compose(title, author, edition, limit - B(pre) - B(post), year=year) + post

def volumes(title, items, author='', edition='', year='', limit=LIMIT):
    """the files of one set: ONE shared part (title, author, editor, publisher…) for every volume, sized for the longest
    «NN - … - <label>», so that no volume says less than another; items = [(nn, label)] → names (without «.pdf»)"""
    clean = [(nn, tidy(re.sub(r'^\((.*)\)$', r'\1', lb or ''))) for nn, lb in items]
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
