"""Names with a missing, cut or wrong author, or a cut title (owner 2026-10-09, the index: «أخلاق النبي وآدابه صلى الله
عليه — الحباني», «أضواء من المولد السعيد — محمد بن»: «المعلومات بها إخلال كبير») → a rename plan from evidence only.

A book is taken when its author is empty, cut («… بن», «ابن»), one bare word that is not a name's known form, or a rare
short form no Shamela author carries (Waqfeya's «الحباني» for أبو الشيخ الأصبهاني), or when its title ends on a particle.
Evidence, strongest first:
  1. Shamela: the book matched to Shamela works of ONE author (data/compare/shamela-matches.tsv, author agreement checked
     there) → the author's common name as Shamela gives it (the part before «،»), and its title when the book's title is
     a cut form of it;
  2. Waqfeya: the record linked to the book's own file by exact size (data/phone/provenance.tsv) → its author (short form)
     and its title (when the book's title is a cut form of it), its editor and publisher when the name has no edition.
A book with no evidence goes to the review list (data/review/name-fix-review.tsv) — never guessed.
Names follow AGENTS.md §4: a folder «<title> - <author> (<edition>)», a single file «<short title> - <author> (<edition>).pdf»;
the honorific formulas are never cut in the middle («صلى الله عليه» without «وسلم»): a short title drops them whole.
Usage: python3 scripts/name_fix_plan.py plans/NNN-name-fix.tsv"""
import csv, json, os, re, sys, unicodedata
from collections import Counter, defaultdict
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from textnorm import norm, title_key, author_tokens
from rename_plan import clean, fit, short_title, author_short, researcher_short, publisher_short, split_wname, redundant, COLLECTION
J = lambda p: os.path.join(ROOT, p)
N = lambda s: unicodedata.normalize('NFC', s)
TAIL = re.compile(r'(^|\s)(في|من|على|عن|الى|إلى|و|بن|ابن|أبي|أبو|عبد|ل|ب)$')
HONOR = re.compile(r'\s*(صلى الله عليه(?: وآله)?(?: وسلم)?|رضي الله عنهما?|رضي الله عنها|رحمه الله(?: تعالى)?|عز وجل|جل جلاله|عليه السلام)\s*$')

def shamela_name_freq():
    f = Counter()
    for l in open(J('data/shamela/authors.jsonl'), encoding='utf-8'):
        a = json.loads(l)
        for w in set(norm(a['name'] + ' ' + a.get('full', '')).split()): f[w] += 1
    return f

def defect(b, freq):
    a, t = (b.get('author') or '').strip(), (b.get('title') or '').strip()
    out = []
    if not a: out.append('no author')
    elif re.search(r'(^|\s)(بن|ابن|أبو|أبي|عبد)$', a) or len(a) <= 2: out.append('author cut')
    elif len(a.split()) == 1 and not a.startswith('ابن') and freq[norm(a)] == 0: out.append('author unknown to Shamela')
    if TAIL.search(norm(t)) or re.search(r'صلى الله عليه$', t): out.append('title cut')
    return out

def drop_attribution(title, author):
    """«التقريب والإرشاد الصغير في أصول الفقه للباقلاني» with the author «الباقلاني»: the closing «لفلان» names him — dropped"""
    if not author: return title
    w, a_ = title.split(), norm(author)                 # «… للخطيب البغدادي» with «الخطيب البغدادي»: the whole name
    forms = {'ل' + a_, 'لل' + a_[2:] if a_.startswith('ال') else 'ل' + a_}
    for k in range(min(4, len(w) - 1), 0, -1):
        if norm(' '.join(w[-k:])) in forms: return ' '.join(w[:-k])
    last = norm(author).split()[-1].removeprefix('ال')
    m = re.search(r'\s+(?:ل|لل|لابن\s+|لأبي\s+)(\S+)$', title)
    if m and norm(m.group(1)).removeprefix('ال').removeprefix('ل') == last: return title[:m.start()].strip()
    return title

