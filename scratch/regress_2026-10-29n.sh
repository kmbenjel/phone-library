#!/usr/bin/env bash
# One-off (2026-10-29): the regression after 27m (4fcdf11f58 = 27l + L, B, B2–B5), whose diff against 27l was looked at by eye
# and held one fault: صبح الأعشى 05 ص 367 — the page of crop-tilt-003 row 21 the owner kept as scanned for its two angles
# («mark all ok», 2026-10-29) — turned −0.625°. Fix L narrowed its text block as scanned by 3.6 pt (a thin mark at the left
# edge now a line), line_tracks read its short foot lines otherwise (y 680: −0.18° → −0.41°, no longer read alike in both
# views; y 654 short of «made worse» by 0.007°), and guard W saw one line made to lean instead of three
# (scratch/crop-fixes-2026-10-29/wcheck.py). A knife edge of the measure, not a new rule to tune: the owner's verdicts become data.
# F — THE OWNER'S «LEAVE AS SCANNED» STANDS: a turn of 0 in data/crop/owner-turns.tsv (his 86 pages: crop-tilt-002's 4,
# crop-tilt-003's 82) = the page is never turned, whatever a reading finds (owner_flat keeps the turn the method would make);
# the owner's turn itself applies to a non-zero turn only. 77 «turn no» case rows added for the pages the regression did not
# hold (scratch/crop-fixes-2026-10-29/stage_f.py).
# N — A TURN THE LINES' TRACKS CANNOT READ AT ITS OWN IS READ AT THE TURNS BESIDE IT (±0.025°, ±0.05°; only when the shear
# cannot confirm the turn either): إرشاد الساري 10 ص 477, left 0.55° tilted by 27m (tracks unread at −0.575°, their spread at
# the 0.3° limit; the shear calls −1.5° level there), turned −0.6° and level (−0.008°); case row «477 turn yes» added.
# Expected against 27m: the kept pages 27m turned, back to 27l's frames (ftest.py: ص 367 crop [141.2, 90.6, 494.5, 718.9],
# as 27l); 5b21 ص 477 turned −0.6°; any other page N reaches (tracks unread, shear unsure) — each one looked at; every other
# page identical. book_crop.py = 4fcdf11f58 + patch_f.py + patch_n.py = a0e20119c2 (scratch/crop-fixes-2026-10-29).
cd "$(dirname "$0")/.."
M=data/crop/.regress-2026-10-29n; [ -e $M ] && { echo "already ran"; exit 1; }; touch $M
R=logs/crop-regress-2026-10-29n.log; : > $R
B=$(md5sum scripts/book_crop.py | cut -c1-10)
echo "$(date -u '+%F %T') regression starts (book_crop $B)"
for try in $(seq 1 30); do                      # a crash (no «N failures» line: the brake killed a worker) is run again
  echo "== attempt $try $(date -u '+%F %T')" >> $R
  python3 - >> $R 2>&1 <<'PY'
import sys, time; sys.path.insert(0, 'scripts')
import crop_regress as cr
for p in ('الأدب/صبح الأعشى في كتابة الإنشا - القلقشندي (ط دار الكتب المصرية)/05 - صبح الأعشى في كتابة الإنشا (تابع المقالة الثانية - المقالة الثالثة).pdf',
          'الأدب/خزانة الأدب للبغدادي/02 - خزانة الأدب للبغدادي.pdf',
          'الأدب/خريدة القصر وجريدة العصر - قسم شعراء الشام - العماد الأصفهاني (ت شكري فيصل - المجمع العلمي العربي بدمشق)/01 - خريدة القصر (قسم شعراء الشام - الجزء الأول).pdf',
          'العروض والقوافي/القوافي للتنوخي - أبو يعلى التنوخي/1824 كتاب اقرا اونلاين pdf القوافي للتنوخي.pdf',
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
python3 scripts/crop_recipe_diff.py 4fcdf11f58 "$B" > logs/crop-regress-diff-2026-10-29n.log 2>&1   # (vs 27m: what F changed)
python3 scripts/crop_recipe_diff.py 6a1fad7b21 "$B" > logs/crop-regress-diff-2026-10-29n-vs-27l.log 2>&1
echo "$(date -u '+%F %T') diffs written: logs/crop-regress-diff-2026-10-29n.log, …-29n-vs-27l.log"
