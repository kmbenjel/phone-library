# Phone Library — guide for AI agents (and humans)

This workspace manages a large Arabic PDF library on an Android phone: `Books/` on the phone's
internal storage, reached over FTP. The laptop keeps the scripts, the source catalogs and the
change log and, for now, the indexes (`site/`); the phone keeps the books. The indexes go to the phone
(`Books/فهارس الويب/`) only when the owner asks.

Read this file first. Keep it current when you change a convention. It holds what most tasks need; the full
text of each section is in `docs/agents/` (open the one your task touches):

| File | Holds |
|------|-------|
| `docs/agents/where.md` | §1 in full: every data file and its source |
| `docs/agents/phone.md` | §2 in full: the phone's address history, the FTP login, rclone mount |
| `docs/agents/rules.md` | §3 in full: deletion and duplicate editions, labels, downloads, page numbering |
| `docs/agents/naming.md` | §4 and §4b in full: every naming rule with the owner's examples, sections |
| `docs/agents/expanding.md` | §5: adding books from the recommendations |
| `docs/agents/scripts.md` | §6: the table of every script in `scripts/` |
| `docs/agents/concurrency.md` | §7 in full: downloads, phone connections, network pacing, memory pen |

## 1. Where things are (full table: `docs/agents/where.md`)

| What | Where |
|------|-------|
| Books (source of truth) | phone `Books/<category>/<book folder>/<file>.pdf` |
| Indexes | laptop `site/00 - الفهرس العام.html` (one file, reports as tabs) + `reports/*.md`; online at https://benjelloun.dev/library (repo `kmbenjel/library`, clone `~/projects/library-site`, updated by `scripts/publish_web.sh` at the end of `refresh.sh`); on the phone `Books/فهارس الويب/` only when the owner asks |
| Workspace | laptop `~/projects/phone-library/` (git; a post-commit hook pushes to the private `kmbenjel/phone-library`; `site/` not tracked) |
| Work log / state | `WORKLOG.md`, `HANDOFF.md` |
| Every move/rename ever applied | `data/changes/changes.tsv` (time, action, from, to, reason, plan) |
| Plans | `plans/NNN-name.tsv` |
| Catalog | `data/catalog.json` / `.tsv`; phone index `data/phone/index-now.tsv` |
| Source catalogs | Shamela `data/shamela/` (local `master.db`, read-only), Waqfeya `data/waqfeya/`, archive.org `data/archive/` |
| Provenance / mappings | `data/phone/provenance.tsv`, `data/mappings/` |

## 2. Connecting to the phone

- FTP on port `2221`. Address reserved in the router: `192.168.11.100`; `scripts/phone_host.py` tries the known
  addresses, then scans the /24 (`PHONE_HOST=<ip>` overrides). rclone remote `phone:` (library `phone:Books`).
- Login: every script uses `phone_host.login(ftp)`; the user name and password live only in
  `~/.config/phone-library/ftp.env` and rclone's config — NEVER write them in this repo (it is pushed and copied to the phone).
- Moves and renames are server-side (RNFR/RNTO), instant. FTP has no checksums: duplicates are proven by size +
  64 KB samples (`dup_check.py`, `verify_dups_deep.py`). Details and the address history: `docs/agents/phone.md`.

## 3. Rules (full text: `docs/agents/rules.md`)

1. **Deleting:** verified duplicates (same size + identical 64 KB samples at start, 25/50/75 %, end) may be deleted
   without asking. Same-edition copies: keep the best (complete > whole pages > resolution > text layer > known
   source), delete the rest. Different editions stay. A volume holding several books is never split.
2. **Every change goes through a plan** (`plans/NNN-*.tsv`: `from<TAB>to<TAB>reason`) applied with
   `scripts/apply_plan.py` — it APPLIES by default; preview with `--dry-run`. Undo: `apply_plan.py --undo NNN-name`.
3. **Names come from evidence, not guesses** (title page, exact-size source file). If unsure, leave the name and
   list it under "needs review". A book is present when its work and author are on the phone, not on an exact
   string match. Labels on Waqfeya/archive.org can be wrong; one archive.org item often holds several books.
