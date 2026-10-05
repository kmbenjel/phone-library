"""Name audit (AGENTS.md §4): raw archive names, >200-byte names, forbidden chars / dots / spaces / _alt /
نسخة ثانية, «تحميل», files directly in a category, non-PDF and <20 KB files, unknown categories.
Usage: python3 scripts/name_audit.py index.tsv [--list]   → data/phone/name-audit.tsv (issue, path, bytes)"""
import csv, os, re, sys
from collections import defaultdict
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ALLOWED_EXTRA = ('أدب عالمي', 'فهارس الويب')

def shamela_cats():
    cats = set()
    for l in open(os.path.join(ROOT, 'data/mappings/shamela-to-phone.tsv'), encoding='utf-8'):
        if l.startswith('#') or not l.strip(): continue
        cats.add(l.rstrip('\r\n').split('\t')[1].strip())
    return cats

RAW = re.compile(r'^\d+_[^/]*\.pdf$', re.I)
BAD = re.compile(r'[\\:*?"<>|]|\.\.\.|  |_alt|نسخة ثانية|^ | $|^\.|\.$| \.pdf$')
def audit(index):
    cats = shamela_cats(); res = defaultdict(list)
    for p, s in csv.reader(open(index, encoding='utf-8'), delimiter='\t'):
        s = int(s.strip())
        if p.startswith('فهارس الويب/'): continue
        parts = p.split('/'); n = parts[-1]
        top = parts[0]
        if top not in cats and top not in ALLOWED_EXTRA: res['unknown category'].append((p, s))
        if top == 'أدب عالمي': depth_ok = len(parts) >= 4
        else: depth_ok = len(parts) >= 3
        if not depth_ok: res['file directly in category'].append((p, s))
        if RAW.match(n): res['raw archive name'].append((p, s))
        if any(len(x.encode()) > 200 for x in parts): res['name > 200 bytes'].append((p, s))
        if any(BAD.search(x) for x in parts): res['forbidden chars/spaces/dots/_alt'].append((p, s))
        if 'تحميل' in p: res['تحميل in name'].append((p, s))
        if not n.lower().endswith('.pdf'): res['not .pdf'].append((p, s))
        if s < 20480: res['< 20 KB'].append((p, s))
    return res

if __name__ == '__main__':
    r = audit(sys.argv[1])
    with open(os.path.join(ROOT, 'data/phone/name-audit.tsv'), 'w', encoding='utf-8') as w:
        for k, v in r.items():
            print(f'{len(v):5d}  {k}')
            for p, s in v:
                w.write(f'{k}\t{p}\t{s}\n')
                if '--list' in sys.argv: print('        ', p, s)
