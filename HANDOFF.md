# HANDOFF — current job (started 2026-10-03 07:00 UTC)

Any agent/model taking over: read `AGENTS.md` (esp. §7), then this file, then the last lines of `WORKLOG.md`.
Each workstream appends its progress below (newest last). Everything is resumable.

## 2026-10-08 02:20 — phone off the network; chain waiting (scratch/when_phone_back_2026-10-08.sh, log logs/when-phone-back.log)
- 224 restore: 18 of 19 originals uploaded into «نسخ محسنة للاستبدال» (exact sizes); «الشفا» (1.77 GB) staged in
  downloads/queue, its upload refused when the phone left. NOTHING substituted yet. The chain reruns the restore (upload
  resumes from the staged file), substitutes the 19, applies plans 236–238, refreshes (guarded full listing), commits.
- Plans 218, 220–223, 225–235 applied tonight (sheets 230–272). If the chain did not run: start it again (resumable).

## 2026-10-08 03:00 — crop revert finished; title-page plans waiting
- Crop revert (212): 3,734 listed; 3,638 by the two lanes; 92 more by scratch/redo_revert_212.py (lanes had raced on
  «نسخ مستبعدة/__المستبدل» folders: 553/550 errors, originals stayed, copies waited — all substituted 01:30, 0 FAIL);
  4 left (نكات القرآن، الحاجب المصحفي، إحياء علوم الدين ج3/ج4: offset MediaBox) — fix_pdf.uncrop fallback written and
  tested on a synthetic file; redo with `python3 scripts/revert_crops.py lists/212-redo.tsv --prefix 212-r2-`.
  219 deleted 12 obsolete cropped copies; 2 lossy copies stay in «نسخ محسنة» (المقنع، تفسير الطبري شاكر: originals intact).
  NEVER run two lanes that create/remove folders under the same parent again.
- refresh.sh now refuses a cut-short listing (one 2-checker listing returned 3,953 of 16,579 files with no error).
- Plans written, to apply when the phone is free (dry-run, then apply + index_update): 218 (retry), 220, 221, 222, 223.
- To compare (duplicate editions, owner's standing permission): المقاصد الشافية (two folders, both جامعة أم القرى 1428;
  one has an 89 KB ج 8); التمهيد (folder «(وزارة الأوقاف المغربية)» 17 files vs the unlabeled 27-file Awqaf set; a 1-page
  cover of the الفرقان edition «172271 - …» sits in the first); شرح التصريح على التوضيح files numbered 00/01/02 but 00 has
  758 pages (renumber from the title pages).
- To compare too: المنتقى للباجي — «الفقه المالكي/… (دار الكتاب الإسلامي)» (cover + ج 1–7) and «شروح الحديث/المنتقى في شرح
  الموطأ للباجي» (8 oddly numbered files, page counts = the same ج 1–7, not byte-identical) are one edition; المفهم للقرطبي —
  «… (دار ابن كثير)» and «المفهم لما أشكل من تلخيص كتاب مسلم» have the same imprint (دار ابن كثير 1417).
- To compare too: الإتقان — «… (مجمع الملك فهد)» (6 files) is in fact محمد أبو الفضل إبراهيم's edition (وزارة الشؤون الإسلامية السعودية,
  title page sheet 259), the same as «… (ت محمد أبو الفضل إبراهيم - وزارة الأوقاف السعودية)»; دلائل الإعجاز (شاكر - الخانجي) in
  «الأدب/دلائل الإعجاز للجرجاني» (one 21 MB file) and «البلاغة/دلائل الإعجاز في علم المعاني …» (3 files). Renumber: «الزيادة والإحسان
  في علوم القرآن - ابن عقيلة (ط جامعة الشارقة)» files 01–10 carry «(جزء 10)…(جزء 1)» (ج 5 missing).
- To check: «علوم القرآن وأصول التفسير/مداخل إعجاز القرآن - محمود محمد شاكر (ط. مكتبة الخانجي)» holds two files; the one read
  (02, sheet 266) is مطبعة المدني ودار المدني بجدة — read the other, then name/compare. «المصطلحات الأربعة في القرآن» holds two files
  (two copies?). «الأدب/لامية العرب - الشنفرى (مكتبة الآ)» and «الشعر ودواوينه/المقصورة - ابن دريد (مكتبة المعا)»: cut names.
