# Max-effort subagent review of the 2026-11-06 crop changes (book_crop.py c25509b → 002b4f3ec1)

Read-only review by a general-purpose subagent at effort max, 2026-11-06 22:46–23:14 UTC (owner 22:46: «use subagents
with the recommended efforts»). Findings only: NOTHING applied — every fix goes through the bench (crop_regress) + a turn
audit, then a partial redo of the affected books (HANDOFF). Its scratch scripts and renders were in
/tmp/claude-1000/-home-k-projects-phone-library/review-max/ (gone at a reboot). The report, verbatim:

---

# Review of `scripts/book_crop.py` c25509b → HEAD (002b4f3ec1): hunks 1–4 in `decide()` / `frames()`

Evidence base: the regression cache — 43 books with both a baseline (`511f6d7a5e`) and new-method (`f3ed545be4`) recipe, 2 new-only books (`01435c38ee4b` الإعلام بنوازل الأحكام, `b875c883f700` الأغاني ج 8), and the 6 books without an `f3ed545be4` recipe (incl. the band-heavy خريدة القصر `064846139175`) read through their `04a1a53259` recipe, whose `decide()`/`frames()` equal HEAD's (only the withdrawn tilt experiments differ).

Where the hunks fired in the new recipes: hunk 2 (`band_print`) 1,014 groups + 715 in the six-book set; hunk 1 (`folio_specks`) 570 + 38; hunk 3 changed no book's `size` (H identical in every comparable book where hunks 1/2 did not move boxes); hunk 4 fired once in 18,579 bench pages (`fc0fb7a344bb` p354, a magazine back cover read as text).

Colour key of the renders: red = crop, blue dashed = `show`, green = text block (dashed = baseline), teal = core, magenta = `band_print`, pink = `folio_specks`, blue dotted = folio, purple = baseline edge marks, olive = specks.

---

## Ranked findings

### 1. Hunk 4 — a cover-like TEXT page is cut out of its own box, and the "line of print" guard checks the wrong thing — CONFIRMED (mechanism), severity HIGH by the owner's rule ("nothing of the text may ever be cut"), exposure low

`scripts/book_crop.py:3390–3407`.

Condition. `cover_like` needs a first-2/last-4 *text* page whose `crop` covers ≥ 80 % of the sheet and whose proportion differs from the book's by ≤ 8 %. A text page's crop is the book's W×H box, so the proportion differs only when the crop was clipped by the sheet. In a clean-margin book that happens through `enlarged` (`decide()` 2752–2760): `sc` is capped at `smax`; when `bw/W` wins (`sc = bw/W`, line 2755) the enlarged box is exactly as wide as the page's box and taller than the sheet, the crop is clipped vertically, `cw/chh > A`, and `cover_window()` takes `d = (cw − chh·A)/2` from **each side of the box itself** — the box which, in a clean book, is `text ∪ notes ∪ figures` (line 2553).

Evidence. `fc0fb7a344bb` (الذخائر 01) p354/355: box `[7.2, 7.2, 505.1, 685.8]`, `enlarged` 1.226 (= bw/W), crop `[7.2, 0, 505.1, 734.4]`, `show` `[12.4, 0, 499.9, 734.4]` — 5.2 pt cut from each side of the box; the recorded `text` block (`[18.5, 39.0, 504.1, 621.2]`) and one of the two `figures` (`[359.4, 211.5, 505.1, 685.8]`) are not inside `show`. On this page the box edge is the torn-edge shadow of a magazine cover, so the result is right by eye — but the mechanism cuts whatever stands at the box edge. Render: `review-max/png/fc0fb7a344bb_p354_f3ed545be4.png`. Before this change the page was shown whole with blank bands (frames() 3410–3420), nothing cut.

The guard added in f6f3b78 (line 3403) reads `p.get('lines')`. `lines` is written exactly once, in `marks()` line 526, and holds **thin long marks** (rules, scan lines, dashed/dotted lines — lines 444–525), never lines of print; `verify()`'s `mk['lines']` (2835) is a different dict. So the guard cannot see a line of text, while any scan sliver or rule in the cut zone (a frame's side rule is in `lines`) blocks the cut — the opposite of the intent in the commit message ("a dense first or last text page whose lines reach the cut keeps its frame"). On p354 (193 `lines`) none lay in the cut zone, so HEAD cuts it too; "identical on 18,579 pages" only says the guard never triggers.

