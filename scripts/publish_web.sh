#!/usr/bin/env bash
# Publish the indexes (site/0*.html) to the owner's GitHub Pages copy: https://benjelloun.dev/library
# (repository kmbenjel/library, branch main, cloned at ~/projects/library-site; WEB_REPO overrides).
# Copies the pages, commits only when something changed, pushes. index.html (redirect to page 00) is kept.
# NO_WEB=1 skips it. Called by refresh.sh after every rebuild (owner, 2026-10-05).
set -euo pipefail
cd "$(dirname "$0")/.."
[ "${NO_WEB:-}" = 1 ] && exit 0
REPO="${WEB_REPO:-$HOME/projects/library-site}"
[ -d "$REPO/.git" ] || git clone -q git@github.com:kmbenjel/library.git "$REPO"
git -C "$REPO" pull -q --ff-only
cp site/0*.html "$REPO/"
cd "$REPO"
git add -A -- '0*.html'
if git diff --cached --quiet; then echo "web: no change"; exit 0; fi
git commit -q -m "Indexes updated $(date '+%F %H:%M')

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
git push -q && echo "web: published to https://benjelloun.dev/library ($(git rev-parse --short HEAD))"
