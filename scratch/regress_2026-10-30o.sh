#!/usr/bin/env bash
# One-off (2026-10-30): the regression after 27n (a0e20119c2 = 27m + F + N), whose diff against 27m was looked at by eye on
# all 31 books. F held (the owner's kept pages back as scanned: صبح الأعشى 05 ص 367, اللآلئ 02 ص 186). N changed 4 pages:
# 1 right — إرشاد الساري 10 ص 477, unturned → −0.6°, level (N's own page); 2 worse — القوافي للتنوخي p. 102 −0.45° → −0.675°
# (a warped page: the rule under the text −0.06° → −0.29°), معجم تيمور الكبير 02 p. 166 −0.65° → −0.875° (the head rule −0.07°
# → −0.29°); 1 trade-off — الفوائد المحصورة p. 457 −0.629° → −0.25° (a sheared index: the columns' edges 0.03° → 0.41°).
# N3 — THE TURNS BESIDE THE LINES' OWN, A LAST RESORT: the turn the lines' tracks set but refused for their spread (≥ 5 lines
# read: fix N2), that the shear could not confirm, is only remembered; the turns ±0.025°/±0.05° beside it are read after guard
# W, only when the page is left unturned (two angles, unsure, disputed, untreated), and the one taken must make no level lines
# lean (two_angles, W's own check). ntest.py: 102 −0.45°, 166 −0.65°, 457 −0.629° (27m's turns), 477 −0.6° (N's).
# New case kind «skew» (crop_regress.py): the turn looked at by eye and measured, ±0.1° — rows for 102, 166, 457 (the level
# check cannot read them); 27m passes them, 27n fails all three.
# Expected against 27n: those 3 pages back to 27m's turns and frames, ص 477 unchanged, any other page fix N reached in 27n's
# last 10 books looked at again — every other page identical. book_crop.py = a0e20119c2 + patch_n3.py
# (scratch/crop-fixes-2026-10-29) = code/bc_fn3.py.
cd "$(dirname "$0")/.."
M=data/crop/.regress-2026-10-30o; [ -e $M ] && { echo "already ran"; exit 1; }; touch $M
R=logs/crop-regress-2026-10-30o.log; : > $R
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
python3 scripts/crop_recipe_diff.py a0e20119c2 "$B" > logs/crop-regress-diff-2026-10-30o.log 2>&1   # (vs 27n: what N3 changed)
python3 scripts/crop_recipe_diff.py 4fcdf11f58 "$B" > logs/crop-regress-diff-2026-10-30o-vs-27m.log 2>&1
echo "$(date -u '+%F %T') diffs written: logs/crop-regress-diff-2026-10-30o.log, …-30o-vs-27m.log"
