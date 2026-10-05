#!/usr/bin/env bash
# One-off (2026-10-05 15:30): when the 139 fixed copies are all made (line B of unattended_2026-10-05.sh ends),
# measure the rest and substitute them as plan 143 (like 141).
cd "$(dirname "$0")/.."
while pgrep -f "[i]mprove_copies.py lists/139-split-and-crop" >/dev/null || pgrep -f "[u]nattended_2026-10-05" >/dev/null; do sleep 60; done
PYTHONPATH=~/.local/share/phone-library-tools/site /usr/bin/python3 scratch/measure_139.py >> logs/measure-139.log 2>&1
python3 scratch/substitute_139.py 143 > logs/143.log 2>&1
ALLOW_PROTECTED=1 python3 scripts/apply_plan.py plans/143a-substitute-fixed-step1.tsv >> logs/143.log 2>&1 && \
ALLOW_PROTECTED=1 python3 scripts/apply_plan.py plans/143b-substitute-fixed.tsv >> logs/143.log 2>&1 && \
ALLOW_PROTECTED=1 python3 scripts/delete_files.py plans/143c-delete-replaced-originals.tsv 143c-delete-replaced-originals >> logs/143.log 2>&1
ALLOW_PROTECTED=1 python3 scripts/delete_files.py plans/143d-delete-noop-fixed.tsv 143d-delete-noop-fixed >> logs/143.log 2>&1
python3 - >> logs/143.log 2>&1 <<'PY'
import csv, re, subprocess, tempfile, os
sz = {}
for r in csv.reader(open('data/changes/changes.tsv'), delimiter='\t'):
    if len(r) > 5 and r[5] == '139-split-and-crop' and r[1] == 'add':
        m = re.search(r"'bytes_out': (\d+)", r[4])
        if m: sz[r[3][6 + len('نسخ محسنة للاستبدال/'):]] = int(m.group(1))
subprocess.run(['python3', 'scripts/index_update.py', '143a-substitute-fixed-step1', '143b-substitute-fixed', '143c-delete-replaced-originals', '143d-delete-noop-fixed'])
idx = {p for p, s in csv.reader(open('data/phone/index-now.tsv'), delimiter='\t')}
subs = [r[1][6:] for r in csv.reader(open('plans/143b-substitute-fixed.tsv'), delimiter='\t')]
t = tempfile.NamedTemporaryFile('w', delete=False, suffix='.tsv')
for p in subs:
    if p not in idx and p in sz: t.write(f'{p}\t{sz[p]}\n')
t.close(); subprocess.run(['python3', 'scripts/index_update.py', '--add', t.name]); os.remove(t.name)
PY
echo "$(date '+%F %T') 143 done: $(tail -1 logs/143.log)" >> logs/unattended-2026-10-05.log
