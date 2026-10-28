# Naming and sections — full text

Moved verbatim from AGENTS.md (2026-10-28) to keep that guide short; AGENTS.md points here. Section numbers are the old ones (code comments cite them).

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

