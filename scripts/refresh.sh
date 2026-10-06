#!/usr/bin/env bash
# Re-index the phone, rebuild everything derived from it, open the main index in Brave. Usage: scripts/refresh.sh [--no-list] [--publish]
set -euo pipefail
cd "$(dirname "$0")/.."
D=$(date +%F-%H%M)
if [ "${1:-}" = "--no-list" ]; then   # phone busy: use index-now.tsv kept current by scripts/index_update.py
    shift; echo "1/6 using data/phone/index-now.tsv (not re-listed)"; cp data/phone/index-now.tsv "data/phone/index-$D.tsv"
else
    echo "1/6 indexing phone:Books ..."
    rclone lsf -R --files-only --format ps --separator $'\t' --checkers 2 phone:Books > "data/phone/index-$D.tsv"
    cp "data/phone/index-$D.tsv" data/phone/index-now.tsv   # stable name for scripts run by hand
fi
echo "    $(wc -l < "data/phone/index-$D.tsv") files"
echo "2/6 provenance";  python3 scripts/substituted_sizes.py; python3 scripts/provenance.py "data/phone/index-$D.tsv"
echo "3/6 catalog";     python3 scripts/build_catalog.py "data/phone/index-$D.tsv"
echo "4/6 comparisons"; python3 scripts/compare_shamela.py; python3 scripts/compare_waqfeya.py
echo "5/6 reports";     python3 scripts/report_shamela.py; python3 scripts/report_waqfeya.py; python3 scripts/report_recommend.py; python3 scripts/report_multi_editions.py; python3 scripts/report_manzumat.py; python3 scripts/report_people.py
                        [ -s data/changes/changes.tsv ] && python3 scripts/report_changes.py || true
python3 scripts/build_selection.py   # selection page catalogue (publish it with the Artifact tool when it changed)
                        python3 scripts/edition_info.py; python3 scripts/build_site.py   # edition cards (owner, 2026-10-06)
# Indexes stay on the laptop for now (owner, 2026-10-05): publish to the phone only when the owner asks.
if [ "${1:-}" = "--publish" ]; then echo "6/6 publish"; python3 scripts/publish.py; else echo "6/6 (kept local; --publish uploads to the phone)"; fi
scripts/publish_web.sh || echo "web: publish failed (see above)"   # online copy: https://benjelloun.dev/library (owner, 2026-10-05)
scripts/open_index.sh || true
