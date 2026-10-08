# Phone Library — guide for AI agents (and humans)

This workspace manages a large Arabic PDF library on an Android phone: `Books/` on the phone's
internal storage, reached over FTP. The laptop keeps the scripts, the source catalogs and the
change log and, for now, the indexes (`site/`); the phone keeps the books. The indexes go to the phone
(`Books/فهارس الويب/`) only when the owner asks.

Read this file first. Keep it current when you change a convention.

## 1. Where things are

| What | Where |
|------|-------|
| Books (source of truth) | phone `Books/<category>/<book folder>/<file>.pdf` |
| Indexes (main + reports) | laptop `site/00 - الفهرس العام.html` (one file, reports as tabs) + `reports/*.md`; kept local for now (owner, 2026-10-05) |
| Indexes online (owner, 2026-10-05) | https://benjelloun.dev/library — GitHub Pages repo `kmbenjel/library` (clone `~/projects/library-site`), updated by `scripts/publish_web.sh` at the end of every `refresh.sh` |
| Indexes on the phone (when published) | phone `Books/فهارس الويب/` (HTML indexes, reports, `catalog.json`, this guide) |
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

- The phone runs an FTP server app on port `2221`, anonymous login. The IP is DHCP; known addresses:
  `192.168.11.103` (2026-10-05 noon), `192.168.11.102` (2026-10-04 and again 2026-10-05 afternoon) and `192.168.11.100` (before). The scripts try them, then scan the /24 for port 2221 (`phone_host.find()`)
  (`scripts/phone_host.py`; `PHONE_HOST=<ip>` overrides). If neither answers, find it with `ip neigh` and
  `nc -z <ip> 2221`, add it to the top of `CANDIDATES` in `phone_host.py` and run
  `rclone config update phone host <ip>` (rclone takes one fixed host).
- rclone remote: `phone:` (library = `phone:Books`). Optional mount:
  `rclone mount phone:Books ~/phone-books --daemon --vfs-cache-mode writes --dir-cache-time 1h`.
- Moves and renames are server-side (FTP RNFR/RNTO): nothing is re-uploaded, so they are instant.
- FTP has no checksums. Duplicates are verified with a head+tail 64 KB fingerprint plus the exact
  size (`scripts/dup_check.py`).

## 3. Rules

1. **Deleting:** Verified duplicates can be deleted directly by the agent without moving them to a temporary folder or asking for permission.
   "Verified" = same byte size + identical 64 KB samples at start, 25%, 50%, 75% and end (`dup_check.py` + `verify_dups_deep.py`).
   **Duplicate editions (owner, 2026-10-08, standing permission):** when several copies are the same edition (same editor
   and publisher/printing, shown by title/imprint pages, or the same scan shown by identical page images), keep the best one
   and delete the others without asking. Best = complete (every volume, introduction, indexes) > whole pages (no crop or
   quality defect) > higher true resolution > text layer > known source (Waqfeya/archive.org). Different editions (another
   editor, publisher or printing) are not duplicates and stay. A volume/folder that holds several books is never split.
2. **Every change goes through a plan** (`plans/NNN-*.tsv`: `from<TAB>to<TAB>reason`) applied with
   `scripts/apply_plan.py` (dry-run first). It never overwrites, removes emptied folders and logs to
   `data/changes/changes.tsv`. Undo a plan: `python3 scripts/apply_plan.py --undo NNN-name`.
3. **Names come from evidence, not guesses.** Match the exact size with the original download source only (which is usually archive.org). If unsure, leave the name and
   list it under "needs review" in the report.
   **Matching principle**: When generating indexes or comparing (Shamela/Waqfeya vs phone), base the logic on whether a book is *conceptually present* on the phone. If the author and title are present on the phone, the book exists. Do not rely on literal, exact string matches of titles and authors to declare a book missing, as differences between the phone's filenames and catalog records are expected.
   **Labels can be wrong** (Waqfeya pages sometimes link one file under two volume titles, and earlier passes copied
   those labels): before renumbering a set, check each file against its exact source file and read the title page or
   the PDF's embedded title («… - ج N: …»). A volume missing on the phone because its record linked another volume's
   file is usually still in the same archive.org item under the next file name.
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
5. After every edit: run `scripts/refresh.sh` (re-index → catalog → reports → site), WITHOUT `--publish` — the
   indexes stay on the laptop until the owner asks for them on the phone. It ends by opening the main index
   (`site/00 - الفهرس العام.html`) in Brave on the laptop (`scripts/open_index.sh`) for the owner to check:
   do this after every edit, also when only the indexes changed. Then add a WORKLOG line.

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
- **Folders that are not categories** (`scripts/special_dirs.py`, all protected like the index folder, never counted as books):
  `نسخ محسنة للاستبدال/<original path>` — improved copies (lossless crop of margins, split spreads, repaired or
  re-downloaded files) waiting for the owner's word; substitution = `ALLOW_PROTECTED=1 apply_plan.py` moving each copy over
  its original after the original is removed. `نسخ مستبعدة/<original path>` — weaker scans of an edition already kept,
  set aside for the owner's final decision (owner, 2026-10-05: keep only the best scan of the same edition).
