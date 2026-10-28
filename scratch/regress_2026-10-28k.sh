#!/usr/bin/env bash
# One-off (2026-10-28): the regression after 26j (9a43a0bc8c = 26i + O, Q3, H, G), which failed on three cases — each traced
# to its cause in scratch/crop-fixes-2026-10-28k (bench: code variants without each fix, bplan.py / fl.py / fl_decide.py):
# C — خزانة 01 ص 1, the cover's year cut again: H made the book's box 15.6 pt shorter (the scan line left out of 34 pages'
# boxes — right), the cover's print then fitted its window with 1.1 pt to spare and cover_window asked 3 + 3: now the ground
# beyond the print is 3 pt or what there is, alike at both ends (only that cover of the 15 changes).
# Q4 — القوافي للتنوخي ص 89 «centred»: Q3 turned ص 70 0.825° instead of the loop's 0.8°, two strokes of a marginal «٤/١» left
# a dotted-line reading, 10 pages of 90 printed in their margins (limit 9), the book lost its clean margins (wider frame,
# ص 84's verse number cut): now the projection loop runs first and its turn stands when the new ruler reads it within 0.05°.
# T — صبح الأعشى 05 ص 234 «turn no»: G and Q3 read its main text truly (−0.42°), the −0.425° turn made the level last section
# lean 0.39–0.52° and guard W's 0.5° bar let it pass: a line is now made worse beyond 0.35° (two_angles' own band). Survey
# of all 7,649 turned pages: survey_w.py (refusals looked at by eye: twoang_vis.py).
# book_crop.py = 9a43a0bc8c + patch_c.py + patch_q4.py + patch_t.py (scratch/crop-fixes-2026-10-28k).
cd "$(dirname "$0")/.."
M=data/crop/.regress-2026-10-28k; [ -e $M ] && { echo "already ran"; exit 1; }; touch $M
R=logs/crop-regress-2026-10-28k.log; : > $R
B=$(md5sum scripts/book_crop.py | cut -c1-10)
echo "$(date -u '+%F %T') regression starts (book_crop $B)"
for try in $(seq 1 30); do                      # a crash (no «N failures» line: the brake killed a worker) is run again
  echo "== attempt $try $(date -u '+%F %T')" >> $R
  python3 - >> $R 2>&1 <<'PY'
import sys, time; sys.path.insert(0, 'scripts')
import crop_regress as cr
for p in ('العروض والقوافي/القوافي للتنوخي - أبو يعلى التنوخي/1824 كتاب اقرا اونلاين pdf القوافي للتنوخي.pdf',
          'الأدب/صبح الأعشى في كتابة الإنشا - القلقشندي (ط دار الكتب المصرية)/05 - صبح الأعشى في كتابة الإنشا (تابع المقالة الثانية - المقالة الثالثة).pdf',
          'الأدب/خزانة الأدب للبغدادي/01 - خزانة الأدب للبغدادي.pdf',
          'التجويد والقراءات/مشتبهات القرآن - الكسائي (ت محمد محمد داود - دار المنار).pdf',
          'الأدب/خزانة الأدب للبغدادي/04 - خزانة الأدب للبغدادي.pdf',
          'فهارس الكتب والأدلة/فهرسة ابن خير الإشبيلي/1 - فهرسة ابن خير الإشبيلي.pdf',
          'كتب اللغة/معجم تيمور الكبير في الألفاظ العامية - أحمد تيمور باشا/02 - معجم تيمور الكبير (الألف - التاء).pdf'):
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
python3 scripts/crop_recipe_diff.py 9a43a0bc8c "$B" > logs/crop-regress-diff-2026-10-28k.log 2>&1   # (vs 26j: what C, Q4, T changed)
python3 scripts/crop_recipe_diff.py 3205efa17f "$B" > logs/crop-regress-diff-2026-10-28k-vs-26i.log 2>&1   # (O, Q3, H, G, C, Q4, T)
python3 scripts/crop_recipe_diff.py f06a68adb2 "$B" > logs/crop-regress-diff-2026-10-28k-vs-26b.log 2>&1
echo "$(date -u '+%F %T') diffs written: logs/crop-regress-diff-2026-10-28k.log, …-28k-vs-26i.log, …-28k-vs-26b.log"
