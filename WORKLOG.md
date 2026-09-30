# Work log — phone library revision

Newest entries at the bottom. "Context left" = tokens remaining in the working session's budget at that moment (out of 15,000,000).

| When | What | Context left |
|------|------|--------------|
| 2026-09-30 01:55 | Phone found: FTP 192.168.11.100:2221 (anonymous). rclone remote `phone`, mount `~/phone-books`. | 14.99M |
| 2026-09-30 02:05 | Inventory: 29 categories, 2,754 book folders, 9,469 PDFs, 99.3 GB. | 14.98M |
| 2026-09-30 02:10 | Local Shamela found (`~/.local/share/shamela`, 8,598 books / 41 categories) → `data/shamela/books.tsv`. | 14.97M |
| 2026-09-30 02:12 | Waqfeya catalog via `waqfeya.net/books/books-api` → 11,594 books (`data/waqfeya/books.jsonl`). | 14.96M |
| 2026-09-30 02:14 | Duplicates verified by head+tail 64 KB fingerprint: 841 extra copies in 818 sets (8.03 GB). 28 same-size pairs were different files. | 14.96M |
| 2026-09-30 02:18 | Plan 001: two index files in `فهارس الويب` had a false `.pdf` extension (really .html/.md) → fixed. | 14.94M |
| 2026-09-30 02:20 | Background: archive.org metadata (exact file sizes) for 11,408 items; Waqfeya book-page details. | 14.94M |
| 2026-09-30 02:25 | Found the cause of most naming errors: the earlier Gemini scripts cut titles to ~35 chars, numbered Waqfeya `00_` (front) files as `01`, tagged `p` (preface) files `_alt`, replaced `:` by `_`, and filed several books into "bucket" folders. | 14.86M |
| 2026-09-30 02:35 | Built: provenance matcher (exact size → archive.org → Waqfeya), rename planner, dedup planner (now uses provenance), phone index page, Shamela comparison (first pass: 1,029 / 8,598 = 12%). Background fetches at ~40–50%. | 14.82M |
| 2026-09-30 03:00 | All sources fetched: Waqfeya 11,594 records + details; archive.org 11,733 item file lists (~2,100 items now 403/404 = gone). | 14.76M |
| 2026-09-30 03:10 | Provenance: 7,159 / 9,469 phone files traced by exact size. 328 doubtful matches byte-checked (first 64 KB): 300 identical, 13 coincidences (dropped), 15 unreachable. Identical-but-differently-titled files are **not** renamed: archive.org items often bundle several works. | 14.72M |
| 2026-09-30 03:12 | Plan 002 (841 duplicate copies, 8.03 GB → `Books-مكررات/`): validated + dry run OK. **Blocked by the auto-mode safety check; awaiting the owner's approval.** | 14.72M |
| 2026-09-30 03:20 | Plan 003 (5,225 renames/merges/splits, computed as if 002 were applied): validated (no overwrite, no clash) + dry run OK. Awaiting approval; apply after 002. 527 items listed for human review. | 14.71M |
| 2026-09-30 03:22 | FTP server on the phone stopped once (port closed); owner restarted it. | 14.71M |
| 2026-09-30 03:25 | Published to `Books/فهارس الويب/`: 00 index, 01 Shamela (1,147 / 8,598 = 13.3%), 02 Waqfeya (1,894 complete, 78 partial, 401 other copy), 03 recommendations (6 of 88 core works missing), 04 change log with pending plans, AGENTS.md, data/*.tsv|json, md/*. | 14.71M |
| 2026-09-30 03:31 | Index/report headers now count titles (≈3,153 incl. current duplicates; ≈2,943 after plan 002) + 484 periodical issues + 9,467 files, instead of 2,752 folders. Publish fixed: phone FTP refuses rename-over-existing (553), so uploads use `--inplace`. | 14.99M |
| 2026-09-30 03:40 | Plan 003 revised: merges never cross sections (3 cross-section merges removed → review). 5,227 moves, validated. | 14.99M |
| 2026-09-30 03:50 | Owner approved plans 002 + 003, asked to remove real duplicates, and to fix sections (Shamela wins on ties). Deep check of all 841 duplicate pairs (+3 inner samples): 841 identical. | 14.99M |
| 2026-09-30 04:05 | Plan 002 applied: 841 copies → `Books-مكررات/` (8.03 GB), 117 empty folders removed, 0 skipped. Re-index matched the planned state exactly (8,626 files). | 14.97M |
| 2026-09-30 04:07 | apply_plan.py now caches folder listings (~50 → ~930 operations/min). Plan 003 running. | 14.97M |
| 2026-09-30 04:10 | Plan 003 applied (5,227 moves, 0 skipped). Found + fixed: bucket leftovers carried into a single-book folder (003b, 10 moves); one-word-title dedup rule; merges never cross sections. | 14.93M |
| 2026-09-30 04:14 | 003c cleanup (67): author-only file names, junk names (اضغط هنا/كاملا/…), Waqfeya "صفحة تجميعية" → "عدة طبعات", merged the two العوالي folders, 2 misplaced books. | 14.91M |
| 2026-09-30 04:16 | 004 sections (238 books / 621 files): Shamela wins; madhhab never → general fiqh; شروح→متون only with Shamela. | 14.90M |
| 2026-09-30 04:18 | 005: the 841 verified duplicates deleted (8.03 GB) after checking every twin is still in the library. rclone must use ≤2 FTP connections (phone limits anonymous logins). | 14.90M |
| 2026-09-30 04:22 | 007: restored 2 collection folders wrongly renamed after one book (series لقاء العشر الأواخر with 113 full issue titles from Waqfeya; مؤلفات الرافعي). Planner: collections never take a book's name; doubtful matches re-detected from current names. | 14.87M |
| 2026-09-30 04:25 | 008 pass 2 (36) + 009 revert of 2 collection-item renames. Refresh + publish. Library: 2,924 titles + 484 issues, 8,626 PDFs, 91.3 GB. | 14.87M |
| 2026-09-30 05:10 | Owner flagged: fake "01 -" on independent books (أعلام المسلمين) and "99" for indexes. Built renumber_plan (independent vs multi-volume), tail_numbering_plan, label_numbering_plan (Waqfeya per-file labels = the authority for volume numbers), companion_plan; applied plans 010–019. Mistakes caught and fixed on the way: plan 012 (wrong "ج 1-1" labels, undone), plan 011 turned 19 booklets of الفوائد into "(الواجهة) (N)" (restored in 019). Tabari split into its 3 editions (016). | 14.83M |
| 2026-09-30 05:12 | Numbering audit original → now: all-01 180 → 5, repeated volume numbers 453 → 29, 99-for-indexes 89 → 0. | 14.83M |
| 2026-09-30 05:20 | Byte check of every file: 392 of 8,626 are NOT PDFs despite ".pdf": 116 shamela.ws pages, 90 archive.org pages (failed downloads!), 24 «الرق المنشور» pages, 107 other web pages, 51 MP3 + 1 ZIP (Nasa'i audio), 3 DOC. Awaiting the owner's decision. | 14.82M |
| 2026-09-30 05:45 | Owner: "delete what is not PDF; replace from Waqfeya if found, else fine". Origin check: 390/392 non-PDF files were written on 2026-09-29; only ~50 during the poems (منظومات) script, ~336 during the 06:00–10:00 bulk transfer from the Waqfeya download scripts, which saved every Waqfeya link (shamela.ws, «الرق المنشور», archive.org pages, audio) as ".pdf". | 14.99M |
| 2026-09-30 05:50 | 020: deleted the 392 non-PDF files (logged; 89 folders became empty and were removed). 022: removed 1 truncated PDF whose complete copy exists. | 14.98M |
| 2026-09-30 05:55 | 021: replacements — 31 books / 177 files / 944 MB from Waqfeya (archive.org), each verified (exact size + %PDF) before upload. 66 folders needed nothing (only a web page was removed); 3 skipped (other edition on phone); 85 not found unambiguously in Waqfeya (left out, per the owner). Running. | 14.98M |
