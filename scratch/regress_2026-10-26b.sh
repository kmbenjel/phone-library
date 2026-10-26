#!/usr/bin/env bash
# One-off (2026-10-26, 02:50): the regression run of the crop revisit WITH THE COVER PRINT RULE — the run regress_2026-10-26.sh
# was stopped after 11 books (60 PASS, 0 FAIL) to take in book_crop.cover_marks / cover_window (owner 2026-10-25 on
# خزانة الأدب ج 1 ص 1: «cover is there but not filling the page»; the even fill cut its last line, the year): a cover is
# still cut evenly to fill the page, but the cut moves into plain ground to keep a line of print or a spine whole.
# History of the method changes in this run: the run of
# 2026-10-25b (regress_2026-10-25b.sh) was stopped: its Turner (one turned copy per page) was NOT exact where a page's
# image is less than 90 % shown (a CropBox, a clip): MuPDF drew a later view from the whole decoded image where a fresh
# copy decodes the part — 19 of 7,160 test renders a sub-pixel apart. Now such a view is drawn from a fresh copy
# (book_crop.Turner, whole_shown, odd_drawing); the rest of the revisit unchanged: speed (each view measured once, the
# coarse projection peak at 0° ends the search), memory (stamp candidates keep their images only where a test reads them),
# best_turn takes a turn level by both measures first, a ruler-certified small tilt with the image measure up to 0.35°,
# the owner's turns (data/crop/owner-turns.tsv)
# → logs/crop-regress-2026-10-26b.log, then the recipe diff against book_crop 5d6113b97c → logs/crop-regress-diff-2026-10-26b.log.
# Regression ONLY: the pilot redo and the redo of the 1,122 books are started by hand after the diff is explained.
# Runs in the memory pen (crop.slice), workers from the governor. Never rerun: refuses when its marker exists.
cd "$(dirname "$0")/.."
M=data/crop/.regress-2026-10-26b; [ -e $M ] && { echo "already ran"; exit 1; }; touch $M
R=logs/crop-regress-2026-10-26b.log; : > $R
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
python3 scratch/crop_recipe_diff_2026-10-26.py "$B" > logs/crop-regress-diff-2026-10-26b.log 2>&1
echo "$(date -u '+%F %T') diff written: logs/crop-regress-diff-2026-10-26b.log"
