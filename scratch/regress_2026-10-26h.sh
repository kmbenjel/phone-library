#!/usr/bin/env bash
# One-off (2026-10-26): the regression after 26g (b32a237bbf, 0 failures, its diff looked at page by page). 26g's new third
# rule (a clear tilt both measures saw, turned when the image reading falls to a third) turned مشتبهات القرآن ص 89 0.6°: its
# Quranic lines are set one by one, the upper ones level, the lower 0.5–1.25°, and the turn made six level lines lean
# 0.6–0.9°. GUARD G: each line of the text block measured on its own at 1,400 px (line_leans); the third rule refuses a turn
# that makes two or more level lines (≤ 0.3°) lean (≥ 0.5°) when they are a fifth of the lines read or more → tilt_disputed
# + lines_lean. Benched on the cached first look (fbwq.py; «fix» reproduced 26g on all 3 books): مشتبهات — only p. 89
# differs (not turned); سيبويه ج 2 — 0 pages (p. 221 still turned); خزانة الأدب ج 1 — see HANDOFF. Case row 126 (مشتبهات
# ص 89 «turn no») is new to this run. book_crop.py = bench code bc_g2.py (byte-identical).
cd "$(dirname "$0")/.."
M=data/crop/.regress-2026-10-26h; [ -e $M ] && { echo "already ran"; exit 1; }; touch $M
R=logs/crop-regress-2026-10-26h.log; : > $R
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
python3 scripts/crop_recipe_diff.py f06a68adb2 "$B" > logs/crop-regress-diff-2026-10-26h.log 2>&1
python3 scripts/crop_recipe_diff.py b32a237bbf "$B" > logs/crop-regress-diff-2026-10-26h-vs-26g.log 2>&1   # (only what guard G changed: 26g was looked at)
echo "$(date -u '+%F %T') diffs written: logs/crop-regress-diff-2026-10-26h.log, logs/crop-regress-diff-2026-10-26h-vs-26g.log"
