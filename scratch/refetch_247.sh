#!/usr/bin/env bash
# One-off (2026-10-08 06:30): the 19 originals restored by 224 were deleted at 06:14 by a second run of that one-off
# (another agent, Antigravity). Fetch them again from archive.org (exact sizes, verified) straight to their places,
# then fix index-now (the second run re-added the 19 paths though the files were gone), refresh, commit.
cd "$(dirname "$0")/.."
export NETPACE=0 NET_MB=0
log(){ echo "$(date '+%F %T') $*"; }
python3 scripts/fetch_queue.py data/queue/247-refetch-originals.tsv 247-refetch-originals > logs/247-refetch.log 2>&1
log "fetch: $(tail -1 logs/247-refetch.log)"
NO_OPEN=1 nice scripts/refresh.sh > logs/refresh-247.log 2>&1      # full guarded listing: index-now = the phone again
log "refresh: $(grep -E 'files$|short|web:' logs/refresh-247.log | tr '\n' ' ')"
python3 scripts/remap_paths.py | tail -2; python3 scripts/report_fixed.py | tail -1
git add -A data/queue/247-* scratch/refetch_247.sh scripts data/changes/changes.tsv data/phone/index-now.tsv data/phone/md5.tsv \
  data/inspect/files.jsonl data/fixed data/editions data/compare data/review data/catalog.json data/catalog.tsv \
  data/phone/provenance.tsv site reports selection WORKLOG.md HANDOFF.md 2>/dev/null
git commit -q -m "247: the 19 originals fetched again (a second run of the 224 one-off by another agent had deleted them); apply_plan exits 1 on a failed move; substitute needs the copy present

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" && log "committed $(git log -1 --format=%h)"
