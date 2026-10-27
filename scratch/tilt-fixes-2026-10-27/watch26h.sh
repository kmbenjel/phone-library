#!/usr/bin/env bash
# wakes the session: 26h ended, a FAIL line, or a brake of the governor (after the given start line count)
cd /home/k/projects/phone-library
L=logs/crop-regress-2026-10-26h.log; G=logs/mem-governor.log
f0=$(grep -c '^FAIL' $L); b0=$(grep -c 'BRAKE' $G)
while true; do
  if ! systemctl --user is-active --quiet crop-regress-2026-10-26h; then echo "ENDED $(date -u '+%T')"; tail -5 $L; exit 0; fi
  f=$(grep -c '^FAIL' $L); [ "$f" -gt "$f0" ] && { echo "FAIL $(date -u '+%T')"; grep '^FAIL' $L | tail -$((f - f0)); exit 0; }
  b=$(grep -c 'BRAKE' $G); [ "$b" -gt "$b0" ] && { echo "BRAKE $(date -u '+%T')"; grep 'BRAKE' $G | tail -1; exit 0; }
  sleep 60
done
