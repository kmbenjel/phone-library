#!/usr/bin/env bash
# One-off (2026-10-28): the regression after 27l (6a1fad7b21 = 26j + C, Q4, T, Q5), which passed (0 failures) but whose diff
# against 26j showed four pages back to 26i's faults — Q4 restored the projection loop's turns, and at those turns the page
# reads differently, 0.025–0.125° apart (scratch/crop-fixes-2026-10-28m: dbg_marks.py, fl.py, bench bplan.py):
# L — A LINE IS THIN BY ITS INK, NOT BY ITS BOX: every turn tilts the scanner's lines with the page; a level one-pixel scan
# line 80 px long is 2–3 px tall turned 0.5–0.8°, over the 0.4 % of the height (2.8 px at 500 px) by a fraction of a pixel,
# and joined the text block: خزانة الأدب ج 2 ص 315 (0.5°, a hook at its end — the page shrunk to 0.86, the book's height
# +3.6 pt) and خزانة الأدب ج 1 ص 332 (−0.8° — the box 29 pt off the text). A mark at a slant is as thin as a level one when
# its ink is (column by column, its middles on one straight line); the grains a turn broke off a line belong to it.
# B — THE SCANNER BANDS READ BEFORE THE TURN BOUND EVERY TURNED PAGE (the generic loop did it, the projection loop, the
# baselines and the tracks did not): خريدة القصر 01 ص 422's black band reads 0.60 dark in its outermost column turned 0.45°
# (the turn's blank wedge) — not over 0.6, no band, the box slid 10 pt onto it. Only the sides that have a band.
# NOT fixed here (known, later): خريدة القصر 01 ص 438 — the dotted-line rule takes the thin strokes at the start of each verse
# line for a dotted line, the footnote/verse numbers fall into the margin, the box 10 pt off (26i the same).
# book_crop.py = 6a1fad7b21 + patch_l.py + patch_b.py (scratch/crop-fixes-2026-10-28m).
cd "$(dirname "$0")/.."
M=data/crop/.regress-2026-10-28m; [ -e $M ] && { echo "already ran"; exit 1; }; touch $M
R=logs/crop-regress-2026-10-28m.log; : > $R
B=$(md5sum scripts/book_crop.py | cut -c1-10)
echo "$(date -u '+%F %T') regression starts (book_crop $B)"
for try in $(seq 1 30); do                      # a crash (no «N failures» line: the brake killed a worker) is run again
  echo "== attempt $try $(date -u '+%F %T')" >> $R
  python3 - >> $R 2>&1 <<'PY'
import sys, time; sys.path.insert(0, 'scripts')
import crop_regress as cr
for p in ('الأدب/خزانة الأدب للبغدادي/02 - خزانة الأدب للبغدادي.pdf',
          'الأدب/خريدة القصر وجريدة العصر - قسم شعراء الشام - العماد الأصفهاني (ت شكري فيصل - المجمع العلمي العربي بدمشق)/01 - خريدة القصر (قسم شعراء الشام - الجزء الأول).pdf',
          'العروض والقوافي/القوافي للتنوخي - أبو يعلى التنوخي/1824 كتاب اقرا اونلاين pdf القوافي للتنوخي.pdf',
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
python3 scripts/crop_recipe_diff.py 6a1fad7b21 "$B" > logs/crop-regress-diff-2026-10-28m.log 2>&1   # (vs 27l: what L and B changed)
python3 scripts/crop_recipe_diff.py 9a43a0bc8c "$B" > logs/crop-regress-diff-2026-10-28m-vs-26j.log 2>&1
python3 scripts/crop_recipe_diff.py 3205efa17f "$B" > logs/crop-regress-diff-2026-10-28m-vs-26i.log 2>&1
echo "$(date -u '+%F %T') diffs written: logs/crop-regress-diff-2026-10-28m.log, …-28m-vs-26j.log, …-28m-vs-26i.log"
