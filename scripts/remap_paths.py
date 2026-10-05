"""Keep the per-file evidence in step with renames: apply the moves (and deletions) logged in
data/changes/changes.tsv for the given plans to data/phone/md5.tsv and data/inspect/files.jsonl.
Run it while phone_md5.py / inspect_files.py are NOT running (they append to these files).
Usage: python3 scripts/remap_paths.py PLAN [PLAN...]"""
import csv, json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J = lambda p: os.path.join(ROOT, p)
plans = set(sys.argv[1:])
strip = lambda p: p[6:] if p.startswith('Books/') else p
moves, gone = {}, set()
for r in csv.reader(open(J('data/changes/changes.tsv'), encoding='utf-8'), delimiter='\t'):
    if len(r) >= 6 and r[5] in plans:
        if r[1] == 'move': moves[strip(r[2])] = strip(r[3])
        elif r[1] == 'delete': gone.add(strip(r[2]))
def new(p):
    if p in moves: return moves[p]
    for a, b in moves.items():
        if p.startswith(a + '/'): return b + p[len(a):]
    return p
n = 0
rows = [r for r in csv.reader(open(J('data/phone/md5.tsv'), encoding='utf-8'), delimiter='\t') if len(r) == 3 and r[0] not in gone]
with open(J('data/phone/md5.tsv'), 'w', encoding='utf-8', newline='') as o:
    w = csv.writer(o, delimiter='\t', lineterminator='\n')
    for r in rows:
        q = new(r[0]); n += q != r[0]; w.writerow([q, r[1], r[2]])
recs = [json.loads(l) for l in open(J('data/inspect/files.jsonl'), encoding='utf-8')]
with open(J('data/inspect/files.jsonl'), 'w', encoding='utf-8') as o:
    for d in recs:
        if d['path'] in gone: continue
        q = new(d['path']); n += q != d['path']; d['path'] = q
        o.write(json.dumps(d, ensure_ascii=False) + '\n')
print('remapped', n, 'paths')
