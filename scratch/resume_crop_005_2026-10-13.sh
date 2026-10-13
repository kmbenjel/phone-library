#!/usr/bin/env bash
# One-off (2026-10-13): the laptop went down on 2026-10-12 ~21:45 (battery) during crop batch-005 (128 cropped) and restarted
# at 00:00. Waits for the phone, then checks every unfinished file of batch-005 still has its logged size (a crop cut off
# during its append would show a different size) — any mismatch: stop and report, nothing resumed. Else finishes batch-005,
# refresh + WORKLOG + commit, then hands over to crop_library.sh. Never rerun: refuses when its marker exists.
cd "$(dirname "$0")/.."
M=data/crop/.resume-005b-done; [ -e $M ] && { echo "already ran"; exit 1; }
until python3 -c "import sys; sys.path.insert(0,'scripts'); import phone_host as p; h=p.find(); open('data/phone/current-address.txt','w').write(h+'\n') if h else None; sys.exit(0 if h else 1)"; do sleep 60; done
H=$(cat data/phone/current-address.txt); rclone config update phone host "$H" >/dev/null
echo "$(date -u '+%F %T') phone on $H — checking batch-005's unfinished files"
python3 - <<'PY' || { echo "SIZE MISMATCH: crop not resumed (see above)"; exit 2; }
import ftplib, sys, unicodedata
N = lambda s: unicodedata.normalize('NFC', s)
host = open('data/phone/current-address.txt').read().strip()
batch = [l.rstrip('\n').split('\t')[0] for l in open('data/crop/batch-005.txt', encoding='utf-8') if l.strip()]
done = {N(l.split('\t')[0]) for l in open('data/crop/done.tsv', encoding='utf-8')}
size = {N(a): int(b) for a, b in (l.rstrip('\n').split('\t')[:2] for l in open('data/phone/index-now.tsv', encoding='utf-8'))}
todo = [p.removeprefix('Books/') for p in batch if N(p.removeprefix('Books/')) not in done]
f = ftplib.FTP(); f.encoding = 'utf-8'; f.connect(host, 2221, timeout=60); f.login(); f.voidcmd('TYPE I')
bad = []
for q in todo:
    try: s = f.size('Books/' + q)
    except Exception as e: print('gone?', q, e); continue
    if s != size.get(N(q)): bad.append((q, size.get(N(q)), s))
f.quit()
print(len(todo), 'unfinished files checked;', len(bad), 'size mismatches')
for b in bad: print('MISMATCH', b)
sys.exit(1 if bad else 0)
PY
b=batch-005; log="logs/crop-$b.log"
echo "$(date -u '+%F %T') resume $b after the laptop went down" | tee -a "$log"
nice python3 scripts/crop_batch.py "data/crop/$b.txt" "crop-$b" --workers "${CROP_WORKERS:-4}" >> "$log" 2>&1
touch $M
NO_OPEN=1 scripts/refresh.sh >> "$log" 2>&1 || echo "refresh failed (see $log)"
c=$(grep -c '^CROPPED' "$log"); s=$(grep -c '^skip' "$log"); f=$(grep -c 'FAIL' "$log")
echo "- $(date -u '+%F %H:%M') — crop $b (library batches; resumed after two laptop restarts): $c cropped, $s left as they are, $f failures (logs/crop-$b.log); refresh." >> WORKLOG.md
git add data/crop data/changes/changes.tsv data/phone WORKLOG.md > /dev/null 2>&1
git commit -q -m "crop $b: $c cropped, $s left as they are, $f failures (resumed after the laptop went down)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" || true
exec scripts/crop_library.sh
