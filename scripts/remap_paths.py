"""Keep the per-file evidence in step with renames: records of data/phone/md5.tsv and data/inspect/files.jsonl whose path
no longer exists in data/phone/index-now.tsv are carried along every move logged in data/changes/changes.tsv (in log order,
so two-step renames and folder moves compose); a record is updated only when it lands on a current path of the same size,
and dropped when its file was deleted. Records whose path still exists are never touched (names get reused by renumbering).
Run it while phone_md5.py / inspect_files.py are NOT running (they append to these files).
Substitutions (moves into «نسخ مستبعدة/__المستبدل/» and from «نسخ محسنة للاستبدال/») are not renames: a record stays with the
path its fixed copy took, and is accepted there at the original's size (data/phone/substituted.tsv; run substituted_sizes.py first).
Usage: python3 scripts/remap_paths.py"""
import csv, json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J = lambda p: os.path.join(ROOT, p)
strip = lambda p: p[6:] if p.startswith('Books/') else p
idx = {p: int(s) for p, s in csv.reader(open(J('data/phone/index-now.tsv'), encoding='utf-8'), delimiter='\t') if s.isdigit()}
ASIDE = ('نسخ مستبعدة/__المستبدل/', 'نسخ محسنة للاستبدال/')     # a substitution: the fixed copy takes the original's place
log = [(r[1], strip(r[2]), strip(r[3])) for r in csv.reader(open(J('data/changes/changes.tsv'), encoding='utf-8'), delimiter='\t')
       if len(r) >= 4 and r[1] in ('move', 'delete') and not strip(r[2]).startswith(ASIDE) and not strip(r[3]).startswith(ASIDE)]

def follow(p):
    for act, a, b in log:
        if p == a: p = None if act == 'delete' else b
        elif act == 'move' and p.startswith(a + '/'): p = b + p[len(a):]
        if p is None: return None
    return p

subs = {}                                                        # substituted copies: path → size of the original they replaced
if os.path.exists(J('data/phone/substituted.tsv')):
    subs = {r['path']: int(r['original_size']) for r in csv.DictReader(open(J('data/phone/substituted.tsv'), encoding='utf-8'), delimiter='\t')}
stats = {'kept': 0, 'remapped': 0, 'dropped': 0, 'unresolved': 0}
def fix(path, size):
    if path in idx: stats['kept'] += 1; return path
    q = follow(path)
    if q is None: stats['dropped'] += 1; return None
    if q in idx and (not size or idx[q] == int(size) or subs.get(q) == int(size)): stats['remapped'] += 1; return q
    stats['unresolved'] += 1; return path                        # left as it is (listed below)

rows = [r for r in csv.reader(open(J('data/phone/md5.tsv'), encoding='utf-8'), delimiter='\t') if len(r) == 3]
with open(J('data/phone/md5.tsv'), 'w', encoding='utf-8', newline='') as o:
    w = csv.writer(o, delimiter='\t', lineterminator='\n')
    for r in rows:
        q = fix(r[0], r[1] if r[1].isdigit() else 0)
        if q: w.writerow([q, r[1], r[2]])
print('md5.tsv', stats); stats.update({k: 0 for k in stats})
recs = [json.loads(l) for l in open(J('data/inspect/files.jsonl'), encoding='utf-8')]
left = []
with open(J('data/inspect/files.jsonl'), 'w', encoding='utf-8') as o:
    for d in recs:
        q = fix(d['path'], d.get('size') or 0)
        if not q: continue
        if q not in idx: left.append(q)
        d['path'] = q; o.write(json.dumps(d, ensure_ascii=False) + '\n')
print('files.jsonl', stats)
for p in left[:10]: print('  unresolved:', p)
