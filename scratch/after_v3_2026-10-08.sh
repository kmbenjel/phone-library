#!/usr/bin/env bash
# One-off (2026-10-08 08:55 GMT, written as the session was ending). Runs unattended, log logs/after-v3-2026-10-08.log:
#  1. waits for the crop v3 re-analysis of the sample books (scratchpad crop/v3_drive.py), rebuilds the sample page
#     site/samples/crop-2026-10-08/index.html (crop/build_v3.py) and opens it in Brave for the owner;
#  2. uploads the 4 front-matter files of المقاصد الشافية (queue 267, pages copied losslessly from the 100 ppi copy),
#     adds the uploaded ones to index-now.tsv, commits.
# NOT here: deleting the 100 ppi copy (plan 268) — next session, after checking that the 4 uploads are on the phone.
# Never rerun once finished (AGENTS.md §6): the log ends with «chain done».
set -u
cd "$HOME/projects/phone-library"
S=/tmp/claude-1000/-home-k-projects-phone-library/522d85d2-5dfc-4f55-aca2-bcb92e64bb5c/scratchpad/crop
LOG=logs/after-v3-2026-10-08.log
if grep -q "chain done" "$LOG" 2>/dev/null; then echo "already done (see $LOG)"; exit 0; fi
{
  echo "$(date -u '+%F %T') start"
  while pgrep -f "[v]3_drive.py" >/dev/null; do sleep 20; done
  echo "$(date -u '+%F %T') re-analysis finished: $(grep -c '^{' "$S/v3/drive.log") books"
  if nice python3 "$S/build_v3.py"; then
    setsid -f brave-browser "$PWD/site/samples/crop-2026-10-08/index.html" >/dev/null 2>&1 && echo "sample page opened in Brave"
  else echo "BUILD FAILED"; fi
  NETPACE=0 python3 scripts/fetch_queue.py data/queue/267-maqasid-fronts.tsv 267-maqasid-fronts
  python3 - <<'EOF' > /tmp/267-added.tsv
import csv
done = {l.strip() for l in open('data/queue/267-maqasid-fronts.done', encoding='utf-8')} if __import__('os').path.exists('data/queue/267-maqasid-fronts.done') else set()
for url, size, target, why in csv.reader(open('data/queue/267-maqasid-fronts.tsv', encoding='utf-8'), delimiter='\t'):
    if target in done: print(f'{target}\t{size}')
EOF
  echo "uploaded: $(wc -l < /tmp/267-added.tsv) of 4"
  [ -s /tmp/267-added.tsv ] && python3 scripts/index_update.py 267-maqasid-fronts --add /tmp/267-added.tsv
  git add data/queue/267-maqasid-fronts.* data/changes/changes.tsv data/phone/index-now.tsv
  git commit -qm "267: the title pages + imprint of المقاصد الشافية ج 4, 5, 6, 9 added to the 300 ppi set (lossless copies from the 100 ppi set, to be deleted by 268)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" && echo "committed $(git log --oneline -1)"
  echo "$(date -u '+%F %T') chain done"
} >> "$LOG" 2>&1
