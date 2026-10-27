#!/usr/bin/env bash
# waitj.sh UNIT PATTERN — until the unit's journal has a line matching PATTERN (grep -E) or the unit ends
u=$1; pat=$2
while true; do
  if journalctl --user -u "$u" -o cat --no-pager | grep -qE "$pat"; then journalctl --user -u "$u" -o cat --no-pager | tail -4; exit 0; fi
  systemctl --user is-active --quiet "$u" || { echo "$u ended"; journalctl --user -u "$u" -o cat --no-pager | tail -6; exit 0; }
  sleep 20
done
