#!/bin/bash
# Keeps a dying battery from killing the jobs (owner 2026-10-31: «upon 7%, pause running jobs without killing them and
# suspend»; the laptop died of an empty battery on 2026-10-12 and 2026-10-17).
#   on battery at ≤ LIMIT % (2 readings) → notice, WARN seconds to plug in, jobs paused, suspend
#   charger back → jobs resumed. Woken without the charger: they stay paused, and it suspends again after GRACE seconds.
# Paused = `systemctl --user freeze` for running transient units (phone_watchdog's SIGCONT cannot undo a freeze), SIGSTOP
# for the jobs started outside a unit. The always-on helpers in KEEP are left alone (a suspend stops them anyway).
# The phone jobs' systemd-inhibit and gnome-session-inhibit block sleep, and polkit asks a password to pass them: hence
# sudo + --check-inhibitors=no. The inhibitors stay in place for the lid and for idle.
# Usage: systemd-run --user --unit=battery-guard --collect --working-directory="$PWD" --setenv=PATH="$PATH" \
#            bash -c "scripts/battery_guard.sh >> logs/battery-guard.log 2>&1"     (stop: systemctl --user stop battery-guard)
cd "$(dirname "$0")/.."
BAT=${BAT:-/sys/class/power_supply/BAT0}
AC=${AC:-/sys/class/power_supply/AC}
LIMIT=${LIMIT:-7}
POLL=${POLL:-30}
WARN=${WARN:-30}
GRACE=${GRACE:-300}
SUSPEND_CMD=${SUSPEND_CMD:-sudo -n systemctl suspend --check-inhibitors=no}
KEEP='^(battery-guard|mem-governor|phone-keepalive|phone-watchdog|reporter-follow|review-server)\.service$'
PAT='^(nice (-n ?[0-9]+ )?)?(python3|bash) (\S*/)?scripts/(crop_|book_crop|fetch_queue|inspect_files|ocr_clean|refresh\.sh|publish_web)|^aria2c |^rclone (copy|copyto|sync|move|moveto|delete)'
log() { echo "$(date '+%F %T') $*"; }
notice() { notify-send -u critical "Battery guard" "$1" 2>/dev/null; }
on_ac() { [ "$(cat "$AC/online" 2>/dev/null)" = 1 ]; }
job_units() {
  systemctl --user list-units --type=service --state=running --no-legend --plain | awk '{print $1}' | grep -Ev "$KEEP" |
    while read -r u; do [ "$(systemctl --user show -P Transient "$u")" = yes ] && echo "$u"; done
}
pause_jobs() {
  STOPPED=$(pgrep -f "$PAT")
  # shellcheck disable=SC2086
  [ -n "$STOPPED" ] && kill -STOP $STOPPED
  FROZEN=$(job_units)
  for u in $FROZEN; do systemctl --user freeze "$u" || log "could not freeze $u"; done
  log "paused: units [$(echo $FROZEN)] pids [$(echo $STOPPED)]"
}
resume_jobs() {
  for u in $FROZEN; do systemctl --user thaw "$u" || log "could not thaw $u"; done
  # shellcheck disable=SC2086
  [ -n "$STOPPED" ] && kill -CONT $STOPPED 2>/dev/null
  log "resumed: units [$(echo $FROZEN)] pids [$(echo $STOPPED)]"
  FROZEN= STOPPED=
}
log "battery guard on: suspend at ≤ $LIMIT % (pid $$)"
paused=0 low=0 wait=0
while :; do
  pct=$(cat "$BAT/capacity" 2>/dev/null)
  if on_ac; then
    low=0 wait=0
    [ $paused = 1 ] && { resume_jobs; paused=0; }
  elif [ -n "$pct" ] && [ "$pct" -le "$LIMIT" ]; then
    low=$((low + 1))
    if [ $wait -gt 0 ]; then
      wait=$((wait - 1))
    elif [ $low -ge 2 ]; then
      notice "Battery at $pct %: pausing the jobs and suspending in $WARN s. Plug in to cancel."
      sleep "$WARN"
      on_ac && continue
      [ $paused = 1 ] || { pause_jobs; paused=1; }
      log "battery $pct %: suspending"
      if $SUSPEND_CMD; then
        wait=$((GRACE / POLL))        # counted in awake ticks: sleep stops during a suspend
      else
        log "SUSPEND FAILED: $SUSPEND_CMD"
        notice "Suspend failed: please suspend by hand."
      fi
    fi
  else
    low=0
  fi
  sleep "$POLL"
done
