#!/usr/bin/env bash
# One-off (2026-10-08 night): the 4 offset-MediaBox files uncropped, title-page plans 218 + 220–223 applied, refresh, commit.
cd "$(dirname "$0")/.."
export NETPACE=0
log(){ echo "$(date '+%F %T') $*"; }
python3 scripts/revert_crops.py lists/212-redo.tsv --prefix 212-r2- && log "r2: $(tail -1 logs/212-r2-01-copies.log | cut -c1-120)"
for p in 218-sheets-230-232 220-sheets-233-235 221-sheets-236-238 222-sheets-239-241 223-sheets-242-244; do
  python3 scripts/apply_plan.py plans/$p.tsv | tail -1 | sed "s/^/$p: /"
  python3 scripts/index_update.py $p | tail -1
done
python3 scripts/substituted_sizes.py; python3 scripts/remap_paths.py
NO_OPEN=1 nice scripts/refresh.sh --no-list > logs/refresh-after-redo.log 2>&1; log "refresh: $(grep -E 'web:' logs/refresh-after-redo.log)"
git add -A plans lists scripts scratch data/changes/changes.tsv data/phone/index-now.tsv data/phone/md5.tsv data/inspect/files.jsonl \
  data/phone/substituted.tsv data/phone/listing-2026-10-08-0130.tsv data/fixed data/editions data/compare data/review data/catalog.json \
  data/catalog.tsv data/phone/provenance.tsv WORKLOG.md HANDOFF.md site reports selection 2>/dev/null
git commit -q -m "212 finished (92 + 4 files), 219 obsolete cropped copies, title-page plans 218 and 220–223 (sheets 230–244)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" && log "committed $(git log -1 --format=%h)"
