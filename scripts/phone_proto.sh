#!/bin/bash
# Which way the scripts reach the phone: FTP app (port 2221) or Termux SSH (port 8022). Owner 2026-11-04.
#   scripts/phone_proto.sh          → prints the current one
#   scripts/phone_proto.sh ssh|ftp  → switches: ~/.config/phone-library/proto (read by phone_host.py: connect(),
#                                     read_range(), the address lookup) and the rclone remote «phone:», which the
#                                     rclone scripts use as phone:Books/...:
#                                       ssh: phone = alias of phonessh:/sdcard (the FTP remote kept as «phoneftp»)
#                                       ftp: phone = the FTP remote again
# Switch only while no phone job runs (a running process keeps the protocol it started with).
set -euo pipefail
CONF=~/.config/phone-library/proto
cur() { [ -s "$CONF" ] && cat "$CONF" || echo ftp; }
[ $# = 0 ] && { echo "$(cur)  (rclone phone: $(rclone config show phone 2>/dev/null | awk '/^type/{print $3}'))"; exit 0; }
want=$1; [[ $want = ssh || $want = ftp ]] || { echo "usage: $0 [ssh|ftp]" >&2; exit 2; }
if pgrep -f '^(nice )?python3 scripts/(crop_batch|crop_redo|inspect_files|ocr_clean|apply_plan|fetch_queue|delete_files)\.py' >/dev/null; then
  echo "a phone job is running — switch after it ends" >&2; exit 1; fi
type_of() { rclone config show "$1" 2>/dev/null | awk '/^type/{print $3}'; }
RCONF=$(rclone config file | tail -1)
rename_remote() {   # rclone has no «config rename»: the section header in rclone.conf (a backup kept beside it)
  grep -q '^# encrypted' "$RCONF" && { echo "rclone.conf is encrypted: rename by hand" >&2; exit 1; }
  cp -p "$RCONF" "$RCONF.before-proto"; sed -i "s/^\[$1\]\$/[$2]/" "$RCONF"; }
if [ "$want" = ssh ]; then
  H=$(PHONE_PROTO=ssh python3 scripts/phone_host.py); timeout 20 ssh -i ~/.config/phone-library/phone_ssh -p 8022 \
    -o BatchMode=yes -o HostKeyAlias=phone-termux "$H" true || { echo "ssh does not answer on $H — is sshd running in Termux?" >&2; exit 1; }
  python3 scripts/phone_ssh.py pin "$H" || { echo "the key on $H is not the phone's (phone-termux in ~/.ssh/known_hosts)" >&2; exit 1; }
  rclone config update phonessh host "$H" >/dev/null
  if [ "$(type_of phone)" = ftp ]; then
    [ -z "$(type_of phoneftp)" ] || rclone config delete phoneftp
    rename_remote phone phoneftp
  fi
  [ "$(type_of phone)" = alias ] || rclone config create phone alias remote=phonessh:/sdcard >/dev/null
else
  if [ "$(type_of phone)" = alias ]; then
    [ "$(type_of phoneftp)" = ftp ] || { echo "no «phoneftp» remote to go back to" >&2; exit 1; }
    rclone config delete phone; rename_remote phoneftp phone
  fi
fi
echo "$want" > "$CONF"
echo "now: $(cur); rclone phone: $(type_of phone); check: rclone lsf phone:Books --max-depth 1 | head -3"
