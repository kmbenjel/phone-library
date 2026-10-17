#!/bin/bash
# Keeps the phone jobs in step with the phone's FTP server (owner 2026-10-11: «I won't be here for some hours, how my
# ftp won't betray me»; «will you connect to my phone whatever the new address is?»). The phone's address changes by
# DHCP (it switched .100 ↔ .102 five times on 2026-10-11), so the address is not fixed here:
#   silent everywhere (2 checks 20 s apart) → SIGSTOP crop_library.sh, crop_batch.py, inspect_files.py, ocr_clean.py
#   answering again (anywhere: the known addresses first, then the /24, scripts/phone_host.py) for 60 s
#       → rclone's «phone:» host updated if the address changed, data/phone/current-address.txt written, SIGCONT
# Jobs started after 2026-10-11 19:10 look the address up again when a connection fails (crop_batch.Phone), so they
# follow a move; an older process only works while the phone keeps the address it started with (else its files are
# skipped, not marked done, and come back in a later batch).
# Usage: setsid nohup scripts/phone_watchdog.sh >> logs/phone-watchdog.log 2>&1 &   (one copy; stop: kill its PID)
cd "$(dirname "$0")/.."
PAT='^(nice )?(python3 scripts/(crop_batch|crop_redo|inspect_files|ocr_clean)\.py|bash .*scripts/crop_library\.sh)'
log() { echo "$(date '+%F %T') $*"; }
answers() { nc -z -w5 "$1" 2221 2>/dev/null; }
locate() { PHONE_HOST= timeout 120 python3 -c "import sys; sys.path.insert(0,'scripts'); import phone_host as p; print(p.find() or '')" 2>/dev/null; }
pids() { pgrep -f "$PAT"; }
HOST=$(locate); [ -z "$HOST" ] && HOST=$(rclone config show phone 2>/dev/null | awk '/^host/{print $3}')
log "watchdog on ${HOST:-?}:2221 (pid $$)"
paused=0
while true; do
  if [ -n "$HOST" ] && answers "$HOST"; then
    if [ $paused = 1 ]; then
      sleep 60
      if answers "$HOST"; then
        P=$(pids); [ -n "$P" ] && kill -CONT $P; paused=0; log "FTP back on $HOST — resumed: $(echo $P | wc -w) processes"
      fi
    fi
  else
    sleep 20
    if [ -z "$HOST" ] || ! answers "$HOST"; then
      if [ $paused = 0 ]; then
        P=$(pids); [ -n "$P" ] && kill -STOP $P; paused=1; log "FTP silent on ${HOST:-?} — paused: $(echo $P | wc -w) processes"
      fi
      NEW=$(locate)
      if [ -n "$NEW" ] && [ "$NEW" != "$HOST" ]; then
        rclone config update phone host "$NEW" >/dev/null 2>&1
        echo "$NEW" > data/phone/current-address.txt
        log "the phone moved: $HOST → $NEW (rclone updated)"; HOST=$NEW
      fi
    fi
  fi
  sleep 20
done