A real victim needs a clean book and a first-2/last-4 text page whose box is wider relative to W than the page is tall relative to H, by ≤ 8.7 % (a wide table/index at the end, a wide colophon). Not in the cache (PLAUSIBLE instance), but by construction the cut then removes up to 4 % of the table's outer columns per side.

Fix sketch (3402–3407): decide by the page's needed print, not by thin marks —
```python
mg = p.get('margin') or []
need_ = union([p['text']] + notes_of(mg, pw, ph) + figures_of(mg, pw, ph) + printed_groups(mg, pw, ph)) if p.get('text') else p['box']
if text_cut and not inside(need_, c2, 1.0):
    p['cover_like_kept'] = [round(v, 1) for v in c2]      # the cut would take print: shown whole, as before
else:
    if text_cut: p['cover_like'] = [round(v, 1) for v in c2]
    c = c2
```
Trade-off: a text block widened by junk at the sheet's edge (p354) then keeps its bands; the الفن ومذاهبه ص 1 case (a cover whose title is well inside) is still cut.

### 2. Hunk 2 — the size tests are applied to the group's bounding box, so a row of specks passes as a line of print — CONFIRMED, severity MEDIUM (small effect seen, larger possible)

`scripts/book_crop.py:2375–2397`, esp. 2395–2396.

Condition. `_lines()` groups edge marks by vertical overlap and tests `u = union(gr)`: height ≥ 0.6 % h, width ≥ 2 % w. Four 1-pt dots spread across the page make a `u` 335 × 4.5 pt and pass. No member is ever required to be letter-sized (contrast `printed_groups()` 1164–1181, which asks for two letter-sized members).

