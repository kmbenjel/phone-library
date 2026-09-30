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
