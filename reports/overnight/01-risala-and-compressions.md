# مجلة الرسالة and the three compressions (2026-10-05)

## What the phone has now
The 45 Risala files (issues 1–1123 + indexes) are the 10-03 Ghostscript re-compression of the RetroNews (BnF) scan
from archive.org item `08-01-208-183` («AL-Ressalah - الرسالة كاملة + الفهارس»): 11.6 GB → 7.1 GB.
The original is NOT lost for good: the same files are still on archive.org (exact names/sizes in data/phone/provenance.tsv).

## Copies compared (issue 26, 1 Jan 1934, same article page, same zoom)
| Copy | Source | Pixels / colour | Per issue | Readability |
|---|---|---|---|---|
| Original (lost locally) | RetroNews/BnF via `08-01-208-183` | ~900 px wide, colour JPEG tiles (141 ppi) | ~13 MB | sharp; yellowed paper; «RETRO NEWS» stamp on every page |
| **Current (compressed)** | same, gs → gray | same pixels, gray JPEG | ~6.3 MB | **identical to the original for reading** (the 150-dpi cap was above the source's 141 ppi, so no detail was lost — only colour) |
| Bibliotheca Alexandrina | `AAlexandrina-2305xx` (IMA microfilm) | 1200 px, 16-level gray | ~6 MB | worst: microfilm grain, speckle, low contrast |
| Sakhrit (ارشيف المجلات) | `arrissalah19xx` per-year items (also re-uploaded as `58_20260917`) | 1760 px, 1-bit JBIG2 | ~0.9 MB | clean, tight crop, no stamp; strokes thinner (bitonal); one file per issue with its date |

Verdict: no better copy exists than what the phone now holds. The compression cost nothing visible. Keep it.
The Sakhrit set is the only interesting alternative: ~1 GB for the whole run instead of 7.1 GB, one file per issue
(fast to reach an issue by number/date), cleaner pages, but thinner strokes. Worth it only if storage becomes tight,
or as a light per-issue companion. Not downloaded (not better in readability).

## The other two compressions (done 10-03, local ~/Books; Kashshaf also uploaded to the phone 10-04)
| Rank | Book | Before → after | Result | Notes |
|---|---|---|---|---|
| 1 | مجلة الرسالة | 11.6 → 7.1 GB (61%) | lossless for reading | source resolution was below the target |
| 2 | جامع البيان (ت شاكر، دار المعارف 1958), 13 vols, local only | 3.8 → 1.7 GB (44%) | very readable, 200-dpi gray | clean modern type; show-through from the back page slightly visible. NOTE: the upload log called it «ت التركي - هجر»; the pages (numbered آثار ١٤٥٢… in vol 2, p. 296) are Shakir's edition — the 10-04 folder rename to Shakir is right. The phone's Tabari is a different edition (Turki/Hajar, ~13 MB/vol). |
| 3 | الكشاف (دار المعرفة), 4 vols, local + phone | 1.58 → 0.75 GB (47%) | readable, 200-dpi gray | small vocalised type and marginal notes are the most sensitive to further compression |

Thoughts: all three compressions were sound (gray, 150–200 dpi, JPEG). But Tabari/Kashshaf are still heavy
(~125–200 MB per volume, 130–190 KB per page) compared with the other editions on the phone (13–19 MB per volume).
A bitonal 300-dpi version (CCITT G4/JBIG2, ~25–40 KB/page) would bring them to ~20–30 MB per volume with the same
legibility for printed text — a candidate for `Books-نسخ-محسنة/` after a visual check.
