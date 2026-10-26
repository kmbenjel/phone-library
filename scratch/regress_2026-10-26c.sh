#!/usr/bin/env bash
# One-off (2026-10-26 07:00): the regression run of book_crop's SECOND LOOK ON PRINT — the 26b run (f06a68adb2, 0 failures)
# was checked by eye: its 20 changed pages were right, but the second look (verify) moved or enlarged 95 pages of the 31
# books, most for a scan line's one-pixel dashes that at 1,000 px count as letters and chained the text block up to the
# line (خزانة الأدب ج 1: over the very lines the owner had the box avoid on 2026-10-18), and on 1d12000b2925 ص 323 the box
# slid to a text block held at its 3 % bound and cut the page number at the foot (its bold «٣٢٣» read as a stain on the
# turned page). Now: the text block on print only (book_crop.text_block / printlike: no hairline, no copier's bar), a mark
# the moved box would cut taken in (verify_cut), a stain at the book's folio place restored as the page number (decide,
# folio_blot) → logs/crop-regress-2026-10-26c.log, then the recipe diff against f06a68adb2 → logs/crop-regress-diff-2026-10-26c.log
# (scripts/crop_recipe_diff.py). Regression ONLY: the pilot and the redo are started by hand after the diff is explained.
# Runs in the memory pen (crop.slice), workers from the governor. Never rerun: refuses when its marker exists.
cd "$(dirname "$0")/.."
M=data/crop/.regress-2026-10-26c; [ -e $M ] && { echo "already ran"; exit 1; }; touch $M
R=logs/crop-regress-2026-10-26c.log; : > $R
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
python3 scripts/crop_recipe_diff.py f06a68adb2 "$B" > logs/crop-regress-diff-2026-10-26c.log 2>&1
echo "$(date -u '+%F %T') diff written: logs/crop-regress-diff-2026-10-26c.log"
