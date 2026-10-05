# Phone Library — guide for AI agents (and humans)

This workspace manages a large Arabic PDF library on an Android phone: `Books/` on the phone's
internal storage, reached over FTP. The laptop keeps the scripts, the source catalogs and the
change log; the phone keeps the books and a copy of the indexes in `Books/فهارس الويب/`.

Read this file first. Keep it current when you change a convention.

## 1. Where things are

| What | Where |
|------|-------|
| Books (source of truth) | phone `Books/<category>/<book folder>/<file>.pdf` |
| Human + AI indexes on the phone | phone `Books/فهارس الويب/` (HTML indexes, reports, `catalog.json`, this guide) |
| Workspace (scripts, data, reports) | laptop `~/projects/phone-library/` (local git repo) |
| Work log (what was done, when) | `WORKLOG.md` |
| Every move/rename ever applied | `data/changes/changes.tsv` (time, action, from, to, reason, plan) |
| Plans (one TSV per batch of moves) | `plans/NNN-name.tsv` |
| Full catalog | `data/catalog.json` / `data/catalog.tsv` (rebuilt from the phone index) |
| Shamela catalog (local install, read-only) | `data/shamela/books.tsv` ← `~/.local/share/shamela/database/master.db` |
| Waqfeya catalog | `data/waqfeya/books.jsonl` (list) + `details.jsonl` (volumes, investigator, publisher, century, links) |
| archive.org file lists (exact sizes) | `data/archive/files.jsonl`, `items.jsonl`, `titles.jsonl` |
| Provenance (phone file → source file) | `data/phone/provenance.tsv` |
| Category mappings | `data/mappings/shamela-to-phone.tsv`, `waqfeya-to-phone.tsv` |

## 2. Connecting to the phone

- The phone runs an FTP server app: `192.168.11.100:2221`, anonymous login. The IP is DHCP; if it
  changes, find it with `ip neigh` and `nc -z <ip> 2221`, then set `PHONE_HOST=<ip>` for the scripts
  and `rclone config update phone host <ip>`.
- rclone remote: `phone:` (library = `phone:Books`). Optional mount:
  `rclone mount phone:Books ~/phone-books --daemon --vfs-cache-mode writes --dir-cache-time 1h`.
- Moves and renames are server-side (FTP RNFR/RNTO): nothing is re-uploaded, so they are instant.
- FTP has no checksums. Duplicates are verified with a head+tail 64 KB fingerprint plus the exact
  size (`scripts/dup_check.py`).

## 3. Rules

1. **Deleting:** Verified duplicates can be deleted directly by the agent without moving them to a temporary folder or asking for permission.
   "Verified" = same byte size + identical 64 KB samples at start, 25%, 50%, 75% and end (`dup_check.py` + `verify_dups_deep.py`).
2. **Every change goes through a plan** (`plans/NNN-*.tsv`: `from<TAB>to<TAB>reason`) applied with
   `scripts/apply_plan.py` (dry-run first). It never overwrites, removes emptied folders and logs to
   `data/changes/changes.tsv`. Undo a plan: `python3 scripts/apply_plan.py --undo NNN-name`.
3. **Names come from evidence, not guesses.** Match the exact size with the original download source only (which is usually archive.org). If unsure, leave the name and
   list it under "needs review" in the report.
   **Matching principle**: When generating indexes or comparing (Shamela/Waqfeya vs phone), base the logic on whether a book is *conceptually present* on the phone. If the author and title are present on the phone, the book exists. Do not rely on literal, exact string matches of titles and authors to declare a book missing, as differences between the phone's filenames and catalog records are expected.
   **One archive.org item often holds several sections or editions** (e.g. خريدة القصر: Iraq and Sham sections of
   two academies in one item). Never name all its files from the item title: read each volume's title page first
   (`pdftotext -l 8`; for image-only scans a low-resolution render of the first pages, `pdftoppm -r 25`).
