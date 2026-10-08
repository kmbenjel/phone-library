"""Compare the phone library with the locally installed Shamela: which Shamela books have a PDF on the phone.
Output: data/compare/shamela-matches.tsv"""
import csv, json, os, re, sys
from collections import defaultdict
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from textnorm import title_key, author_tokens, norm
J = lambda p: os.path.join(ROOT, p)
cat = json.load(open(J('data/catalog.json')))
# A Waqfeya name is a name of the phone book only when it shares a word with the book's own title (2026-10-08: some links
# came from archive.org items that bundle other books — «تفسير المنار» ⟵ «الفرج بعد الشدة»); a collection keeps all its
# links (its items). Doubtful links → data/review/waqfeya-link-doubts.tsv
_COLL = re.compile(r'^(?:سلسلة|مؤلفات|مجموع|مجموعة|رسائل|الرسائل|آثار|الأعمال|موسوعة|جوامع|مجلة)')
_GEN = set('كتاب رساله في علي من عن الي و بن ابن ابي ابو عبد الله شرح'.split())
def _ws(t): return {w[2:] if w.startswith('ال') and len(w) > 3 else w for w in norm(t).split() if w not in _GEN and len(w) > 1}
doubts = []
def waq_names(b):
    if _COLL.match(b['folder']) or b['cat'] == 'الجوامع': return [w['name'] for w in b.get('waqfeya', [])]
    own = _ws(b['title']) | _ws(re.split(r'\s+-\s+|\s\(', b['folder'])[0])
    out = []
    for w in b.get('waqfeya', []):
        if own & _ws(w['name']): out.append(w['name'])
        else: doubts.append((b['cat'] + '/' + b['folder'], w.get('id', ''), w['name']))
    return out
# every title a phone book is known by: folder title, Waqfeya names, per-file bracketed titles (bucket folders)
keys = defaultdict(set)   # title key -> set(book id)
auth = {}
for b in cat['books']:
    b['waqfeya_names'] = waq_names(b)
    ts = {b['title']} | set(b['waqfeya_names'])
    for t in ts:
        k = title_key(t)
        if k: keys[k].add(b['id'])
    auth[b['id']] = author_tokens(b.get('author', ''))
by_first = defaultdict(list)
for k in keys: by_first[k.split()[0]].append(k)

# Additional inverted index on clean title tokens for fallback matching
word_to_books = defaultdict(set)
# Additional inverted index on clean title tokens for fallback matching
word_to_books = defaultdict(set)
phone_books = {}
phone_full_tks = {}
phone_folder_words = {}
phone_authors = {}
for b in cat['books']:
    phone_books[b['id']] = b
    tk = title_key(b['title'])
    fk = title_key(b['folder'])
    phone_folder_words[b['id']] = set(fk.split())
    phone_authors[b['id']] = auth[b['id']] | author_tokens(b['folder'])
    
    ts = {b['title']} | set(b['waqfeya_names'])
    phone_full_tks[b['id']] = [title_key(t) for t in ts if t]
    
    all_words = set(tk.split()) | set(fk.split())
    for w in all_words:
        if len(w) > 2 and w not in ('كتاب', 'رسالة', 'جزء', 'شرح', 'مختصر'):
            word_to_books[w].add(b['id'])

# works contained in a phone book (scripts/contents.py; owner 2026-10-07: count them as present, never split the volume)
contained = defaultdict(set)
_CF = J('data/editions/contents.json')
if os.path.exists(_CF):
    _ids = {f"{b['cat']}/{b['folder']}": b['id'] for b in cat['books']}
    for _k, _items in json.load(open(_CF, encoding='utf-8')).items():
        for _it in _items:
            for _sid in _it.get('sh') or []:
                if _k in _ids: contained[_sid].add(_ids[_k])

