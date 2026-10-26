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
| Workspace (scripts, data, reports) | laptop `~/projects/phone-library/` (git repo; backed up to the private GitHub repo `kmbenjel/phone-library` — a post-commit hook pushes every commit, owner 2026-10-08; `site/` is not tracked: its pages are versioned in `kmbenjel/library`) |
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

- The phone runs an FTP server app on port `2221`, anonymous login. The IP is DHCP; known addresses: `192.168.11.100` — reserved for the phone in the router by the owner (2026-10-17; before that it wandered .100/.102/.104/.109 with a randomized MAC), `192.168.11.104` (2026-10-17 evening), `192.168.11.102` (2026-10-11 evening: it switched .100 ↔ .102 several times;
  owner: «keep up with 102»; a DHCP reservation in the router would stop it),
  `192.168.11.103` (2026-10-05 noon), `192.168.11.102` (2026-10-04 and again 2026-10-05 afternoon) and `192.168.11.100` (before). The scripts try them, then scan the /24 for port 2221 (`phone_host.find()`)
  (`scripts/phone_host.py`; `PHONE_HOST=<ip>` overrides). If neither answers, find it with `ip neigh` and
  `nc -z <ip> 2221`, add it to the top of `CANDIDATES` in `phone_host.py` and run
  `rclone config update phone host <ip>` (rclone takes one fixed host).
- **Login (owner 2026-10-18):** the FTP app has an account. Its user name and password are NEVER written in this repo (it is pushed
  to GitHub and this guide is copied to the phone): they live in `~/.config/phone-library/ftp.env` (lines `USER=…` and `PASS=…`, mode
  600, written by the owner) and in rclone's own config for the remote `phone:`. Every script logs in through
  `phone_host.login(ftp)` (`phone_host.creds()`); without that file it logs in anonymously. Ask the owner if you need it.
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
   (`scripts/fetch_replacements.py` does). Waqfeya and Shamela are references among others, not the only sources (owner 2026-10-10: «not a rule — I only started with Waqfeya at the very beginning»): a missing or incomplete book may come from any trustworthy upload (archive.org and others), its title and imprint pages read before it is named and added.
   **Never download a whole archive.org item for one book:** items often bundle dozens of books. Take only the
   files the Waqfeya record links (its `links`), then run `scripts/additions_audit.py` — it keeps a file only if
   the record links it (or it follows the record's own pattern: link typos, `NN_IDp` prefaces), drops other books
   of the bundle, byte-identical copies of files already in the library, and double uploads.
5. **The file's page numbers follow the printed ones** (owner 2026-10-18: «عند وجود صفحة فارغة أو الغلاف الخارجي وذلك يخالف
   بين الترقيمين تحذف الصفحة»; «يتوافق الترقيم ولا يضيع شيء»): a blank page or the outer cover that puts the PDF's numbering
   out of step with the print is dropped — `scripts/drop_pages.py` (an incremental update: the original bytes stay, undo =
   truncate; a non-blank page only with `--cover`), logged as «pages». Check the printed number of a few text pages after.
