#!/usr/bin/env bash
# One-off (2026-10-27): the regression after 26h (20d30c2020, guard G). Four tilt changes, each benched first on the cached
# first look of whole books (scratch/tilt-fixes-2026-10-27/bench/fbq.py; the base version reproduced 26h's recipes):
# P — a sheet's or copier's line across the whole sheet is no ruler: the projection read again without it (الموسوعة 38
# ص 423, 437, 438); Q — a page the projection finds tilted is turned by its lines' baselines when ≥ 6 lines agree (book_crop
# base_tilt, 1,400 px), checked by them on the turned page (≤ 0.1°), instead of the 0.2°-step loop the shear measure picked
# from (خزانة 01 ص 68 and 110, صبح الأعشى 05 ص 250); R — a page the measures' gates left whose lines agree on ≥ 0.25° and
# the shear measure reads the same tilt: turned by its baselines (روضة المستبين ص 491). W — lines at two angles (the owner on
# crop-tilt-002, 2026-10-27: «Leave as scanned»): every turn checked line by line, each line followed across the page
# (line_tracks), on the page as scanned and as turned; a turn that makes level lines lean while the lines do not take it is
# undone and the page listed (الموسوعة 38 ص 42, 423, 892; صبح الأعشى 05 ص 234; أنساب الأشراف المقدمة ص 47), or turned
# by the angle its lines take when that levels them (خزانة ج 4 ص 469); a turn that levels every printed rule while the
# text gives no reading of its own stays (an index under its head rule: خريدة القصر 01 ص 637, 703 — W step 3). Q2 — when
# the baselines cannot read the turned page at all, their turn is confirmed by the shear as the projection's were (أنساب
# الأشراف المقدمة ص 44 had its right turn undone). P, Q, W benched on whole books (00597fea27cf, 2b47002d18ab); W and W3
# replayed on every turned page of 9 books' recipes (scratch/tilt-fixes-2026-10-27/w/wsim2.py, wsim3.py + wsim3_eval.py,
# wsim4.py); Q2 on the 116 pages of 5 books it can touch (w/fbc.py). New check «level» and 15 cases.
# book_crop.py = scripts/book_crop.py 20d30c2020 + patch_p, patch_q, patch_r, patch_w, patch_w3, patch_q2
# (scratch/tilt-fixes-2026-10-27).
cd "$(dirname "$0")/.."
M=data/crop/.regress-2026-10-27i; [ -e $M ] && { echo "already ran"; exit 1; }; touch $M
R=logs/crop-regress-2026-10-27i.log; : > $R
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
python3 scripts/crop_recipe_diff.py 20d30c2020 "$B" > logs/crop-regress-diff-2026-10-27i.log 2>&1   # (vs 26h: what P, Q, R, W, W3, Q2 changed)
python3 scripts/crop_recipe_diff.py f06a68adb2 "$B" > logs/crop-regress-diff-2026-10-27i-vs-26b.log 2>&1
echo "$(date -u '+%F %T') diffs written: logs/crop-regress-diff-2026-10-27i.log, logs/crop-regress-diff-2026-10-27i-vs-26b.log"
