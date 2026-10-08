#!/usr/bin/env bash
# One-off (2026-10-08 ~02:20): the phone left the network mid-restore. When it answers again:
#   224 restore finished (الشفا upload from the staged file, then the 19 originals substituted — nothing was moved before),
#   title-page plans 236–238 applied, records remapped, full guarded listing + refresh + web, commit.
cd "$(dirname "$0")/.."
export NETPACE=0 NET_MB=0
log(){ echo "$(date '+%F %T') $*"; }
until H=$(python3 -c "import sys; sys.path.insert(0,'scripts'); import phone_host; print(phone_host.find() or '')" 2>/dev/null) && [ -n "$H" ]; do sleep 120; done
rclone config update phone host "$H" >/dev/null; log "phone back at $H"
python3 scratch/restore_recompressed_224.py >> logs/224-restore.log 2>&1; log "224: $(tail -2 logs/224-restore.log | tr '\n' ' ')"
for p in 236-sheets-273-275 237-sheets-276-278 238-sheets-279-281; do
  grep -q $'\t'"$p"'$' data/changes/changes.tsv && continue
  python3 scripts/apply_plan.py plans/$p.tsv | tail -1 | sed "s/^/$p: /"; python3 scripts/index_update.py $p | tail -1
done
python3 scripts/substituted_sizes.py; python3 scripts/remap_paths.py | tail -2
python3 scripts/report_fixed.py | tail -1
NO_OPEN=1 nice scripts/refresh.sh > logs/refresh-after-224.log 2>&1; log "refresh: $(grep -E 'files$|short|web:' logs/refresh-after-224.log | tr '\n' ' ')"
git add -A plans lists scratch scripts data/changes/changes.tsv data/phone/index-now.tsv data/phone/md5.tsv data/inspect/files.jsonl \
  data/phone/substituted.tsv data/queue/224-restore-recompressed.* data/fixed data/editions data/compare data/review data/catalog.json \
  data/catalog.tsv data/phone/provenance.tsv WORKLOG.md HANDOFF.md site reports selection 2>/dev/null
git commit -q -m "224: recompressed files back to their originals; title-page plans 236–238 (sheets 273–281)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" && log "committed $(git log -1 --format=%h)"
