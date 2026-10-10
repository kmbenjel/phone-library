#!/usr/bin/env bash
# One-off (2026-10-10): OCR the queued front pages (no tokens), then re-run the automatic first-pages check and commit.
cd "$(dirname "$0")/.."
nice /usr/bin/python3 scripts/inspect_ocr.py 2 >> logs/ocr-2026-10-10.log 2>&1
python3 scripts/read_status.py >> logs/ocr-2026-10-10.log 2>&1
python3 scripts/auto_check.py >> logs/ocr-2026-10-10.log 2>&1
git add data/names/auto-check.tsv data/names/read-status.tsv data/inspect/ocr.jsonl > /dev/null 2>&1
git commit -q -m "auto_check after the OCR of the queued front pages (scratch/after_ocr_2026-10-10.sh)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" || true
