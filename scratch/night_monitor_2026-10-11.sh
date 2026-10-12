#!/bin/bash
# One-off (2026-10-11 night, owner away until tomorrow: «be working and monitoring as needed»): exits — and so wakes the
# agent — on the first thing that needs attention: a crop write problem, the crop chain stopping, a new crop batch
# (to review the finished one), the phone away > 30 min, disk < 3 GB, or after 3 hours anyway. Prints the reason.
cd "$(dirname "$0")/.."
start=$(date +%s); last_batch=$(grep -c "start batch-" logs/crop-library.log)
while true; do
  log=$(ls -t logs/crop-batch-*.log | head -1)
  if grep -qE "RESTORE NOT VERIFIED|APPEND ERROR|append not verified" "$log"; then echo "CROP WRITE PROBLEM in $log"; grep -E "RESTORE|APPEND|not verified" "$log" | tail -3; exit 0; fi
  if ! pgrep -f "[c]rop_library.sh" >/dev/null; then echo "CROP CHAIN STOPPED"; tail -3 logs/crop-library.log; exit 0; fi
  n=$(grep -c "start batch-" logs/crop-library.log); if [ "$n" -gt "$last_batch" ]; then echo "NEW BATCH"; tail -2 logs/crop-library.log; exit 0; fi
  free=$(df -BG --output=avail / | tail -1 | tr -dc 0-9); if [ "$free" -lt 3 ]; then echo "DISK LOW: ${free} GB"; exit 0; fi
  lastline=$(tail -1 logs/phone-watchdog.log)
  if echo "$lastline" | grep -q "silent\|moved"; then
    t=$(date -d "$(echo "$lastline" | cut -c1-19)" +%s); if [ $(( $(date +%s) - t )) -gt 1800 ]; then echo "PHONE AWAY > 30 min"; echo "$lastline"; exit 0; fi
  fi
  if [ $(( $(date +%s) - start )) -gt 10800 ]; then echo "3 HOURS — routine check"; exit 0; fi
  sleep 60
done
