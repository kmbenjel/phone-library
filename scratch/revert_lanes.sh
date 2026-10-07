#!/usr/bin/env bash
# One-off (2026-10-07): the crop revert in two FTP lanes (owner: «تزامن ذكي غير ضار»; full speed until he says otherwise).
# lists/212-uncrop-x.tsv and -y.tsv are disjoint halves of what was left (alternating by size); each lane is resumable.
# Then a second pass of each lane (phone drops), records remapped, indexes refreshed and published, commit.
cd "$(dirname "$0")/.."
export NETPACE=${NETPACE:-0}
log(){ echo "$(date '+%F %T') $*"; }
until python3 -c "import sys; sys.path.insert(0,'scripts'); import phone_host; sys.exit(0 if phone_host.find() else 1)" 2>/dev/null; do sleep 120; done
for pass in 1 2; do
  python3 scripts/revert_crops.py lists/212-uncrop-x.tsv --prefix 212-x >> logs/212-uncrop-x.log 2>&1 &
  sleep 20
  python3 scripts/revert_crops.py lists/212-uncrop-y.tsv --prefix 212-y >> logs/212-uncrop-y.log 2>&1 &
  wait
  log "pass $pass: x $(tail -1 logs/212-uncrop-x.log); y $(tail -1 logs/212-uncrop-y.log)"
done
python3 scripts/substituted_sizes.py; python3 scripts/remap_paths.py
NO_OPEN=1 nice scripts/refresh.sh --no-list > logs/refresh-212.log 2>&1
log "refresh: $(tail -2 logs/refresh-212.log | tr '\n' ' ')"
git add -A plans lists scripts data/changes/changes.tsv data/phone/index-now.tsv data/phone/md5.tsv data/inspect/files.jsonl \
  data/phone/substituted.tsv data/fixed WORKLOG.md HANDOFF.md site reports data/catalog.json data/catalog.tsv data/editions 2>/dev/null
git commit -q -m "212: crops undone — every cropped file back to its whole scanned page (owner 2026-10-07)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" && log "committed $(git log -1 --format=%h)"
