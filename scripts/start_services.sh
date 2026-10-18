#!/usr/bin/env bash
# After a reboot or a lost session: starts again the library's background services, each as a user unit (skipped when it
# already runs) — the memory governor (and its pen, crop.slice), the phone keep-alive and watchdog, the review server.
# Long jobs (crop redo, regression) are not started here: they are launched on purpose (AGENTS.md §7.12).
# Usage: scripts/start_services.sh
cd "$(dirname "$0")/.."
start() {  # unit, command
  if systemctl --user is-active -q "$1"; then echo "$1: already running"; return; fi
  systemctl --user reset-failed "$1" 2>/dev/null
  systemd-run --user --unit="$1" --nice=5 --working-directory="$PWD" bash -c "$2" >/dev/null && echo "$1: started"
}
start mem-governor    "python3 scripts/mem_governor.py >> logs/mem-governor.log 2>&1"
start phone-keepalive "python3 scripts/phone_keepalive.py 120 >> logs/phone-keepalive.log 2>&1"
start phone-watchdog  "scripts/phone_watchdog.sh >> logs/phone-watchdog.log 2>&1"
start review-server   "python3 scripts/review_server.py 8765 >> logs/review-server.log 2>&1"
