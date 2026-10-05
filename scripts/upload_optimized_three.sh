#!/usr/bin/env bash
set -euo pipefail

LOCK="/tmp/phone-ftp.lock"
LOG="/home/k/projects/phone-library/data/changes/upload_optimized.log"

echo "$(date '+%F %T') STARTING UPLOAD OF OPTIMIZED THREE TARGETS" | tee -a "$LOG"

# 1. Risala: 45 files in-place update
echo "=== STEP 1: Uploading Majallat al-Risala ===" | tee -a "$LOG"
flock "$LOCK" rclone copy "/home/k/Books/الجوامع/مجلة الرسالة" \
    "phone:Books/الجوامع/مجلة الرسالة" \
    --checkers=2 --transfers=2 --ftp-concurrency=2 --inplace -v 2>&1 | tee -a "$LOG"

echo "$(date '+%F %T') COMPLETED UPLOAD OF RISALA (STOPPED AT RISALA ONLY PER USER REQUEST)!" | tee -a "$LOG"
