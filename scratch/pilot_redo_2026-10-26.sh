#!/usr/bin/env bash
# One-off (2026-10-26): the PILOT of the crop redo (the owner's order of 2026-10-25, item 3: «start the redo with a pilot of
# about 10 books … you review the doubts page; then the full redo runs by itself»), launched by hand only after the
# regression passed (0 failures) and its recipe diff was explained page by page — 26b (f06a68adb2) did, but its second look
# moved boxes over scan lines and cut a page number (HANDOFF 06:45); 26f (2bb44a7384) failed twice (side headings, a colophon's
# tilt — HANDOFF 17:50); 26g (b32a237bbf) passed, but its new third rule turned a page whose lines lie at two angles
# (مشتبهات القرآن ص 89 — guard G, HANDOFF 22:50); 26h passed, then the tilt fixes P, Q, R and guard W (the owner's «Leave
# as scanned» for lines at two angles, 2026-10-27); 26i–27m brought O, Q3–Q5, H, G, T, C, L and the band fixes B–B5, each
# regression's diff looked at by eye; then F (the owner's «leave as scanned» stands: his 86 pages never turned) and N (a turn
# the lines' tracks cannot read is read at the turns beside it): the pilot waits for crop-regress-2026-10-29n (a0e20119c2),
# 0 failures and its diff looked at. Then the method is FROZEN (told the owner 10-29): after it only his pilot remarks or a
# new kind of fault change it.
# The 10 books (data/crop/pilot-2026-10-26.tsv): خزانة الأدب ج 1 (the owner's cover «not filling the page», his «turn»
# pages 26/164/307), four books he marked on 2026-10-14 that are no regression case (مواد البيان: the cover; الإعلام ج 9:
# «444 مالت عكسيا»; كتاب المغازي: «ميلان»; روضة الفهوم: «قبل وبعد كلاهما خطأ») and five drawn at random from the redo list
# (one per section, 4–40 MB). Each phone file was checked first: still the file the old crop wrote (logged MD5).
#   1. crop_redo.py on the list, batch crop-redo-pilot (the phone file replaced only after its upload is verified; resumable;
#      data/crop/redo-done.tsv — the full redo will skip these books);
#   2. the doubts page of the batch → site/crop-doubts.html (report «crop-doubts») for the owner;
#   3. WORKLOG and commit. No refresh here (run it after, outside the memory pen's busy hours).
# Runs in the memory pen (crop.slice), books in parallel as the governor allows. Never rerun: refuses when its marker exists.
cd "$(dirname "$0")/.."
M=data/crop/.pilot-redo-2026-10-26; [ -e $M ] && { echo "already ran"; exit 1; }; touch $M
L=logs/crop-redo-pilot.log
echo "$(date -u '+%F %T') pilot redo starts (book_crop $(md5sum scripts/book_crop.py | cut -c1-10))" >> $L
scripts/run_resumable.sh $L -- python3 scripts/crop_redo.py data/crop/pilot-2026-10-26.tsv crop-redo-pilot --workers 3
python3 scripts/crop_doubts_page.py crop-redo-pilot >> $L 2>&1
r=$(grep -c '^REDONE' $L); o=$(grep -c '^RESTORED' $L); s=$(grep -c '^SAME' $L); x=$(grep -cE '^(FAIL|ANALYSE FAIL|SKIP)' $L)
echo "- $(date -u '+%F %H:%M') — crop redo PILOT (10 books, data/crop/pilot-2026-10-26.tsv, book_crop $(md5sum scripts/book_crop.py | cut -c1-10)): $r redone, $o restored to the original, $s unchanged, $x failed or skipped (logs/crop-redo-pilot.log); the doubtful pages on site/crop-doubts.html for the owner." >> WORKLOG.md
git add data/crop data/changes/changes.tsv data/phone/index-now.tsv WORKLOG.md >/dev/null 2>&1
git commit -q -m "crop redo pilot: $r redone, $o restored, $s unchanged, $x failed or skipped

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" || true
echo "$(date -u '+%F %T') pilot finished: $r redone, $o restored, $s unchanged, $x failed or skipped" >> $L
