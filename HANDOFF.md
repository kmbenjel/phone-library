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
- Finish: `scripts/additions_audit.py`, `flock /tmp/phone-ftp.lock scripts/refresh.sh` (indexes stay local; it opens the main index in Brave), WORKLOG line, git commit.

## Progress log
- 07:02 AGENTS.md §7 + fetch_queue.py written; streams A, B, C launched.

- 07:09 UTC:
  * Local library queue `data/queue/local-30gb.tsv` (824 books, ~7.05 GB) generated and launched in background (`task-138`). Speed benchmark showed Phone FTP is faster (~1.57 MB/s vs 0.34 MB/s on archive.org), with archive.org fallback for large files.
  * Sira, poetry, adab, essential single-volume works, and all missing Shamela categories are being populated into `~/Books/`. Protected folders `أبو العلاء المعري` and `ابن الزبير الغرناطي` strictly untouched.
  * Alam al-Ma'rifa queue prepared: `data/queue/alam_almarifa.tsv` (455 missing issues from 061 to 515, ~2.57 GB).
  * Ali al-Omran missing books queue prepared: `data/queue/omran.tsv` / `omran_clean.tsv`.
  * Pre-700 authors candidates queue prepared: `data/queue/pre700_clean.tsv` (2,541 files, >18 GB).
  * Duplicates analysis: 225 groups identified; duplicate investigation shows false files (e.g. `tilbatu't talabah` wrongly copied into multiple folders). Per owner's instructions ("investigate and decide"), verified duplicates will be quarantined to `Books-مكررات/`.

## Overnight 2026-10-05 (owner asleep; work without asking; resume from here after any stop)
Owner's request (full text in the session; summary):
- Editions (الطبعات) of the same book are KEPT for now, clearly distinguished in names + indexes (investigator, publisher,
  year, pages, scan quality, scholars' opinions on the edition). Gather everything needed for a later purge decision.
- Find books with size / cropping / readability problems; list exact issues for the owner. When the fix is clear,
  produce fixed copies into phone `Books-نسخ-محسنة/` (same relative path) for later substitution — never replace originals.
  A better copy of the same edition found elsewhere (library or web) may serve as the substitute.
- مجلة الرسالة: original lost (compressed in place). Look for a better, very readable copy → second folder; else get a
  sample of the original (archive.org) and judge whether compression is acceptable. Rank the Tabari + Kashshaf
  compressions and give thoughts.
- Fix all errors: names verified from INSIDE the files (title pages, prefaces), Waqfeya/logs as secondary; missing
  categories; duplicates; missing volumes; unfinished queues; same edition / different scans → keep the best
  (weaker → `Books-نسخ-مستبعدة/`, not deleted); expansion per strategy (pre-700 authors, العمران, quality first, no copy
  already present).
- Local ~/Books: fix what the audit found; expand ≈5 GB ("surprise me").
- End: insights on fast phone access (Acrobat, Google Files), desktop browsing, backup/restore to a new phone, and
  "open the pages cited in the margins of a book" workflows (desktop + phone, e.g. extract cited pages into one PDF).
- Indexes stay local; open site/00 in Brave after each edit (scripts/open_index.sh). Never remove the index folder.

Phone FTP: 192.168.11.102:2221, max 2 connections. The server has `MD5 <path>` (hash computed on the phone, ~70 MB/s).

### Steps (status)
1. [nearly done] `scripts/phone_md5.py` → data/phone/md5.tsv (exact dups). Log logs/phone_md5.log. 1 connection.
2. [running] `scripts/inspect_files.py data/phone/index-now.tsv data/inspect/priority.txt` → data/inspect/files.jsonl
   (+ ocr-queue/, thumbs/). 1 connection, ~3 h for 168 GB. Re-run the same command to resume.
3. [running] `/usr/bin/python3 scripts/inspect_ocr.py 5` (keeps front pages in data/inspect/pages/) (tesseract ara) on data/inspect/ocr-queue → data/inspect/ocr.jsonl.
4. [DONE] Risala/Tabari/Kashshaf → reports/overnight/01-risala-and-compressions.md.
5. [DONE 068–079] 1,124 copies deleted (≈8 GB). Left: 3 groups unreadable (data/phone/visual-check-state.json pending 3, 9, 12).
6. [PART] 070 named 574 batch files. Left: folder/section fixes (recat), single-file folders (singles_plan.py, after inspection).
7. [todo] Problems report (size/cropping/readability) + fixed copies → Books-نسخ-محسنة/.
8. [PART] report 05 rebuilt with quality + sourced notes (data/editions/notes.json). Re-run after inspection. Editions report (groups, distinctions, quality metrics, scholars' notes) → site tab.
9. [todo] Same edition / different scans → keep best, weaker → Books-نسخ-مستبعدة/.
10. [todo] Names verification across the library (inspect + OCR vs names) → plans. Then singles_plan.py (1,950 single-file folders → plain files): ONLY after inspection, junk names («- أحمد ا», «( - ط)») rebuilt from the PDF title/author metadata; never shorten away an author; shorten only for length.
11. [todo] Missing volumes, failed queues, expansion (pre-700, العمران).
12. [todo] Local ~/Books fixes + ≈5 GB expansion. Owner (05:xx): EVERY Shamela category must have at least a few books locally, and the sub-sections too (الأدب/أدب عالمي/… English, French, German, Spanish, translated). Local names mirror the phone. Protected: أبو العلاء المعري, ابن الزبير الغرناطي.
13. [todo] Insights write-up (phone access, desktop, backup, citations workflow).

### Notes for whoever resumes (2026-10-05 ~03:00)
- Index of the phone is kept current WITHOUT re-listing: after each plan run `python3 scripts/index_update.py <plan>`;
  before restarting inspect/md5 run `python3 scripts/remap_paths.py <plans since last remap>` (pending: 071 072 074–079).
- Kill jobs with `kill <pid>` from `pgrep -f "[n]ame"` in a SEPARATE command (pkill in a command line that also names the
  script kills the shell).
- Pending: renumber_inside_plan.py on data/phone/renumber-from-inside.txt (needs PDF titles → after inspection);
  073 queue re-run for archive.org failures (التحبير items return HTTP 500); local sync (local_sync_plan.py) after md5;
  Books-نسخ-محسنة samples (fix_pdf.py: crop sample 20 books, split 5 spreads); singles_plan.py after inspection.

### Status 2026-10-05 ~03:45
- Done tonight: duplicates 068–081 (1,125 files ≈ 8 GB), names 070/079/085/086/087, sections 088/089, singles 090 (407),
  reports 05–08 rebuilt/new, local mirror + expansion queue, insights (reports/overnight/03).
- Running: inspect_files.py (paced, ~1 MB/s while others game), inspect_ocr.py; resume_when_calm.sh waits for a calm
  network to run 083 (local expansion), 080 (improved samples), 084, 082 (almtoon), 073 (missing volumes retry).
- Owner: do NOT open Brave until the whole job is finished (data/.no-open); then delete data/.no-open and open once.
- Next when inspection progresses: renumber_inside_plan.py (32 folders in review), singles_plan.py (1,337 waiting),
  names_plan.py (all folders), verify_names.py → fixes, quality_report.py → crop recipes at scale, same-edition scans
  (keep best → «نسخ مستبعدة» only on the owner's word), remap_paths.py before each inspect restart.
