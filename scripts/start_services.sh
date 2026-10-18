#!/usr/bin/env bash
# After a reboot or a lost session: starts again the library's background services, each as a user unit (skipped when it
# already runs) — the memory governor (and its pen, crop.slice), the phone keep-alive and watchdog, the review server, the
# reporter in the owner's GNOME Terminal — and the two inhibitors that keep the laptop awake with its lid closed and idle
# (owner 2026-10-12 «the lid script»; started from the session, not as units: a unit has no session to inhibit from).
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
start reporter-follow "scripts/reporter_follow.sh"
if systemd-inhibit --list 2>/dev/null | grep -q phone-library; then echo "lid inhibitor: already running"
else setsid nohup systemd-inhibit --what=handle-lid-switch:sleep:idle --who=phone-library --why="permanent inhibitor requested by user" \
       --mode=block sleep infinity >/dev/null 2>&1 < /dev/null & echo "lid inhibitor: started"; fi
if pgrep -f "[g]nome-session-inhibit --inhibit suspend:idle" >/dev/null; then echo "idle inhibitor: already running"
else setsid nohup gnome-session-inhibit --inhibit suspend:idle --reason "phone-library jobs" sleep infinity >/dev/null 2>&1 < /dev/null &
     echo "idle inhibitor: started"; fi