- **The index folder is not a category and is never removed.** `Books/فهارس الويب/` (and any folder that holds the
  library's own indexes/reports) must never be deleted, emptied, moved or renamed — not by the category rule below,
  not by a duplicate or cleanup pass. `apply_plan.py` and `delete_files.py` refuse paths inside it
  (`PROTECTED` in `apply_plan.py`; add any new index folder there). On 2026-10-04 a category purge removed it.
- All 40 Shamela categories must be strictly represented on the phone library. No custom category may ever be introduced if its contents can belong to any of the 40 Shamela categories. Any folder found outside the official Shamela classifications (except the index folder above) is assumed to be an error: its books must be moved to the appropriate Shamela category, and the stray category folder must then be deleted.

## 5. Expanding the library

1. Pick candidates from `site/03 - توصيات التوسعة.html` (or `reports/03 - توصيات التوسعة.md`). Each lists the Waqfeya
   page and the archive.org item.
2. Check it is not already present: search `data/catalog.tsv` by normalized title and check exact sizes
   in `data/phone/provenance.tsv`.
3. Download from archive.org (`https://archive.org/download/<id>/<file>`), name it per §4, upload
   with `rclone copyto <local> "phone:Books/<category>/<folder>/<file>"`.
4. Re-index and rebuild the indexes (rule 5). Add the new book's source to the WORKLOG line.

## 6. Scripts (all in `scripts/`, Python 3, stdlib only)

**One command after any edit:** `scripts/refresh.sh` (re-index → provenance → catalog → comparisons → reports →
HTML → opens the main index in Brave). `--publish` also uploads to `Books/فهارس الويب/` — only when the owner asks.
Reports are written twice: `site/*.html` (Arabic, offline) and `reports/*.md` (for agents); when published, the
Markdown copies are in `فهارس الويب/md/` and the data tables in `فهارس الويب/data/`.

| Script | Does |
|--------|------|
| `fetch_waqfeya.py` | Waqfeya book list via `waqfeya.net/books/books-api?page=N&pageSize=100` |
| `fetch_waqfeya_details.py` | each Waqfeya book page's full record (links, volumes, investigator…) |
| `fetch_archive_files.py` | archive.org `<id>_files.xml` → file names + exact sizes (fast) |
| `fetch_archive_titles.py` | archive.org titles in bulk (advancedsearch) |
| `export_shamela.py` | local Shamela `master.db` → `data/shamela/books.tsv` |
| `export_shamela_cards.py`, `shamela_cards.py` | the local Shamela's book cards (printed title, full author, editor, publisher, edition, volumes, نبذة) and author biographies, read from its Lucene store with `tools/shamela-dump` → `data/shamela/cards.jsonl`, `authors.jsonl`; helpers for the edition line, «same edition?» and the match evidence (report 01) |
| `dup_check.py` | fingerprints same-size files on the phone |
| `provenance.py` | phone file → archive.org file → Waqfeya book |
| `dedup_plan.py` | picks the copy to keep, writes a quarantine plan |
| `apply_plan.py` | applies/undoes a plan over FTP, logs every change |
| `build_catalog.py` | `data/catalog.json` + `.tsv` |
| `periodical_plan.py` | periodicals: issue range per file + what the source item still has |
| `anthologies_check.py` | a canon of poetry anthologies checked against the library and Waqfeya |
| `build_site.py` | ONE self-contained file (index + every report as tabs, reports shown in a frame) — Android browsers do not follow links between local files |
| `compare_shamela.py`, `compare_waqfeya.py` | status of every Shamela / Waqfeya book vs the phone → `data/compare/*.tsv`. Shamela: a work is present in any edition, with the author agreeing (not on a common name); never an abridgement, commentary, selection, other part or recension; card titles and «ضمن …» collections count; rejected matches → `data/review/shamela-vetoed.tsv`, doubtful Waqfeya links → `data/review/waqfeya-link-doubts.tsv` |
| `report_shamela.py`, `report_waqfeya.py`, `report_recommend.py`, `report_changes.py` | reports 01–04 (HTML + MD) |
| `report_multi_editions.py` | report 05: works in several editions or scans — completeness, scan quality from the files, sourced notes (`data/editions/notes.json`) |
| `report_manzumat.py` | report 06: the teaching poems of each science (`data/mappings/manzumat-canon.tsv`) with their text and commentaries on the phone, Waqfeya offers for the missing; all other poems by section (replaces the old static «خزانة المنظومات» page) |
| `report_people.py` | reports 07 (authors by century of death; Shamela death year / Waqfeya century) and 08 (editors and their editions, from the «(ت …)» of the names) |
| `report_fixed.py` | report 09 «النسخ المحسنة»: every book whose scan had defects and was fixed (crop/split lossless, recompress lossy, repairs), from the change log + quality.tsv + provenance + edition cards; candidates to publish first (old prints, known source, whole set fixed), a ready «وصف النشر» per book; `data/fixed/fixed-copies.tsv` one row per file (owner, 2026-10-06) |
| `name_audit.py` | §4 name audit: raw archive names, >200-byte names, forbidden chars, non-PDF/tiny files, unknown categories → `data/phone/name-audit.tsv` |
| `raw_names_plan.py` | names files still called `NN_<id>.pdf` from the Waqfeya record that links them → plan + review list |
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
| `verify_pairs.py` | the same proof for explicit pairs of phone files |
| `verify_provenance.py` | byte-checks doubtful provenance matches (first 64 KB phone vs archive.org) |
| `recat_plan.py` | section-correction planner (rules in §4b) |
| `rename_plan.py` | the rename/merge/split planner (evidence-based; writes `plans/NNN-*.tsv` + review list) |
| `buckets.py`, `textnorm.py`, `report_lib.py` | helpers |
| `phone_host.py` | the phone's FTP address: first answering of the known addresses (§2); `PHONE_HOST` overrides |
| `publish.py` | uploads `site/`, `reports/`, data tables and this guide to the phone (copy, never deletes) — only when the owner asks |
| `publish_web.sh` | copies `site/0*.html` to the GitHub Pages copy (benjelloun.dev/library), commits only changes, pushes (`NO_WEB=1` skips) |
| `open_index.sh` | opens `site/00 - الفهرس العام.html` in Brave on the laptop (`NO_OPEN=1` skips) |
| `refresh.sh` | everything above in order |
| `fetch_queue.py` | THE download/upload pipeline (§7): parallel aria2c, verify, one serialized phone connection, resumable; `file:///…` = a file already downloaded and read; falls back to the item's own storage servers when archive.org's redirect lands on a failing node (HTTP 500) |
| `waq_queue.py` | Waqfeya records → `fetch_queue.py` lines (only the files each record links; skips what the phone already has) |
| `local_selection.py` | picks the best of the phone library for the laptop's local `~/Books` (group budgets) |
| `local_sync_plan.py`, `apply_local_plan.py` | local `~/Books` mirrors the phone's names/sections by MD5 (`md5sum` in ~/Books → plan → apply, logged in `data/local/changes.tsv`; the two protected local folders are never touched) |
| `phone_md5.py` | server-side `MD5` of every phone file → `data/phone/md5.tsv` (exact duplicates, local mirroring) |
| `exact_dups_plan.py` | groups of byte-identical phone files → which copy to keep (section, completeness, name quality) |
| `inspect_files.py` | reads every phone file (download → analyse → delete): PDF metadata (Waqfeya titles «… - ج N: label»), page sizes, image ppi/colour (page windows), text layer, margins, OCR queue → `data/inspect/files.jsonl`; `SHARD=k/n` runs n in parallel; `CROP_RECIPES=1` also stores per-page crop boxes |
| `inspect_ocr.py` | tesseract (ara+eng) on the front pages of image-only files → `data/inspect/ocr.jsonl`, keeps the page JPEGs |
| `remap_paths.py` | after renames: carries md5.tsv / files.jsonl records along the logged moves (chained), only for paths that no longer exist |
| `index_update.py` | keeps `data/phone/index-now.tsv` current from the change log without listing the phone (`--add` for uploads) |
| `names_plan.py`, `renumber_inside_plan.py`, `singles_plan.py`, `verify_names.py` | names and volume numbers from the files themselves (`data/phone/renumber-from-inside.txt` lists sets to renumber); single-file folders → plain files; name/edition checks |
| `quality_report.py`, `fix_pdf.py`, `improve_copies.py`, `front_pages.py` | scan problems (margins, spreads, low resolution, bloat) → lossless fixed copies into `Books/نسخ محسنة للاستبدال/` |
| `fix_at_scale.py` | fixed copies at scale, batch by batch: copies made (`improve_copies.py` with `MAX_KEPT=0.9`: a crop still showing > 90 % of the page is not uploaded — `data/improve/noop.tsv`), then substituted (original → «نسخ مستبعدة/__المستبدل», copy → its place, original deleted) and the index kept current. Lossy recompression only for gray/bitonal scans and never for a colour edition the owner likes (the Shakir Tabari stays in colour). Check crops with `pdftoppm -cropbox` (without it the full page is drawn) |
| `excerpt.py` | citations («book | volume | pages») → one bookmarked PDF for the phone, or Brave tabs at the right pages |
| `find_on_archive.py` | other archive.org uploads of books whose Waqfeya items went dark (candidates to read before adding) |

Only reusable tools live in `scripts/`. A one-off generator goes in `scratch/`; the plan or queue it writes is the
record.
**Never rerun a `scratch/` script or a plan that already ran** (2026-10-08: another agent relaunched the finished one-off
`scratch/restore_recompressed_224.py`; its second substitution set the 19 restored originals aside and deleted them —
fetched again by queue 247). Before launching anything, read `HANDOFF.md` and the tail of `data/changes/changes.tsv`:
if the plan name is already there, it is done. Only one agent works on the phone at a time. Safeguards since then:
`apply_plan.py` exits 1 when any move fails (callers stop before the next step) and `fix_at_scale.substitute` skips a
file whose improved copy is not in `index-now.tsv`. Nothing goes in the repo root. Removed one-offs (2026-10-05) are in git history at commit `0e64d80`.

## 7. Speed and concurrency (binding rule)

1. **Every download goes through `scripts/fetch_queue.py`** (or follows its model). Never `curl` files one by one.
2. **Internet downloads are always parallel and multi-connection:** `aria2c -x8 -s8 -k1M --continue`, 12 files at a
   time (`DL_JOBS=12 CONN=8`). Lower these only on HTTP 429/503 or repeated resets, and raise them back afterwards.
3. **The phone takes several FTP connections** (tested 2026-10-05: 5 at once accepted; use ≤ 3 for stability) (`--checkers=2 --transfers=2 --ftp-concurrency 2`). All phone I/O
   (upload, copy from phone, moves, listings) holds the shared lock `/tmp/phone-ftp.lock` (`flock`), so several
   jobs can run at once without fighting over the phone. The phone thread is never idle while files are waiting:
   download → verify → upload are separate stages; downloads never wait for uploads (except the staging cap).
4. **Git stays packed:** large derived files (site/00 is ~30 MB) are committed often; loose objects once grew `.git` to 9 GB
   (2026-10-06). `gc.auto` is set to 300; if `git count-objects -vH` shows GBs of loose objects, run `nice git gc --prune=now`.
5. **Staging cap:** the laptop disk is small (≈15 GB free on 2026-10-03). Staged files ≤ `STAGE_GB` (6), each staged
   file is deleted right after a successful upload.
6. **Verification runs in parallel** with the downloads: exact size, `%PDF`, `%%EOF`, `pdfinfo`.
7. **Independent tasks run at the same time in the background** (catalog fetches, dup checks, phone uploads, local
   downloads). A new request from the owner never cancels a running job; only an explicit order does.
8. **Everything is resumable:** `data/queue/<name>.done` lists finished targets, `<name>.failed` the failures with the
   reason. Re-running the same queue continues where it stopped.
9. **Never make the home network lag** (other people game and call on it — owner, 2026-10-05, twice; latency-based
   pacing alone did NOT stop the lag: while someone games, PAUSE bulk transfers entirely; when the owner says they are done,
   run at full speed, `NETPACE=0`). Only ONE bulk
   transfer at a time. Long phone transfers pace themselves (`scripts/netpace.py`): worst Wi-Fi ping to the router
   > 10 ms or internet ping > its baseline + 15 ms → 40 % slower; ceiling 6 MB/s. Internet downloads (`fetch_queue.py`,
   `NET_MB`, default 3 MB/s, 1.5 while anyone is home) and other queues start only after `scripts/wait_calm.py 10`
   (10 calm minutes); `scripts/resume_when_calm.sh` chains the paused queues that way. CPU-heavy jobs run with
   `nice`. Phone-side work (`MD5`, moves, renames, deletes) costs no bandwidth and can run any time.
10. **Stopping a job:** `kill <pid>` with the PID from `pgrep -f "[n]ame"` in a separate command — a `pkill -f name`
   in the same command line that restarts the job kills the shell itself.