# «cover» tier (2026-10-08, owner: «تستطيع تماما تمييز ما هو غير موجود؟»): a Shamela title is present when every one of its
# words that tells works apart is in a phone book's names, the first word agrees, and the author agrees. Words compared without
# «ال» and with «و» joined; edition tails (- ط …, - ت …), attributions («للبيهقي», «لابن تيمية») and honorifics are left out;
# a part or recension («السفر الثاني», «رواية ابن الصلت») must be named on the phone too. Titles of two words must be equal.
FUNC = set('في علي من عن الي و ما او مع التي الذي منه منها فيه فيها'.split())
FILL = set('امام قاضي شيخ حافظ علامه اسلام كتاب رساله شريف نبويه كريم صلي الله عليه وسلم سلم رضي عنه عنهم تعالي بن ابي ابو ابا عبد'.split())
TAIL = re.compile(r'^(?:(?:ط|ت)\s|ط\.|ضمن|تحقيق|بتحقيق|طبعة|الطبعة|المنسوب|منسوب|دراسة|جامعة|رسالة|مخطوط|نشرة|ق\s*\d|\d)')
PART = re.compile(r'^(?:السفر|الجزء|القسم|المجلد|رواية|المستوى)\s')
JOINW = re.compile(r'\s(?:ويليه|ويليها|ويليهما|ومعه|ومعها|ومعهما|وبهامشه|وبهامشها|وبذيله|وبذيلها|ويذيله|ويذيلها|وعليه|وعليها|ويتلوه|وتليه)[\s\-–]')
def tok(w):
    if w == 'ابن': return 'بن'
    if w in ('ديوان', 'الديوان'): return 'شعر'
    if w.startswith('بال') and len(w) > 5: return w[3:]
    if w.startswith('وال') and len(w) > 5: return w[3:]
    if w.startswith('ال') and len(w) > 3 and w != 'الله': return w[2:]
    return w
def words(t):
    return [tok(w) for w in norm(t).split() if w not in FUNC and len(w) > 1]
def shamela_variants(title, at):
    """the Shamela title as word lists: each «=» part, edition tails and the author's own attribution left out"""
    t = re.sub(r'\([^)]*\)|\[[^\]]*\]', ' ', title)
    parts = [x.strip() for x in t.split(' - ')]
    ata0 = {tok(a) for a in at}
    def kept(x):                                        # «- أخبار المكيين», «- الياقوتة», «- تراجم ساقطة» name a part: kept
        if PART.match(x): return True
        if TAIL.match(x): return False
        xs = [y for y in words(x) if y not in FILL and not y.isdigit()]
        return bool(xs) and not all(y in ata0 for y in xs)          # «- الضياء المقدسي»: the author, left out
    head = parts[0] + ''.join(' ' + re.split(r'\s+(?:ط|ت)\s', ' ' + x + ' ')[0] for x in parts[1:] if kept(x))
    out = []
    for v in head.split('='):
        v = JOINW.split(' ' + v + ' ')[0]                 # «طبقات الصوفية ويليه ذكر النسوة»: the main work is the first
        w = words(v)
        if w and w[0] == 'كتاب' and len(w) > 2: w = w[1:]
        ata = {tok(a) for a in at}; strip = set()
        for i in range(len(w) - 1, 0, -1):                 # «… للبيهقي», «… لابن أبي خيثمة»: the author's own name
            first = w[i][2:] if w[i].startswith('لل') else w[i][1:] if w[i].startswith('ل') else None
            if first is None: continue
            tail = [tok(first)] + w[i + 1:]
            if any(x in ata for x in tail) and all(x in ata or x in FILL or x in ('بن', 'ابن') for x in tail):
                w = w[:i]; strip = {a for a in at if tok(a) in tail}
            break
        if w: out.append((w, strip))
    return out
pvars, pset, ptitle, phead, phead2 = {}, {}, {}, defaultdict(set), defaultdict(set)
def phead_of(bid): return {[x for x in v if x not in FILL][0] for v in pvars[bid] if [x for x in v if x not in FILL]}
for b in cat['books']:
    raw = [b['title'], re.split(r'\s+-\s+|\s\(', b['folder'])[0]] + b['waqfeya_names']
    vs = []
    for x in raw:
        x = re.split(r'\s+-\s+|\s+ط\s|\s+ت\s', ' ' + re.sub(r'\([^)]*\)', ' ', x) + ' ')[0]
        for y in re.split(r'=', x):
            for z in JOINW.split(' ' + y + ' '):
                w = words(z)
                if w and w[0] == 'كتاب' and len(w) > 1: w = w[1:]
                if w: vs.append(w)
    pvars[b['id']] = vs
    ptitle[b['id']] = {x for v in vs for x in v}
    pset[b['id']] = ptitle[b['id']] | {tok(a) for a in phone_authors[b['id']]}
    for v in vs:
        h = [x for x in v if x not in FILL]
        if h: phead[h[0]].add(b['id'])
        if len(h) > 1: phead2[h[1]].add(b['id'])
