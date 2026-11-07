# Self-review of the 2026-11-06 crop redo (method 002b4f3ec1) — 2026-11-07

Owner 2026-11-06 16:50: «لا أستطيع مراجعة الجميع، فراجعه بنفسك حتى التمام». The run: 1,114 books, 1,111 redone, 1 same,
1 expected SKIP (a set-aside original); 267 recipes differ from the 11-05 method's. Review page site/crop-doubts.html:
1,087 books with doubts (3,749 shown pages), 23 without.

## 1. Counts by kind, before → after (scratch/doubts_compare_2026-11-06.py)

shown pages 3,731 → 3,749; «بقعة أُبقيت داخل الإطار» 1,226 → 1,194; «ميل لم تحسمه المقاييس» 1,081 → 1,080; «إطار أكبر قليلا»
508 → 495; «رقم الصفحة قُرئ بقعةً … فأعيد إلى النص» 239 → 300 (+61: the folio rule fires more — judged sound below);
«ختم غُطّي» 222 → 226; «حافة … غُطّيت» 171 → 169; «صفحة بقيت كاملة» 86 → 92; the owner's earlier pages unchanged.

## 2. The recipes' audit (data/improve/crop-redo-2026-11-06-audit.txt)

Over the 267 changed recipes: 17 books with a first-2/last-4 TEXT page newly cut like a cover (finding 1 of the max-effort
review: the «line of print» guard reads thin marks) — the two Sachau الطبقات title pages lose ~4 pt of their widest lines a
side (HARMFUL), المحرر الوجيز p1 harmless, 14 not yet seen by eye; 4 books whose decision went crop → level (تأويلات أهل
السنة 1.044, المنتخب من السياق 1.175, سلم الوصول 1.116, ديوان اللصوص 1.12 — the head line in the block pushed the gain under
the bar; the rule's own outcome, listed for the owner); الشكوى والعتاب (alkottob watermark): 14 pages whose box spans the
sheet (the watermark footer/diagonal taken as a number/head line) → shown whole at 0.942, nothing cut; معجم تيمور 04/05 and
الرحلة الناصرية 1: H down 11–18 % = the intended fix (one tall page no longer sets the box), 1–2 pages shrunk each.

## 3. The after-images scan (data/improve/crop-redo-2026-11-06-sheets-scan.txt)

5,894 after images: 76 pages / 60 books with print at the top or bottom edge while the other margin is wide (212 / 140
before the 11-06 fix), 68 with ink at a side edge (mostly 'larger'/'whole' pages whose scan runs off the sheet). By eye:
دلائل النبوة 039612a752e5 p133 — the running head «المصادر … ١٣٣» CUT at the top of a section-title page (the head stands
at its usual sheet place but this page's text is a short title in the middle: FAULT, for the fix round); الفوائد المحصورة
0697061b1361 p264 — a printed mark under the folio cut at the bottom (FAULT); الفن ومذاهبه 0022362994e5 p1 — a cover shown
whole with the scanner's banner line (fine); الاستقصا 02633978b4d5 p53 — a stamp kept at a short page's foot (fine).

## 4. Random sheets by kind, judged by eye (xhigh subagents, 2026-11-07 02:00–)

### 'tilt' (14), 'two' (5), 'owner' (7) — seed 11 — ONE FAULT, one book
No print cut on any page; no page turned the wrong way or turned while level; no off-centre frame; the owner's «أجزتَ
تدويرها» pages are level and his «أبقيتَها كما مُسحت» pages within ~0.5°. FAULT: مورد الظمآن في رسم القرآن (مطبعة
الاستقامة) dea10c3fe97d p0004 — verse in two hemistich columns leaning ~1.7–2.2° to the left, one angle, before = after
(not turned); its neighbours p0003/p0005/p0006 keep the same lean, alternating by page (−1°, +1.7°, −1.9°, +2°: recto/verso
of that scan lean opposite ways and none was turned; the book lists 11 tilt doubts, «39 tilted pages») — systematic for
that book: FOR THE FIX ROUND (why the verse pages' tilt was not certified). Remarks: معاهد التنصيص ج4 c3e79004da97
p0034 is a true two-angle page whose lower half visibly slopes ~1.5° (left as scanned by the owner's rule); الفوائد
المحصورة 0697061b1361 p0264 shows a fragment of the uploader's logo at its bottom-left corner (the «mark under the folio»
of §3 is that logo: not print — downgrade that one from fault to remark).

### 'larger' (10), 'whole' (8), 'sheet' (5), 'edge' (5) — seed 23 — 6 FAULTS, concentrated in 'sheet' and 'edge'
'larger': 1 mild of 10 (53995cba8be9 p0014: a 10 % blank band under the page number of a first text page, nothing cut);
the frames hold diagrams, stamps, marginal numbers, signatures with proper margins. 'whole': 0 of 8 (every whole page had
its reason: marginalia, cover, blank leaf). 'sheet': 3 of 5 — مجلة المنار ج16 026c3ae46830 p0193: the running head
«(المنار ـ ج ١٦) كيف السبيل إلى الحكم بالشريعة ٣٣٣» clear in the before, WIPED to faint traces in the after (the rule under it
survives), and the window off-centre (2.5 % right / 14.8 % left: the scan's noisy left strip replaced by fill, the window
not re-centred); بداية الهداية 542d02652dbe p0053: the fill blanks a corner of the ornamental end-paper; الخطط التوفيقية 06
89561824400d p0004: black scanner-bed strips (6–7 % of the width) left on both sides, not filled. ALL THREE RECIPES ARE
IDENTICAL TO THE 11-05 ONES (checked): pre-existing faults of the sheet/bands step, not this run's — for the fix round
all the same (an erased running head is worse than a cut). 'edge': 2 of 5 — c8249fecfc4f p0471: a printed marginal
verse reference «١٤٠/٢» touches the frame's left edge with 4 % of white scan beyond it; 10d6fae51133 p0201: the frame
hugs the text's right side (1 % vs 12 % left; the scan may end there). The pattern: a printed marginal at the scan's edge
gets the frame ON it, not beside it. 0e7cea1fb8d4 p0010 (the scan itself ends at the marginal) is rightly not a fault.

### 'folio' (24 sampled, seed 5) — SOUND
24 of 24 have a real page number at the joined place (23 numerals, 1 abjad letter ح in the notes of قصة الحضارة); junk taken
for a folio: 0; no frame pulled toward dust, halftone dots or the opposite page; no folio cut or touched (smallest clearance
8 px on 9da5c530d977 p0124, forced by a scan cut tight at the right — that page's frame is off-centre horizontally for that
reason, not the rule's). In six sheets the before image circles specks near the folio's row and none was joined. Remarks:
5f410d374595 p0042 bottom gap ≈ 2× the top (the scan starts at the folio's level); 94d9cc846cde p0278 faint blotches
inside at the top-left, frame unaffected.
