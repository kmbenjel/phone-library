#!/usr/bin/env bash
# One-off (2026-10-26): regression 26e again (book_crop 2bb44a7384 unchanged), restarted because 26e could not start its
# second book: crop_batch.room() counted the memory its own process kept from the first book (0.83 GB) as taken, and the
# governor's pen (free + what it holds − 2.5 GB) then needed ≥ 4.7 GB free whatever the job held. Now a book analysed in
# the caller's own process (one worker) discounts what that process holds (room(own=…)). 26e's first book is in the cache
# (same key) and comes back at once. Whole-book bench of the fix (session 3c2ec828): equal to 7d358b26b0 on 4 of the 5
# books; خريدة القصر 01: 22 pages differ — 231, 278 and 20 pages of footnote ends, heading starts and note numbers in the
# paper's edge shadow, all looked at: the fix keeps print that 7d358b26b0 (and 26b) cut.
cd "$(dirname "$0")/.."
M=data/crop/.regress-2026-10-26f; [ -e $M ] && { echo "already ran"; exit 1; }; touch $M
R=logs/crop-regress-2026-10-26f.log; : > $R
B=$(md5sum scripts/book_crop.py | cut -c1-10)
echo "$(date -u '+%F %T') regression starts (book_crop $B)"
for try in $(seq 1 30); do                      # a crash (no «N failures» line: the brake killed a worker) is run again
  echo "== attempt $try $(date -u '+%F %T')" >> $R
  python3 scripts/crop_regress.py >> $R 2>&1
  tail -3 $R | grep -qE '^[0-9]+ failures' && break
  echo "$(date -u '+%F %T') regression crashed (attempt $try) — waiting for memory, then again"
  ok=0; while [ "$ok" -lt 4 ]; do sleep 30; [ "$(awk '/^MemAvailable:/{printf "%d", $2/1048576}' /proc/meminfo)" -ge 4 ] && ok=$((ok + 1)) || ok=0; done
done
f=$(grep -oE '^[0-9]+ failures' $R | tail -1 | cut -d' ' -f1)
echo "$(date -u '+%F %T') regression finished: ${f:-?} failures — see $R"
[ "$(md5sum scripts/book_crop.py | cut -c1-10)" = "$B" ] || echo "WARNING: book_crop.py changed during the run"
python3 scripts/crop_recipe_diff.py f06a68adb2 "$B" > logs/crop-regress-diff-2026-10-26f.log 2>&1
echo "$(date -u '+%F %T') diff written: logs/crop-regress-diff-2026-10-26f.log"
