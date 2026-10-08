#!/usr/bin/env bash
# One-off (2026-10-08 20:25 GMT, owner: «نواقص ما قبل 700 هـ (113 كتابًا مفقودًا) حمّل هذه الكتب كلها بعد التدقيق وأخضعها لما يلزم من
# فحص وعناية واضمن استمرار الأعمال بعد توقف هذه الحصة»). Unattended, log logs/pre700-2026-10-08.log. Never rerun once it logged
# «chain done» (AGENTS.md §6); a rerun before that resumes (fetch_queue keeps .done/.failed).
#  1. waits for the running refresh; 2. ids = Waqfeya books missing on the phone, author died in centuries 1–7 AH, in a phone
#     section (data/compare/waqfeya-matches.tsv, after the 2026-10-08 fix: wrong links count as missing, other copies excluded);
#  3. waq_queue.py: only the files each record links, skipping exact sizes already on the phone; 4. fetch_queue.py: parallel
#     download (full speed: owner), verify (size, %PDF, %%EOF, pdfinfo), upload; 5. additions_audit.py: other books of a bundled
#     item and copies already in the library removed (only these new additions), files named from the Waqfeya labels;
#  6. index, refresh, commit.
set -u
cd "$HOME/projects/phone-library"
LOG=logs/pre700-2026-10-08.log
if grep -q "chain done" "$LOG" 2>/dev/null; then echo "already done (see $LOG)"; exit 0; fi
Q=data/queue/271-pre700-missing
{
  echo "$(date -u '+%F %T') start"
  while pgrep -f "[s]cripts/refresh.sh" >/dev/null; do sleep 20; done
  if [ ! -s $Q-ids.tsv ]; then
    python3 - <<'EOF'
import csv, re
rows = csv.DictReader(open('data/compare/waqfeya-matches.tsv', encoding='utf-8'), delimiter='\t')
ids = []
for r in rows:
    m = re.search(r'(\d+)', r.get('century') or '')
    if r['status'] == 'missing' and r['phone_category'] and m and 1 <= int(m.group(1)) <= 7:
        ids.append(r['waqfeya_id'])
open('data/queue/271-pre700-missing-ids.tsv', 'w').write(''.join(i + '\n' for i in ids))
print(len(ids), 'missing pre-700 books')
EOF
  fi
  [ -s $Q.tsv ] || python3 scripts/waq_queue.py $Q-ids.tsv $Q.tsv
  echo "queue: $(wc -l < $Q.tsv) files"
  NETPACE=0 NET_MB=0 DL_JOBS=12 CONN=8 STAGE_GB=5 python3 scripts/fetch_queue.py $Q.tsv 271-pre700-missing
  python3 - <<'EOF' > /tmp/271-added.tsv
import csv, os
done = {l.strip() for l in open('data/queue/271-pre700-missing.done', encoding='utf-8')} if os.path.exists('data/queue/271-pre700-missing.done') else set()
for row in csv.reader(open('data/queue/271-pre700-missing.tsv', encoding='utf-8'), delimiter='\t'):
    if len(row) >= 3 and row[2] in done: print(f'{row[2]}\t{row[1]}')
EOF
  echo "uploaded: $(wc -l < /tmp/271-added.tsv) files"
  [ -s /tmp/271-added.tsv ] && python3 scripts/index_update.py 271-pre700-missing --add /tmp/271-added.tsv
  AUDIT_PLANS=271-pre700-missing python3 scripts/additions_audit.py data/phone/index-now.tsv plans/272-pre700-audit-remove.tsv plans/273-pre700-audit-names.tsv
  if [ -s plans/272-pre700-audit-remove.tsv ]; then
    flock /tmp/phone-ftp.lock python3 scripts/delete_files.py plans/272-pre700-audit-remove.tsv 272-pre700-audit-remove && python3 scripts/index_update.py 272-pre700-audit-remove
  fi
  if [ -s plans/273-pre700-audit-names.tsv ] && python3 scripts/apply_plan.py plans/273-pre700-audit-names.tsv --dry-run | tail -1; then
    flock /tmp/phone-ftp.lock python3 scripts/apply_plan.py plans/273-pre700-audit-names.tsv && python3 scripts/index_update.py 273-pre700-audit-names
  fi
  NO_OPEN=1 scripts/refresh.sh
  git add data/queue/271-pre700-missing* plans/272-pre700-audit-remove.tsv plans/273-pre700-audit-names.tsv data reports 2>/dev/null
  git commit -qm "271–273: missing pre-700 AH Waqfeya books added (only linked files, verified), bundled other books and copies removed by the audit, named from Waqfeya labels; refresh

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" && echo "committed $(git log --oneline -1)"
  echo "$(date -u '+%F %T') chain done"
} >> "$LOG" 2>&1