Evidence (members read from the baseline's `edge`/`specks`, move-adjusted — `members.py`): of 718 `band_print` groups on comparable pages, 89 have **no member ≥ 0.6 % h** (37 "dust rows", every member < 0.4 % h; 52 "small"), on 7 books. Most are the diacritics row of a real head/first line and change nothing (`99e85531fbc7` p110: text block already began there; `01435c38ee4b` p37, `5b214426d112` p90: dots of the first/last line, box moved ≤ 1.2 pt). But:
- `170f985fb5d3` (هذا هو علم البيولوجيا) p49: the six halftone dots of the grey box under the page number «48» (1–2 pt each) became the "foot line" `[375.0, 592.2, 390.6, 598.0]` and, being ≤ 8 % w with no folio on the page, the page's **folio** (line 2421) — the real number is 5 pt above, inside the text block. Crop moved 1 pt.
- `c63a21351cba` p206/239/359/363/465, `d20f1fe41833` p60: dust/small groups at the head moved the crop 1.4–2.8 pt.

Harm is bounded in the cache by the margins (≥ 5 % H), but the rule also extends `text`, `box` and `allowed` to the group, so a dotted scan edge or dust row at a steady height 0.3–3 % h above the usual text top (a tight scan) would widen the box and, at the foot, be made the folio. (No scanner band was pulled in anywhere: `allowed` changed on 0 of 1,031 pages where hunks 1/2 fired; on خريدة القصر neither hunk fired at all.)

Fix sketch (in `_lines()` after `u = union(gr)`):
```python
if not any(e[3] - e[1] >= 0.006 * h and e[2] - e[0] >= 0.003 * w for e in gr): continue   # a line of print holds a letter
```
and in the foot→folio step (2421) require the same letter-sized member (or reuse `printed_groups` on `gr`).

### 3. Hunk 2 — the "where the book prints its head" reference is nearly vacuous — CONFIRMED (statistically), severity MEDIUM-LOW

`scripts/book_crop.py:2403–2408` (the `ys.append(t_[k1])` branch).

Condition. A page contributes its text-block top as a head reference when `core.top − text.top ≥ 1 % h`. The core is the 2nd/98th percentile of the content ink (marks() 567–568), so on an ordinary page the core's top sits about half a line (≈ 1–1.5 % h) below the first line's top. The 1 % test is true on most pages of books with **no running head at all**, and `len(ref) ≥ need_` always holds.

Evidence: share of text pages giving a head reference — `2af978d37d97` 0.99 (folio found on 0 % of pages), `c63a21351cba` 1.00, `435bf8357444` 1.00, `5b214426d112` 0.99, `2b47002d18ab` 0.99; 33 of 43 books ≥ 0.80. The foot reference behaves alike (0.5–1.0). The test thus reduces to "an edge group within 3 % h above the usual text top", which is what lets finding 2's dust rows through. Nothing wrong was pulled in because of this alone in the cache: the 629 groups with a letter-sized member were sampled 30 times by eye — all running heads, first lines of tight scans, chapter titles or page numbers.

Fix sketch: count only real heads/number lines as references — `c_[1] − t_[1] ≥ 0.025 * h` (a head stands ≥ a line above the core), or only pages whose `folio` (marks() 608–617: a short group with a ≥ 1.2 % h gap) or an `L[j]` line of the same kind exists.

### 4. Hunk 1 — dust where the number should be becomes the number; the page's own folio is held to a stricter test than the candidates — CONFIRMED, severity LOW

`scripts/book_crop.py:2341–2366`.

(a) `same_rel` (2337) lets a group of specks ≤ 8 % × 2.5 % at the folio's offset from the text centre / core foot count as the page number; no letter-sized member is required (the motivating «- ٥ -» of فهرسة ابن خير ص 4 was grains). Evidence: `01435c38ee4b` p19 (a section title page): two dust specks 16 pt apart, `[224.5, 518.8, 240.8, 527.8]`, became the folio and were joined to the text block. Placement unaffected in effect (the specks lie where a number would be). The other firings sampled (14 by eye) are real page numbers under the text block that the baseline's crop cut (the owner's complaint on that book).

(b) `own` (2347) is confirmed by `same_place` only, while a candidate passes by `same_place or same_rel`; a page whose real folio was found by marks() but is shifted > 3 % on the sheet loses it to any speck/edge group passing by `same_rel` (overwrite at 2363). Four overwrites in the cache: `9b98ea8b9570` p111/p177 (old "folio" = a stray «==» in the margin, new = the real «١١١» — right), `9da5c530d977` p124/p214 (old = a word of the first line, new = the centred running head «معجم تيمور الكبير», which marks() reads as the "folio" on the other pages — consistent), `558b0f1096a9` p9 (an adjacent group of the same number). The asymmetry has not hurt, but it is one-directional by design.

Fix sketch: for a match passing only by `same_rel`, require a letter-sized member (as in finding 2); and test `own` with the same predicate as the candidates when the page's own folio is the one marks() read with a gap (it is print by construction): `own = at(p['folio']) if p.get('folio') else []`.

### 5. Hunk 3 — `Th` from "typical" pages: no effect in the cache; wrong on a book whose typical page is the short one — PLAUSIBLE, severity LOW

`scripts/book_crop.py:2463–2464`.

No effect: H identical old/new in every comparable book not moved by hunks 1/2; the books with `max_bh > 1.15 × median` (`0c32c1a4815b` 683.9 vs typical 590.2; `2b47002d18ab` 686.9 vs 625.0; `fc0fb7a344bb`, `68600214e7de`, `810908d4ed05`, `35fbe344b8c6`, `51cfa6854fda`) already had H held down by `fitH`/`ph`. The H changes seen (+35.7 `558b0f1096a9`, +16.9 `560169646f16`, +3.8 `8d7204a7003a`, +2.3 `9e4e95703bcd`, −6.7 `d20f1fe41833`) come from hunks 1/2 moving boxes (page numbers now inside the box; boxes re-centred), with no page lost to "whole".

Failure mode: a book with more short pages than full ones (a divan/anthology with wide leading, an index of short entries without a foot number, a book whose folio is found on few pages so the box ends at the last line) has a short median; every full page is > 1.15 × median, is excluded, and every full page is then shown shrunk (`crop None` → `frames()` scale < 1 in a non-clean book; `enlarged` in a clean one). The old `max` kept them at the book's size. The clean-margin path (2544–2545) has used the same 1.15 rule since before this change, so the new exposure is the non-clean third of the books. Deep footnotes and two-column pages are NOT affected: the box spans head to folio regardless of footnote depth (all cached books: ≤ 3 % of pages beyond 1.15 × median).

Fix sketch — exclude outliers only when they are few:
```python
typ = [v for v in bh.values() if v <= 1.15 * _mh]
Th = q(typ, 1.0) if len(bh) - len(typ) <= max(2, 0.1 * len(bh)) else q(list(bh.values()), 1.0)
```
(or take `_mh` over `full_h` pages).

### 6. Small things in the diff (no observed harm)

- 2364–2365, 2417–2420: `allowed` widened without clamping (`u[1] − 0.01 h` can go < 0, `u[3] + 0.01 h` > h). Harmless: every consumer (2485, 2732–2733, 2774, `banded()` 1450, verify 3222–3253, 3296) treats ≤ 0.5 / ≥ h − 0.5 as "no band"; it never fired in the cache (0 pages). Clamp anyway.
- 2329/2347: `fols` is a snapshot; a folio overwritten at 2363 still contributes its old box to later pages' tests. Minor.
- 2421: a foot line ≤ 8 % w becomes the folio without any test against where other pages' numbers stand (hunk 1's loop already ran). `FO`'s spread test (2578–2584) protects anchoring; finding 2's fix covers the dust case.
- 3402: `not own_cover and p['kind'] != 'cover'` are implied by `cover_like` (kind == 'text'). Cosmetic.
- 2412: `e in p['edge']` compares by value, the removal at 2414 by identity — consistent. Hunk 1's removal (2358–2360) rebuilds the lists; nothing is mutated while iterated.
- Touched but not in the diff: `rec['pages'].index(p)` at 3383 compares dicts, O(n²) on a 1,500-page book.

---

## Checked and found sound

- Indices and units: `k0, k1 = (1, 1)/(3, 3)` compare the line's top with the text's top (head) and bottoms (foot); every threshold is a share of the page's own `w`/`h`; no w/h mix-up; `rel()`/`same_rel()` use page i's `w, h` for both pages (only matters for mixed page sizes).
- `same_rel` with missing `core`/`text`: `rel()` falls back to `box` (a text page always has one); `_lines()` returns `[]` without `text` or `core`; non-text pages are never touched.
- Move bookkeeping: `band_print`, `folio_specks`, `text`, `core`, `folio`, `allowed` are pre-move; `box`/`crop`/`show`/`edge`/`specks` post-move — the convention the rest of `decide()` uses (2659–2665). The large crop moves on `9e4e95703bcd` p126/p202 (52/49 pt) are a content move + off-band slide after the head joined the box; the shown window holds head and foot.
- `marks_to_erase()` (3454–3500) paints only dropped rules and dot fields, never `edge`/`specks`: a mark left as "edge" is kept out by the frame, not erased, so the stricter member tests proposed above cannot erase print.
- The 629 letter-sized head/foot groups and the 570/38 folio groups: samples of 30 and 14 pages by eye are all print (running heads, first lines of tight scans, chapter titles, page numbers — including the numbers in grey boxes of the عالم المعرفة series that the baseline cut: `558b0f1096a9` p92/p196, `560169646f16` p174/p162).
- Book-level outcomes: no page newly "whole" or shrunk in any comparable book because of the hunks (`01435c38ee4b` p224 is whole for a text block reaching the sheet's edge in `marks()`, no hunk fired on it; `9e4e95703bcd`'s scale-0.99984 pages follow its 2.3-pt taller H). `folio_anchor`/`folio_axis` unchanged where compared (`8d7204a7003a`: its foot "folios" are footnote markers in the baseline already, 219 of 246 pages).
- Hunk 5 (`sheet()` 3788–3791): drawing only; the dashed window renders correctly on p354.
- Bench coverage note: the six baseline-only books (خريدة القصر among them) were benched under the later keys `c5a81781fc`/`aa692d067e`/`04a1a53259`, not `f3ed545be4`; through `04a1a53259`, hunks 1/2 did not fire on خريدة القصر at all, so no band interaction was exercised there either way.
