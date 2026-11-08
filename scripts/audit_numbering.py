"""Audit numbering problems per folder (deliberate patterns — a volume's own preface "NN - x (المقدمة)",
parts "(أ)/(ب)", editions "(نسخة أخرى)" — are not counted). Usage: python3 scripts/audit_numbering.py index.tsv [--list]"""
import csv, re, sys
from collections import defaultdict, Counter
FRONT = re.compile(r'\((?:الواجهة|المقدمة|مقدمة[^)]*|تصدير|تقديم)\)\.pdf$')
SECTION = re.compile(r'القسم|المجلد|نصف|الجزء')
PART = re.compile(r'\((?:[أبجدهوزحطي]|نسخة أخرى)\)\.pdf$')
def audit(index):
    files = defaultdict(list)
    for p, s in csv.reader(open(index), delimiter='\t'):
        if p.startswith('فهارس الويب/') or p.count('/') != 2: continue
        f, n = p.rsplit('/', 1); files[f].append(n)
    res = defaultdict(list)
    for f, ns in files.items():
        num = lambda n: (m.group(1) if (m := re.match(r'^(\d+) - ', n)) else None)
        main = [n for n in ns if not FRONT.search(n) and not PART.search(n)]
        # same number with distinct section labels (القسم الأول / الثاني …) is deliberate
        lab = lambda n: (m.group(1) if (m := re.search(r'\(([^()]*)\)\.pdf$', n)) else '')
        main = [n for n in main if not (SECTION.search(lab(n)) and sum(1 for x in main if x[:3] == n[:3] and SECTION.search(lab(x))) == sum(1 for x in main if x[:3] == n[:3]))]
        c = Counter(num(n) for n in main if num(n))
        if len(ns) >= 3 and Counter(num(n) for n in ns if num(n)).get('01', 0) >= 0.6 * len(ns): res['all files numbered 01'].append(f)
        elif any(v > 1 for v in c.values()): res['repeated volume number'].append(f)
        if any(num(n) in ('99', '999') for n in ns) and max([int(num(n)) for n in ns if num(n) and num(n) not in ('99', '999')] or [0]) < 98: res['99 for indexes'].append(f)
        COMP = re.compile(r'نسخة|صفحة|موقع|مخطوط|ملحق|كامل|مدمج|ملف واحد|صوت|الفهارس|تصدير|الواجهة|المقدمة|التكملة|قسم|ذيل')
        if len(ns) >= 2 and 0 < sum(1 for n in ns if num(n)) < len(ns) and any(not num(n) and not FRONT.search(n) and not COMP.search(n) for n in ns): res['numbered and unnumbered mixed'].append(f)
    return res
if __name__ == '__main__':
    r = audit(sys.argv[1])
    for k in ('all files numbered 01', 'repeated volume number', '99 for indexes', 'numbered and unnumbered mixed'):
        print(f'{len(r[k]):5d}  {k}')
        if '--list' in sys.argv:
            for f in sorted(r[k]): print('        ', f)