- To check: «كتب السنة/الجامع المسند الصحيح المختصر - الإمام البخاري (طوق النجاة)»: its introduction (sheet 278, دمشق 1423/2002)
  describes a one-volume two-colour printing (دار ابن كثير?) — read its imprint page before naming.
- To check: «كتب السنة/المعجم الأوسط - الحافظ الطبراني (ت الطحان - دار الحرمين)»: imprint (sheet 282) is دار الحرمين 1415/1995,
  which is طارق عوض الله وعبد المحسن الحسيني's edition, not الطحان's (مكتبة المعارف) — read the title page, then fix the editor.
- To check: «كتب السنة/خصائص أمير المؤمنين علي بن أبي طالب رضي الله عنه - النسائي» (3 files: introduction, a file
  labelled «(بن أبي طالب…)», the book) next to the plain file «… بن أبي - النسائي (ط دار الكتاب العربي)»: which edition is
  each (sheet 287 showed مكتبة الآداب، عبد الرحمن حسن محمود)?
- Duplicate to resolve (standing permission): «شروح الحديث/عارضة الأحوذي بشرح سنن الترمذي - ابن العربي المالكي (دار الكتب العلمية)»
  and «شروح الحديث/عارضة الأحوذي بشرح صحيح الترمذي - أبو بكر ابن العربي (ط دار الكتب العلمية)» (after plan 242): 14 files each,
  sizes differ by ≤ 20 KB per volume (same scan, metadata edited?) — verify the page images, keep the labelled set.
- Duplicate to resolve: «كتب السنة/فضائل شهر رمضان - ابن شاهين (ت سعد آل حميد - مكتبة المنار)» (949,589 B) and «… (ط مكتبة
  المنار)» (1,382,605 B): identical imprint pages (مكتبة المنار، الطبعة الثانية 1410) — compare the scans, keep the better.
- Duplicate to resolve: «كتب السنة/مسند الحميدي - عبد الله بن الزبير الحميدي (ت الأعظمي - عالم الكتب)» — its vol 1 imprint
  (sheet 298) is حسين سليم أسد، دار السقا 1996, the edition of «كتب السنة/مسند الحميدي (ت حسين سليم أسد الداراني)»: compare.
- Renumber: «كتب السنة/موطأ مالك - رواية يحيى (ت محمد مصطفى الأعظمي - مؤسسة زايد…)» holds «01 - موطأ مالك (alt - 01).pdf»
  (24.8 MB, «alt» is forbidden by §4) next to «01 - … (المقدمة)» (8 KB): read the volumes, renumber.
- To check: «كتب اللغة/الصاحبي في فقه اللغة العربية … (ت أحمد حسن بسج - دار الكتب العلمية)» (2 files): file 1 is عمر فاروق
  الطباع's edition (مكتبة المعارف 1414/1993, sheet 303) — read file 2, then name (two editions? two copies?).
