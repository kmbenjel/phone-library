# Where things are — full table

Moved verbatim from AGENTS.md (2026-10-28) to keep that guide short; AGENTS.md points here. Section numbers are the old ones (code comments cite them).

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

