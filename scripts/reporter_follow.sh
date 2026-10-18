#!/usr/bin/env bash
# Keeps the 5-minute resources report (scripts/resources_report.sh) in the owner's GNOME Terminal: every 30 s, the newest
# shell whose parent is gnome-terminal-server gets a report if none prints there yet (owner 2026-10-13: «start the reporter on
# the GNOME Terminal»; terminals come and go). Usage: setsid nohup scripts/reporter_follow.sh >/dev/null 2>&1 &
cd "$(dirname "$0")/.."
while :; do
  for p in $(pgrep -x zsh; pgrep -x bash); do
    t=$(ps -o tty= -p "$p" 2>/dev/null | tr -d ' '); [[ $t == pts/* ]] || continue
    par=$(ps -o cmd= -p "$(ps -o ppid= -p "$p" | tr -d ' ')" 2>/dev/null)   # (ps refuses a pid with a leading space)
    [[ $par == *gnome-terminal-server* ]] || continue
    pgrep -f "resources_report.sh /dev/$t " >/dev/null || setsid nohup scripts/resources_report.sh "/dev/$t" 300 >/dev/null 2>&1 &
  done
  sleep 30
done
