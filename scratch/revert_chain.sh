#!/usr/bin/env bash
# One-off (2026-10-07, owner: «قم باللازم … لا يضيع شيء من النص»): undo all crops, unattended.
#   1. waits for the phone; applies plan 211 (four section moves read from title pages)
#   2. scripts/revert_crops.py: 3,734 cropped files back to their whole scanned pages (paced: netpace, ≤ 6 MB/s)
#   3. records remapped, report 09 rebuilt, indexes refreshed and published, commit
cd "$(dirname "$0")/.."
log(){ echo "$(date '+%F %T') $*"; }
until python3 -c "import sys; sys.path.insert(0,'scripts'); import phone_host; sys.exit(0 if phone_host.find() else 1)" 2>/dev/null; do sleep 120; done
h=$(python3 -c "import sys; sys.path.insert(0,'scripts'); import phone_host; print(phone_host.find())"); rclone config update phone host "$h" >/dev/null
log "phone at $h"
if ! grep -q $'\t211-sections-read$' data/changes/changes.tsv; then
  python3 scripts/apply_plan.py plans/211-sections-read.tsv && python3 scripts/index_update.py 211-sections-read && log "211 applied"
fi
python3 scripts/revert_crops.py lists/212-uncrop.tsv --batch 200 > logs/212-uncrop.log 2>&1
log "revert: $(tail -1 logs/212-uncrop.log)"
python3 scripts/substituted_sizes.py; python3 scripts/remap_paths.py
NO_OPEN=1 nice scripts/refresh.sh --no-list > logs/refresh-212.log 2>&1
log "refresh: $(tail -2 logs/refresh-212.log | tr '\n' ' ')"
git add -A plans lists scripts data/changes/changes.tsv data/phone/index-now.tsv data/phone/md5.tsv data/inspect/files.jsonl \
  data/phone/substituted.tsv data/fixed WORKLOG.md HANDOFF.md site reports data/catalog.json data/catalog.tsv data/editions 2>/dev/null
git commit -q -m "212: crops undone — every cropped file back to its whole scanned page (owner 2026-10-07)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" && log "committed $(git log -1 --format=%h)"
