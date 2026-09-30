#!/usr/bin/env bash
# Re-index the phone and rebuild everything derived from it. Usage: scripts/refresh.sh [--publish]
set -euo pipefail
cd "$(dirname "$0")/.."
D=$(date +%F-%H%M)
echo "1/6 indexing phone:Books ..."
rclone lsf -R --files-only --format ps --separator $'\t' --checkers 2 phone:Books > "data/phone/index-$D.tsv"
echo "    $(wc -l < "data/phone/index-$D.tsv") files"
cp "data/phone/index-$D.tsv" data/phone/index-now.tsv   # stable name for scripts run by hand
echo "2/6 provenance";  python3 scripts/provenance.py "data/phone/index-$D.tsv"
echo "3/6 catalog";     python3 scripts/build_catalog.py "data/phone/index-$D.tsv"
echo "4/6 comparisons"; python3 scripts/compare_shamela.py; python3 scripts/compare_waqfeya.py
echo "5/6 reports";     python3 scripts/report_shamela.py; python3 scripts/report_waqfeya.py; python3 scripts/report_recommend.py
                        [ -s data/changes/changes.tsv ] && python3 scripts/report_changes.py || true
                        python3 scripts/build_site.py
if [ "${1:-}" = "--publish" ]; then echo "6/6 publish"; python3 scripts/publish.py; else echo "6/6 (skipped publish; pass --publish)"; fi