def common_name(a):
    a = re.sub(r'\s*\([^)]*\)', '', a or '').strip()
    return a.split('،')[0].strip()

def main(out):
    freq = shamela_name_freq()
    books = json.load(open(J('data/catalog.json'), encoding='utf-8'))['books']
    idx = {N(l.split('\t')[0]) for l in open(J('data/phone/index-now.tsv'), encoding='utf-8')}
    prov = {N(r['path']): r for r in csv.DictReader(open(J('data/phone/provenance.tsv'), encoding='utf-8'), delimiter='\t')}
    det = {}
    for l in open(J('data/waqfeya/details.jsonl'), encoding='utf-8'):
        try: d = json.loads(l)
        except ValueError: continue
        det[d.get('_id')] = d
    sh = defaultdict(list)
    for r in csv.DictReader(open(J('data/compare/shamela-matches.tsv'), encoding='utf-8'), delimiter='\t'):
        for i in (r['phone_book_ids'] or '').split(): sh[i].append(r)
    plan, review, stats = [], [], Counter()
    for b in books:
        why = defect(b, freq)
        if not why: continue
        if COLLECTION.match(b['folder']) or b['cat'] == 'الجوامع': continue     # magazines, series, collections: no author (§4)
        plain = N(f"{b['cat']}/{b['folder']}.pdf") in idx
        paths = [N(f"{b['cat']}/{b['folder']}.pdf")] if plain else [N(f"{b['cat']}/{b['folder']}/{f[0]}") for f in b['files']]
        recs = {prov[p]['waqfeya_id'] for p in paths if p in prov and prov[p].get('waqfeya_id')}
        wrec = [det[x] for x in recs if x in det]
        sauth = {common_name(r['author']) for r in sh.get(str(b['id']), []) if r['author']}
        stitles = [r['title'] for r in sh.get(str(b['id']), [])]
        title, author, ed = b['title'], (b.get('author') or '').strip(), (b.get('edition') or '').strip()
        m_ = re.search(r'\s+(?:تحقيق|بتحقيق|ت)\s*[:.]?\s+(.+)$', title)          # «تاريخ بغداد … تحقيق بشار عواد»
        if m_ and len(title[:m_.start()].split()) >= 2:
            title = title[:m_.start()].strip(); ed = ed or f'ت {m_.group(1).strip()}'
        new_author, new_title, src = '', title, []
        generic = len(norm(title).split()) <= 2 and not author             # «الحكمة» of no known author: too common a title
        if len(sauth) == 1 and not generic: new_author = next(iter(sauth)); src.append('الشاملة')
        elif len(wrec) == 1:
            wa = (wrec[0].get('author') or {}); wa = wa.get('name') if isinstance(wa, dict) else wa
            new_author = author_short(wa or ''); src.append('الوقفية (الحجم بالبايت)') if new_author else None
        if 'title cut' in why:
            cands = [split_wname(w['name'])[0] for w in wrec] + [re.sub(r'\s+-\s+.*$', '', t) for t in stitles]
            k = title_key(title)
            full = [c for c in cands if title_key(c).startswith(k) and len(title_key(c)) > len(k)]
            if full: new_title = clean(min(full, key=len)); src.append('العنوان من السجل')
        if 'author unknown to Shamela' in why and new_author and author and set(norm(author).split()) & set(norm(new_author).split()):
            new_author = author                       # «النهشلي» / «النهشلي القيرواني»: the same name, left as it is
        if not ed and len(wrec) == 1:
            r_, p_ = researcher_short(wrec[0].get('researcher')), publisher_short(wrec[0].get('publisher'))
            ed = f'ت {r_} - {p_}' if r_ and p_ else (f'ت {r_}' if r_ else (f'ط {p_}' if p_ else ''))
        if ('no author' in why or 'author cut' in why or 'author unknown to Shamela' in why) and not new_author:
            review.append((b['cat'] + '/' + b['folder'], ', '.join(why), 'no evidence')); stats['review'] += 1; continue
        if 'title cut' in why and new_title == title:
            review.append((b['cat'] + '/' + b['folder'], ', '.join(why), 'cut title, no record completes it')); stats['review'] += 1; continue
        if ed and not re.match(r'^(ت|ط)\s', ed) and len(ed.split()) <= 2:
            review.append((b['cat'] + '/' + b['folder'], ', '.join(why), f'«({ed})» is not an edition')); stats['review'] += 1; continue
        if not new_author: new_author = author
        m = re.search(r'\s+(?:ل|لل|لابن\s+|لأبي\s+)(\S+)$', new_title)     # «… للقفطي» but the evidence names another man
        if m and new_author and norm(m.group(1)).removeprefix('ال').removeprefix('ل') not in norm(new_author).replace('ال', ' ').split():
            review.append((b['cat'] + '/' + b['folder'], ', '.join(why), f'the title names «{m.group(1)}», the evidence «{new_author}»'))
            stats['review'] += 1; continue
        if re.search(r'(^|\s|-)(خ|رس|و ط|خ ط)(\s|$)', ed):                     # old collection codes, not an edition
            review.append((b['cat'] + '/' + b['folder'], ', '.join(why), f'codes in the name: «{ed}»')); stats['review'] += 1; continue
        new_title = drop_attribution(new_title, new_author)
        if new_author and redundant(new_author, new_title): new_author = ''
        one = (not plain and len(paths) == 1 and not re.match(r'^\d+\s*-', paths[0].rsplit('/', 1)[1]))   # a single book in a folder
        if one: plain = True                         # of its own: a plain file in its section (AGENTS.md §4)
        if new_title == title and new_author == author:
            stats['nothing to change'] += 1; continue
        if plain:
            tail = (f' - {clean(new_author)}' if new_author else '') + (f' ({clean(ed)})' if ed else '')
            name = clean(new_title) + tail                 # the full title when the name holds it (§4: shortened only so
            if len(name.encode()) > 196:                   # the author and the publisher fit)
                full_w = HONOR.sub('', new_title).split()
                st = HONOR.sub('', short_title(HONOR.sub('', new_title), new_author)).strip().split()
                n = len(st)
                while n < len(full_w) and TAIL.search(norm(' '.join(full_w[:n]))): n += 1   # never end on «بن», «في»…
                st = ' '.join(full_w[:n])
                name = clean(st) + tail
                if len(name.encode()) > 196: name = clean(st) + (f' - {clean(new_author)}' if new_author else '')   # the
                if len(name.encode()) > 196:                                                         # edition gives way
                    review.append((b['cat'] + '/' + b['folder'], ', '.join(why), 'the name does not fit 200 bytes')); stats['review'] += 1; continue
            name += '.pdf'
            plan.append((f"Books/{paths[0]}", f"Books/{b['cat']}/{name}", f"{', '.join(why)}: {'، '.join(src)}"))
        else:
            name = clean(new_title) + (f' - {clean(new_author)}' if new_author else '') + (f' ({clean(ed)})' if ed else '')
            name = fit(name)
            for p in paths:
                plan.append((f"Books/{p}", f"Books/{b['cat']}/{name}/{p.rsplit('/', 1)[1]}", f"{', '.join(why)}: {'، '.join(src)}"))
        stats['renamed'] += 1
    plan = [r for r in plan if N(r[0]) != N(r[1])]
    with open(out, 'w', newline='', encoding='utf-8') as f:
        csv.writer(f, delimiter='\t', lineterminator='\n').writerows(plan)
    os.makedirs(J('data/review'), exist_ok=True)
    with open(J('data/review/name-fix-review.tsv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f, delimiter='\t', lineterminator='\n'); w.writerow(['book', 'defect', 'why left']); w.writerows(review)
    print(dict(stats), '| plan rows', len(plan), '→', out)

if __name__ == '__main__':
    main(sys.argv[1])
