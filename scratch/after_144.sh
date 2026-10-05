#!/usr/bin/env bash
# One-off (2026-10-05): after the 144 upload, a second pass (البدء والتاريخ, whose volume 3 arrived late; any drop),
# then the phone index gets every uploaded file of 144.
cd "$(dirname "$0")/.."
while pgrep -f "[f]etch_queue.py data/queue/144-final" >/dev/null; do sleep 30; done
until python3 -c "import sys; sys.path.insert(0,'scripts'); import phone_host; sys.exit(0 if phone_host.find() else 1)"; do sleep 60; done
PHONE_BW=8M python3 scripts/fetch_queue.py data/queue/144-final.tsv 144-pre700 >> logs/144-pre700.log 2>&1
python3 - <<'PY'
import csv, os, tempfile, subprocess
done = set(open('data/queue/144-final.done').read().split('\n'))
idx = {p for p, s in csv.reader(open('data/phone/index-now.tsv'), delimiter='\t')}
t = tempfile.NamedTemporaryFile('w', delete=False, suffix='.tsv')
for r in csv.reader(open('data/queue/144-final.tsv'), delimiter='\t'):
    if r[2] in done and r[2][6:] not in idx: t.write(r[2][6:] + '\t' + r[1] + '\n')
t.close(); subprocess.run(['python3', 'scripts/index_update.py', '--add', t.name]); os.remove(t.name)
PY
echo "$(date '+%F %T') 144 done: $(tail -1 logs/144-pre700.log)" >> logs/unattended-2026-10-05.log
