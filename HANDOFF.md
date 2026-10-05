# HANDOFF — current job (started 2026-10-03 07:00 UTC)

Any agent/model taking over: read `AGENTS.md` (esp. §7), then this file, then the last lines of `WORKLOG.md`.
Each workstream appends its progress below (newest last). Everything is resumable.

## Owner's request (summary)
1. Fix errors/organization of the phone library (`phone:Books`, FTP 192.168.11.102:2221 (formerly .100, see AGENTS.md §2), ONE connection).
2. Grow phone library 128.9 GB → 200 GB. Priority: authors died before 700 AH; all missing books of
   علي بن محمد العمران; complete سلسلة عالم المعرفة (phone has 001–060) to the highest issue on archive.org (archive.org only).
3. Local library `~/Books` 23 GB → 30 GB: the best of the phone library (poetry, sira, adab, single-volume
   essentials for every Muslim) + all/most Shamela categories. NEVER touch `أبو العلاء المعري` and `ابن الزبير الغرناطي`.
   Owner: transfer directly, no list review needed.
4. Max speed/concurrency → rule §7 in AGENTS.md (done) + `scripts/fetch_queue.py` (done).

## Decisions / assumptions
- "before 700" = author's death year < 700 AH.
- Verified duplicates → MOVE to `Books-مكررات/` only; deletion needs the owner's explicit approval (not given yet).
- Broken/non-PDF files → move to `Books-مراجعة/`, no deletion.
- Laptop disk ≈15 GB free: STAGE_GB ≤ 5–6, keep ≥ 6 GB free.

## Workstreams (each has its own queue + log)
| Stream | Queue / state | Done-file |
|---|---|---|
| A. Local library → 30 GB | `data/queue/local-30gb.tsv` | `data/queue/local-30gb.done` / `.failed` |
| B. Phone fixes | `plans/NNN-*.tsv` (latest after 050) | `data/changes/changes.tsv` |
| C. Phone expansion → 200 GB | `data/queue/<batch>.tsv` (omran, alam-almarifa, pre700-*) | `data/queue/<batch>.done` / `.failed` |

## How to resume
- Re-run the same queue: `DL_JOBS=12 CONN=8 STAGE_GB=5 python3 scripts/fetch_queue.py data/queue/<q>.tsv <plan>`.
- Phone size now: `flock /tmp/phone-ftp.lock rclone lsf -R --files-only --format ps --separator $'\t' --checkers=1 --transfers=1 phone:Books > data/phone/index-<date>.tsv` then sum column 2.
- Local size: `du -sh ~/Books`.
- Finish: `scripts/additions_audit.py`, `flock /tmp/phone-ftp.lock scripts/refresh.sh --publish`, WORKLOG line, git commit.

## Progress log
- 07:02 AGENTS.md §7 + fetch_queue.py written; streams A, B, C launched.

- 07:09 UTC:
  * Local library queue `data/queue/local-30gb.tsv` (824 books, ~7.05 GB) generated and launched in background (`task-138`). Speed benchmark showed Phone FTP is faster (~1.57 MB/s vs 0.34 MB/s on archive.org), with archive.org fallback for large files.
  * Sira, poetry, adab, essential single-volume works, and all missing Shamela categories are being populated into `~/Books/`. Protected folders `أبو العلاء المعري` and `ابن الزبير الغرناطي` strictly untouched.
  * Alam al-Ma'rifa queue prepared: `data/queue/alam_almarifa.tsv` (455 missing issues from 061 to 515, ~2.57 GB).
  * Ali al-Omran missing books queue prepared: `data/queue/omran.tsv` / `omran_clean.tsv`.
  * Pre-700 authors candidates queue prepared: `data/queue/pre700_clean.tsv` (2,541 files, >18 GB).
  * Duplicates analysis: 225 groups identified; duplicate investigation shows false files (e.g. `tilbatu't talabah` wrongly copied into multiple folders). Per owner's instructions ("investigate and decide"), verified duplicates will be quarantined to `Books-مكررات/`.