def mand(core):                                            # the two words after «رواية», «السفر», «الجزء» … name the part
    out = set()
    for i, x in enumerate(core):
        if x in ('روايه', 'بروايه', 'سفر', 'جزء', 'قسم', 'مجلد'): out |= set(core[i + 1:i + 3])
    return out
def has(t, P):                                              # «و», «ب», «ل» joined to a word: «بعلم» = «علم», «لألفية» = «ألفية»
    return t in P or any(c + t in P for c in ('و', 'ب', 'ل', 'لل', 'بال', 'وال')) or \
        (len(t) > 4 and t[0] in 'وبل' and (t[1:] in P or tok(t[1:]) in P))
# a work derived from another (abridgement, excerpt, supplement, commentary …) is not the work itself
DERIV = set(words('مختصر اختصار زوائد تهذيب مقتطفات منتقى منتخب انتخاب تكملة ذيل صفحات تعليق تعليقات حاشية شرح نظم تخريج '
                  'فهارس فهرس دراسة نقد رد ترتيب تقريب مستدرك استدراك قطعة مجلس مجلسان مجالس جزء السفر الأول الثاني الثالث '
                  'الرابع الخامس رواية صحيح ضعيف متن ساقطة مختار المختار منظومة أرجوزة قصيدة ألفية نونية لامية متمم تتمة صلة'))
AMBIG = set(words('جزء أحاديث حديث مجلس أمالي فوائد مشيخة نسخة الجزء مسند معجم'))   # two-word hadith-part titles stay exact

COMMON = set(norm('الحسن الحسين محمد أحمد علي عمر عثمان إبراهيم يحيى إسماعيل يوسف سليمان موسى عيسى داود خالد سعيد سعد '
                  'جعفر حفص بكر زيد يزيد منصور القاسم الرحمن العزيز الملك الوهاب الفضل العباس طاهر صالح حسن حسين '
                  'مصطفى عمرو عامر أيوب حمد ناصر الدين الإمام مؤلف مجهول '
                  # honorific names shared by many («تقي الدين», «العز») and the second part of «عبد …» names
                  'تقي شمس جمال بدر زين عز العز علاء سراج محيي شهاب فخر الفخر نجم صلاح برهان عماد مجد موفق ضياء رضي كمال صدر '
                  'المالكي الحنفي الشافعي الحنبلي الظاهري الدمشقي البغدادي المصري بنت نصر '
                  'قطب نور السلام الرحيم الكريم الحميد المجيد اللطيف الغني القادر الواحد الباقي الجبار الحليم الوهاب').split())
# how many Shamela authors carry each name (data/shamela/authors.jsonl): a name carried by many («نصر»: 43) does not tell
# two people apart on its own; a rare one («سريج»: 2) does
NAMEFREQ = defaultdict(int)
if os.path.exists(J('data/shamela/authors.jsonl')):
    for _l in open(J('data/shamela/authors.jsonl'), encoding='utf-8'):
        _a = json.loads(_l)
        for _w in author_tokens(_a['name']) | author_tokens(_a.get('full', '')): NAMEFREQ[tok(_w)] += 1
pauth, praw, plast = {}, {}, {}
def last_name(a):
    """the name that tells the person apart: the last word of the short name that is not a common one («رقية بنت نصر الله
    نياز» → نياز, «محمد بن نصر المروزي» → المروزي, «ابن رجب الحنبلي» → رجب)"""
    ws = [tok(w) for w in norm(a).split() if w in author_tokens(a) and w not in COMMON]
    return ws[-1] if ws else ''
