# Using the library: phone, computer, backup, citations (2026-10-05)

## 1. Reaching a book fast on the phone (Acrobat + Google Files)
- **Layout:** `Books/<one of the 40 Shamela sections>/<book>`. A multi-volume work is a folder named
  «title - author (edition)». Its files are `NN - short title (contents of the volume).pdf`, sorted 00, 01, 02…
  Single-volume books are becoming plain files, «short title - author (edition).pdf». That pass runs after the
  read-inside pass, because names come from the files themselves.
- **Google Files:** its search matches any word of a file or folder name, offline and instantly. That is why names
  carry title, author and edition, and why junk names (`mst1.pdf`, «… - - ط») are being replaced. Star the books you
  use daily (Files → Favourites); they open in two taps.
- **Acrobat:** «Recent» plus bookmarks inside a book. Searching *inside* a scan needs a text layer, which most scans
  lack. Adding an OCR layer to your most-used books (tesseract has Arabic) would make them searchable in Acrobat.
  It's worth doing for the 50–100 books you use most. Tell me which ones.
- **Reading comfort:** many scans waste 30–45 % of the screen on blank margins. The lossless crop (samples in
  `Books/نسخ محسنة للاستبدال/`) makes the text about 40 % larger at the same file size. If you like the samples,
  ~1,500 books can be cropped. The crop boxes are already computed while the files are being read.
- **The phone index (HTML):** it's one 22 MB page, heavy for a phone browser. When you want indexes on the phone, I
  suggest one light page per section, and the full page on the computer.

## 2. Browsing the phone library from the computer
- The FTP app on the phone (192.168.11.102:2221) must be running and the phone on the same Wi-Fi.
- Read-only mount: `rclone mount phone:Books ~/phone-books --read-only --daemon` → browse in the file manager, open
  PDFs directly. A web view: `rclone serve http phone:Books --addr 127.0.0.1:8081` → http://127.0.0.1:8081 in Brave.
- The local index (`site/00 - الفهرس العام.html`, opened in Brave after every change) lists every book with its
  phone path, edition notes and the comparisons with Shamela and Waqfeya.

## 3. Getting the library back on a new phone (or after losing this one)
- Size: 158.5 GB in 15,044 files. **64 % (102 GB, 10,540 files) are byte-identical to files on archive.org**, with
  their exact address and size recorded (`data/phone/provenance.tsv`). They can be re-downloaded by a script
  (verified by size and MD5) without any backup. Only **36 % (56 GB, 4,504 files)** need a real copy.
- Recommended:
  1. **Keep the manifest safe:** this git repository (names, sections, MD5 of every file, sources, change log).
     It is small. Copy it to Google Drive or a private GitHub repository.
  2. **Back up the 56 GB without a public source** to an external drive (USB 128–256 GB) or Google Drive (needs
     the 200 GB plan). Command: `rclone copy phone:Books <drive>/Books --files-from data/phone/no-public-source.txt`.
  3. **Restore on a new phone:** copy the drive back over USB-OTG or FTP. A restore script re-downloads the 102 GB
     from archive.org into the same paths, verifying each file's size and MD5.
- The laptop alone cannot hold a full copy (23 GB free).

## 4. «Open everything cited about خالد بن الوليد in the margins of سير أعلام النبلاء»
What exists now (`scripts/excerpt.py`):
- A list of citations, «book | volume | pages», for example `الطبقات الكبرى | 7 | 396`. Each book is resolved in the
  local library first, then on the phone.
- **Desktop:** `--open` opens every cited page in Brave tabs, one after another, at the right page.
- **Phone:** `--phone` builds one small PDF of all the cited pages, with a bookmark per citation, and drops it into
  the phone's `Download/مقتطفات/`. Acrobat opens it straight away.
- Printed page → PDF page: through the PDF's page labels or the page number printed on the page (text layer or
  OCR). Some scans were cropped without page numbers (the Risala edition of «سير أعلام النبلاء» on the laptop is
  one). For those, give PDF pages («p412») until the next step exists.

The next step, for a one-sentence request like yours:
1. Your local Shamela has the full text of «سير أعلام النبلاء», footnotes included, with printed page numbers
   (`~/.local/share/shamela/database/store`, a search index). Finding «خالد بن الوليد» there gives the biography's
   pages and the footnote references (e.g. «طبقات ابن سعد 4/252»).
2. Each reference is matched to a book on the phone by title and author (the catalogue) and to the right edition.
   Footnote references follow the editor's edition (the Risala apparatus cites specific prints), so the editions
   report matters here too.
3. Printed page → PDF page: the same Shamela text matched against an OCR of a few candidate pages gives each
   volume's page offset once. It's then cached.
4. Then `excerpt.py` opens them on the desktop or builds the PDF for the phone.
Reading Shamela's index needs a small Lucene reader. That's a self-contained job for a later session.

## 5. Decisions waiting for you (nothing has been done about these)
- **Editions:** report 05 (in the index) lists every work held in several editions or scans, with completeness,
  scan quality read from the files, and sourced notes on the best editions. Tell me which editions to purge.
- **Same edition, other scan:** 435 copies are a second scan of an edition already kept. Once the read-inside pass
  ends, I'll mark the best scan of each. The weaker ones go to `Books/نسخ مستبعدة/` only when you say so.
- **Improved copies:** look at `Books/نسخ محسنة للاستبدال/` (cropped, split and complete copies) and say «استبدل» to
  replace the originals.
- **The 7 almtoon.com متون:** their complete copies (cut at 1 MiB on the phone) are being fetched from the Wayback
  Machine into the same folder.
