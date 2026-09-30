"""Clean leftover naming errors that predate the evidence-based renames (no provenance needed):
 A. file named only by the folder's author/edition part  -> named after the book title
 B. junk file names (اضغط هنا، كاملا، a publisher fragment, "(نسخة للشاملة)")  -> book title (+ the useful part)
 C. Waqfeya "صفحة تجميعية" (several editions in one folder) -> folder "<title> - عدة طبعات", files "<title> (<edition>).pdf"
 D. "alt_" prefixes -> the same number with "(… - نسخة أخرى)"
Usage: python3 scripts/cleanup_plan.py data/phone/index-<state>.tsv plans/NNN-cleanup.tsv"""
import csv, os, re, sys
from collections import defaultdict, Counter
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from textnorm import norm
from rename_plan import COLLECTION, clean, fit, short_title
from build_catalog import split_folder

SKIP_SECTIONS = {'المجلات والدوريات والسلاسل الكبرى', 'أدب عالمي ومترجم', 'أدباء ومفكرو العصر الحديث', 'فهارس الويب'}
JUNK = re.compile(r'^(اضغط هنا|كاملا?|كامل|الإسلامي|الكتاب|الملف|تحميل|pdf|\d+)$')
USEFUL = re.compile(r'نسخة|تحقيق|\bت\s|شرح|الشاملة|المجلد|الجزء|القسم|مقدمة|فهارس')
W = lambda t: {w for w in norm(t).split() if len(w) > 2}

def main(index, out):
    files = defaultdict(list)
    for p, s in csv.reader(open(index), delimiter='\t'):
        sec = p.split('/')[0]
        if sec in SKIP_SECTIONS or p.count('/') != 2: continue
        files[p.rsplit('/', 1)[0]].append(p.rsplit('/', 1)[1])
    moves = []; why = Counter()
    for folder, names in files.items():
        sec, name = folder.split('/', 1)
        if COLLECTION.match(name): continue
        title, author, edition = split_folder(name)
        rest = name[len(title):].strip(' -')
        short = clean(short_title(title, author))
        dest_folder = folder
        # C. compilation pages (several editions of one book)
        if re.search(r'\s-\sصفحة تجميعية$', name):
            base = clean(re.sub(r'\s-\sصفحة تجميعية$', '', name))
            dest_folder = f'{sec}/{base} - عدة طبعات'
        taken = set()
        plan = []
        for n in sorted(names):
            stem = n[:-4] if n.lower().endswith('.pdf') else n
            new = None
            m = re.match(r'^\d+ - صفحة تجميعية - (.+)$', stem)
            if m: new = clean(m.group(1)); why['C edition page'] += 1
            elif re.match(r'^\d+ - \(نسخة للشاملة من (.+?)\)?$', stem):                    # 01 - (نسخة للشاملة من عوالي مالك …)
                t = re.match(r'^\d+ - \(نسخة للشاملة من (.+?)\)?$', stem).group(1)
                new = f'{clean(t)} (نسخة الشاملة)'; why['B shamela copy'] += 1
            elif stem.startswith('alt_'):
                m2 = re.match(r'^alt_(\d+) - (.+)$', stem)
                if m2: new = f'{m2.group(1)} - {short} ({clean(m2.group(2))} - نسخة أخرى)'; why['D alt_'] += 1
            else:
                core = re.sub(r'^\d+ - ', '', stem); num = re.match(r'^(\d+) - ', stem)
                ctitle = core.split(' (')[0].split(' - ')[0]
                if W(ctitle) & W(title) or not W(title): continue
                if rest and norm(core) == norm(rest):                                          # A
                    new = (f'{num.group(1)} - {short}' if num else clean(title)); why['A author-only'] += 1
                elif JUNK.match(core.strip()) or core.startswith('(') or len(W(core)) <= 1 or re.match(r'^(تحقيق|ت)\s', core) or re.match(r'^(على|في|من) ', core):
                    frag = clean(core.strip('()'))
                    keep = f' ({frag})' if USEFUL.search(frag) and not JUNK.match(frag) else ''
                    new = (f'{num.group(1)} - {short}' if num else clean(title)) + keep; why['B junk name'] += 1
            if not new: continue
            new = fit(new, 190) + '.pdf'
            if new in taken or (new in names and new != n): why['skipped: name taken'] += 1; continue
            taken.add(new); plan.append((n, new))
        renamed = {a for a, b in plan}
        for n, new in plan:
            moves.append((f'Books/{folder}/{n}', f'Books/{dest_folder}/{new}', 'cleanup'))
        if dest_folder != folder:
            for n in names:
                if n not in renamed: moves.append((f'Books/{folder}/{n}', f'Books/{dest_folder}/{n}', 'cleanup'))
    with open(out, 'w') as f:
        for a, b, r in moves:
            if a != b: f.write(f'{a}\t{b}\t{r}\n')
    print(dict(why), '| moves:', sum(1 for a, b, r in moves if a != b))

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