_ED = re.compile(r'^\s*(?:ط|ت)[\s.\-]')                              # «- ط. الأوقاف», «ت- الرحيلي»: an edition, not an author
def _an(x): return re.sub(r'عبد(?=ال)', 'عبد ', x or '')             # «عبدالهادي» = «عبد الهادي»
for b in cat['books']:
    tail = re.sub(r'\([^)]*\)', ' ', b['folder']).rsplit(' - ', 1)
    tail = tail[1] if len(tail) == 2 and not _ED.match(tail[1]) else ''
    ba = '' if _ED.match(b.get('author', '') or '') else b.get('author', '')
    pauth[b['id']] = author_tokens(_an(ba)) | author_tokens(_an(tail))
    praw[b['id']] = ' ' + norm(_an(ba).split('؛')[0]) + ' | ' + norm(_an(tail)) + ' | ' + norm(_an(b['folder'])) + ' '
    plast[b['id']] = last_name(_an(ba).split('؛')[0] or tail)
full_at, cur_author, card_toks = set(), '', set()
def agree(at, bid):
    """the Shamela author and the phone book's author are the same person: a shared name that is not a common one, or
    the phone's author name read inside the full name on the Shamela card («الجماعيلي» in «عبد الغني … المقدسي الجماعيلي»)"""
    A = {tok(a) for a in at - COMMON}; PA = {tok(a) for a in pauth[bid] - COMMON}
    shared = A & PA
    if shared and (shared & {last_name(cur_author), plast[bid]} or len(shared) >= 2 or
                   any(NAMEFREQ[x] < 20 for x in shared)): return True          # not one common given name
    if any(has(a, ptitle[bid]) for a in A): return True
    if not A and at and {tok(a) for a in at} <= {tok(a) for a in pauth[bid]} and not PA: return True   # «الشافعي» = «الإمام الشافعي»
    if len(cur_author.split()) >= 2 and (f' {cur_author} ' in praw[bid] or f' ل{cur_author} ' in praw[bid]): return True  # «عبد الله بن أحمد» written alike
    if PA and full_at and PA <= full_at and (len(PA) >= 2 or any(NAMEFREQ[x] < 20 for x in PA)): return True
    return bool(PA) and PA <= card_toks         # the phone's «author» is the editor, abridger or compiler the card names
def cover(title, at, collection=False):
    found = set()
    if any(norm(x) in ('مولف', 'مجهول') for x in at) or norm(title).startswith('مولف'): return found
    for sv, strip in shamela_variants(title, at):
        core = [x for x in sv if x not in FILL]
        if len(core) == 1 and not collection:
            for bid in phead.get(core[0], set()):
                if agree(at, bid) and any([x for x in v if x not in FILL][:1] == core and not set(v) & (DERIV | CUT) - {'روايه'} and
                                          (len([x for x in v if x not in FILL]) <= 2 or [x for x in v if x not in FILL][1] in SIZE)
                                          for v in pvars[bid]): found.add(bid)
            continue
        if len(core) < 2: continue
        for bid in phead.get(core[0], set()) | (phead2.get(core[0], set()) if len(core) >= 4 else set()):
            T = ptitle[bid]
            miss = [x for x in core if not has(x, T)]
            if set(miss) & mand(core): continue                 # «رواية الحصكفي» is not «رواية أبي نعيم»
            if len(core) == 2 and miss == [core[1]] and core[1] in {tok(a) for a in at - COMMON} and core[0] not in AMBIG \
                    and core[1] in {tok(a) for a in pauth[bid]}:
                pa = {tok(a) for a in pauth[bid]} - {tok(a) for a in at}      # «قواعد ابن رجب» = «القواعد» by ابن رجب
                if any([x for x in v if x not in FILL][:1] == [core[0]] and not set(v) & pa for v in pvars[bid]):
                    found.add(bid)
                continue
            if len(miss) > (1 if len(core) >= 3 else 0) or (miss and not has(miss[0], pset[bid])): continue
            if core[0] not in phead_of(bid) and any(v and [x for x in v if x not in FILL][:1] and
                    [x for x in v if x not in FILL][0] in DERIV and [x for x in v if x not in FILL][0] not in core
                    for v in pvars[bid] if core[0] in v): continue     # «شرح ألفية العراقي» is not «ألفية العراقي»
            if not agree(at, bid): continue                    # the author agrees (not on a common name)
            if strip and not strip & pauth[bid]: continue             # «… للآبري»: that name must be the phone book's author
            if len(core) == 2 and not collection and not any(
                    ([x for x in v if x not in FILL] == core) if core[0] in AMBIG else
                    (set(core) <= set([x for x in v if x not in FILL][:3])) for v in pvars[bid]): continue
            found.add(bid)
        if found or len(core) < 3: continue
        # the phone's own title is the whole of a longer Shamela title («شرح الشاطبية فتح الوصيد في شرح القصيد» ⊃ «فتح الوصيد
        # في شرح القصيد»): every phone word in the Shamela title, at least three, and the extra Shamela words derive nothing
        cs = set(core)
        for bid in set().union(*(phead.get(x, set()) for x in cs)):
            if not agree(at, bid): continue
            if strip and not strip & pauth[bid]: continue
            for v in pvars[bid]:
                vc = [x for x in v if x not in FILL]
                if len(vc) >= 3 and len(vc) >= 0.5 * len(cs) and all(has(x, cs) for x in vc):
                    extra = {x for x in cs if not has(x, set(vc))}
                    if not extra & (DERIV | mand(core)): found.add(bid); break
    return found