4. **Only real PDFs belong in `Books/`.** A file named `.pdf` must start with `%PDF` and open. Earlier download
   scripts saved web pages (shamela.ws, archive.org error pages, «الرق المنشور»), MP3s and Word files as `.pdf`
   (392 removed on 2026-09-30 by the owner's decision). Check with `scripts/check_magic.py` (first bytes) and
   `scripts/check_pdf_tail.py` (end marker). When downloading, verify exact size + `%PDF` before uploading
   (`scripts/fetch_replacements.py` does). Missing books are replaced only from Waqfeya; otherwise left out.
   **Never download a whole archive.org item for one book:** items often bundle dozens of books. Take only the
   files the Waqfeya record links (its `links`), then run `scripts/additions_audit.py` — it keeps a file only if
   the record links it (or it follows the record's own pattern: link typos, `NN_IDp` prefaces), drops other books
   of the bundle, byte-identical copies of files already in the library, and double uploads.
5. After changes: re-index (`rclone lsf -R --files-only --format ps --separator $'\t' phone:Books`),
   rebuild the catalog, the site and the reports, publish them to the phone, add a WORKLOG line.

## 4. Naming conventions

Layout: `Books/<category>/<book folder>/<files>` or `Books/<category>/<file>.pdf`.
Single-volume books are stored as plain files in the category folder without their own subfolder. Folders are used only for multi-file works.

**Category** — All Shamela categories must be present and contain books. It is strictly forbidden to create any category that can fit into one of Shamela's categories.

**Book folder** (for multi-file works): `<title> - <author> (<edition>)`
- `<title>`: the full title, never cut. No `...`, no half words.
- `<author>`: the commonly used name (e.g. `ابن قدامة`, `الإمام الغزالي`). Omit for periodicals/series.
- `<edition>`: `ت <investigator> - <publisher>` or `ط <publisher>`; omit when unknown.
- Collections: `مؤلفات <author> (<publisher>)`; periodicals: `مجلة <name> (<publisher>)`; series: `سلسلة <name> (<publisher>)`.
- Different editions of the same book are separate folders that differ only in `(<edition>)`.

**Single file** (no folder): `<short title> - <author> (<edition>).pdf`
- `<short title>`: shorten the title by dropping subtitles (e.g., `زاد المعاد` instead of `زاد المعاد في هدي خير العباد`) so the filename can always include the author and publisher.

**Files**
- Independent books collected in one folder (a series such as «سلسلة أعلام المسلمين», «مؤلفات فلان») carry **no
  number**: each file is `<its own title>.pdf`. Only a series whose issues are really numbered keeps the issue
  number (e.g. «عالم المعرفة»: `003 - التفكير العلمي.pdf`). Never "01 -" in front of every item.
- Indexes (الفهارس) take the number after the last volume, never 99. For a periodical they take `00`.
- A companion that is not a volume (نسخة أخرى، صور المخطوطات، ملحق، the whole book in one file) has no number.
- Multi-volume: `NN - <short title> (<volume label>).pdf` — `NN` = the volume number, zero-padded to two digits (`01, 02`) or more for large collections. Volume numbers are never repeated. `00` is reserved for
  front matter and may appear more than once: `00 - <short title> (الواجهة).pdf` (cover/title pages),
  `00 - <short title> (المقدمة).pdf`. A preface belonging to one volume keeps that volume's number with
  `(المقدمة)`. The label describes the contents (`(الطهارة - الصلاة)`, `(الفهارس)`), balanced parentheses.
- `<short title>` = the title up to its first subtitle marker (`=`, ` - `, `ويليه`, `ومعه`, `المسمى`,
  `الموسوم`, `،`) or its first particle after two words; a one-word title gets ` - <author>`.
- Periodicals are named by what the file really contains, read from the source or the cover:
  `الأعداد 0026-0051 (السنة 2، 1934 - النصف الأول).pdf` (مجلة الرسالة), `المجلد 42 - الجزء الثاني (1998).pdf`
  (مجلة معهد المخطوطات), `فهارس المجلة - الجزء 6 (المجلدات 51-60).pdf` (مجلة مجمع اللغة العربية بدمشق).
- Items inside a collection/series folder: `<title> - <author>.pdf` or `NNN - <title>.pdf` for numbered issues.

**Characters** (the files are also copied to FAT/Windows sometimes):
- no `\ / : * ? " < > |`: `ت: فلان` → `ت فلان`, `?` → `؟`, `"` → `«»`
- no `_` used as a stand-in for `:` or `/`, no `_alt`, no `(نسخة ثانية)` (that is a duplicate → quarantine)
- single spaces, no leading/trailing spaces or dots; ≤ 200 bytes per name (≈ 95 Arabic letters)

## 4b. Sections (categories)

- **World literature** is a sub-category strictly inside the `الأدب` section (e.g. `الأدب/أدب عالمي`).
  Folder and file names are in the book's own language (`Les Misérables - Victor Hugo/01 - Les Misérables (Tome I - Fantine).pdf`).
  A translated non-literary work goes to its subject section (قصة الحضارة → التاريخ).
- Modern educational and general science books belong strictly inside Shamela categories: `الطب` (health guides, medicine) and `علوم أخرى` (Science, Mathematics, Psychology, Sociology, Humanities, OpenStax, Strang, Siyavula, Hindawi).
- All 40 Shamela categories must be strictly represented on the phone library. No custom category may ever be introduced if its contents can belong to any of the 40 Shamela categories. Any folder found outside the official Shamela classifications is assumed to be an error: its books must be moved to the appropriate Shamela category, and the stray category folder must then be deleted.

## 5. Expanding the library

1. Pick candidates from `Books/فهارس الويب/03 - توصيات التوسعة.html` (or its `.md`). Each lists the Waqfeya
   page and the archive.org item.
2. Check it is not already present: search `data/catalog.tsv` by normalized title and check exact sizes
   in `data/phone/provenance.tsv`.
3. Download from archive.org (`https://archive.org/download/<id>/<file>`), name it per §4, upload
   with `rclone copyto <local> "phone:Books/<category>/<folder>/<file>"`.
4. Re-index and republish (rule 4). Add the new book's source to the WORKLOG line.

## 6. Scripts (all in `scripts/`, Python 3, stdlib only)

**One command after any change on the phone:** `scripts/refresh.sh --publish` (re-index → provenance →
catalog → comparisons → reports → HTML → upload to `Books/فهارس الويب/`). Reports are written twice:
`site/*.html` (phone, Arabic, offline) and `reports/*.md` (for agents); on the phone the Markdown copies
are in `فهارس الويب/md/` and the data tables in `فهارس الويب/data/`.

| Script | Does |
|--------|------|
| `fetch_waqfeya.py` | Waqfeya book list via `waqfeya.net/books/books-api?page=N&pageSize=100` |
| `fetch_waqfeya_details.py` | each Waqfeya book page's full record (links, volumes, investigator…) |
| `fetch_archive_files.py` | archive.org `<id>_files.xml` → file names + exact sizes (fast) |
| `fetch_archive_titles.py` | archive.org titles in bulk (advancedsearch) |
| `export_shamela.py` | local Shamela `master.db` → `data/shamela/books.tsv` |
| `dup_check.py` | fingerprints same-size files on the phone |
| `provenance.py` | phone file → archive.org file → Waqfeya book |
| `dedup_plan.py` | picks the copy to keep, writes a quarantine plan |
| `apply_plan.py` | applies/undoes a plan over FTP, logs every change |
| `build_catalog.py` | `data/catalog.json` + `.tsv` |
| `periodical_plan.py` | periodicals: issue range per file + what the source item still has |
| `anthologies_check.py` | a canon of poetry anthologies checked against the library and Waqfeya |
| `build_site.py` | ONE self-contained file (index + every report as tabs, reports shown in a frame) — Android browsers do not follow links between local files |
| `compare_shamela.py`, `compare_waqfeya.py` | status of every Shamela / Waqfeya book vs the phone → `data/compare/*.tsv` |
| `report_shamela.py`, `report_waqfeya.py`, `report_recommend.py`, `report_changes.py` | reports 01–04 (HTML + MD) |
| `check_magic.py`, `check_pdf_tail.py` | is every ".pdf" a real, complete PDF? |
| `delete_files.py` | logged deletion (owner-approved only), removes emptied folders |
| `replacement_plan.py`, `fetch_replacements.py` | find Waqfeya replacements for removed files; download, verify, upload, log |
| `fetch_gutenberg.py` | public-domain books from Project Gutenberg: EPUB → A5 PDF (calibre), checked, uploaded, logged |
| `fetch_archive_pdfs.py` | chosen archive.org items as named PDFs (LIST file; `UPLOAD=0` downloads and prints first/last text to check content first) |
| `build_selection.py` | rebuilds the selection page (catalogue + Waqfeya/Shamela missing lists) from the comparisons |
| `fetch_selection.py` | downloads what the owner ticked on the selection page (saved `selections/current` → JSON): Hindawi, OpenStax, Hesperian, Siyavula; one uploader connection |
| `fetch_chapter_book.py` | a book its publisher offers only as chapter PDFs (Hesperian): download in order, join with pdfunite, upload, log |
| `fetch_new_books.py` | adds chosen archive.org items as new books (parallel, ZIPs extracted, `%PDF` check) |
| `additions_audit.py` | audits files added from Waqfeya/archive.org: removes other books of a bundled item and copies already in the library, names the rest from Waqfeya labels |
| `renumber_plan.py`, `tail_numbering_plan.py`, `label_numbering_plan.py`, `companion_plan.py` | numbering passes (independent books vs volumes; Waqfeya per-file labels are the authority) |
| `audit_numbering.py` | numbering audit (runs in the change-log report) |
| `restore_cut_names.py` | completes cut folder names by a unique prefix match (Waqfeya / Shamela / poems catalog) |
| `verify_dups_deep.py` | extra proof for duplicates (64 KB at 25/50/75%) before removal |
| `verify_provenance.py` | byte-checks doubtful provenance matches (first 64 KB phone vs archive.org) |
| `recat_plan.py` | section-correction planner (rules in §4b) |
| `rename_plan.py` | the rename/merge/split planner (evidence-based; writes `plans/NNN-*.tsv` + review list) |
| `buckets.py`, `textnorm.py`, `report_lib.py` | helpers |
| `publish.py` | uploads `site/`, `reports/`, data tables and this guide to the phone (copy, never deletes) |
| `refresh.sh` | everything above in order |
| `fetch_queue.py` | THE download/upload pipeline (§7): parallel aria2c, verify, one serialized phone connection, resumable |

## 7. Speed and concurrency (binding rule)

1. **Every download goes through `scripts/fetch_queue.py`** (or follows its model). Never `curl` files one by one.
2. **Internet downloads are always parallel and multi-connection:** `aria2c -x8 -s8 -k1M --continue`, 12 files at a
   time (`DL_JOBS=12 CONN=8`). Lower these only on HTTP 429/503 or repeated resets, and raise them back afterwards.
3. **The phone takes TWO FTP connections** (`--checkers=2 --transfers=2 --ftp-concurrency 2`). All phone I/O
   (upload, copy from phone, moves, listings) holds the shared lock `/tmp/phone-ftp.lock` (`flock`), so several
   jobs can run at once without fighting over the phone. The phone thread is never idle while files are waiting:
   download → verify → upload are separate stages; downloads never wait for uploads (except the staging cap).
4. **Staging cap:** the laptop disk is small (≈15 GB free on 2026-10-03). Staged files ≤ `STAGE_GB` (6), each staged
   file is deleted right after a successful upload.
5. **Verification runs in parallel** with the downloads: exact size, `%PDF`, `%%EOF`, `pdfinfo`.
6. **Independent tasks run at the same time in the background** (catalog fetches, dup checks, phone uploads, local
   downloads). A new request from the owner never cancels a running job; only an explicit order does.
7. **Everything is resumable:** `data/queue/<name>.done` lists finished targets, `<name>.failed` the failures with the
   reason. Re-running the same queue continues where it stopped.
