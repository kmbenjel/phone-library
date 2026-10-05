#!/usr/bin/env bash
# One-off (2026-10-05 14:40, owner): keep the machine working while the agent's usage is exhausted (until ~19:22).
# Two independent lines, each waits for its running job, retries once for phone drops, then goes on:
#   A. uploads 134 → phone index → stage 136b (disk allows it once 134 is uploaded) → title sheets 136a/136b → refresh (web)
#   B. recompression 135 → lossless fixed copies 139 (split spreads, crop dark scanner edges) into «نسخ محسنة للاستبدال»
# Nothing here deletes or substitutes: substitutions and names stay for the agent to judge when it is back.
cd "$(dirname "$0")/.."
export NETPACE=0
log(){ echo "$(date '+%F %T') $*"; }
waitfor(){ while pgrep -f "$1" >/dev/null; do sleep 60; done; }
TOOLS="$HOME/.local/share/phone-library-tools/site"
fixhost(){ h=$(python3 -c "import sys; sys.path.insert(0,'scripts'); from phone_host import HOST; print(HOST)"); rclone config update phone host "$h" >/dev/null; log "phone at $h"; }   # the phone's DHCP address moves

add_done(){   # queue name → add its uploaded targets to data/phone/index-now.tsv
  python3 - "$1" <<'EOF'
import csv, sys, os, tempfile, subprocess
q = sys.argv[1]
done = set(open(f'data/queue/{q}.done').read().split('\n')) if os.path.exists(f'data/queue/{q}.done') else set()
rows = [r for r in csv.reader(open(f'data/queue/{q}.tsv'), delimiter='\t') if r and r[2] in done]
t = tempfile.NamedTemporaryFile('w', delete=False, suffix='.tsv')
for r in rows: t.write(r[2][6:] + '\t' + r[1] + '\n')
t.close(); subprocess.run(['python3', 'scripts/index_update.py', '--add', t.name]); os.remove(t.name)
EOF
}

lineA(){
  waitfor "[f]etch_queue.py data/queue/134-printers-final"
  log "A: 134 finished; retry once"; fixhost
  PHONE_BW=8M python3 scripts/fetch_queue.py data/queue/134-printers-final.tsv 134-printers >> logs/134-printers.log 2>&1
  add_done 134-printers-final; log "A: index updated with 134"
  python3 scratch/stage_queue.py data/queue/136b-top-missing.tsv downloads/stage-136b >> logs/stage-136b.log 2>&1
  python3 scratch/stage_queue.py data/queue/136b-top-missing.tsv downloads/stage-136b >> logs/stage-136b.log 2>&1   # resume pass
  log "A: 136b staged: $(tail -1 logs/stage-136b.log)"
  for p in 136a 136b; do nice python3 scratch/title_sheets.py downloads/stage-$p downloads/stage-$p/sheets 28; done
  log "A: title sheets ready in downloads/stage-136{a,b}/sheets"
  NO_OPEN=1 nice scripts/refresh.sh --no-list > logs/refresh-unattended.log 2>&1; log "A: refresh done: $(tail -2 logs/refresh-unattended.log | tr '\n' ' ')"
}

lineB(){
  waitfor "[i]mprove_copies.py lists/135-recompress"
  log "B: 135 finished; retry once"; fixhost
  PYTHONPATH="$TOOLS" nice /usr/bin/python3 scripts/improve_copies.py lists/135-recompress.tsv 135-recompress >> logs/135-recompress.log 2>&1
  python3 - <<'EOF'
import csv
skip = {r[0] for r in csv.reader(open('lists/135-recompress.tsv'), delimiter='\t') if r}
SPECIAL = ('نسخ محسنة للاستبدال', 'نسخ مستبعدة', 'فهارس الويب')
idx = {p: int(s) for p, s in csv.reader(open('data/phone/index-now.tsv'), delimiter='\t') if s.isdigit()}
ops = {}
for r in csv.reader(open('data/phone/quality.tsv'), delimiter='\t'):
    if not r or r[1] in skip or r[1].startswith(SPECIAL) or r[1] not in idx: continue
    if r[0] == 'spreads': ops.setdefault(r[1], set()).add('split')
    elif r[0] == 'dark-borders': ops.setdefault(r[1], set()).add('crop')
rows = sorted(ops.items(), key=lambda kv: idx[kv[0]])          # small files first
with open('lists/139-split-and-crop.tsv', 'w') as w:
    for p, o in rows: w.write(p + '\t' + ','.join(sorted(o, key=['split', 'crop'].index)) + '\n')
print(len(rows), 'files,', round(sum(idx[p] for p, _ in rows) / 1e9, 1), 'GB')
EOF
  log "B: 139 list built: $(wc -l < lists/139-split-and-crop.tsv) files"
  PYTHONPATH="$TOOLS" nice /usr/bin/python3 scripts/improve_copies.py lists/139-split-and-crop.tsv 139-split-and-crop > logs/139-split-and-crop.log 2>&1
  PYTHONPATH="$TOOLS" nice /usr/bin/python3 scripts/improve_copies.py lists/139-split-and-crop.tsv 139-split-and-crop >> logs/139-split-and-crop.log 2>&1   # retry pass
  log "B: 139 done: $(grep -c '^OK' logs/139-split-and-crop.log) OK, $(grep -c '^FAIL' logs/139-split-and-crop.log) failed"
}

log "unattended chain started (pid $$)"
lineA & lineB & wait
log "unattended chain finished"
