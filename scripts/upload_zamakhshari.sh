#!/usr/bin/env bash
set -euo pipefail

LOCK="/tmp/phone-ftp.lock"
LOG="/home/k/projects/phone-library/data/changes/upload_zamakhshari.log"

echo "$(date '+%F %T') STARTING UPLOAD OF ZAMAKHSHARI TO PHONE" | tee -a "$LOG"

SRC="/home/k/Books/التفسير/الكشاف عن حقائق التنزيل - الزمخشري (دار المعرفة)"
DST="phone:Books/التفسير/الكشاف عن حقائق التنزيل - الزمخشري (دار المعرفة)"

flock "$LOCK" rclone copy "$SRC" "$DST" \
    --checkers=2 --transfers=2 --ftp-concurrency=2 -v 2>&1 | tee -a "$LOG"

echo "$(date '+%F %T') COMPLETED UPLOAD OF ZAMAKHSHARI!" | tee -a "$LOG"
