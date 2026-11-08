"""Apply a local-library plan written by local_sync_plan.py (rows: action<TAB>from<TAB>to<TAB>reason; action = move |
delete; paths relative to ~/Books). Moves never overwrite; deletes only remove byte-identical copies (the planner
proved it by MD5); folders emptied by the plan are removed; the folders «أبو العلاء المعري» and «ابن الزبير الغرناطي»
are never touched. Every change is logged to data/local/changes.tsv (time, action, from, to, reason, plan).
Usage: python3 scripts/apply_local_plan.py plan.tsv PLAN_NAME [--dry-run]"""
import csv, os, sys, time
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LB = os.path.expanduser('~/Books')
PROTECTED = ('أبو العلاء المعري', 'ابن الزبير الغرناطي')
plan, name, dry = sys.argv[1], sys.argv[2], '--dry-run' in sys.argv
log = None if dry else open(os.path.join(ROOT, 'data/local/changes.tsv'), 'a', encoding='utf-8')
def note(*r):
    if log: log.write('\t'.join([time.strftime('%F %T'), *r, name]) + '\n')
stats, touched = {'move': 0, 'delete': 0, 'skip': 0}, set()
for act, a, b, why in csv.reader(open(plan, encoding='utf-8'), delimiter='\t'):
    if a.split('/')[0] in PROTECTED or (b and b.split('/')[0] in PROTECTED): stats['skip'] += 1; continue
    src = os.path.join(LB, a)
    if not os.path.exists(src): stats['skip'] += 1; continue
    if act == 'move':
        dst = os.path.join(LB, b)
        if os.path.exists(dst): stats['skip'] += 1; print('exists, skipped:', b); continue
        if not dry:
            os.makedirs(os.path.dirname(dst), exist_ok=True); os.rename(src, dst); note('move', a, b, why)
    elif act == 'delete':
        if not dry: os.remove(src); note('delete', a, '', why)
    else: stats['skip'] += 1; continue
    stats[act] += 1; touched.add(os.path.dirname(src))
for d in sorted(touched, key=len, reverse=True):          # remove folders the plan emptied (up to the section)
    while d.startswith(LB + '/') and d != LB and os.path.isdir(d) and not os.listdir(d) and not dry:
        os.rmdir(d); note('rmdir', os.path.relpath(d, LB), '', 'empty after sync'); d = os.path.dirname(d)
print(('DRY ' if dry else '') + str(stats))
