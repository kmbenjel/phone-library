#!/usr/bin/env bash
# One-off (2026-10-06 12:20, owner: 80 % of the agent's session used — keep the home machines working until the
# renewal ≈ 16:20 without loading the home connection). No internet downloads at all.
#   1. phone_md5.py: MD5 of the ~1,660 files that have none, computed by the phone itself (nothing transferred)
#   2. fix_at_scale.py 142 and after_139.sh keep going on their own (LAN crop/split copies → substituted); wait for them
#   3. then: substituted sizes → records remapped → refresh (--no-list: index-now is kept current) → web copy → commit
# Nothing here names, moves or deletes books: that stays for the agent to judge when it is back.
cd "$(dirname "$0")/.."
log(){ echo "$(date '+%F %T') $*"; }
waitfor(){ while pgrep -f "$1" >/dev/null; do sleep 60; done; }
log "1: phone MD5 of the files without one"
nice python3 scripts/phone_md5.py >> logs/phone-md5.log 2>&1
log "1: done: $(tail -1 logs/phone-md5.log)"
waitfor "[f]ix_at_scale.py 142"; log "2: fix_at_scale 142 finished: $(tail -1 logs/fix-at-scale-142.log)"
waitfor "[a]fter_139.sh";        log "2: after_139 finished"
python3 scripts/substituted_sizes.py; python3 scripts/remap_paths.py
NO_OPEN=1 nice scripts/refresh.sh --no-list > logs/refresh-unattended.log 2>&1
log "3: refresh: $(tail -2 logs/refresh-unattended.log | tr '\n' ' ')"
echo "- $(date '+%F %H:%M') — unattended (owner's session paused): phone MD5 of the files without one; fix_at_scale 142 finished; records remapped; indexes refreshed and published." >> WORKLOG.md
git add -u && git add plans lists && git commit -q -m "unattended 2026-10-06: fixed copies 142 finished, phone MD5s, refresh

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" && log "3: committed $(git log -1 --format=%h)"
