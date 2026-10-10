#!/usr/bin/env bash
# The whole library through scripts/book_crop.py, batch after batch (owner 2026-10-10: after trial batch 001, «continue to
# the library»; ~15,600 scans, ≈ 15 books an hour with 4 workers). Waits for any crop_batch.py still running, then:
# crop_queue.py → crop_batch.py (4 workers, nice) → refresh.sh (no Brave) → WORKLOG line → commit. Resumable: run it again.
# Stop: kill the PID of this script (pgrep -f "[c]rop_library.sh"), then the crop_batch.py it started.
cd "$(dirname "$0")/.."
while pgrep -f "[c]rop_batch.py" > /dev/null; do sleep 300; done
while :; do
    b=$(python3 scripts/crop_queue.py --size "${CROP_BATCH:-300}") || { echo "nothing left to crop"; break; }
    log="logs/crop-$b.log"
    echo "$(date -u '+%F %T') start $b" | tee -a "$log"
    nice python3 scripts/crop_batch.py "data/crop/$b.txt" "crop-$b" --workers "${CROP_WORKERS:-4}" >> "$log" 2>&1
    NO_OPEN=1 scripts/refresh.sh >> "$log" 2>&1 || echo "refresh failed (see $log)"
    c=$(grep -c '^CROPPED' "$log"); s=$(grep -c '^skip' "$log"); f=$(grep -c 'FAIL' "$log")
    echo "- $(date -u '+%F %H:%M') — crop $b (library batches, scripts/crop_library.sh): $c cropped, $s left as they are, $f failures (logs/crop-$b.log); refresh." >> WORKLOG.md
    git add data/crop data/changes/changes.tsv data/phone WORKLOG.md > /dev/null 2>&1
    git commit -q -m "crop $b: $c cropped, $s left as they are, $f failures (library batches)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" || true
done
