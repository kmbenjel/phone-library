"""One-off (2026-10-26, the owner's order item 2: the name composer no longer cuts a title inside a phrase — «مراقي السعود
لمبتغي الرقي», «صلى الله عليه» — while a long nasab, a printed role or a co-author stays whole): the read single books whose
name on the phone is exactly what the composer of HEAD (before this change) made from their reading are named again
with the new composer. Any other name — set by hand, approved in plan 315, held by names_plan_read's rules, a part of a
set — is left as it is. Writes plans/383-names-recompose.tsv (from = the phone's own bytes). Never rerun after it ran."""
import csv, os, sys, unicodedata, collections, subprocess, tempfile
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(ROOT); sys.path.insert(0, 'scripts')
OUT = 'plans/383-names-recompose.tsv'
if os.path.exists(OUT) or any('383-names-recompose' in l for l in open('data/changes/changes.tsv', encoding='utf-8')):
    sys.exit('plan 383 exists or ran already')
import names_from_reading as nfr
N = lambda s: unicodedata.normalize('NFC', s)
idx = {N(l.split('\t')[0]): l.split('\t')[0] for l in open('data/phone/index-now.tsv', encoding='utf-8')}
fwd = {}
for r in csv.reader(open('data/changes/changes.tsv', encoding='utf-8'), delimiter='\t'):
    if len(r) > 3 and r[1] == 'move' and r[2] and r[3]: fwd[N(r[2].removeprefix('Books/'))] = N(r[3].removeprefix('Books/'))
def follow(p):
    seen = set()
    while p not in idx and p in fwd and p not in seen: seen.add(p); p = fwd[p]
    return p
# the HEAD composer's names (git show HEAD:… into a temporary tree that reads the same data)
tmp = tempfile.mkdtemp(); os.makedirs(f'{tmp}/scripts'); os.symlink(f'{ROOT}/data', f'{tmp}/data')
for f in ('name_compose.py', 'names_from_reading.py'):
    open(f'{tmp}/scripts/{f}', 'w', encoding='utf-8').write(subprocess.run(['git', 'show', f'HEAD:scripts/{f}'], capture_output=True, text=True, check=True).stdout)
for f in ('textnorm.py', 'names_plan_read.py'): os.symlink(f'{ROOT}/scripts/{f}', f'{tmp}/scripts/{f}')
old = dict(l.split('\t', 1) for l in subprocess.run([sys.executable, '-c', f'''
import csv, sys; sys.path.insert(0, "{tmp}/scripts"); import names_from_reading as m
for r in csv.DictReader(open("data/names/title-read.tsv", encoding="utf-8"), delimiter="\\t"): print(r["n"] + "\\t" + (m.name_of(r) if r.get("title") else ""))
'''], capture_output=True, text=True, check=True).stdout.splitlines())
sheet = {l.split('\t')[0]: l.rstrip('\n').split('\t') for l in open('data/names/sheets/books.tsv', encoding='utf-8')}
last = {}
for r in csv.DictReader(open('data/names/title-read.tsv', encoding='utf-8'), delimiter='\t'): last[r['n']] = r
taken = collections.defaultdict(set)
for p in idx: taken['/'.join(p.split('/')[:-1])].add(p.split('/')[-1])
rows, c = [], collections.Counter()
for n, r in sorted(last.items(), key=lambda kv: int(kv[0])):
    if r['verdict'] not in ('ok', 'other-book', 'other-edition') or n not in sheet: continue
    p = follow(N(sheet[n][2]))
    if p not in idx: continue
    cur = p.split('/')[-1].removesuffix('.pdf'); new = nfr.name_of(r)
    if cur == new or cur != old.get(n): continue                 # already right, or not the old composer's own name
    d = '/'.join(p.split('/')[:-1])
    if new + '.pdf' in taken[d]: c['taken'] += 1; continue
    taken[d].add(new + '.pdf')
    rows.append((f'Books/{idx[p]}', f'Books/{d}/{new}.pdf', f'the composer no longer cuts a title inside a phrase (book {n}; owner 2026-10-19 «لا يمكن أن تكون الجملة مقصوصة هكذا أبدا»)'))
with open(OUT, 'w', encoding='utf-8') as w:
    for x in rows: w.write('\t'.join(x) + '\n')
print(len(rows), 'renames →', OUT, dict(c))
