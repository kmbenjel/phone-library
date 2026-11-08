# Expanding the library

Moved verbatim from AGENTS.md (2026-10-28) to keep that guide short; AGENTS.md points here. Section numbers are the old ones (code comments cite them).

## 5. Expanding the library

1. Pick candidates from `site/03 - توصيات التوسعة.html` (or `reports/03 - توصيات التوسعة.md`). Each lists the Waqfeya
   page and the archive.org item.
2. Check it is not already present: search `data/catalog.tsv` by normalized title and check exact sizes
   in `data/phone/provenance.tsv`.
3. Download from archive.org (`https://archive.org/download/<id>/<file>`), name it per §4, upload
   with `rclone copyto <local> "phone:Books/<category>/<folder>/<file>"`.
4. Re-index and rebuild the indexes (rule 5). Add the new book's source to the WORKLOG line.

