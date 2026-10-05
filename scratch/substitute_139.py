"""One-off (2026-10-05): substitution plans for the lossless fixed copies of plan 139, from the measurements of
scratch/measure_139.py (worth it: a split, or a crop keeping ≤ 90 % of the median page; checked by eye on samples,
nothing cut). Only rows not handled by an earlier batch. Writes plans/<PREFIX>a..d like 125/140:
  a  original → «نسخ مستبعدة/__المستبدل/<path>»     b  copy → <path>     c  delete set-aside originals
  d  delete the near no-op copies (crop keeping > 90 %: the reader would show the same page)
Usage: python3 scratch/substitute_139.py PREFIX   (e.g. 141)"""
import csv, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J = lambda p: os.path.join(ROOT, p)
P = sys.argv[1]
IMP, OUT = 'نسخ محسنة للاستبدال/', 'نسخ مستبعدة/__المستبدل/'
handled = set()
for r in csv.reader(open(J('data/changes/changes.tsv'), encoding='utf-8'), delimiter='\t'):
    if len(r) > 5 and r[5].endswith(('-substitute-fixed', '-delete-noop-fixed')):
        handled.add(r[2][6 + len(IMP):] if r[2].startswith('Books/' + IMP) else r[2][6:])
idx = {p for p, s in csv.reader(open(J('data/phone/index-now.tsv'), encoding='utf-8'), delimiter='\t')}
a, b, c, d = [], [], [], []
for path, ops, pin, pout, kept, worth in csv.reader(open(J('data/improve/139-measure.tsv'), encoding='utf-8'), delimiter='\t'):
    if path in handled: continue
    if worth == 'yes':
        if path not in idx: print('original not in index, skipped:', path); continue
        what = f'split spreads ({pin} → {pout} pages)' if int(pout) > int(pin) else f'lossless crop to the content ({float(kept):.0%} of the page shown)'
        a.append((f'Books/{path}', f'Books/{OUT}{path}', f'replaced by its fixed copy: {what}'))
        b.append((f'Books/{IMP}{path}', f'Books/{path}', f'fixed copy takes the original\'s place: {what}'))
        c.append((f'Books/{OUT}{path}', f'replaced by its fixed copy ({what}; owner 2026-10-05: substitute the improved copies)'))
    else:
        d.append((f'Books/{IMP}{path}', f'fixed copy shows {float(kept):.0%} of the page: no gain over the original, which stays'))
for suffix, rows in (('a-substitute-fixed-step1', a), ('b-substitute-fixed', b), ('c-delete-replaced-originals', c), ('d-delete-noop-fixed', d)):
    with open(J(f'plans/{P}{suffix}.tsv'), 'w', encoding='utf-8') as w:
        for x in rows: w.write('\t'.join(x) + '\n')
print(f'{len(a)} to substitute, {len(d)} no-op copies to delete')
