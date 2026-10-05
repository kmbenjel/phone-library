"""One-off (2026-10-05): substitution plans for the recompressed copies of plan 135 (owner approved substituting improved
copies; a LOSSY copy replaces its original only when it is at most half the size — otherwise the copy is removed).
Writes, like 125a/b/c:
  140a  original → «نسخ مستبعدة/__المستبدل/<path>»      (ALLOW_PROTECTED=1 apply_plan.py)
  140b  copy «نسخ محسنة للاستبدال/<path>» → <path>      (ALLOW_PROTECTED=1 apply_plan.py)
  140c  delete the set-aside originals                  (delete_files.py)
  140d  delete the copies not worth substituting        (delete_files.py)
Usage: python3 scratch/substitute_135.py"""
import csv, os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J = lambda p: os.path.join(ROOT, p)
IMP, OUT = 'نسخ محسنة للاستبدال/', 'نسخ مستبعدة/__المستبدل/'
idx = {p: int(s) for p, s in csv.reader(open(J('data/phone/index-now.tsv'), encoding='utf-8'), delimiter='\t') if s.isdigit()}
copies = {}
for r in csv.reader(open(J('data/changes/changes.tsv'), encoding='utf-8'), delimiter='\t'):
    if len(r) > 5 and r[5] == '135-recompress' and r[1] == 'add':
        m = re.search(r"'bytes_out': (\d+)", r[4])
        if m: copies[r[3][6 + len(IMP):]] = int(m.group(1))
a, b, c, d = [], [], [], []
for p, out in sorted(copies.items()):
    orig = idx.get(p)
    if not orig: print('original gone?', p); continue
    ratio = out / orig
    if ratio <= 0.5:
        a.append((f'Books/{p}', f'Books/{OUT}{p}', f'replaced by its recompressed copy ({out / 1e6:.0f} MB = {ratio:.0%} of {orig / 1e6:.0f} MB; gray 200 ppi)'))
        b.append((f'Books/{IMP}{p}', f'Books/{p}', f'recompressed copy ({ratio:.0%} of the original) takes the original\'s place'))
        c.append((f'Books/{OUT}{p}', f'replaced by its recompressed copy ({ratio:.0%} of its size; owner 2026-10-05: substitute the improved copies)'))
    else:
        d.append((f'Books/{IMP}{p}', f'recompressed copy only {1 - ratio:.0%} smaller ({ratio:.0%}): a lossy copy is not worth it; the original stays'))
for name, rows in (('140a-substitute-recompressed-step1', a), ('140b-substitute-recompressed', b)):
    with open(J(f'plans/{name}.tsv'), 'w', encoding='utf-8') as w:
        for x in rows: w.write('\t'.join(x) + '\n')
for name, rows in (('140c-delete-replaced-originals', c), ('140d-delete-unworthy-copies', d)):
    with open(J(f'plans/{name}.tsv'), 'w', encoding='utf-8') as w:
        for x in rows: w.write('\t'.join(x) + '\n')
print(f'{len(a)} to substitute (saving {sum(idx[p[6:]] - copies[p[6:]] for p, _, _ in a) / 1e9:.1f} GB), {len(d)} copies to remove')
