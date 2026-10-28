#!/usr/bin/env bash
# One-off (2026-10-28): the regression after 26i (3205efa17f: P, Q+Q2, R, W+W3), whose diff was read page by page first
# (scratch/crop-fixes-2026-10-27b: turn_judge.py, sel_sheets.py, inkjudge in the session scratchpad). Four changes:
# O — (1) an ornament the book repeats (فهرسة ابن خير: the end-of-section fleuron on 12 pages) was read as a stain: a «stain»
# whose twin (same size ± 10 %, same vertical axis ± 3 %) stands on 3 other text pages is print; (2) a dodge that takes nothing
# of the mark out of the box is not made; (3) specks where the book prints its page number are that number. Benched (fbo.py).
# Q3 — a projection page fix Q's baselines could not read: the lines followed across it (line_tracks) set the turn, then the
# baselines with lines > 1° from their median left out.
# H — a scan line broken into one-pixel dashes is no letter at the first look: a horizontal hairline counts only beside a
# letter on its row (26i: خزانة 01 ص 53, 176, خزانة 04 ص 74, 194, 247, 491 — the box pulled ≈ 20 pt over the scan's top line,
# one piece read as the page number).
# G — a line split into a label and its text is no baseline: an index row's page number across the empty middle tilted every
# row's fit (26i: مشتبهات القرآن ص 178, a level index page, turned 1.425°). Surveyed on every page 26i reads by its baselines.
# book_crop.py = 3205efa17f + patch_o.py + patch_q3.py + patch_h.py + patch_g.py (scratch/crop-fixes-2026-10-27b) = 9a43a0bc8c.
# The six books the changes were found on are analysed first (crop_regress.recipe, the same cache key), so their diff can be
# looked at while the others run.
cd "$(dirname "$0")/.."
M=data/crop/.regress-2026-10-28j; [ -e $M ] && { echo "already ran"; exit 1; }; touch $M
R=logs/crop-regress-2026-10-28j.log; : > $R
B=$(md5sum scripts/book_crop.py | cut -c1-10)
echo "$(date -u '+%F %T') regression starts (book_crop $B)"
for try in $(seq 1 30); do                      # a crash (no «N failures» line: the brake killed a worker) is run again
  echo "== attempt $try $(date -u '+%F %T')" >> $R
  python3 - >> $R 2>&1 <<'PY'
import sys, time; sys.path.insert(0, 'scripts')
import crop_regress as cr
for p in ('الأدب/خزانة الأدب للبغدادي/01 - خزانة الأدب للبغدادي.pdf',
          'التجويد والقراءات/مشتبهات القرآن - الكسائي (ت محمد محمد داود - دار المنار).pdf',
          'الأدب/خزانة الأدب للبغدادي/04 - خزانة الأدب للبغدادي.pdf',
          'فهارس الكتب والأدلة/فهرسة ابن خير الإشبيلي/1 - فهرسة ابن خير الإشبيلي.pdf',
          'كتب اللغة/معجم تيمور الكبير في الألفاظ العامية - أحمد تيمور باشا/02 - معجم تيمور الكبير (الألف - التاء).pdf',
          'الأدب/صبح الأعشى في كتابة الإنشا - القلقشندي (ط دار الكتب المصرية)/05 - صبح الأعشى في كتابة الإنشا (تابع المقالة الثانية - المقالة الثالثة).pdf'):
    pdf = cr.local_copy(p); cr.PATHS[pdf] = p; t = time.time(); cr.recipe(pdf)
    print(f'   (key book first: {p.rsplit("/", 1)[-1][:60]} in {time.time() - t:.0f} s)', flush=True)
PY
  python3 scripts/crop_regress.py >> $R 2>&1
  tail -3 $R | grep -qE '^[0-9]+ failures' && break
  echo "$(date -u '+%F %T') regression crashed (attempt $try) — waiting for memory, then again"
  ok=0; while [ "$ok" -lt 4 ]; do sleep 30; [ "$(awk '/^MemAvailable:/{printf "%d", $2/1048576}' /proc/meminfo)" -ge 4 ] && ok=$((ok + 1)) || ok=0; done
done
f=$(grep -oE '^[0-9]+ failures' $R | tail -1 | cut -d' ' -f1)
echo "$(date -u '+%F %T') regression finished: ${f:-?} failures — see $R"
[ "$(md5sum scripts/book_crop.py | cut -c1-10)" = "$B" ] || echo "WARNING: book_crop.py changed during the run"
python3 scripts/crop_recipe_diff.py 3205efa17f "$B" > logs/crop-regress-diff-2026-10-28j.log 2>&1   # (vs 26i: what O, Q3, H, G changed)
python3 scripts/crop_recipe_diff.py f06a68adb2 "$B" > logs/crop-regress-diff-2026-10-28j-vs-26b.log 2>&1
echo "$(date -u '+%F %T') diffs written: logs/crop-regress-diff-2026-10-28j.log, logs/crop-regress-diff-2026-10-28j-vs-26b.log"