LEAD = set(words('أخبار عنوان ذم قصة معجم'))        # «أخبار الأذكياء» = «الأذكياء», «ذم الغيبة» = «الغيبة», «قصة الأندلس»
SKIP_S = set(words('شرح حاشية كتاب متن')) | LEAD     # «شرح الخرشي» = «الخرشي على مختصر خليل» when the author agrees
SKIP_P = set(words('جزء الجزء فيه كتاب')) | LEAD     # «جزء فيه حديث لوين» = «حديث لوين»
def heads(v, skip):
    c = [x for x in v if x not in FILL] or list(v)
    while len(c) > 1 and c[0] in skip: c = c[1:]
    return c[:1]
def plausible(title, at, bid):
    """the older tiers (prefix, smart-tokens, in-collection) checked again (2026-10-08): the author agrees, the Shamela title
    starts where a phone title starts, and nothing the Shamela title adds makes it another work (an abridgement, a part …)"""
    A = {tok(a) for a in at - COMMON}; PA = {tok(a) for a in pauth[bid] - COMMON}
    unknown = (not at and not full_at and len(cur_author.split()) < 2) or any(norm(x) in ('مولف', 'مجهول') for x in at)
    svs = shamela_variants(title, at)
    if not svs: return True
    short = all(len([x for x in sv if x not in FILL]) <= 2 for sv, _ in svs)
    if not unknown:
        if PA and not agree(at, bid): return False
        if not PA and short and not any(has(a, ptitle[bid]) for a in A) and not agree(at, bid): return False  # «التوبة» of an unknown author is not Ibn Asakir's
    pheads = {h for v in pvars[bid] for h in heads(v, SKIP_P) + heads(v, ())}
    ok = False
    for sv, strip in svs:
        core = [x for x in sv if x not in FILL] or sv                      # «الرسالة», «الكتاب»: the word itself
        if unknown and not any([x for x in v if x not in FILL] == core for v in pvars[bid]): continue
        if not set(heads(core, SKIP_S)) & pheads and core[0] not in pheads: continue
        extra = {x for x in core if not has(x, ptitle[bid])}
        for x in core[:2]:
            if x in SKIP_S: extra.discard(x)
        if extra & (DERIV | mand(core)): continue
        if extra and not PA and not unknown and not agree(at, bid): continue   # longer Shamela title, phone author unknown
        if strip and PA and not {tok(a) for a in strip} & PA: continue
        ok = True; break
    if not ok: return False
    for v in pvars[bid]:                                   # «شرح نواقض الإسلام للعدني» names another author
        last = v[-1] if v else ''
        if len(v) > 2 and last.startswith('ل') and len(last) > 4 and not unknown:
            nm = last[2:] if last.startswith('لل') else last[1:]
            if tok(nm) in ptitle[bid] and tok(nm) not in A and tok('ال' + nm) not in A and nm not in A and not has(nm, set(A)):
                if not any(x in A for x in v): return False
    return True
PARTOF = re.compile(r'ضمن\s*[«"](.+?)[»"]')

rows, vetoed = [], []
col_keywords = {'مجموع', 'مؤلفات', 'رسائل', 'أعمال', 'فتاوى', 'تراث', 'موسوعة', 'جامع', 'الجامع'}

def named_part(title, at):
    """the Shamela title names a part, a recension or a section after « - » («- السفر الثاني», «- رواية أبي مصعب», «- الياقوتة»)"""
    return any(PART.match(x) or not TAIL.match(x) and {y for y in words(x) if y not in FILL and not y.isdigit()} - {tok(a) for a in at}
               for x in [y.strip() for y in re.sub(r'\([^)]*\)', ' ', title).split(' - ')][1:])
