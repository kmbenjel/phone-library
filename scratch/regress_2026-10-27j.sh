#!/usr/bin/env bash
# One-off (2026-10-27): the regression after 26i (3205efa17f: P, Q+Q2, R, W+W3). Two changes, each benched first on whole
# books (scratch/crop-fixes-2026-10-27b: fbo.py runs book_crop.plan() on one cached first look; the base version reproduced
# 26i's recipe exactly):
# O — (1) an ornament the book repeats (فهرسة ابن خير: the end-of-section fleuron, a 59 pt square, on 12 pages) was read as a
# stain: a «stain» at least M across both ways whose twin (same width and height ± 10 %, centre on the same vertical line ±
# 3 %) stands on 3 other text pages, at any height, is print — joining its page's box after the full/short sort (a section's
# end keeps its neighbours' place); (2) a dodge that takes nothing of the mark out of the box is not made (the fleuron pages
# had slid to the page's top, their page numbers 120 pt low; أسرار البلاغة pp. 82–107 and 4 more books alike); (3) specks
# where the book prints its page number are that number («- ٥ -» read as dust, فهرسة ابن خير ص 4; مناقب أحمد ص 500–601).
# Q3 — a projection page's turn set by its lines when fix Q's ruler could not read them: base_tilt leaves out lines more than
# 1° from the median (two lines run together) before it counts them, and when even so the baselines cannot read the page,
# the lines followed across it (line_tracks, ≥ 5 lines, IQR < 0.3°) set the turn and check it on the turned page. On the
# 26h projection pages, judged by the independent ruler: turns ≥ 0.2° off fell from 23 % to 2.4 % of the pages the robust
# baselines alone read.
# book_crop.py = scripts/book_crop.py 3205efa17f + patch_o.py + patch_q3.py (scratch/crop-fixes-2026-10-27b).
cd "$(dirname "$0")/.."
M=data/crop/.regress-2026-10-27j; [ -e $M ] && { echo "already ran"; exit 1; }; touch $M
R=logs/crop-regress-2026-10-27j.log; : > $R
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
python3 scripts/crop_recipe_diff.py 3205efa17f "$B" > logs/crop-regress-diff-2026-10-27j.log 2>&1   # (vs 26i: what O and Q3 changed)
python3 scripts/crop_recipe_diff.py f06a68adb2 "$B" > logs/crop-regress-diff-2026-10-27j-vs-26b.log 2>&1
echo "$(date -u '+%F %T') diffs written: logs/crop-regress-diff-2026-10-27j.log, logs/crop-regress-diff-2026-10-27j-vs-26b.log"
