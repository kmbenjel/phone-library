#!/usr/bin/env bash
# One-off (2026-10-26): the regression run after the faithful bench of 7d358b26b0 (26d, stopped) found two real cuts on
# خريدة القصر قسم شعراء الشام 01: p. 231 «وقوله», «(١)», «(٢)» standing out into the paper's edge shadow (read as the sheet's
# edge by marks()' border zone; 26b had moved the box only because the footnote rule — a hairline — crossed it) and p. 278
# «انظر» (its alif, 1.3 pt thick and five times as tall, a «hairline» by printlike's shape, so the text block stopped short
# of the word). Now (second look only, the first look unchanged): letters in the edge shadow that continue a line of print
# are letters (book_crop.edge_letters); a thin upright stroke on a row of print is print (print_marks). Faithful bench: the
# fix equals 7d358b26b0 on all 106 bench pages of 5 books but those two. → logs/crop-regress-2026-10-26e.log, then the
# recipe diff against f06a68adb2 → logs/crop-regress-diff-2026-10-26e.log (scripts/crop_recipe_diff.py). Regression ONLY:
# the pilot and the redo are started by hand after the diff is explained. Runs in the memory pen (crop.slice), workers
# from the governor. Never rerun: refuses when its marker exists.
cd "$(dirname "$0")/.."
M=data/crop/.regress-2026-10-26e; [ -e $M ] && { echo "already ran"; exit 1; }; touch $M
R=logs/crop-regress-2026-10-26e.log; : > $R
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
python3 scripts/crop_recipe_diff.py f06a68adb2 "$B" > logs/crop-regress-diff-2026-10-26e.log 2>&1
echo "$(date -u '+%F %T') diff written: logs/crop-regress-diff-2026-10-26e.log"
