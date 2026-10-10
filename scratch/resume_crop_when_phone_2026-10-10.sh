#!/bin/bash
# One-off (2026-10-10 18:20): the phone's FTP server stopped (port 2221 closed, phone still answers ping); the crop
# chain (crop_library.sh 2427158, crop_batch main 2428437) was paused with SIGSTOP so that it would not mark books as
# failed or burn through batches. This waits until the FTP port answers again ON THE SAME ADDRESS (the paused
# processes resolved 192.168.11.100 at start), waits 20 s more, then resumes them with SIGCONT. Another address → only
# reported (the chain must then be restarted after phone_host/rclone are updated).
while true; do
  if nc -z -w3 192.168.11.100 2221; then
    sleep 20
    if nc -z -w3 192.168.11.100 2221; then
      kill -CONT 2428437 2427158 && echo "$(date '+%F %T') phone back on .100 — crop chain resumed"; exit 0
    fi
  fi
  h=$(timeout 90 python3 scripts/phone_host.py 2>/dev/null)
  if [ -n "$h" ] && [ "$h" != "192.168.11.100" ] && nc -z -w3 "$h" 2221; then
    echo "$(date '+%F %T') phone FTP is back on ANOTHER address $h — crop chain left paused"; exit 2
  fi
  sleep 30
done