SIZE = set(words('الكبرى الكبير الصغرى الصغير الوسيط الأوسط'))       # «المدونة» = «المدونة الكبرى»
def stem_in(w, ws):                                        # «التابعين» in «لتابعي أهل المدينة»
    return has(w, ws) or len(w) >= 4 and any(c.lstrip('لبو')[:4] == w[:4] for c in ws if len(c) >= 4)
def part_words(title, at):
    return {y for x in [y.strip() for y in re.sub(r'\([^)]*\)', ' ', title).split(' - ')][1:] if not TAIL.match(x)
            for y in words(x) if y not in FILL and not y.isdigit() and y not in {tok(a) for a in at}}
CUT = set(words('مختصر اختصار زوائد تهذيب مقتطفات منتقى منتخب انتخاب تكملة ذيل صفحات قطعة مجلس مجلسان مجالس جزء مختار المختار '
                'متمم تتمة صلة السفر ساقطة'))                      # a selection, abridgement or part of a book
def match_title(title, at, sid):
    """one Shamela title → (phone book ids, how)"""
    k = title_key(title)
    hit, how = set(), ''
    if k in keys: hit, how = set(keys[k]), 'exact'
    else:
        kw = k.split()
        for pk in by_first.get(kw[0] if kw else '', []):
            if pk.startswith(k + ' ') or k.startswith(pk + ' '):
                if len(kw) >= 3 and len(pk.split()) >= 3: hit |= keys[pk]; how = 'prefix'
                elif at:                                   # short title: only with a matching author
                    ok = {h for h in keys[pk] if auth[h] & at}
                    if ok: hit |= ok; how = 'prefix+author'
    if hit and len(k.split()) <= 2 and at:        # short titles are ambiguous: reject a *different* known author
        hit = {h for h in hit if not auth[h] or auth[h] & at}; how = '' if not hit else how
    if not hit:
        # Smart fallback: token matching + author verification
        kw = [w for w in k.split() if len(w) > 2 and w not in ('كتاب', 'رسالة', 'جزء', 'شرح', 'مختصر')]
        if len(kw) >= 2:
            candidates = word_to_books[kw[0]]
            for w in kw[1:]:
                candidates = candidates & word_to_books[w]
                if not candidates: break
            if candidates:
                valid = set()
                for cid in candidates:
                    cb_at = phone_authors[cid]
                    if not at or not cb_at or (at & cb_at):
                        valid.add(cid)
                if valid:
                    hit, how = valid, 'smart-tokens'
                    
    if not hit and at:
        # Check strictly for attached books by the same author
        valid = set()
        for cid, cb in phone_books.items():
            cb_at = phone_authors[cid]
            if cb_at and (at & cb_at):
                # Rule A: Attached books (exact phrase match within full Waqfeya names)
                tk_list = phone_full_tks[cid]
                kw = k.split()
                # Ensure the missing title is not just a single common word, or check if it matches as a whole phrase
                if len(kw) >= 2 or len(k) >= 5:
                    if any(f" {k} " in f" {t} " for t in tk_list):
                        valid.add(cid)
        if valid:
            hit, how = valid, 'in-collection'
            
    if hit and how == 'exact' and at and not any(norm(x) in ('مولف', 'مجهول') for x in at):   # the same title by another author
        kept = {h for h in hit if not pauth[h] - COMMON or agree(at, h)}
        if kept != hit: vetoed.append((str(sid), title, how + ' (author)', ' '.join(str(h) for h in sorted(hit - kept))))
        hit = kept; how = how if hit else ''
    if hit and how == 'exact' and named_part(title, at):          # «موطأ مالك - رواية أبي مصعب», «الطبقات الكبرى - متمم التابعين»
        kept = {h for h in hit if plausible(title, at, h)}
        if kept != hit: vetoed.append((str(sid), title, how, ' '.join(str(h) for h in sorted(hit - kept))))
        hit = kept; how = how if hit else ''
    if hit and how in ('prefix', 'prefix+author', 'smart-tokens', 'in-collection'):
        kept = {h for h in hit if plausible(title, at, h)}
        if kept != hit: vetoed.append((str(sid), title, how, ' '.join(str(h) for h in sorted(hit - kept))))
        hit = kept; how = how if hit else ''
    if not hit and sid in contained:          # printed inside a phone book (collection, «ويليه», commentary kept with its text)
        hit, how = contained[sid], 'contained'
    if not hit:
        hit = cover(title, at); how = 'cover' if hit else ''
    if not hit and PARTOF.search(title):               # Shamela itself says «ضمن «آثار المعلمي»»: the collection is on the phone
        hit = cover(PARTOF.search(title).group(1), at, collection=True); how = 'part-of' if hit else ''

    return hit, how
