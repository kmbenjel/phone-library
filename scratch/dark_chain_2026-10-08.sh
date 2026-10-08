#!/usr/bin/env bash
# One-off (2026-10-08 ~20:55 GMT, written as the session limit neared). Unattended, log logs/dark-chain-2026-10-08.log.
# The missing pre-700 AH Waqfeya books whose archive.org items went dark (100 books, data/queue/274-pre700-dark-ids.txt):
#  1. waits for scripts/find_on_archive.py (other uploads of the same books → data/queue/274-pre700-dark-candidates.json);
#  2. scripts/dark_replace.py verifies each candidate from its title page (title words ≥ 60 % + author) → queue 274, review list
#     data/review/274-dark-review.tsv (nothing uploaded for those);
#  3. fetch_queue (verified: size, %PDF, %%EOF, pdfinfo), index, refresh, commit.
# Never rerun once the log says «chain done» (AGENTS.md §6); before that a rerun resumes.
set -u
cd "$HOME/projects/phone-library"
LOG=logs/dark-chain-2026-10-08.log
if grep -q "chain done" "$LOG" 2>/dev/null; then echo "already done (see $LOG)"; exit 0; fi
Q=data/queue/274-pre700-dark
{
  echo "$(date -u '+%F %T') start"
  while pgrep -f "[f]ind_on_archive.py data/queue/274" >/dev/null; do sleep 30; done
  if [ ! -s $Q-candidates.json ]; then
    echo "no candidates file — running the search now"
    nice python3 scripts/find_on_archive.py $Q-ids.txt $Q-candidates.json 3
  fi
  [ -s $Q-candidates.json ] || { echo "SEARCH FAILED"; exit 1; }
  [ -s $Q.tsv ] || nice python3 scripts/dark_replace.py $Q-candidates.json $Q.tsv data/review/274-dark-review.tsv
  echo "queue: $(wc -l < $Q.tsv) files; review: $(($(wc -l < data/review/274-dark-review.tsv) - 1)) books"
  if [ -s $Q.tsv ]; then
    NETPACE=0 NET_MB=0 DL_JOBS=12 CONN=8 STAGE_GB=5 python3 scripts/fetch_queue.py $Q.tsv 274-pre700-dark
    python3 - <<'EOF' > /tmp/274-added.tsv
import csv, os
done = {l.strip() for l in open('data/queue/274-pre700-dark.done', encoding='utf-8')} if os.path.exists('data/queue/274-pre700-dark.done') else set()
for row in csv.reader(open('data/queue/274-pre700-dark.tsv', encoding='utf-8'), delimiter='\t'):
    if len(row) >= 3 and row[2] in done: print(f'{row[2]}\t{row[1]}')
EOF
    echo "uploaded: $(wc -l < /tmp/274-added.tsv) files"
    [ -s /tmp/274-added.tsv ] && python3 scripts/index_update.py 274-pre700-dark --add /tmp/274-added.tsv
  fi
  NO_OPEN=1 scripts/refresh.sh
  git add data/queue/274-pre700-dark* data/review/274-dark-review.tsv data reports 2>/dev/null
  git commit -qm "274: pre-700 AH books whose Waqfeya items went dark — other archive.org uploads verified from their title pages and added; the rest listed for review

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" && echo "committed $(git log --oneline -1)"
  echo "$(date -u '+%F %T') chain done"
} >> "$LOG" 2>&1