- Missing now: البطليوسي «ذكر الفرق بين الأحرف الخمسة» (the file so named was الحميد's رقية book, moved by plan 246).
- To check: «شروح الحديث/مفتاح المنهل العذب المورود … (ت ابن بيومي - مطبعة الإستقامة)» (8 files): its file read on sheet 251
  is «المنهل العذب المورود» ج 2 by the father محمود محمد خطاب السبكي (مؤسسة التاريخ العربي) — read every volume, then name.
- To check: «الدرة الألفية - ابن معط (دار الف)» (cut publisher; German apparatus = Zetterstéen's edition?); «الروضة
  الأنيقة في نصرة العفيفة الصديقة - الصامولي» filed under النحو (subject?); «المسائل الاعتزالية …» linked to Waqfeya
  «التبصير في معالم الدين» (data/review/waqfeya-link-doubts.tsv); phone names whose author slot holds the editor
  («المحدث الفاصل - ت - الخطيب», «الفروق اللغوية - ت - سليم», «ذم قرناء السوء لاين عساكر», «تفسير القرآن - تفسير السمعاني»).

## 2026-10-08 01:30 — Shamela comparison made accurate (owner: «الآن تستطيع تماما تمييز ما هو غير موجود؟», «… تعتمد على البطاقات»)
- scripts/export_shamela_cards.py: the local Shamela's book cards (8,598: printed title, full author, editor, publisher,
  edition, volumes, نبذة) + author biographies (3,190) → data/shamela/cards.jsonl, authors.jsonl (tools/shamela-dump, Shamela's JRE).
  books.tsv gained author_id. scripts/shamela_cards.py: edition line, same-edition test, match evidence in Arabic.
- compare_shamela.py: new tiers cover / part-of («ضمن آثار المعلمي»: 122) / card title; every older tier re-checked by
  plausible() (author agrees on a non-common name — NAMEFREQ from Shamela authors —, no abridgement/commentary/part/other
  recension); doubtful Waqfeya links ignored (data/review/waqfeya-link-doubts.tsv, 96 rows: provenance to fix);
  vetoed matches in data/review/shamela-vetoed.tsv. Result 2,868 → 3,064 present, errors removed both ways.
  Regression ids kept in my session; samples: present ≈ 96–97 % right; remaining «missing» probe ≈ 25 % present (phone
  names lacking the author, synonyms) — next: fix those phone names (review list from vetoed «exact (author)»).
- report_shamela.py: «طبعة الشاملة» column (cards), «الطبعة على الهاتف» (same edition?), «وجه المطابقة». TODO: main index
  book cards could show the Shamela card + نبذة; refresh.sh should run export_shamela_cards.py when the Shamela store changes.
- Owner 2026-10-08: specks surely not text may be painted with the background colour (memory speck-cleaning-rule) — part
  of the improvement method AFTER the revert, samples for his approval first.

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

Phone FTP: 192.168.11.103:2221 since 2026-10-05 noon (was .102; scripts/phone_host.py tries both), ≤ 3 connections. The server has `MD5 <path>` (hash computed on the phone, ~70 MB/s).

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

### Status 2026-10-05 ~05:10
- Done since 03:45: العمران (092/093, data/authors/omran-works-status.tsv); 094/096/098 reverse-numbered sets by labels,
  verified against exact source files (two wrong labels fixed by reading); 095 (46 pre-700 works, 62 files, every title
  page read); missing volumes 097/099/100/103/104 (records that linked one file for two volumes: data/missing-by-duplinks.json);
  101 long names (none > 200 bytes left); 102 renumber-from-inside (417 files, ~70 sets; 52 sets in
  data/phone/renumber-inside-review.tsv need titles from OCR or reading); local-003 mirror (apply_local_plan.py).
- Running: inspect_files.py ×3 shards (SHARD=k/3, NETPACE=0), inspect_ocr.py (backlog ~4,700 front-page sets).
- Next: re-list the phone (index-now drifted: uploads of 073/082/084 were never added) → compare; renumber review list;
  edition-mixing folders (درج الدرر: two editions in one folder; ديوان جرير: الصاوي + dgsmh; تهذيب الآثار musnads);
  names_plan across raw names; singles_plan for the waiting single-file folders; verify_names; quality fixes;
  report 05 with full inspection data; then refresh.sh, delete data/.no-open, open Brave once.
- Lesson: labels lie sometimes (Waqfeya links one file under two volume titles; earlier passes copied labels). Check
  against the exact source file and the PDF's embedded title before renumbering (AGENTS §3 rule 3).

### Status 2026-10-05 ~12:30 (owner approved the 6 morning items + new requests; work continues without asking)
- Owner's new requests: approve all 6 (substitute improved copies; delete junk; 4 broken without source; other scans of
  the same edition → throw away; fixed copies at scale; more pre-700), keep the laptop disk safe, indexes: sections
  superposed (no sideways scroll), editors merged (بشار عواد = بشار عواد معروف), no change log online, header usable on
  phones; more chosen Waqfeya books; حميتو's missing works; careful printers (عامرة/بولاق، الحلبي، الخانجي، دار المعارف،
  حجرية فاس…), the dawawin of الأسد «مصادر الشعر الجاهلي»; a selection of the most-read missing Waqfeya titles.
