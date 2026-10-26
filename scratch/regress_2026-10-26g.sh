#!/usr/bin/env bash
# One-off (2026-10-26): the regression after 26f's two failures, both understood and fixed in book_crop (diff against
# f06a68adb2, the last passing run, 26b). A — أسرار البلاغة ت شاكر fell to «level only»: its printed side headings run out to
# the scan's edge, the 26b crop cut them on 74 pages; edge_letters (2bb44a7384) saw them, but 31 pages needed a sideways slide
# of 2–3.6 % and stayed whole (> 5 %): the non-clean branch now slides up to 4 % for the page's own print when the slide leaves
# out none of the print the box held (verify_far). B — سيبويه ج 2 p. 221, a colophon whose long display lines lie 0.75–0.85°,
# was left «tilted by both measures»: a clear tilt (≥ 0.4°) both measures saw is turned when the shear then reads level and
# the image ≤ 0.35° and ≤ a third of its reading before (third(), image_third). Benched first on the cached first look of
# both books (fbwq.py, scratchpad of session 3c2ec828…). With them, on the bench: letters in the edge shadow are the page's
# own print, never cut as strays (A2: 25 more side headings of أسرار البلاغة, the manuscript folio references of سيبويه);
# in the clean branch an edge letter wholly outside the box is taken in too (A3, خريدة القصر 01 ص 259، 451); the dots and
# tails of an edge letter go with it (A4, أسرار ص 136 «المجاز»). book_crop.py = bench code b32a237bbf (byte-identical).
# 6 cases added (crop-regression.tsv, the last 6 rows). Also: crop_batch.room() 1.5 GB a book (measured 0.97–1.29).
cd "$(dirname "$0")/.."
M=data/crop/.regress-2026-10-26g; [ -e $M ] && { echo "already ran"; exit 1; }; touch $M
R=logs/crop-regress-2026-10-26g.log; : > $R
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
python3 scripts/crop_recipe_diff.py f06a68adb2 "$B" > logs/crop-regress-diff-2026-10-26g.log 2>&1
python3 scripts/crop_recipe_diff.py 2bb44a7384 "$B" > logs/crop-regress-diff-2026-10-26g-vs-26f.log 2>&1   # (only what fixes A and B changed: 26f was looked at)
echo "$(date -u '+%F %T') diffs written: logs/crop-regress-diff-2026-10-26g.log, logs/crop-regress-diff-2026-10-26g-vs-26f.log"