# the Shamela book cards (scripts/export_shamela_cards.py; owner 2026-10-08): the title as printed and the author's full name
CARDS = {}
if os.path.exists(J('data/shamela/cards.jsonl')):
    for _l in open(J('data/shamela/cards.jsonl'), encoding='utf-8'):
        _c = json.loads(_l); CARDS[_c['id']] = _c
AUTHFULL = {}                                          # author id → the name and full-name line of the Shamela biography
if os.path.exists(J('data/shamela/authors.jsonl')):
    for _l in open(J('data/shamela/authors.jsonl'), encoding='utf-8'):
        _a = json.loads(_l); AUTHFULL[str(_a['id'])] = _a['name'] + ' ' + _a.get('full', '')
full_at, cur_author, card_toks = set(), '', set()
for r in csv.DictReader(open(J('data/shamela/books.tsv')), delimiter='\t'):
    sid = int(r['book_id']); at = author_tokens(r['author']); card = CARDS.get(sid, {})
    cur_author = norm(r['author'])
    full_at = {tok(x) for x in author_tokens(re.sub(r'\([^)]*\)|\[[^\]]*\]', ' ', card.get('author', '')) + ' ' +
                                             AUTHFULL.get(r.get('author_id', ''), ''))} - {tok(x) for x in COMMON}
    card_toks = {tok(x) for x in author_tokens(' '.join(                 # the people the card names for the text itself
        l.split(':', 1)[1] for l in card.get('card', '').split('\n') if ':' in l[:40] and
        re.search(r'تحقيق|حقق|جمع|اختصار|اختصره|انتخاب|ترتيب|رتبه|شرح|الشارح|تهذيب|إعداد|المحقق|اعتنى|ضبط|تخريج|رواية|مؤلف الأصل',
                  l.split(':', 1)[0])))}
    hit, how = match_title(r['title'], at, sid)
    ct = card.get('title', '')
    if not hit and ct and (at or full_at) and title_key(ct) != title_key(r['title']) and \
            not (set(words(r['title'].split(' - ')[0])) - set(words(ct))) & CUT:        # «المختار من …»: not the card's whole book
        hit, how = match_title(ct, at, sid)
        hit = set() if named_part(r['title'], at) and not all(stem_in(w, set(words(ct))) for w in part_words(r['title'], at)) else {h for h in hit if plausible(ct, at, h) or how.startswith(('contained', 'part-of'))}
        how = how + ' (card title)' if hit else ''
    rows.append([r['book_id'], r['title'], r['author'], r['death'], r['category'], r['has_pdf'], how, ' '.join(map(str, sorted(hit)))])
os.makedirs(J('data/review'), exist_ok=True)
with open(J('data/review/waqfeya-link-doubts.tsv'), 'w', encoding='utf-8') as f:
    f.write('phone_book\twaqfeya_id\twaqfeya_name\n'); f.writelines('\t'.join(d) + '\n' for d in doubts)
with open(J('data/review/shamela-vetoed.tsv'), 'w', encoding='utf-8') as f:
    f.write('shamela_id\ttitle\ttier\tphone_book_ids\n'); f.writelines('\t'.join(v) + '\n' for v in vetoed)
with open(J('data/compare/shamela-matches.tsv'), 'w') as f:
    w = csv.writer(f, delimiter='\t'); w.writerow(['shamela_id', 'title', 'author', 'death', 'category', 'shamela_pdf', 'match', 'phone_book_ids']); w.writerows(rows)
found = sum(1 for r in rows if r[7])
print(f'shamela books: {len(rows)}  on phone: {found} ({found*100/len(rows):.1f}%)')

