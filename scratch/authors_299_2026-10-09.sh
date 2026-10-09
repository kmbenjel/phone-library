#!/usr/bin/env bash
# One-off (2026-10-09, owner: «you can add Anouar's books as well. also mahmoud sheet khattab»). Unattended, log
# logs/authors-299-2026-10-09.log. Never rerun once it logged «chain done» (AGENTS.md §6); before that a rerun resumes.
#  1. ids = the Waqfeya books of أنور الجندي (109) and محمود شيت خطاب (22) missing on the phone (data/queue/299-*-ids.tsv);
#  2. waq_queue.py: only the files each record links; the same work already on the phone is skipped (samework.py);
#  3. fetch_queue.py (verified: size, %PDF, %%EOF, pdfinfo), paced (default NET_MB);
#  4. additions_audit.py: other books of a bundled item and copies already in the library removed (plan 300), names
#     from the Waqfeya labels (plan 301); 5. index, refresh, commit.
set -u
cd "$HOME/projects/phone-library"
LOG=logs/authors-299-2026-10-09.log
if grep -q "chain done" "$LOG" 2>/dev/null; then echo "already done (see $LOG)"; exit 0; fi
Q=data/queue/299-authors
{
  echo "$(date -u '+%F %T') start"
  [ -s $Q-ids.tsv ] || cat data/queue/299-anwar-jundi-ids.tsv data/queue/299-shit-khattab-ids.tsv > $Q-ids.tsv
  [ -s $Q.tsv ] || python3 scripts/waq_queue.py $Q-ids.tsv $Q.tsv
  echo "queue: $(wc -l < $Q.tsv) files"
  DL_JOBS=12 CONN=8 STAGE_GB=4 python3 scripts/fetch_queue.py $Q.tsv 299-authors
  python3 - <<'EOF' > /tmp/299-added.tsv
import csv, os
done = {l.strip() for l in open('data/queue/299-authors.done', encoding='utf-8')} if os.path.exists('data/queue/299-authors.done') else set()
for row in csv.reader(open('data/queue/299-authors.tsv', encoding='utf-8'), delimiter='\t'):
    if len(row) >= 3 and row[2] in done: print(f'{row[2]}\t{row[1]}')
EOF
  echo "uploaded: $(wc -l < /tmp/299-added.tsv) files"
  [ -s /tmp/299-added.tsv ] && python3 scripts/index_update.py 299-authors --add /tmp/299-added.tsv
  AUDIT_PLANS=299-authors python3 scripts/additions_audit.py data/phone/index-now.tsv plans/300-authors-audit-remove.tsv plans/301-authors-audit-names.tsv
  if [ -s plans/300-authors-audit-remove.tsv ]; then
    flock /tmp/phone-ftp.lock python3 scripts/delete_files.py plans/300-authors-audit-remove.tsv 300-authors-audit-remove && python3 scripts/index_update.py 300-authors-audit-remove
  fi
  if [ -s plans/301-authors-audit-names.tsv ] && python3 scripts/apply_plan.py plans/301-authors-audit-names.tsv --dry-run | tail -1; then
    flock /tmp/phone-ftp.lock python3 scripts/apply_plan.py plans/301-authors-audit-names.tsv && python3 scripts/index_update.py 301-authors-audit-names
  fi
  NO_OPEN=1 scripts/refresh.sh --no-list
  git add data/queue/299-* plans/300-authors-audit-remove.tsv plans/301-authors-audit-names.tsv data reports 2>/dev/null
  git commit -qm "299–301: the Waqfeya books of أنور الجندي and محمود شيت خطاب (owner) — only linked files, verified; bundled other books and copies removed by the audit, named from Waqfeya labels; refresh

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" && echo "committed $(git log --oneline -1)"
  echo "$(date -u '+%F %T') chain done"
} >> "$LOG" 2>&1
