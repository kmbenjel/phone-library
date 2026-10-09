#!/usr/bin/env bash
# One-off (2026-10-09, owner: «you can add Anouar's books as well. also mahmoud sheet khattab»): the second part — the 63
# Waqfeya records of أنور الجندي and محمود شيت خطاب that 299 held back for want of a section (their Waqfeya sections — الدعوة
# والدفاع، الموسوعات، الصحافة، العلوم العسكرية… — now mapped in waq_queue.WMAP). Unattended, log logs/authors-303-2026-10-09.log.
# Never rerun once it logged «chain done» (AGENTS.md §6); before that a rerun resumes.
#  1. queue data/queue/303-authors2.tsv (built by waq_queue.py from data/queue/299-authors-ids.tsv: only the files each
#     record links; works already on the phone skipped; two targets fixed by hand: «الضربات التي وجهت…» had lost its author
#     to the length limit, «الزهاوي شاعر الحرية» is a biography → التراجم والطبقات);
#  2. fetch_queue.py (verified: size, %PDF, %%EOF, pdfinfo), paced (default NET_MB);
#  3. additions_audit.py: other books of a bundled item and copies already in the library removed (plan 304), names from
#     the Waqfeya labels (plan 305); 4. index, refresh, commit. (Single-file folders → plain files: a separate plan after.)
set -u
cd "$HOME/projects/phone-library"
LOG=logs/authors-303-2026-10-09.log
if grep -q "chain done" "$LOG" 2>/dev/null; then echo "already done (see $LOG)"; exit 0; fi
Q=data/queue/303-authors2
{
  echo "$(date -u '+%F %T') start"
  echo "queue: $(wc -l < $Q.tsv) files"
  DL_JOBS=12 CONN=8 STAGE_GB=4 python3 scripts/fetch_queue.py $Q.tsv 303-authors2
  python3 - <<'EOF' > /tmp/303-added.tsv
import csv, os
done = {l.strip() for l in open('data/queue/303-authors2.done', encoding='utf-8')} if os.path.exists('data/queue/303-authors2.done') else set()
for row in csv.reader(open('data/queue/303-authors2.tsv', encoding='utf-8'), delimiter='\t'):
    if len(row) >= 3 and row[2] in done: print(f'{row[2]}\t{row[1]}')
EOF
  echo "uploaded: $(wc -l < /tmp/303-added.tsv) files"
  [ -s /tmp/303-added.tsv ] && python3 scripts/index_update.py 303-authors2 --add /tmp/303-added.tsv
  AUDIT_PLANS=303-authors2 python3 scripts/additions_audit.py data/phone/index-now.tsv plans/304-authors2-audit-remove.tsv plans/305-authors2-audit-names.tsv
  if [ -s plans/304-authors2-audit-remove.tsv ]; then
    flock /tmp/phone-ftp.lock python3 scripts/delete_files.py plans/304-authors2-audit-remove.tsv 304-authors2-audit-remove && python3 scripts/index_update.py 304-authors2-audit-remove
  fi
  if [ -s plans/305-authors2-audit-names.tsv ] && python3 scripts/apply_plan.py plans/305-authors2-audit-names.tsv --dry-run | tail -1; then
    flock /tmp/phone-ftp.lock python3 scripts/apply_plan.py plans/305-authors2-audit-names.tsv && python3 scripts/index_update.py 305-authors2-audit-names
  fi
  NO_OPEN=1 scripts/refresh.sh --no-list
  git add data/queue/303-* plans/304-authors2-audit-remove.tsv plans/305-authors2-audit-names.tsv data reports scratch/authors_303_2026-10-09.sh 2>/dev/null
  git commit -qm "303–305: the remaining Waqfeya books of أنور الجندي and محمود شيت خطاب (owner) — the records 299 held back for want of a section; only linked files, verified; audit; refresh

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" && echo "committed $(git log --oneline -1)"
  echo "$(date -u '+%F %T') chain done"
} >> "$LOG" 2>&1
