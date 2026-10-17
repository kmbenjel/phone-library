#!/usr/bin/env bash
# One-off (2026-10-17, third attempt: gate b showed 2 centring failures (أسرار البلاغة ص 187, إرشاد الساري ص 492), fixed): after the regression gate of the corrected crop method (crop-regress.service → logs/crop-regress-2026-10-17c.log):
#   any failure → stop here, nothing reaches the phone; 0 failures → wait for the phone, then redo the 1,122 books cropped by
#   the old method (scripts/crop_redo.py, data/crop/redo-list-2026-10-17.tsv), then resume the library's crop (crop_library.sh).
# Never rerun: refuses when its marker exists.
cd "$(dirname "$0")/.."
M=data/crop/.after-regress-2026-10-17c; [ -e $M ] && { echo "already ran"; exit 1; }; touch $M
while systemctl --user is-active -q crop-regress-c; do sleep 60; done
f=$(grep -oE '^[0-9]+ failures' logs/crop-regress-2026-10-17c.log | tail -1 | cut -d' ' -f1)
echo "$(date -u '+%F %T') regression finished: ${f:-?} failures"
[ "$f" = "0" ] || { echo "STOP: the regression did not pass — see logs/crop-regress-2026-10-17c.log"; exit 2; }
until python3 -c "import sys; sys.path.insert(0,'scripts'); import phone_host as p; h=p.find(); open('data/phone/current-address.txt','w').write(h+'\n') if h else None; sys.exit(0 if h else 1)"; do sleep 120; done
rclone config update phone host "$(cat data/phone/current-address.txt)" >/dev/null
echo "$(date -u '+%F %T') phone on $(cat data/phone/current-address.txt): redo starts"
nice python3 scripts/crop_redo.py data/crop/redo-list-2026-10-17.tsv crop-redo-001 --workers 3 >> logs/crop-redo-001.log 2>&1
r=$(grep -c '^REDONE' logs/crop-redo-001.log); o=$(grep -c '^RESTORED' logs/crop-redo-001.log); x=$(grep -c 'FAIL' logs/crop-redo-001.log)
echo "- $(date -u '+%F %H:%M') — crop redo with the corrected method (owner's review 2026-10-14): $r redone, $o restored to the original, $x failures (logs/crop-redo-001.log)." >> WORKLOG.md
NO_OPEN=1 scripts/refresh.sh >> logs/crop-redo-001.log 2>&1
git add data/crop data/changes/changes.tsv data/phone WORKLOG.md >/dev/null 2>&1; git commit -q -m "crop redo 001: $r redone, $o restored, $x failures

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" || true
exec scripts/crop_library.sh
