#!/usr/bin/env bash
# One-off (2026-10-25): the crop regression gate on book_crop.py after the fixes of 2026-10-25 (turns certified by rules or
# by their own ink no longer listed as «still tilted»; scanner bands not counted as ink once a page is turned; a small
# tilt confirmed by the page's own ruler; best_turn's tie-break; the uploader's signature in a foot corner) →
# logs/crop-regress-2026-10-25.log. Regression ONLY: the redo of the 1,122 books is started by hand after the result and
# the owner's verdicts on site/crop-tilt-001.html (the pages the measures still cannot decide).
# Runs in the memory pen (crop.slice), workers from the governor. Never rerun: refuses when its marker exists.
cd "$(dirname "$0")/.."
M=data/crop/.regress-2026-10-25; [ -e $M ] && { echo "already ran"; exit 1; }; touch $M
R=logs/crop-regress-2026-10-25.log; : > $R
echo "$(date -u '+%F %T') regression starts (book_crop $(md5sum scripts/book_crop.py | cut -c1-10))"
for try in $(seq 1 30); do                      # a crash (no «N failures» line: the brake killed a worker) is run again
  echo "== attempt $try $(date -u '+%F %T')" >> $R
  python3 scripts/crop_regress.py >> $R 2>&1
  tail -3 $R | grep -qE '^[0-9]+ failures' && break
  echo "$(date -u '+%F %T') regression crashed (attempt $try) — waiting for memory, then again"
  ok=0; while [ "$ok" -lt 4 ]; do sleep 30; [ "$(awk '/^MemAvailable:/{printf "%d", $2/1048576}' /proc/meminfo)" -ge 4 ] && ok=$((ok + 1)) || ok=0; done
done
f=$(grep -oE '^[0-9]+ failures' $R | tail -1 | cut -d' ' -f1)
echo "$(date -u '+%F %T') regression finished: ${f:-?} failures — see $R"
