#!/usr/bin/env bash
# Runs a resumable crop job (crop_redo.py, crop_batch.py, crop_regress.py …) until it ends on its own: if the memory
# governor's emergency brake (scripts/mem_governor.py) or anything else kills it, it waits until memory is comfortable
# again (≥ 4 GB free for 2 minutes) and runs it once more — the job continues where it stopped (owner 2026-10-18: more
# workers, but never at the cost of his session). Stops after 20 restarts in a row without progress in the log.
# Usage: scripts/run_resumable.sh LOG -- CMD ARGS…   (run it inside a capped unit: AGENTS.md §7.12)
cd "$(dirname "$0")/.."
LOG=${1:?usage: run_resumable.sh LOG -- CMD…}; shift; [ "$1" = "--" ] && shift
free_gb() { awk '/^MemAvailable:/{printf "%d", $2/1048576}' /proc/meminfo; }
tries=0
while :; do
  before=$(wc -l < "$LOG" 2>/dev/null || echo 0)
  echo "$(date -u '+%F %T') run: $*" >> "$LOG"
  "$@" >> "$LOG" 2>&1 && { echo "$(date -u '+%F %T') done" >> "$LOG"; exit 0; }
  rc=$?; after=$(wc -l < "$LOG")
  [ "$after" -gt $((before + 2)) ] && tries=0 || tries=$((tries + 1))
  [ "$tries" -ge 20 ] && { echo "$(date -u '+%F %T') stopped: 20 restarts without progress (exit $rc)" >> "$LOG"; exit "$rc"; }
  echo "$(date -u '+%F %T') ended with exit $rc — waiting for memory before going on" >> "$LOG"
  ok=0; while [ "$ok" -lt 4 ]; do sleep 30; [ "$(free_gb)" -ge 4 ] && ok=$((ok + 1)) || ok=0; done
done
