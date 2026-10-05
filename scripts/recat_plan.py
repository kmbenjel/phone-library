"""Plan section (category) corrections from evidence: Shamela's section for the same title and Waqfeya's category.

A book moves only when its current section matches NEITHER source (nor a close neighbour of them).
Shamela wins when the sources disagree. Author/type-based sections and collection folders are never moved.
Run after build_catalog.py + compare_shamela.py on a fresh index.
Usage: python3 scripts/recat_plan.py plans/NNN-sections.tsv"""
import csv, json, os, re, sys
from collections import Counter, defaultdict
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from rename_plan import COLLECTION
J = lambda p: os.path.join(ROOT, p)

EXEMPT = {'كتب ابن تيمية وابن القيم', 'أدب عالمي - فرنسي (Littérature française)', 'أدب عالمي - إنجليزي (English Literature)', 'أدب عالمي - ألماني (Deutsche Literatur)', 'أدب عالمي - إسباني (Literatura en español)', 'أدب عالمي - مترجم', 'فهارس الويب'}
NEIGHBOURS = [  # either section is acceptable for books that sit on the border
    {'الدواوين الشعرية', 'الأدب والبلاغة ونقد الشعر'},
    {'التراجم والطبقات والأعلام', 'كتب العلل والزوائد والرجال'},
    {'التفاسير', 'علوم القرآن والقراءات'},
    {'أصول الفقه والقواعد الفقهية', 'الفقه المقارن والعام'},
    {'السيرة والشمائل النبوية', 'التراجم والطبقات والأعلام'},
    {'المعاجم والقواميس اللغوية', 'النحو والصرف وعلم الوضع'},
    {'المعاجم والقواميس اللغوية', 'الأدب والبلاغة ونقد الشعر'},
]
def near(a, b): return a == b or any(a in s and b in s for s in NEIGHBOURS)
MADHHAB = {'الفقه المالكي', 'الفقه الحنفي', 'الفقه الشافعي', 'الفقه الحنبلي'}
# moves that need Shamela's confirmation (Waqfeya files commentaries with the texts, and topic before madhhab)
NEEDS_SHAMELA = {('شروح الحديث', 'متون الحديث والمسانيد والمعاجم')}
def stays(cur, target):
    return cur in MADHHAB and target == 'الفقه المقارن والعام'   # a madhhab section is more specific than general fiqh

def mapping(fn):
    m = {}
    for l in open(J(fn)):
        if l.startswith('#') or not l.strip(): continue
        k, _, v = l.rstrip('\n').partition('\t'); m[k.strip()] = v.strip()
    return m

def main(out):
    cat = json.load(open(J('data/catalog.json')))
    smap, wmap = mapping('data/mappings/shamela-to-phone.tsv'), mapping('data/mappings/waqfeya-to-phone.tsv')
    wcat = {}
    for l in open(J('data/waqfeya/books.jsonl')):
        b = json.loads(l); wcat[b['_id']] = wmap.get(re.sub(r'^[\d.]+\s+', '', ((b.get('category') or {}).get('name') or '').strip()), '')
    shamela = defaultdict(list)            # phone book id -> mapped sections of matching Shamela books
    for r in csv.DictReader(open(J('data/compare/shamela-matches.tsv')), delimiter='\t'):
        for i in r['phone_book_ids'].split():
            shamela[int(i)].append(smap.get(r['category'], ''))
    existing = {(b['cat'], b['folder']): {f for f, _ in b['files']} for b in cat['books']}
    shamela_cats = set()
    for r in csv.DictReader(open(J('data/shamela/books.tsv')), delimiter='\t'):
        shamela_cats.add(r['category'])
    moves, review, stats = [], [], Counter()

    for b in cat['books']:
        cur = b['cat']
        if cur in EXEMPT or COLLECTION.match(b['folder']): continue
        S = Counter(s for s in shamela.get(b['id'], []) if s)
        W = Counter(wcat.get(w['id'], '') for w in b.get('waqfeya', []) if wcat.get(w['id']))
        if not S and not W:
            if cur not in shamela_cats:
                # It is in a stray category and we have no book-level evidence. Map the category itself.
                target = smap.get(cur) or wmap.get(cur)
                if not target:
                    # Simple heuristics for known strays if unmapped
                    if 'رقاق' in cur: target = 'الرقائق والآداب والأذكار'
                    elif 'قواعد' in cur and 'فقه' in cur: target = 'علوم الفقه والقواعد الفقهية'
                    elif 'سيرة' in cur: target = 'السيرة النبوية'
                    elif 'حديث' in cur: target = 'كتب السنة'
                    else: target = 'كتب عامة'
                why = f'stray category ({cur}) fallback mapping'
            else:
                stats['no evidence'] += 1
                continue
        elif any(near(cur, s) for s in list(S) + list(W)) and cur in shamela_cats:
            stats['section agrees'] += 1
            continue
        elif len(S) > 1:
            review.append((f"{cur}/{b['folder']}", 'Shamela matches point to several sections: ' + ' / '.join(S)))
            continue
        else:
            target = next(iter(S)) if S else W.most_common(1)[0][0]
            why = 'section: ' + ' / '.join(x for x in [f'Shamela «{next(iter(S))}»' if S else '', f'Waqfeya «{W.most_common(1)[0][0]}»' if W else ''] if x)
        
        if not target or target in EXEMPT: continue
        if stays(cur, target): stats['madhhab kept'] += 1; continue
        if not S and (cur, target) in NEEDS_SHAMELA: stats['needs Shamela'] += 1; continue
        dest_files = existing.get((target, b['folder']), set())
        clash = [f for f, _ in b['files'] if f in dest_files]
        if clash:
            review.append((f"{cur}/{b['folder']}", f'same folder already in «{target}» with clashing file names')); continue
        why = 'section: ' + ' / '.join(x for x in [f'Shamela «{next(iter(S))}»' if S else '', f'Waqfeya «{W.most_common(1)[0][0]}»' if W else ''] if x)
        for f, _ in b['files']:
            moves.append((f"Books/{cur}/{b['folder']}/{f}", f"Books/{target}/{b['folder']}/{f}", why))
        stats['move'] += 1
    with open(out, 'w') as w:
        for a, b2, why in moves: w.write(f'{a}\t{b2}\t{why}\n')
    with open(J('data/phone/sections-review.tsv'), 'w') as w:
        for x, why in review: w.write(f'{x}\t{why}\n')
    print(dict(stats), '| files to move:', len(moves), '| review:', len(review))

if __name__ == '__main__':
    main(sys.argv[1])
