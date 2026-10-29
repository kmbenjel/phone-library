"""stage_f.py [--apply] — fix F's data (2026-10-29): the owner's «leave as scanned» verdicts as turns of 0.
  1. data/crop/owner-turns.tsv: a row (path, page, 0, verdict) for every page he kept as scanned — crop-tilt-002's 4 rows
     (2026-10-27 «Leave as scanned») and crop-tilt-003's rows marked OK (2026-10-29 «mark all ok»); the path as the phone
     has it now (index-now, renames followed — what the redo passes), so crop_batch.owner_turns finds them;
  2. data/improve/crop-regression.tsv: a «turn no» case row for each of them the regression does not hold yet, under the
     regression's own path string for the book (crop_regress.local_copy names its copy by that string: another string
     would fetch the book again from the phone).
Writes owner-turns-add.tsv and regression-add.tsv beside this script; --apply appends them (a row already there is never
added twice). Run --apply only after regression 27m has ended: both files are read by crop_regress / book_crop."""
import csv, hashlib, os, sys, unicodedata
ROOT = '/home/k/projects/phone-library'; S = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT + '/scripts')
import crop_batch as cb
N = lambda x: unicodedata.normalize('NFC', x.removeprefix('Books/'))
H = lambda p: hashlib.md5(N(p).encode()).hexdigest()[:12]
J = lambda *p: os.path.join(ROOT, *p)

idx = {N(l.split('\t')[0]): l.split('\t')[0] for l in open(J('data/phone/index-now.tsv'), encoding='utf-8') if l.strip()}
fwd = {N(a): N(b) for a, b in cb.moves()[0].items()}
def now(x):
    x, seen = N(x), set()
    while x not in idx and x in fwd and x not in seen: seen.add(x); x = fwd[x]
    return x

reg = [r for r in csv.reader(open(J('data/improve/crop-regression.tsv'), encoding='utf-8'), delimiter='\t') if r and not r[0].startswith('#')]
reg_path = {}                                         # current name → the regression's own path string for that book
for r in reg: reg_path.setdefault(now(r[0]), r[0])
have_no = {(now(r[0]), int(r[1])) for r in reg if r[2] == 'turn' and r[3] == 'no'}
have_yes = {(now(r[0]), int(r[1])) for r in reg if r[2] == 'turn' and r[3] == 'yes'}
ot_rows = [l.rstrip('\n').split('\t') for l in open(cb.OWNER_TURNS, encoding='utf-8') if l.strip() and not l.startswith('#')]
have_ot = {(now(r[0]), int(r[1])): r for r in ot_rows}

verdicts = []                                         # (path as reviewed, page, review, row number, date, words)
for f, date, words, ok in (('crop-tilt-002', '2026-10-27', 'Leave as scanned', {'A', 'B'}), ('crop-tilt-003', '2026-10-29', 'mark all ok', {'OK'})):
    rows = [l.rstrip('\n').split('\t') for l in open(J('data/review', f + '.tsv'), encoding='utf-8') if l.strip() and not l.startswith('#')]
    for n, r in enumerate(rows, 1):
        if r[0] not in ok: continue
        pg = int(r[2].split('ص ', 1)[1].split()[0]); verdicts.append((r[1], pg, f, n, date, words))

ot_add, reg_add, notes = [], [], []
for p, pg, f, n, date, words in verdicts:
    cur = now(p)
    if cur not in idx: notes.append(f'NOT ON THE PHONE: {p} p. {pg}'); continue
    k = (cur, pg)
    if k in have_ot: notes.append(f'owner-turns already holds {cur[:50]} p. {pg}: {have_ot[k][2:]}')
    else: ot_add.append([idx[cur], str(pg), '0', f'leave as scanned (site/{f}.html row {n}, {date} «{words}»)'])
    if k in have_yes: notes.append(f'CONFLICT: the regression wants a turn on {cur[:50]} p. {pg}')
    if k not in have_no and cur in reg_path:
        reg_add.append([reg_path[cur], str(pg), 'turn', 'no',
                        f'lines at two angles, left as scanned — the owner kept it so ({f} row {n}, {date} «{words}»); fix F holds it'])
    elif cur not in reg_path: notes.append(f'not a regression book: {cur[:60]}')

w = lambda fn, rows: open(os.path.join(S, fn), 'w', encoding='utf-8').write(''.join('\t'.join(r) + '\n' for r in rows))
w('owner-turns-add.tsv', ot_add); w('regression-add.tsv', reg_add)
print(len(verdicts), 'verdicts;', len(ot_add), 'owner-turns rows and', len(reg_add), 'regression rows staged'); [print(' ', x) for x in notes]
if '--apply' in sys.argv:
    for fn, rows in ((cb.OWNER_TURNS, ot_add), (J('data/improve/crop-regression.tsv'), reg_add)):
        s = open(fn, encoding='utf-8').read()
        with open(fn, 'a', encoding='utf-8') as o:
            if s and not s.endswith('\n'): o.write('\n')
            for r in rows: o.write('\t'.join(r) + '\n')
        print('appended', len(rows), 'rows to', fn)
