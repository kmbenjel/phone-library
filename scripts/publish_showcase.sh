#!/usr/bin/env bash
# THE PUBLIC SHOWCASE REPO (owner 2026-11-08 on the film review page: «نفّذ الاقتراح كله» — GitHub is for presentation only;
# the work repo with data, plans, the change log and his review comments is private: kmbenjel/phone-library-work).
# Exports the curated part of HEAD (code, rules, README, screenshots, CI) into ~/projects/phone-library-public and commits
# it there; with --push also pushes to the public kmbenjel/phone-library. Never data/, plans/, lists/, scratch/, build/,
# reports/, WORKLOG.md, HANDOFF.md.
#   scripts/publish_showcase.sh [--push]
set -euo pipefail
cd "$(dirname "$0")/.."
OUT=${SHOWCASE_DIR:-$HOME/projects/phone-library-public}
PATHS=(README.md AGENTS.md docs scripts .github .gitattributes)
[ -d "$OUT/.git" ] || { mkdir -p "$OUT"; git -C "$OUT" init -q -b main; }
# replace the tree (keep .git), then lay the curated paths from HEAD
find "$OUT" -mindepth 1 -maxdepth 1 ! -name .git -exec rm -rf {} +
git archive HEAD "${PATHS[@]}" | tar -x -C "$OUT"
[ -f LICENSE ] && cp LICENSE "$OUT/"
printf '__pycache__/\n*.pyc\n' > "$OUT/.gitignore"
cd "$OUT"
git add -A
if git diff --cached --quiet; then echo "showcase: no change"; else
  git commit -q -m "showcase: sync from the work repo ($(git -C "$OLDPWD" rev-parse --short HEAD))" && echo "showcase: committed"; fi
if [ "${1:-}" = --push ]; then git push -q origin main && echo "showcase: pushed"; fi
