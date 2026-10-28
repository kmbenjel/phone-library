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
# B2 — THE BANDS AS SCANNED ARE NO INK ON A TURNED PAGE THAT LOST THEM (the bench of L + B on خريدة القصر 01): turned 1.5–2.5°,
# a band's outermost column takes in the turn's blank wedge and falls under bands()' 60 % (ص 634: 0.52); read as the page's
# ink, the band ran the box to the sheet's edge and joined a table's rules into one «picture» — 8 pages left whole (633, 634,
# 636, 637, 638, 644, 652, 660). On a side where the turned page shows no band, the band read before the turn (band_mask) is
# no ink, the paper's grey rim beside it a shadow along its turned edge (ص 694); decide()'s off-band slide never passes the box.
# B3 — BESIDE A BAND THE SECOND LOOK KEEPS 4 PT OFF THE PRINT AND SLIDES OFF THE BAND: holding line ends that run to the
# paper's edge with half the margin, or re-centring on them, the frame went back into the band 15–33 pt (ص 344 «عليه», 54,
# 70, 87, 326…); ص 400's line end «حديد», cut in 27l, is whole.
# B4 — B2's rim took a table's grid touching the band for the rim (ص 636–638: the allowed area cut 362–431 pt into the text):
# the rim lies along the band; and nothing beyond the allowed area on a band's side is dodged (ص 389, 579, 585, 637: a
# sliver of the band's turned edge dodged, the text 10–15 pt higher in the frame than on the pages around).
# B5 — THE BAND'S OWN EDGE PIXELS ARE THE BAND: band_mask's straight edge misses the band's last pixel where its edge wobbles;
# a mark wholly within 2.4 pt of a lost band is the band (ص 71: a 16-pt sliver read as a letter, the text block 23 pt longer,
# the page 11 pt high; the top-corner slivers B4 no longer dodges are gone too). A rim, a grid, a letter reach further.
# NOT fixed here (known, later): خريدة القصر 01 ص 438 — the dotted-line rule takes the thin strokes at the start of each verse
# line for a dotted line, the footnote/verse numbers fall into the margin, the box 10 pt off (26i the same). A turn the second
# look drops keeps the first look's turned-view box (ص 636: 5 pt of band in view). The full-height knife edge (ص 595, 606).
# book_crop.py = 6a1fad7b21 + patch_l.py + patch_b.py + patch_b2.py + patch_b3.py + patch_b4.py + patch_b5.py (scratch/crop-fixes-2026-10-28m).
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
python3 scripts/crop_recipe_diff.py 6a1fad7b21 "$B" > logs/crop-regress-diff-2026-10-28m.log 2>&1   # (vs 27l: what L, B, B2–B5 changed)
python3 scripts/crop_recipe_diff.py 9a43a0bc8c "$B" > logs/crop-regress-diff-2026-10-28m-vs-26j.log 2>&1
python3 scripts/crop_recipe_diff.py 3205efa17f "$B" > logs/crop-regress-diff-2026-10-28m-vs-26i.log 2>&1
echo "$(date -u '+%F %T') diffs written: logs/crop-regress-diff-2026-10-28m.log, …-28m-vs-26j.log, …-28m-vs-26i.log"
