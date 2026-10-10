#!/usr/bin/env bash
# One-off (2026-10-10, owner: «كان ينبغي أن تستمر مهام القطع في ظل توقف الحصة»): when the regression run with the
# two-column fix ends with 0 failures, commit book_crop.py and start the library crop chain (scripts/crop_library.sh,
# 300 books a batch, 6 % margins, widest margins first), which then runs on its own. On any failure: nothing starts.
cd "$(dirname "$0")/.."
while pgrep -f "[c]rop_regress.py" > /dev/null; do sleep 60; done
if grep -q "^0 failures" logs/crop-regress-2026-10-10e.log; then
    git add scripts/book_crop.py data/improve/crop-regression.tsv > /dev/null 2>&1
    git commit -q -m "book_crop: two-column pages decided by their columns (gutter + each column's line-start edge; both agree on ≥ 0.3° → the turn leaving both straight, else no turn); crop_regress 0 failures incl. الفوائد 456/457

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" || true
    echo "$(date -u '+%F %T') regression passed: library crop chain started" >> logs/crop-library.log
    exec scripts/crop_library.sh >> logs/crop-library.log 2>&1
else
    echo "$(date -u '+%F %T') regression FAILED: the crop chain was not started (logs/crop-regress-2026-10-10e.log)" >> logs/crop-library.log
fi
