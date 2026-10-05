#!/usr/bin/env bash
# Open the main index (site/00 - الفهرس العام.html) in Brave on this laptop, for the owner to check after every edit.
# NO_OPEN=1 skips it (e.g. in a loop); also skipped when there is no display.
set -euo pipefail
cd "$(dirname "$0")/.."
INDEX="$PWD/site/00 - الفهرس العام.html"
[ "${NO_OPEN:-}" = 1 ] && exit 0
[ -f data/.no-open ] && { echo "not opened (data/.no-open: owner asked to open only when the current work is finished)"; exit 0; }
[ -z "${DISPLAY:-}${WAYLAND_DISPLAY:-}" ] && { echo "no display: open $INDEX yourself"; exit 0; }
[ -f "$INDEX" ] || { echo "missing: $INDEX (run scripts/refresh.sh)"; exit 1; }
setsid -f brave-browser "$INDEX" >/dev/null 2>&1
echo "opened in Brave: $INDEX"
