"""Pass over folders flagged by audit_numbering.py (periodicals excluded):
 - label names the volume ("(المجلد الثمانون)") and the number is 01 or clashes -> number from the label
 - companion files (Shamela copy, web page, manuscript images, supplement, whole book in one file, audio) -> no number
 - "_alt" sharing a number -> "(نسخة أخرى)"
A folder whose names would still clash is left unchanged. Usage: python3 scripts/companion_plan.py index.tsv plans/NNN.tsv"""
import csv, os, re, sys
from collections import defaultdict, Counter
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from rename_plan import clean, fit, short_title
from build_catalog import split_folder
from audit_numbering import audit
from tail_numbering_plan import first_ordinal
from textnorm import norm
COMP = re.compile(r'نسخة للشاملة|نسخة الشاملة|للشاملة|صفحة|موقع|صور المخطوطات|ملحق|كاملة|مدمجة|في ملف واحد|ملف واح|صوتي|الصوتي|بصوت|الشرح الصوتي')
VOLLAB = re.compile(r'^(?:المجلد|الجزء|مجلد|جزء)\s+(\S+(?:\s+و\S+)?(?:\s+عشر)?)')
def main(index, out):
    flagged = set(f for k, v in audit(index).items() for f in v if not f.startswith('المجلات'))
    files = defaultdict(list)
    for p, s in csv.reader(open(index), delimiter='\t'):
        f = p.rsplit('/', 1)[0]
        if f in flagged: files[f].append(p.rsplit('/', 1)[1])
    moves, stats = [], Counter()
    for folder, names in sorted(files.items()):
        title, author, _ = split_folder(folder.split('/', 1)[1])
        short = clean(short_title(title, author))
        num = lambda n: (int(m.group(1)) if (m := re.match(r'^(\d+) - ', n)) else None)
        lab = lambda n: (m.group(1) if (m := re.search(r'\(([^()]*(?:\([^()]*\))?[^()]*)\)(?:_alt)?\.pdf$', n)) else '')
        counts = Counter(num(n) for n in names if num(n) is not None)
        plan = {}
        for n in names:
            L = lab(n); k = num(n)
            vm = VOLLAB.match(L)
            o = first_ordinal(L) if vm else None
            if o and (k in (None, 1) or counts[k] > 1) and o != k:
                plan[n] = f'{o:02d} - {short} ({clean(L)}).pdf'; stats['number from label'] += 1
            elif L and COMP.search(L) and (k is None or counts[k] > 1) and \
                    norm(title).startswith(norm(re.sub(r'^\d+ - ', '', n).split(' (')[0])[:12]):   # the file is this book, not another work
                plan[n] = f'{fit(short, 150)} ({fit(clean(L), 80)}).pdf'; stats['companion: no number'] += 1
            elif n.endswith('_alt.pdf') and k is not None and counts[k] > 1:
                plan[n] = re.sub(r'_alt\.pdf$', ' (نسخة أخرى).pdf', n); stats['_alt'] += 1
        final = {n: plan.get(n, n) for n in names}
        if len(set(final.values())) < len(final): stats['folder skipped (clash)'] += 1; continue
        for n, v in final.items():
            if v != n: moves.append((f'Books/{folder}/{n}', f'Books/{folder}/{v}', 'numbering: companions / label volume numbers'))
    open(out, 'w').write(''.join(f'{a}\t{b}\t{r}\n' for a, b, r in moves))
    print(dict(stats), '| moves:', len(moves))
if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
