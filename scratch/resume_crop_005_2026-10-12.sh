#!/usr/bin/env bash
# One-off (2026-10-12): the laptop restarted at 13:57 during crop batch-005 (65 of 300 done; no phone file was left half
# written — every unfinished file still had its logged size). Finishes batch-005 (crop_batch skips what done.tsv holds),
# then refresh + WORKLOG + commit as crop_library.sh does, then hands over to crop_library.sh for the next batches.
# Never rerun: refuses when its marker exists.
cd "$(dirname "$0")/.."
M=data/crop/.resume-005-done; [ -e $M ] && { echo "already ran"; exit 1; }
b=batch-005; log="logs/crop-$b.log"
echo "$(date -u '+%F %T') resume $b after the laptop restart" | tee -a "$log"
nice python3 scripts/crop_batch.py "data/crop/$b.txt" "crop-$b" --workers "${CROP_WORKERS:-4}" >> "$log" 2>&1
touch $M
NO_OPEN=1 scripts/refresh.sh >> "$log" 2>&1 || echo "refresh failed (see $log)"
c=$(grep -c '^CROPPED' "$log"); s=$(grep -c '^skip' "$log"); f=$(grep -c 'FAIL' "$log")
echo "- $(date -u '+%F %H:%M') — crop $b (library batches; resumed after the laptop restart): $c cropped, $s left as they are, $f failures (logs/crop-$b.log); refresh." >> WORKLOG.md
git add data/crop data/changes/changes.tsv data/phone WORKLOG.md > /dev/null 2>&1
git commit -q -m "crop $b: $c cropped, $s left as they are, $f failures (resumed after the laptop restart)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" || true
exec scripts/crop_library.sh
