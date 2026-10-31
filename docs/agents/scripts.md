# Scripts — full table

Moved verbatim from AGENTS.md (2026-10-28) to keep that guide short; AGENTS.md points here. Section numbers are the old ones (code comments cite them).

## 6. Scripts (all in `scripts/`, Python 3, stdlib only)

**One command after any edit:** `scripts/refresh.sh` (re-index → provenance → catalog → comparisons → reports →
HTML; the index is not opened in Brave unless `OPEN=1`). `--publish` also uploads to `Books/فهارس الويب/` — only when the owner asks.
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
| `name_audit.py` | §4 name audit as the rules stand (2026-10-18): categories, > 240 bytes, forbidden chars, parentheses, commas, «ط», raw archive names, uploader words, tiny/non-PDF files, 99 for indexes, one-file folders, a volume number used twice, a hamza on a hamzat al-wasl (by the local Shamela's spellings) → `data/phone/name-audit.tsv` |
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
| `phone_watchdog.sh` | runs detached (`setsid nohup … >> logs/phone-watchdog.log &`): pauses (SIGSTOP) crop_library/crop_batch/inspect_files/ocr_clean while the FTP port is silent, resumes when it is back on the same address; another address → stays paused, written to data/phone/new-address.txt |
| `battery_guard.sh` | runs as the user unit `battery-guard` (`logs/battery-guard.log`): on battery at ≤ 7 % it freezes the running transient units and SIGSTOPs jobs outside a unit (never kills), then suspends past the inhibitors with sudo; jobs resume when the charger is back |
| `publish.py` | uploads `site/`, `reports/`, data tables and this guide to the phone (copy, never deletes) — only when the owner asks |
| `publish_web.sh` | copies `site/0*.html` to the GitHub Pages copy (benjelloun.dev/library), commits only changes, pushes (`NO_WEB=1` skips) |
| `watch_comments.py` | one line per settled owner comment on the review pages (and lasting phone up/away): an agent watches it and acts on each comment as it comes |
| `start_services.sh` | after a reboot or a lost session: starts the governor, phone keep-alive and watchdog, review server, the terminal reporter and the two inhibitors (lid closed, idle) again — each skipped if it runs. Run it from a terminal of the owner's session |
| `run_resumable.sh` | runs a resumable crop job in the pen until it ends on its own; after a kill it waits for memory and goes on (§7.12) |
| `mem_governor.py` | the crop jobs' worker count by free memory: closes idle browsers first, then fewer workers (§7.12) |
| `phone_keepalive.py` | logs in + NOOP every 2 min so the phone's FTP app never goes idle and sleeps (owner 2026-10-12: «the phone said it will go into sleep mode for lack of use»); follows the address; `setsid nohup python3 scripts/phone_keepalive.py >> logs/phone-keepalive.log 2>&1 &` — relaunch after a laptop restart |
| `resources_report.sh` | a few lines every 5 min (load, memory, disk, temperature, battery, top processes, phone up/away, crop batch progress) printed into a terminal the owner has open: `setsid nohup scripts/resources_report.sh /dev/pts/N &`; stops when that terminal closes |
| `reporter_follow.sh` | keeps resources_report.sh printing in whatever GNOME Terminal the owner has open (checks every 30 s); `setsid nohup scripts/reporter_follow.sh >/dev/null 2>&1 &` — relaunch after a restart |
| `open_index.sh` | opens `site/00 - الفهرس العام.html` in Brave on the laptop — only on request (refresh.sh calls it with `OPEN=1`) |
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
| `book_crop.py` | crop + levelling of scanned books (the method after the 2026-10-07 revert; full description in its docstring): ONE box size per file, placed on each page so its text block is centred (short pages take their full neighbours' place, odd pages are centred on their own content); stains, edge streaks, scanner edge noise, sheet edges, corner marks and dust stay outside, printed rules and frames inside; tilted pages levelled (the owner's verdicts in data/crop/owner-turns.tsv: a tilt — turned by it; 0 — never turned, fix F); second look at 1,000 px; the narrowest box that leaves ≤ 5 % of the pages whole (`plan()`). LOSSLESS: only the CropBox and, for tilted/moved pages, a «q … cm» / «Q» pair around the content change — image streams untouched. `analyse`, `apply`, `sheet`; `review_page()` builds the Arabic approval page. Needs numpy + scipy. Nothing reaches the phone without the owner's approval of a sample page |
| `crop_doubts_page.py` | the review page of a crop run: only the pages the method itself doubts (tilt undecided or untreated, page left whole, stain kept, stamp covered, page shown larger, sheet filled), up to 6 a book, kept by crop_batch.analyse for every book (owner 2026-10-18), and every page the owner pointed at in an earlier review with his words (crop_batch.owner_pages ← data/crop/owner-pages.tsv, owner-turns.tsv; add each new remark there) → site/crop-doubts.html (report «crop-doubts») |
| `crop_redo.py` | the crop of books cropped by an earlier book_crop, done again with the method as it is now (owner 2026-10-15): the original bytes (the logged crop's MD5), the new file uploaded beside the old as «.redo», checked, swapped in, checked; logged, resumable (`data/crop/redo-done.tsv`); a lost connection resumes the upload where it stopped, a phone away pauses the run until it answers (2026-10-29; `scratch/crop-fixes-2026-10-29/redo_upload_test.py` drops the connection at every step against a fake phone). `--list-all OUT`, `LIST BATCH [--workers N] [--dry]`; run it through `run_resumable.sh` in the pen |
| `drop_pages.py` | drops the blank pages / outer cover that put the file's numbering out of step with the print (§3.5), reversibly |
| `crop_fixes_page.py`, `crop_minitest.py` | the crop-fixes review page (verdicts in `data/crop/fixes-verdicts.tsv`, rounds, closed items leave it); the quick bench: each marked page ±20 pages of the owner's marked books through book_crop |
| `crop_regress.py` | the regression check of book_crop.py: every page the method once got wrong or the owner pointed at (`data/improve/crop-regression.tsv`: path, page, check, expected, note — checks turn, level, skew (a turn looked at by eye and measured, X±T°), cropped, cover, figures_in, scale1, parity, xcentre, ycentre, centred, in/out) and, on whole books, no page left tilted after turning; the books fetched once into `~/.cache/phone-library/crop-regress/` (a cropped book's original bytes), recipes cached per (book, book_crop md5). Run as a unit in `crop.slice` through a `scratch/regress_*.sh` one-off (key books first, crash = run again), then `crop_recipe_diff.py`; exit 1 on any FAIL. Never edit it, the cases or book_crop.py while a run is on (its check phase reads them) |
| `crop_recipe_diff.py`, `crop_diff_sheets.py` | after a regression run: every page whose turn, box, shown part, scale, move or kind changed between two book_crop versions (`OLDMD5 NEWMD5`), with the flag that explains it (owner turn, level first, folio stain, second look, cover print … or OTHER — each OTHER explained before the pilot/redo); the changed pages drawn old \| new as the reader sees them (`OLDMD5 NEWMD5 OUTDIR`) — look at every one (2026-10-26: the diff alone passed a moved box over a scan line) |
| `turner_check.py` | proof that book_crop's Turner (one turned copy per page, the speed-up) draws every view exactly as a fresh copy: byte-for-byte renders on the regression's books (`STEP [HASH …]`, exit 1 on any difference). Run it after a PyMuPDF/MuPDF upgrade or a change to Turner (2026-10-26: the first Turner was not exact on pages whose image the CropBox cuts) |
| `same_scan.py` | are two phone files the same scan? identical raw image streams page by page (`--sets "A1\|A2" "B1"` for copies split differently: pages of each set missing from the other) — proof for the duplicate-editions rule |
| `excerpt.py` | citations («book | volume | pages») → one bookmarked PDF for the phone, or Brave tabs at the right pages |
| `name_compose.py`, `names_from_reading.py`, `title_read_fix.py` | names under §4 (no parentheses/commas/«ط»/«=»; city after the publisher; year from the cover or old prints; printed roles; one shared part per set; ≤ 240 bytes); a title-page reading → its name; field corrections of earlier readings («n \| field=value») |
| `read_status.py`, `auto_check.py` | which books were already read by eye (→ data/names/read-status.tsv); the OCR/text-layer check of every unread book (→ data/names/auto-check.tsv) |
| `title_sheets.py`, `title_read_add.py`, `pages_sheet.py` | reading sheets of the first pages (+ the Shamela/Waqfeya candidates by title); recording a reading («n \| verdict \| title \| author \| editor \| publisher \| city \| year \| kind \| section \| note» → data/names/title-read.tsv; a later row for the same n supersedes); any page range of a PDF as one sheet (reading further) |
| `report_unreadable.py`, `review_server.py` | books whose name cannot be read from the book itself, appended one by one with a local copy (data/names/copies/, not in git) → site/names-unreadable.html; a 127.0.0.1 server so the owner checks and comments there (→ data/names/review-comments.jsonl; read those comments) |
| `plan_review_page.py`, `owner_decisions_page.py` | a rename plan as a review page (old → new, earlier proposals and comments with `--prev`; several applied plans on one page, rows «NNN:k»); the owner's open decisions from data/names/owner-actions.tsv in one page (site/decisions.html, report «decisions») |
| `doubts_page.py`, `review_on_demand_x.py` | what the agent is still unsure about as one page (data/review/<report>.tsv: sections, path, why, first-page images → site/<report>.html); the owner types **x** in a row's box to have the file fetched from the phone and opened in Brave — `review_on_demand_x.py` watches the comments for plan pages and these lists (run it as a user unit: `systemd-run --user --unit=review-x-opener …`, never from the VS Code shell) |
| `find_on_archive.py` | other archive.org uploads of books whose Waqfeya items went dark (candidates to read before adding) |

Only reusable tools live in `scripts/`. A one-off generator goes in `scratch/`; the plan or queue it writes is the
record.
**Never rerun a `scratch/` script or a plan that already ran** (2026-10-08: another agent relaunched the finished one-off
`scratch/restore_recompressed_224.py`; its second substitution set the 19 restored originals aside and deleted them —
fetched again by queue 247). Before launching anything, read `HANDOFF.md` and the tail of `data/changes/changes.tsv`:
if the plan name is already there, it is done. Only one agent works on the phone at a time. Safeguards since then:
`apply_plan.py` exits 1 when any move fails (callers stop before the next step) and `fix_at_scale.substitute` skips a
file whose improved copy is not in `index-now.tsv`. Nothing goes in the repo root. Removed one-offs (2026-10-05) are in git history at commit `0e64d80`.