6. After every edit: run `scripts/refresh.sh` (re-index → catalog → reports → site), WITHOUT `--publish` — the
   indexes stay on the laptop until the owner asks for them on the phone. It does NOT open the index in Brave
   (owner 2026-10-25: «don't auto open indexes» — every refresh left another 41 MB tab, Brave reached 7 GB); `OPEN=1
   scripts/refresh.sh` or `scripts/open_index.sh` opens it when he asks. Do this after every edit, also when only the
   indexes changed. Then add a WORKLOG line.

## 4. Naming conventions

Layout: `Books/<category>/<book folder>/<files>` or `Books/<category>/<file>.pdf`.
Single-volume books are stored as plain files in the category folder without their own subfolder. Folders are used only for multi-file works.

**Category** — All Shamela categories must be present and contain books. It is strictly forbidden to create any category that can fit into one of Shamela's categories.

**Names: one rule for folders, single files and volumes** (owner, 2026-10-10; built by `scripts/name_compose.py`)
- **Nothing is shortened when the whole name fits (≤ 240 bytes).** Every piece of information we have is in it: the
  full title, the author, the editor(s), the publisher — taken from evidence (the name itself, the exact-size Waqfeya
  record when its title is the same book, the title page).
- **No parentheses and no commas anywhere** (owner: «avoid ()», «تبقي على الأقواس», «استغن عن الفواصل في كل العناوين»):
  the parts follow one another with « - »; the editor marked by «ت», a translator by «ترجمة», the publisher by nothing
  (owner: no «ط»); no «=» — an alternative title joins with «أو».
  After the owner's review of plan 313 (2026-10-10 night, corrected 2026-10-11): the **publisher as printed** and the
  **city** after it with a space only («مكتبة المعارف الرباط», «وزارة الأوقاف والشؤون الإسلامية المغرب»); a printed form
  such as «مطبعة حجازي بالقاهرة» is copied as it is, but the city is NOT joined with «بـ» as a rule; a city without a
  publisher stands alone; the **year** when it has a special useful meaning (the owner's convention: an old print ≤ 1950 / ≤ 1370 هـ, a
  journal offprint's issue) and, added to that (not a limit), whenever it is on the main cover (page 1's text/OCR, or «[cover-year]» in the reading): «المطبعة السلفية بمصر 1341 هـ»; **people's names in full** or by their famous kunya/laqab, shortened only
  when a long title forces it; the editor's **printed role** when it is not plain tahqiq («صححه وعلق عليه فلان», «تنسيق فلان»,
  «قدم لها فلان») — also a tahqiq with its own wording («قرأه وشرحه» as محمود شاكر writes it); plain «تحقيق/حققه» → «ت»; never a «ويليه», «في» or subject the title page does not print; the book's own author before the
  authors of companion texts; a collection of poems names all of them. Corrections by hand: data/names/name-override.tsv;
  the owner's remove/replace/add decisions: data/names/owner-actions.tsv (held out of rename plans).
  `<title> - <author> - ت <editor> - <publisher> <city>` («… - ت محمد حجي - دار الغرب الإسلامي بيروت»,
  «الجمع والفرق أو كتاب الفروق - الجويني - …»). A title's
  own «(مخطوط)», «(رسالة ماجستير)» go after the edition («… - مخطوط»); a one- or two-word aside is written inline
  («ابن رشد (الجد)» → «ابن رشد الجد»); a longer aside becomes a «، …» subtitle.
- **Only when the name is too long**, the combination that keeps the most information is chosen. What gives way, first
  to last: the year, the city; a subtitle that came from parentheses; the publisher (owner: when the whole title and the publisher cannot
  both fit, the publisher goes); editors after the second; the words after the title's head — joined titles keep their
  heads: «جمع الجوامع في كذا كذا ويليه همع الهوامع في كذا كذا» → «جمع الجوامع ويليه همع الهوامع»; the later joined titles
  («ويليه، ومعه، وبهامشه، =»); the first editor. A title is never cut inside a word or a name; no `...`.

**Book folder** (for multi-file works): `<title> - <author> - <edition>`
- `<author>`: the commonly used name (e.g. `ابن قدامة`, `الإمام الغزالي`); not repeated when the title already holds it
  («تفسير ابن أبي حاتم الرازي»). Omit for periodicals/series.
- `<edition>`: `ت <editor> و<editor> - <publisher>` or `<publisher>`; omit what is unknown.
- Collections: `مؤلفات <author> - <publisher>`; periodicals: `مجلة <name> - <publisher>`; series: `سلسلة <name> - <publisher>`.
- Different editions of the same book are separate folders that differ only in their edition part.

**Single file** (no folder): `<title> - <author> - <edition>.pdf` — the same rule as a folder.

**Files**
- Independent books collected in one folder (a series such as «سلسلة أعلام المسلمين», «مؤلفات فلان») carry **no
  number**: each file is `<its own title>.pdf`. Only a series whose issues are really numbered keeps the issue
  number (e.g. «عالم المعرفة»: `003 - التفكير العلمي.pdf`). Never "01 -" in front of every item.
- Indexes (الفهارس) take the number after the last volume, never 99. For a periodical they take `00`.
- A companion that is not a volume (نسخة أخرى، صور المخطوطات، ملحق، the whole book in one file) has no number.
- Multi-volume: `NN - <title> - <author> - ت <editor> - <publisher>.pdf` — no label for the range of contents (owner:
  «إحياء الموات - أمهات الأولاد» not kept); a label only when it says what the file IS: `- الواجهة`, `- المقدمة`,
  `- الفهارس`, `- ملحق`, `- صور المخطوطات` (name_compose.keep_label); a part with its own printed title keeps it as
  part of its title («أعمال الأعلام - القسم الثالث تاريخ المغرب العربي»). Every volume carries all
  the folder's information (owner 2026-10-10), the same shared part in every volume of the set (name_compose.volumes:
  sized for the longest label, shortened by the rule above only when needed), `NN` = the volume number, zero-padded to two digits (`01, 02`) or more for large collections. Volume
  numbers are never repeated. `00` is reserved for front matter and may appear more than once:
  `00 - <title> - الواجهة.pdf` (cover/title pages), `00 - <title> - المقدمة.pdf`. A preface belonging to one volume keeps
  that volume's number with `- المقدمة`. The label describes the contents (`- الطهارة - الصلاة`, `- الفهارس`); a volume
  without a label is `NN - <title>.pdf`.
- Periodicals are named by what the file really contains, read from the source or the cover, labels without parentheses:
  `الأعداد 0026-0051 - السنة 2، 1934 - النصف الأول.pdf` (مجلة الرسالة), `المجلد 42 - الجزء الثاني - 1998.pdf`
  (مجلة معهد المخطوطات), `فهارس المجلة - الجزء 6 - المجلدات 51-60.pdf` (مجلة مجمع اللغة العربية بدمشق).
- Items inside a collection/series folder: `<title> - <author>.pdf` or `NNN - <title>.pdf` for numbered issues.
- Names on the phone are not all in NFC (diacritics in another order): a plan's «from» must be the phone's own bytes
  (from the index), never a normalised copy — else the emptied folder is left behind (plan 310).

**Characters** (the files are also copied to FAT/Windows sometimes):
- no `\ / : * ? " < > |`: `ت: فلان` → `ت فلان`, `?` → `؟`, `"` → `«»`
- no `_` used as a stand-in for `:` or `/`, no `_alt`, no `(نسخة ثانية)` (that is a duplicate → quarantine)
- single spaces, no leading/trailing spaces or dots; ≤ 240 bytes per name (≈ 118 Arabic letters). Why: the phone's file
  system allows 255 bytes per name (UTF-8; an Arabic letter takes 2); ~15 bytes are kept for temporary upload suffixes.
  Any length within that is fine when it is useful (owner 2026-10-10). Copies to Windows: Explorer limits the whole path to
  ~260 characters unless long paths are enabled.

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
| `book_crop.py` | crop + levelling of scanned books (the method after the 2026-10-07 revert; full description in its docstring): ONE box size per file, placed on each page so its text block is centred (short pages take their full neighbours' place, odd pages are centred on their own content); stains, edge streaks, scanner edge noise, sheet edges, corner marks and dust stay outside, printed rules and frames inside; tilted pages levelled; second look at 1,000 px; the narrowest box that leaves ≤ 5 % of the pages whole (`plan()`). LOSSLESS: only the CropBox and, for tilted/moved pages, a «q … cm» / «Q» pair around the content change — image streams untouched. `analyse`, `apply`, `sheet`; `review_page()` builds the Arabic approval page. Needs numpy + scipy. Nothing reaches the phone without the owner's approval of a sample page |
| `crop_doubts_page.py` | the review page of a crop run: only the pages the method itself doubts (tilt undecided or untreated, page left whole, stain kept, stamp covered, page shown larger, sheet filled), up to 6 a book, kept by crop_batch.analyse for every book (owner 2026-10-18), and every page the owner pointed at in an earlier review with his words (crop_batch.owner_pages ← data/crop/owner-pages.tsv, owner-turns.tsv; add each new remark there) → site/crop-doubts.html (report «crop-doubts») |
| `drop_pages.py` | drops the blank pages / outer cover that put the file's numbering out of step with the print (§3.5), reversibly |
| `crop_fixes_page.py`, `crop_minitest.py` | the crop-fixes review page (verdicts in `data/crop/fixes-verdicts.tsv`, rounds, closed items leave it); the quick bench: each marked page ±20 pages of the owner's marked books through book_crop |
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
10. **Never build a phone path from a lookup that can come back empty.** Write `"phone:Books/${P:?empty path}"` (or check in
   Python), never `"phone:Books/$P"`: on 2026-10-08 a `grep` missed a name (different Unicode order of «لَّ») and
   `rclone copyto "phone:Books/"` copied the whole library (9.3 GB, 1,020 files) to the laptop before it was stopped. Look up
   names with Unicode-normalised comparison (`unicodedata.normalize('NFC', …)`).
12. **Memory: never let a job take the desktop down** (2026-10-17 03:38: the crop baseline ran 6 workers on a large book, memory ran
   out and systemd-oomd closed the owner's whole GNOME session — every job and his desktop with it). Heavy jobs (book_crop analyses,
   OCR, inspection) run as capped user services, ≤ 3 workers: `systemd-run --user --unit=NAME --property=MemoryHigh=3G
   --property=MemoryMax=4G --nice=10 --working-directory=$PWD CMD` (linger is on, so they survive a session end too).
   **More workers, governed (owner 2026-10-18):** the crop jobs (crop_redo, crop_batch, crop_regress) take as many books at
   once as `data/crop/workers` says (read before each book), set by `scripts/mem_governor.py` (unit `mem-governor`): up to 6;
   free memory < 2 GB → it closes Brave/Chrome the normal way if nobody has touched the laptop for 10 min and no sound plays,
   then, if still short, one worker fewer; < 1 GB or memory pressure ≥ 20 % → the EMERGENCY BRAKE: the largest crop process is
   killed at once, then two workers fewer; > 4.5 GB for 10 min → one more. **A book starts only with ≥ 3 GB free**
   (`crop_batch.room()`, in every crop tool, the bench included). **Every crop job runs in ONE memory pen, `crop.slice`**
   (`systemd-run --user --slice=crop.slice --unit=NAME --nice=10 --working-directory=$PWD scripts/run_resumable.sh LOG -- CMD`,
   no memory properties of its own): the governor sizes the pen every few seconds from what the owner uses (free memory + what the
   pen holds − 2.5 GB, 2–10 GB) — when he opens more (browsers, VS Code, Antigravity), the jobs are reclaimed and swapped, never
   his session; the worker count follows the pen (2.2 GB per book, 1.5 GB kept for the job's own process; no climb for 20 minutes after a brake — owner: «reduce the workers at that point for a while»). `run_resumable.sh` reruns a killed job once memory is back.
   Never a per-unit `MemoryHigh` above the pen — a unit throttled at a high MemoryHigh reclaims
   hard, the user slice's memory pressure rises and systemd-oomd kills by reclaim, GNOME Shell first: on 2026-10-18 03:05 a
   bench with MemoryHigh=6G (raised by the agent) and 3 analyses beside the owner's browsers closed his session again.
11. **Stopping a job:** `kill <pid>` with the PID from `pgrep -f "[n]ame"` in a separate command — a `pkill -f name`
   in the same command line that restarts the job kills the shell itself.
