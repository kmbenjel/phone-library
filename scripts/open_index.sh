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
# Brave runs as its own user unit (2026-10-19, the owner: «nothing opened in Brave»): launched from refresh.sh inside a
# systemd unit it was killed with that unit's cgroup when the refresh ended, and launched from a shell inside the VS Code
# snap it crashed on the snap's GSettings schemas (GSETTINGS_SCHEMA_DIR, GTK_PATH…). The user manager's environment is clean.
if systemd-run --user --collect --quiet --unit="brave-index-$(date +%s)" brave-browser "$INDEX" >/dev/null 2>&1; then :
else env -u GSETTINGS_SCHEMA_DIR -u GTK_PATH -u GTK_EXE_PREFIX -u GIO_MODULE_DIR -u GTK_IM_MODULE_FILE -u GDK_PIXBUF_MODULEDIR \
       -u GDK_PIXBUF_MODULE_FILE -u LOCPATH XDG_DATA_DIRS="${XDG_DATA_DIRS_VSCODE_SNAP_ORIG:-/usr/local/share/:/usr/share/}" \
       setsid -f brave-browser "$INDEX" >/dev/null 2>&1
fi
echo "opened in Brave: $INDEX"
