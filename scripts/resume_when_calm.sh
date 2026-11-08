#!/usr/bin/env bash
# Resume the paused transfer jobs one at a time, each only after the home network has been calm for 10 minutes
# (AGENTS §7.8: never make other people's games or calls lag). Every queue is resumable.
cd "$(dirname "$0")/.."
python3 scripts/wait_calm.py 10 && PHONE_BW=3M DL_JOBS=1 python3 scripts/fetch_queue.py data/queue/083-local-expansion.tsv 083-local-expansion >> logs/fetch-083.log 2>&1
python3 scripts/wait_calm.py 10 && PYTHONPATH=$HOME/.local/share/phone-library-tools/site /usr/bin/python3 scripts/improve_copies.py lists/080-improved-copies-sample.tsv 080-improved-copies-sample >> logs/improve-080.log 2>&1
python3 scripts/wait_calm.py 10 && NET_MB=1.5 PHONE_BW=2M DL_JOBS=1 CONN=1 python3 scripts/fetch_queue.py data/queue/084-failed-queues-rebuilt.tsv 084-failed-queues-rebuilt >> logs/fetch-084.log 2>&1
python3 scripts/wait_calm.py 10 && NET_MB=1.5 PHONE_BW=2M DL_JOBS=1 CONN=1 python3 scripts/fetch_queue.py data/queue/082-almtoon-complete.tsv 082-almtoon-complete >> logs/fetch-082b.log 2>&1
python3 scripts/wait_calm.py 10 && NET_MB=1.5 PHONE_BW=2M DL_JOBS=1 CONN=1 python3 scripts/fetch_queue.py data/queue/073-complete-partial.tsv 073-complete-partial >> logs/fetch-073b.log 2>&1
echo "$(date '+%T') all paused queues done" >> logs/resume.log