- Done: 125–127 (substitutions, deletions), 128/128b (junk codes in names), 129/129b (singles), 130/131 (حميتو), 132,
  133/133b (14 jahili dawawin; canon in data/mappings/jahili-dawawin.tsv now complete), 137 (الكشف folder held 3 misfiled
  articles; the complete الكشف moved to التجويد والقراءات), 138/138b (split sets التحبير and سنن الترمذي joined; other
  scans of أبي تمام، مسند عابس، مصنف عبد الرزاق، فضل عشر ذي الحجة deleted), index page: slim sticky search bar only
  (templates/index.html), published to benjelloun.dev/library.
- Running (logs/): 134-printers (230 files, names from title pages: scratch/name_134.py), 137b-masoul (complete المعسول,
  then delete the old set with plans/137c-delete-masoul-old-set.tsv), 135-recompress (26 bloated gray scans → «نسخ محسنة»;
  substitute only copies ≤ 50 % of the original), stage-136a (top-missing selection, 141 works in data/expansion/top-pick.json;
  136b staged after 134 frees disk; then title sheets → names → upload, like 134).
- Not yet: crop/spread fixed copies at scale; the Tabari «طبعة ملونة» set (bloated but labelled colour: ask before graying).

### Status 2026-10-05 ~14:40 (unattended until the usage renewal ≈ 19:22; owner asleep)
- Running alone: `scratch/unattended_2026-10-05.sh` (log logs/unattended-2026-10-05.log), two lines:
  A. 134 printers DONE (230/230 uploaded) → index → stage 136b (downloads/stage-136b) → title sheets
     downloads/stage-136{a,b}/sheets (books.tsv + sheetNN.png) → refresh.sh --no-list (web published, Brave not opened).
  B. 135 recompress (retry of the 18 that timed out when the phone moved) → 139: lossless fixed copies (split spreads,
     crop dark scanner edges; lists/139-split-and-crop.tsv, small files first) into «نسخ محسنة للاستبدال».
