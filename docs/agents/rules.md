# Rules — full text

Moved verbatim from AGENTS.md (2026-10-28) to keep that guide short; AGENTS.md points here. Section numbers are the old ones (code comments cite them).

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

