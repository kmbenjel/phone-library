#!/usr/bin/env bash
# One-off (2026-10-18, ninth start: the eighth was stopped at book 18 of 31 to apply the fix its only failure called for (a level printed rule vetoes a projection turn: سؤالات أبي داود ص 177) — every book is analysed again with it; crashes are rerun as before; the owner: «start»): after tonight's crop corrections (crop-fixes rounds 2–3, the questions page),
#   1. the full regression gate (crop_regress.py) → logs/crop-regress-2026-10-18j.log; any failure: stop here, nothing on the phone;
#   2. 0 failures → the redo of the 1,122 books cropped by the old method (crop_redo.py, data/crop/redo-list-2026-10-17.tsv,
#      batch crop-redo-001), the doubtful pages kept for the owner (scripts/crop_doubts_page.py → site/crop-doubts.html, rebuilt
#      every 30 minutes meanwhile);
#   3. WORKLOG, refresh, commit; then the rest of the library (crop_library.sh).
# Runs in the memory pen (crop.slice), workers from the governor. Never rerun: refuses when its marker exists.
cd "$(dirname "$0")/.."
M=data/crop/.start-redo-2026-10-18i; [ -e $M ] && { echo "already ran"; exit 1; }; touch $M
echo "$(date -u '+%F %T') regression starts"
R=logs/crop-regress-2026-10-18j.log; : > $R
for try in $(seq 1 30); do                      # a crash (no «N failures» line: the brake killed a worker) is run again
  echo "== attempt $try $(date -u '+%F %T')" >> $R
  python3 scripts/crop_regress.py >> $R 2>&1
  tail -3 $R | grep -qE '^[0-9]+ failures' && break
  echo "$(date -u '+%F %T') regression crashed (attempt $try) — waiting for memory, then again" 
  ok=0; while [ "$ok" -lt 4 ]; do sleep 30; [ "$(awk '/^MemAvailable:/{printf "%d", $2/1048576}' /proc/meminfo)" -ge 4 ] && ok=$((ok + 1)) || ok=0; done
done
f=$(grep -oE '^[0-9]+ failures' $R | tail -1 | cut -d' ' -f1)
echo "$(date -u '+%F %T') regression finished: ${f:-?} failures"
[ "$f" = "0" ] || { echo "STOP: the regression did not pass — see logs/crop-regress-2026-10-18j.log"; exit 2; }
( while sleep 1800; do python3 scripts/crop_doubts_page.py crop-redo-001 >/dev/null 2>&1; done ) & PAGER=$!
echo "$(date -u '+%F %T') redo starts"
scripts/run_resumable.sh logs/crop-redo-001.log -- python3 scripts/crop_redo.py data/crop/redo-list-2026-10-17.tsv crop-redo-001 --workers 6   # (a brake kill: run again, resumes from its done list)
kill $PAGER 2>/dev/null; python3 scripts/crop_doubts_page.py crop-redo-001
r=$(grep -c '^REDONE' logs/crop-redo-001.log); o=$(grep -c '^RESTORED' logs/crop-redo-001.log); x=$(grep -c 'FAIL' logs/crop-redo-001.log)
echo "- $(date -u '+%F %H:%M') — crop redo 001 with the corrected method (the owner's reviews 2026-10-14 and 10-18): $r redone, $o restored to the original, $x failures (logs/crop-redo-001.log); the doubtful pages on site/crop-doubts.html." >> WORKLOG.md
NO_OPEN=1 scripts/refresh.sh >> logs/crop-redo-001.log 2>&1
git add data/crop data/changes/changes.tsv data/phone WORKLOG.md >/dev/null 2>&1; git commit -q -m "crop redo 001: $r redone, $o restored, $x failures

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" || true
CROP_WORKERS=6 exec scripts/crop_library.sh
