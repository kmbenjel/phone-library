#!/bin/bash
# Pauses every job that talks to the phone while its FTP server is silent, resumes them when it is back (owner
# 2026-10-11: «I won't be here for some hours, how my ftp won't betray me»; on 2026-10-10 the server stopped 18:17–20:08).
# Without it, crop_batch.py meets a dead server on every book: each one is skipped («STAGE FAIL»), the batch ends at
# once, crop_library.sh moves to the next batch, and a book listed in two batches is never queued again.
#   down (2 checks 20 s apart)  → SIGSTOP crop_library.sh, crop_batch.py, inspect_files.py, ocr_clean.py
#   back on the SAME address for 60 s → SIGCONT them
#   back on ANOTHER address     → they stay paused (their FTP address was fixed when they started); the new address is
#                                  written to logs/phone-watchdog.log and data/phone/new-address.txt for the agent
# Usage: setsid nohup scripts/phone_watchdog.sh >> logs/phone-watchdog.log 2>&1 &   (one copy; stop: kill its PID)
cd "$(dirname "$0")/.."
HOST=${PHONE_HOST:-$(python3 scripts/phone_host.py 2>/dev/null)}
PAT='^(python3 scripts/(crop_batch|inspect_files|ocr_clean)\.py|bash .*scripts/crop_library\.sh)'
up() { nc -z -w5 "$HOST" 2221 2>/dev/null; }
pids() { pgrep -f "$PAT" | grep -v "^$$\$"; }
log() { echo "$(date '+%F %T') $*"; }
log "watchdog on $HOST:2221 (pid $$)"
paused=0
while true; do
  if up; then
    if [ $paused = 1 ]; then
      sleep 60
      if up; then P=$(pids); [ -n "$P" ] && kill -CONT $P; paused=0; log "FTP back on $HOST — resumed: $(echo $P | wc -w) processes"; fi
    fi
  else
    sleep 20
    if ! up && [ $paused = 0 ]; then
      P=$(pids); [ -n "$P" ] && kill -STOP $P; paused=1; log "FTP silent on $HOST — paused: $(echo $P | wc -w) processes"
    fi
    if [ $paused = 1 ]; then
      NEW=$(PHONE_HOST= timeout 120 python3 -c "import sys; sys.path.insert(0,'scripts'); import phone_host as p; print(p.find() or '')" 2>/dev/null)
      if [ -n "$NEW" ] && [ "$NEW" != "$HOST" ]; then
        log "the phone answers on ANOTHER address: $NEW — jobs stay paused (restart them with this address)"; echo "$NEW" > data/phone/new-address.txt
      fi
    fi
  fi
  sleep 20
done
