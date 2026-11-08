#!/usr/bin/env bash
# Keeps the 5-minute resources report (scripts/resources_report.sh) in ONE of the owner's GNOME Terminals, and only in an idle
# one: a terminal whose shell runs something (claude, an editor, any command) gets no report, and a report in a terminal that
# becomes busy is stopped (owner 2026-10-28: «shouldn't output in every terminal session or while something is open in it like
# my claude cli session»). Checks every 30 s. Usage: setsid nohup scripts/reporter_follow.sh >/dev/null 2>&1 &
cd "$(dirname "$0")/.."
idle() { [ -z "$(pgrep -P "$1")" ]; }       # the shell has no child: nothing runs in it
while :; do
  cand=""
  for p in $(pgrep -x zsh; pgrep -x bash); do
    t=$(ps -o tty= -p "$p" 2>/dev/null | tr -d ' '); [[ $t == pts/* ]] || continue
    par=$(ps -o cmd= -p "$(ps -o ppid= -p "$p" | tr -d ' ')" 2>/dev/null)
    [[ $par == *gnome-terminal-server* ]] || continue
    r=$(pgrep -f "resources_report.sh /dev/$t ")
    if idle "$p"; then [ -z "$cand" ] && cand=$t
    else [ -n "$r" ] && kill $r; fi           # busy now: no report there
  done
  running=$(pgrep -fa "resources_report.sh /dev/pts" | grep -o '/dev/pts/[0-9]*' | sort -u)
  n=$(echo -n "$running" | grep -c .)
  if [ "$n" -gt 1 ]; then for t in $(echo "$running" | tail -n +2); do kill $(pgrep -f "resources_report.sh $t "); done; fi
  if [ "$n" -eq 0 ] && [ -n "$cand" ]; then setsid nohup scripts/resources_report.sh "/dev/$cand" 300 >/dev/null 2>&1 & fi
  sleep 30
done
