#!/usr/bin/env bash
# A few lines about the laptop's resources and the library jobs, every 5 minutes, printed into a terminal the owner has
# open (owner 2026-10-12: «launch a tiny reporting script on my open zsh session, reporting about resources every 5 min»).
# Usage: setsid nohup scripts/resources_report.sh /dev/pts/N [SECONDS=300] >/dev/null 2>&1 &
# Stops by itself when that terminal is closed. Stop by hand: kill the PID from pgrep -f "[r]esources_report".
cd "$(dirname "$0")/.."
TTY=${1:?usage: resources_report.sh /dev/pts/N [seconds]}; EVERY=${2:-300}
while [ -w "$TTY" ]; do
  load=$(cut -d' ' -f1-3 /proc/loadavg)
  mem=$(free -m | awk '/^Mem:/{printf "%.1f/%.1f GB", $3/1024, $2/1024} /^Swap:/{printf ", swap %.1f GB", $3/1024}')
  disk=$(df -h --output=avail / | tail -1 | tr -d ' ')
  temp=$(awk '{t=$1/1000; if (t>m) m=t} END{if (m) printf "%d°C", m}' /sys/class/thermal/thermal_zone*/temp 2>/dev/null)
  bat=$(for b in /sys/class/power_supply/BAT*; do [ -e "$b" ] && echo "$(cat $b/capacity)% $(cat $b/status)"; done | head -1)
  top=$(ps -eo pcpu,comm --sort=-pcpu | awk 'NR>1 && $2!="ps" && c<3{c++; printf "%s %s%%  ", $2, int($1)}')
  host=$(cat data/phone/current-address.txt 2>/dev/null || echo 192.168.11.100)
  nc -z -w3 "$host" 2221 2>/dev/null && phone="phone up ($host)" || phone="phone AWAY"
  state=$(ps -o stat= -p "$(pgrep -f '[c]rop_batch.py' | head -1)" 2>/dev/null | cut -c1)
  b=$(ls -t data/crop/batch-*.txt 2>/dev/null | head -1)
  if [ -n "$b" ]; then
    n=$(grep -c . "$b"); d=$(python3 -c "
import sys, unicodedata as u
N=lambda s:u.normalize('NFC',s)
done={N(l.split('\t')[0]) for l in open('data/crop/done.tsv',encoding='utf-8')}
print(sum(1 for l in open(sys.argv[1],encoding='utf-8') if l.strip() and N(l.split('\t')[0].strip().removeprefix('Books/')) in done))" "$b")
    crop="crop $(basename "$b" .txt) $d/$n $([ "$state" = T ] && echo '(paused)' || ([ -n "$state" ] && echo '(running)' || echo '(not running)'))"
  fi
  {
    printf '\n\033[1m── %s ──\033[0m\n' "$(date '+%H:%M')"
    printf 'cpu load %s | mem %s | disk free %s%s%s\n' "$load" "$mem" "$disk" "${temp:+ | $temp}" "${bat:+ | battery $bat}"
    printf 'top: %s\n' "$top"
    printf '%s | %s\n' "$phone" "$crop"
  } > "$TTY" 2>/dev/null || break
  sleep "$EVERY"
done