- Done before: 137b/137c المعسول replaced by the complete set (22 files) and the old misnumbered set deleted (18).
- Next for the agent (one-shot resume task at 19:29 + the hourly check-in):
  1. 136a/136b: read the title sheets, write scratch/name_136.py like scratch/name_134.py (single files plain, sets
     numbered, editions from title pages), upload with fetch_queue (file://), index_update --add.
  2. 135: substitute only copies ≤ 50 % of the original (الشفا 19 %، فتوح البلدان 27 %، الطبقات 05 25 %، 03 39 % so far);
     delete the other recompressed copies from «نسخ محسنة» (خريدة القصر ×3، طبقات فحول الشعراء ≈ 80 %: not worth a lossy copy).
  3. 139: spot-check a few copies (render a page: original vs copy), then substitute (125-style: original out, copy in).
  4. Margins (3,895 files, 35 GB) in batches with substitution right after each batch (phone space unknown: FTP has no AVBL).
  5. WORKLOG line, git commit, summary to the owner.
- Owner 2026-10-05 ~14:45: the Tabari «جامع البيان … (ت شاكر - دار المعارف 1958 - طبعة ملونة)» STAYS IN COLOUR (he likes its colours;
  do not gray it to save 3 GB). Lossless crops are fine; never a gray recompression.
- 15:10 check of 139 (lossless crops): many copies barely change the page (samples: 100 %, 95 % of the page kept; one 72 %;
  splits work: 18 → 30 pages). Substitute ONLY splits and crops that keep ≤ 90 % of the page (measure CropBox/MediaBox
  on the copy with pymupdf); delete the near no-op copies from «نسخ محسنة». fix_pdf.py misses dark bands that have a
  thin white strip outside them (القول الفصل في تأييد سنة السدل: black bar at the bottom kept) — improve content_box().
- 136a uploaded (364 files) and indexed; 136b (389 files, names scratch/name_136b.py) uploading; فيض الباري (2/7 staged)
  and المحرر في أسباب النزول left out until their files download (archive.org nodes fail).
- 140: 17 recompressed copies substituted (≤ 50 % of the original; saving 3.8 GB), 9 unworthy copies deleted.
- Lid: systemd-inhibit blocks lid-close suspend until ~21:00 (pid in `systemd-inhibit --list`).
- 15:30: running `scripts/fix_at_scale.py 142 --batch 150` (log logs/fix-at-scale-142.log; per batch logs/142-bNN*.log):
  margins + dark borders + spreads (≈ 4,500 files, smallest first), copies made, measured before upload, substituted.
  `scratch/after_139.sh` waits for 139 to end, then measures and substitutes its last copies as plan 143.
  If interrupted: re-run the same commands (resumable). 136 complete (136a/136b/136c, 771 files).
- 15:35: the phone left the network (FTP not answering anywhere on 192.168.11.0/24). fix_at_scale.py now waits for the phone
  (and no longer counts merely-listed files as done; batches b02–b06 had failed and will be redone); after_139.sh waits too.
  Owner notified to reopen the FTP app. Everything resumes by itself when the phone answers (any known address).
- 20:10: phone back at .102 since 19:30; 142 running batch by batch (crops substituted at once). 144 (pre-700, 185 books)
  uploading → after_144.sh (second pass + index). 143 (last copies of 139) runs by itself after the 139 retry pass.
  Next: refresh.sh --no-list when 144 is indexed (rebuilds and publishes the indexes), WORKLOG, commit.
- 20:15: 144 done (253/253 uploaded and indexed); indexes rebuilt and published. Phone index: 16,553 files, 169.3 GB.
  Still running by itself: fix_at_scale.py 142 (batch 9 of ~30; each batch substitutes its copies at once) and
  after_139.sh → plan 143. Left for later: pre-700 works with no strong archive.org match (543; search by author/other
  uploads with scripts/find_on_archive.py), local ~/Books sync for today's additions.
- 20:30: 142 at batch 10 (≈ 1,330 books substituted so far; 3 checked by eye: nothing cut, footnotes/page numbers kept).
  139 retry pass running, then after_139.sh → 143. Nothing else pending for tonight; fix_at_scale writes its WORKLOG
  line when it ends. Morning: refresh.sh --no-list, commit, local ~/Books sync for today's additions.
- 2026-10-06 07:40: 142 crawled overnight (batch 13: 52 files in 10.5 h — the phone dozes with its screen off; a 7 MB
  download now takes 0.7 s) and is moving again (~3 files/min). ≈ 1,800 of ≈ 4,600 quality rows done; later batches
  hold bigger books. Keeping the phone awake (charger + screen-on/«stay awake» in the FTP app) keeps it fast.

## 2026-10-06: index improvements (owner approved, 07:45; credit renews ≈ 11:10 — resume task set for 11:17)
Owner: «الطبعة وسنة الطبع غير مذكورة في معظم الحالات» → make the indexes more helpful for knowledge; use the local official
Shamela (~/.local/share/shamela) when useful; ABSOLUTE ACCURACY first; tesseract again if needed. Steps:
1. [DONE 08:40, published] Edition card per book (data/editions/edition-info.json via scripts/edition_info.py; Shamela cards dumped
   with tools/shamela-dump → data/shamela/book-cards.jsonl; provenance kept across substitutions via scripts/substituted_sizes.py).
   Year known for 48%. Tesseract cannot read calligraphic imprints → READ BY EYE: scripts/imprint_sheets.py (running in the
   background, resumable: `nice python3 scripts/imprint_sheets.py --workers 4`) writes data/editions/imprint-sheets/sNNNN.png
   (6 books each, numbered) + books.tsv; read each sheet and append to data/editions/imprint-read.tsv (n, hijri, gregorian,
   edition, note) ONLY what is plainly printed (no year printed → no row); then edition_info.py + build_site.py + publish_web.sh.
   Done: 145 (111 books to Shamela's section), 145b, 146/146b (§4 names from records), Western digits everywhere (owner).
   [old text] Edition card per book (data/editions/edition-info.json via scripts/edition_info.py): editor, publisher (+city),
   edition number, year (hijri/gregorian), volumes, pages, each with its source. Evidence must be the phone's OWN edition:
   (a) Waqfeya record linked to the phone file by exact size (provenance) → yearOfPublish, copyNumber, pages, publisher,
   researcher; (b) Shamela book card ONLY when the editor/publisher in the phone name match the card; (c) title/imprint
   page OCR (tesseract ara, data/inspect/pages + new renders of pages 2-4) for the rest, accepted only when the year and
   publisher are read cleanly; (d) the phone folder name «(ت …- …)». Never guess.
2. [todo] Author death year (not only the century) from Shamela's author table, matched on the author + the work.
3. [todo] One-line description from Waqfeya; editions of the same work side by side with scan quality and notes.
4. [todo] Category audit (e.g. «أرجوزة في علم رسم الخط - الموصلي» sits in أصول الفقه → التجويد والقراءات).
5. [todo] Header numbers consistent («نحو 6,044 عنوانًا» vs «الكل 5,891»); sizes in GB (169.3) not GiB (157.6).
6. [later] Work tree (متن → شروح، حواشي، مختصرات، منظومات), author/editor pages, filters (printer, old prints).
   Owner 08:20: the «before 700 AH» filter belongs ONLY in the comparison reports (01 الشاملة، 02 الوقفية: what early
   books are missing), not in the main index. Reading paths per science: not now.
Background meanwhile: fix_at_scale.py 142 (margins), after_139.sh → 143.
- 09:15 (2026-10-06): imprint reading reveals misfiled content too: 149 — «الرسائل الأدبية - الجاحظ» and «العمدة - ابن رشيق» held
  only an article / a thesis (renamed to what they are). TO FETCH: العمدة في محاسن الشعر (ابن رشيق) and رسائل الجاحظ (هارون).
  148/148c: قادة فتح الأندلس vol 1 and فتح الباري 02-03 added (re-upload of the same scan); 147/148b names.
- 12:20 (2026-10-06): sheets 32–46 read (books 192–281). Reading keeps finding misfiled content → plans 152–155 (articles and
  Algerian university theses filed under classical titles «رسائل الثعالبي», «طوق الحمامة», «تحسين القبيح»; other works of
  اليوسي under «زهر الأكم»; الإمتاع ج 2 under «الصداقة والصديق»; «النحو الكوفي» under «معاني القرآن للفراء»; wrong publisher
  labels of the 2026-10-03 «عيون الأدب» batch: الرافعي = وكالة الصحافة العربية, فيض الخاطر = مكتبة النهضة المصرية,
  الأغاني = دار صادر). NOT ON THE PHONE (only misfiled stand-ins were): رسائل الثعالبي، طوق الحمامة (other edition kept),
  تحسين القبيح، زهر الأكم، الصداقة والصديق → candidates to fetch from Waqfeya.
  NEEDS REVIEW (owner): «Momen Tak Terlupakan …» (Indonesian AI-assisted translation of «مواقف لا تنسى») — keep?;
  «رسالة جامعية - بيان الصاف» (title in a broken font); two Shakir «دلائل الإعجاز» scans remain (الأدب 400 ppi 1-bit,
  البلاغة 300 ppi with text) — keep one?
  TODO: the 300-poem «منظومات» batch (data/mappings/mandumat_catalog.json) — its parser split titles at «لـ…» («ميسر التحصيل
  فيما - مالك من التأصيل», «منظومة المكفرات - كل ذنب سابق وآت»), and all 300 were put in الأدب whatever their subject: one
  pass over them (raw_title → full title, author from the title page, Shamela section by subject). 155 fixed six of them.
- 13:55: sheets 62–67 read (books 372–407) → plans 162 (seven التاريخ files to their subjects: الفرق والردود، التفسير، العقيدة،
  النحو، البلدان), 163 (المفصل في تاريخ العرب قبل الإسلام, only vols 1–4 of 10 on the phone → TO FETCH vols 5–10 of the
  جامعة بغداد 2nd ed. 1413/1993; تاريخ خليفة ت العمري; ابن طولون → التفسير). The التاريخ section holds many stray single
  files from the منظومات/blog batches: worth one dedicated pass over التاريخ plain files after the sheets.
- 12:20 PAUSE (owner: 80 % of the session used; renewal ≈ 16:20). Running unattended: scratch/unattended_2026-10-06.sh
  (log logs/unattended-2026-10-06.log): phone MD5s → waits for fix_at_scale 142 + after_139 → remap → refresh (web) → commit.
  No internet downloads during the pause. RESUME HERE: imprint sheets from s0306 (book 1836); plans 168–174 applied after the pause began (أزهار الرياض case DONE in 168).
  OPEN CASE «أزهار الرياض» (3 folders in التراجم والطبقات, title pages seen at 25 dpi, read them larger before any plan):
  «- المقري التلمساني» arfaa1–3 = ج 1–3 of the صندوق إحياء التراث الإسلامي (المغرب والإمارات) reprint 1398/1978, arfaa4 =
  ج 4 ت سعيد أعراب ومحمد بن تاويت; «للمقري» 1–3 look like the Cairo لجنة التأليف volumes (same as the third folder «ت السقا
  والإبياري»?) and 4–5 like ج 5 / ج 4 of the صندوق edition — check sizes/md5 against the third folder for duplicates,
  then one folder per edition.
- 17:00: NEEDS REVIEW (owner): «النكت والعيون تفسير الماوردي … (دار الكتب العلمية).pdf» (one file, 3,085 pages) is the same DKI
  edition as the 6-volume folder «ت السيد بن عبد المقصود» (3,021 pages) with 64 more pages — keep both or only one?
  «البحر المحيط - دار إحياء التراث (ت المهدي)» has vols 1–4 of 8 → candidates to fetch.
- 18:30 NEEDS REVIEW (owner): «الروض الأنف» ت الوكيل (دار الكتب الحديثة 1387) exists as two scans: the complete 7-volume «المسهم»
  scan (1582×2599 px + a logo on every page) and a sharper Waqfeya scan (WAQ164489, ≈1940×2770 px) of vols 1–3 only — keep
  both until the Waqfeya vols 4–7 are fetched? «النكت والعيون» DKI exists as one file and as 6 volumes (see 17:00).
- 19:10 NEEDS REVIEW (owner, two scans of one edition — keep the better?): «جامع العلوم والحكم» ت الأرناؤوط (الرسالة) as one file in
  شروح الحديث and as a folder in الجوامع (1,073 pages each, different scans; the work belongs in شروح الحديث); «نصب الراية»
  ت عوامة (مؤسسة الريان / دار القبلة) as one file and as a folder (2,342 pages each, different scans).
  Plans 183/185/190/193 removed split copies that were the same scan as a one-file copy (image lists identical).
- 2026-10-07 15:20 STOPPED fix_at_scale.py 142 (owner: crops made pages of unequal width, ate the natural margins of e.g. the
  هارون editions, and a speck kept a page of «اللآلئ المصنوعة» wider). DO NOT RESUME. 3,542 files had been substituted.
  Audit of 40 random crop files (scratch/crop_audit.py → data/fixed/crop-audit.tsv): median margin left 2.8 % of the page,
  10/40 with text touching the edge; 22/40 with a page ≥ 10 % wider than the median, 8/40 ≥ 20 %. Selection was too broad:
  of 1,743 files with a measure, 1,220 had text using 60–69 % of the width (an ordinary book). Crops are CropBox-only
  (images untouched): reverting = CropBox := MediaBox per page, lossless. Awaiting the owner's decision (revert all / redo few).
- 2026-10-07 18:30: phone not on the network (no FTP at .102, network scan found none) — renames from sheets wait for it.
  To check later: books 1257 «اختيارات شيخ الإسلام - ابن عبد الهادي» (1.9 MB) and 1261 «الاختيارات الفقهية … لدى تلاميذه -
  سامي جاد الله» (16 MB) show the same عطاءات ISBN 978-9959-857-88-0: is the small file a part of the big one?
- 2026-10-07 22:40: plans/211-sections-read.tsv written (4 moves: الطب النبوي لأبي نعيم → كتب السنة، نخبة الأصول → أصول
  الفقه، نظم الأخضري → الفقه المالكي، رسالة أهل السنة في المغرب → العقيدة) — NOT YET APPLIED (phone FTP down): apply it first.
- 2026-10-07 23:00: OWNER DECIDED «قم باللازم» → undo all crops. scratch/revert_chain.sh (log logs/revert-chain.log) waits
  for the phone, applies 211, then scripts/revert_crops.py lists/212-uncrop.tsv (3,734 files, 30 GB, paced): fix_pdf.py
  --uncrop = every CropBox := MediaBox by incremental save (asserts: same pages, same images, no page cropped), upload size
  checked, three-step substitution (plans 212-uNNa/b/c). Split spreads stay split (halves tile the page). Recompressed (19):
  still to restore from archive.org by their original sizes (data/phone/substituted.tsv). Report 09 to be reworked after.
- 2026-10-07 22:55 owner: transfers at full speed (NETPACE=0) until he says otherwise; revert chain restarted with NETPACE=0.
- 2026-10-07 23:05: revert switched to two FTP lanes (scratch/revert_lanes.sh; lists/212-uncrop-x/-y.tsv; logs/212-uncrop-x/-y.log); u01–u05 done by the single lane.
- 2026-10-08 00:00 owner: a volume/folder holding several books is never split; its contents are recorded by
  scripts/contents.py (collections, «ويليه/ومعه/وبهامشه», a commentary kept with its text) → data/editions/contents.json,
  counted as present in compare_shamela.py (match «contained»), shown in the index as «يضم N عملًا» (✓ = in Shamela).
  Plan 214 put العبقري and its commentary back in one folder. Hourly check-in cron 7dc09905 (:23) carries the current plan.

## TASK QUEUE (2026-10-08 00:20, in order; the hourly check-in works through it)
1. [running] crop revert, two lanes (scratch/revert_lanes.sh). After it: delete the leftover cropped copies in
   «نسخ محسنة للاستبدال» that no plan substituted (from the stopped 142 batches and the killed u03/u06 batches; the originals are
   in place — check each path still exists before deleting its copy).
2. Restore the 19 recompressed files from archive.org by their original sizes (data/phone/substituted.tsv; fetch_queue.py).
3. Rework report 09 (report_fixed.py) for the state after the revert (splits and repairs remain; crops undone).
4. inspect_files.py on the 1,349 phone files never inspected (added since 10-05; one FTP lane, after the revert).
5. Imprint sheets s0224–s0312 (books 1344–1868); refresh every ~10 sheets.
6. contents.py: widen matching (titles joined by «و», author-less items via the collection's author) — keep it conservative.
7. [cancelled by the owner 2026-10-08] old queues of 2026-10-03 → data/queue/cancelled/ (see its README).
8. To fetch (found while reading): المفصل لجواد علي ج 5–10؛ البحر المحيط (دار إحياء التراث) ج 5–8؛ العمدة لابن رشيق؛ رسائل
   الثعالبي؛ تحسين القبيح؛ زهر الأكم؛ الصداقة والصديق؛ كتاب المحن؛ الغرر في فضائل عمر؛ التفسير البسيط؛ رجال المعلقات العشر.
9. Local ~/Books mirror: re-sync names/sections with the phone (local_sync_plan.py → apply_local_plan.py; the two protected
   local folders are never touched).
10. Review lists: edition-review.tsv (131), renumber-inside-review.tsv (54 sets), 15 «- ت-» names, 2 raw names, 35 doubtful
    section pairs. Owner decisions pending: the 11 files in «نسخ مستبعدة», duplicate editions (النكت والعيون، جامع العلوم
    والحكم، نصب الراية، الروض الأنف), Momen Tak Terlupakan, «رسالة جامعية - بيان الصاف».
- 2026-10-08 00:00: «النوادر والزيادات» دار الغرب 1999 twice: one file «(دار الغرب الإسلامي - نسخة أخرى)» 116 MB, 7,836 pages,
  and the 14-file folder «النوادر والزيادات على ما في المدونة … (دار الغرب الإسلامي)» 120 MB, 7,835 pages → same edition:
  compare after the revert, keep the better (owner's permission), delete the other.
- «الكافي في فقه أهل المدينة» DKI edition three times (title pages read): «… (مكتبة الرياض الحديثة).pdf» (mislabelled, 644 p,
  62 MB), «… المالكي (ط دار الكتب العلمية).pdf» (636 p, 12 MB, Waqfeya fp73997), folder «الكافي … لابن عبد البر/» (636 p,
  60 MB); the 1,184-page «(ط مكتبة الرياض الحديثة)» (Waqfeya fp16620, ت ولد ماديك) is another edition and stays. After the
  revert: compare the three DKI copies page by page, keep the best, delete the others (plan 216 was skipped: name taken).
- «حاشية الدسوقي على الشرح الكبير»: the folder «(دار الفكر)» (4 files, 104 MB) shows the Halabi title page, like the folder
  «مع تقريرات الشيخ عليش (ط عيسى البابي الحلبي)» (5 files, 103 MB): same edition? compare after the revert; keep the better.
