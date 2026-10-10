#!/usr/bin/env bash
# One-off (2026-10-10): once crop batch 001 is over, inspect the never-inspected files (the 141 single books without page
# images first: data/inspect/priority-names-2026-10-10.txt), OCR their front pages, re-run the automatic first-pages
# check (auto_check.py) and commit. Token-free; resumable (inspect_files skips what files.jsonl has).
cd "$(dirname "$0")/.."
while pgrep -f "[c]rop_batch.py" > /dev/null; do sleep 300; done
nice python3 scripts/inspect_files.py data/phone/index-now.tsv data/inspect/priority-names-2026-10-10.txt >> logs/inspect-2026-10-10.log 2>&1
while pgrep -f "[i]nspect_ocr.py" > /dev/null; do sleep 120; done
nice /usr/bin/python3 scripts/inspect_ocr.py 3 >> logs/inspect-2026-10-10.log 2>&1
python3 scripts/read_status.py >> logs/inspect-2026-10-10.log 2>&1
python3 scripts/auto_check.py >> logs/inspect-2026-10-10.log 2>&1
git add data/inspect/files.jsonl data/inspect/ocr.jsonl data/names/auto-check.tsv data/names/read-status.tsv > /dev/null 2>&1
git commit -q -m "inspect the never-inspected files (single books without page images first), OCR, auto_check (scratch/inspect_after_crop001_2026-10-10.sh)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" || true
