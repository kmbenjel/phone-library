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