4. **Only real PDFs in `Books/`** (`%PDF` + opens; `check_magic.py`, `check_pdf_tail.py`). Any trustworthy upload may
   be a source. Never download a whole archive.org item for one book; run `additions_audit.py` after additions.
5. **Page numbers follow the printed ones:** a blank page or outer cover that breaks the match is dropped with
   `scripts/drop_pages.py` (reversible).
6. **After every edit:** `scripts/refresh.sh` (no `--publish`; it does not open Brave unless `OPEN=1`), then a WORKLOG line.

## 4. Naming (full text: `docs/agents/naming.md`)

- `<title> - <author> - ت <editor> - <publisher> <city>`; the same rule for folders, single files and volumes
  (`scripts/name_compose.py` builds it). Single-volume books are plain files in the category folder; folders only for
  multi-file works. Volumes: `NN - <shared name>.pdf`, `00` for front matter, indexes after the last volume (never 99).
- **No parentheses, no commas, no «ط», no «=»** anywhere. Nothing is shortened when it fits in 240 bytes.
- No `\ / : * ? " < > |`, single spaces, ≤ 240 bytes per name. A plan's «from» must be the phone's own bytes
  (names are not all NFC).
- Owner corrections: `data/names/name-override.tsv`, `data/names/owner-actions.tsv`.

## 4b. Sections

- Only the 40 Shamela categories. Any other folder is an error: move its books into a Shamela category, remove it.
  World literature lives in `الأدب/أدب عالمي`; modern science and education go in `الطب` or `علوم أخرى`.
- **Protected folders, never deleted, moved or emptied:** `Books/فهارس الويب/` and the special folders in
  `scripts/special_dirs.py` (`نسخ محسنة للاستبدال`, `نسخ مستبعدة`).

## 5. Expanding the library

See `docs/agents/expanding.md`. Check the catalog and provenance before adding; every download goes through
`scripts/fetch_queue.py` (§7).

## 6. Scripts (all in `scripts/`; full table: `docs/agents/scripts.md`)

**One command after any edit:** `scripts/refresh.sh`. Most used: `apply_plan.py` (plans), `fetch_queue.py`
(downloads), `name_compose.py` (names), `name_audit.py` (§4 audit), `dup_check.py` / `verify_dups_deep.py`
(duplicates), `delete_files.py` (logged deletion), `phone_host.py` (address), `book_crop.py` (crops; owner approval first).

Only reusable tools live in `scripts/`; one-offs go in `scratch/`. **Never rerun a `scratch/` script or a plan that
already ran**: read `HANDOFF.md` and the tail of `data/changes/changes.tsv` first — if the plan name is there, it is
done. Only one agent works on the phone at a time. Nothing goes in the repo root.

## 7. Speed and concurrency (binding; full text: `docs/agents/concurrency.md`)

1. Every download goes through `scripts/fetch_queue.py`; never `curl` files one by one.
2. Internet downloads are parallel: `aria2c -x8 -s8 -k1M --continue`, 12 files at a time.
3. Phone: ≤ 3 FTP connections; all phone I/O holds `/tmp/phone-ftp.lock` (`flock`).
4. Keep git packed: if `git count-objects -vH` shows GBs loose, `nice git gc --prune=now`.
5. Staging ≤ `STAGE_GB` (6); delete each staged file after its upload.
6. Verify in parallel with downloads: size, `%PDF`, `%%EOF`, `pdfinfo`.
7. Independent tasks run in the background; a new request never cancels a running job.
8. Everything is resumable (`data/queue/<name>.done` / `.failed`).
9. **Never make the home network lag:** one bulk transfer at a time; pause bulk transfers while someone games;
   queues start after `scripts/wait_calm.py 10`; `NETPACE=0` only when the owner says so.
10. **Never build a phone path from a lookup that can come back empty:** `"phone:Books/${P:?empty path}"`; compare
    names NFC-normalised.
11. **Stopping a job:** `kill <pid>` from `pgrep -f "[n]ame"` in a separate command.
12. **Memory:** heavy jobs run as `systemd-run --user` units, ≤ 3 workers; crop jobs run in `crop.slice` under
    `mem_governor.py` with no `MemoryHigh` of their own. Never raise a unit's memory limit above the pen.
