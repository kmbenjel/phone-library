#!/usr/bin/env bash
# Re-index the phone, rebuild everything derived from it, open the main index in Brave. Usage: scripts/refresh.sh [--no-list] [--publish]
set -euo pipefail
cd "$(dirname "$0")/.."
D=$(date +%F-%H%M)
if [ "${1:-}" = "--no-list" ]; then   # phone busy: use index-now.tsv kept current by scripts/index_update.py
    shift; echo "1/6 using data/phone/index-now.tsv (not re-listed)"; cp data/phone/index-now.tsv "data/phone/index-$D.tsv"
else
    echo "1/6 indexing phone:Books ..."
    # A listing can come back cut short with no error (2026-10-08: 3,953 of 16,579 files with --checkers 2 while the phone
    # dozed): one connection, retried once, and refused if it holds fewer than 95 % of the files index-now.tsv knows.
    prev=$(wc -l < data/phone/index-now.tsv 2>/dev/null || echo 0)
    for try in 1 2; do
        flock /tmp/phone-ftp.lock rclone lsf -R --files-only --format ps --separator $'\t' --checkers 1 --low-level-retries 20 phone:Books > "data/phone/index-$D.tsv" || true
        n=$(wc -l < "data/phone/index-$D.tsv")
        [ "$n" -ge $(( prev * 95 / 100 )) ] && break
        echo "    listing cut short ($n files, index-now has $prev): retrying"; sleep 60
    done
    if [ "$n" -lt $(( prev * 95 / 100 )) ]; then
        echo "    listing still short ($n of $prev): keeping data/phone/index-now.tsv"; cp data/phone/index-now.tsv "data/phone/index-$D.tsv"
    else
        cp "data/phone/index-$D.tsv" data/phone/index-now.tsv   # stable name for scripts run by hand
    fi
fi
echo "    $(wc -l < "data/phone/index-$D.tsv") files"
echo "2/6 provenance";  python3 scripts/substituted_sizes.py; python3 scripts/provenance.py "data/phone/index-$D.tsv"
echo "3/6 catalog";     python3 scripts/build_catalog.py "data/phone/index-$D.tsv"
echo "4/6 comparisons"; python3 scripts/contents.py; python3 scripts/compare_shamela.py; python3 scripts/compare_waqfeya.py   # contents.py: works inside a book count as present
echo "5/6 reports";     python3 scripts/report_shamela.py; python3 scripts/report_waqfeya.py; python3 scripts/report_recommend.py; python3 scripts/report_multi_editions.py; python3 scripts/report_manzumat.py; python3 scripts/report_people.py
                        [ -s data/changes/changes.tsv ] && python3 scripts/report_changes.py || true
python3 scripts/build_selection.py   # selection page catalogue (publish it with the Artifact tool when it changed)
                        python3 scripts/edition_info.py; python3 scripts/report_fixed.py; python3 scripts/build_site.py   # edition cards; report 09 fixed copies (owner, 2026-10-06)
# Indexes stay on the laptop for now (owner, 2026-10-05): publish to the phone only when the owner asks.
if [ "${1:-}" = "--publish" ]; then echo "6/6 publish"; python3 scripts/publish.py; else echo "6/6 (kept local; --publish uploads to the phone)"; fi
scripts/publish_web.sh || echo "web: publish failed (see above)"   # online copy: https://benjelloun.dev/library (owner, 2026-10-05)
[ "${OPEN:-}" = 1 ] && scripts/open_index.sh || true   # not opened by default (owner 2026-10-25: «don't auto open indexes» — each refresh left a 41 MB tab open in Brave); OPEN=1 opens it
