# HANDOFF — current job (started 2026-10-03 07:00 UTC)

Any agent/model taking over: read `AGENTS.md` (esp. §7), then this file, then the last lines of `WORKLOG.md`.
Each workstream appends its progress below (the newest state first, then the history). Everything is resumable.

OWNER 2026-10-26 ~03:00: the ~11,000 old-format names (parentheses) WAIT for the reading pass — no mechanical format pass («ننتظر مرحلة القراءة»). He clears and switches to xhigh.
OWNER 2026-10-26 03:10 (after the /clear): «max is set» — the session runs at max: the regression's end (a–e), then the pilot.

## 2026-10-26 03:35 — max effort; regression 26b still running; the pilot's review page shows his earlier remarks (Claude)
- RUNNING (unchanged): crop-regress-2026-10-26b (see 02:00). At 03:24: 12 of 31 books, 61 PASS, 0 FAIL; 10,167 pages left
  ≈ 3 h → ends ≈ 06:30 UTC (the 04:15 of the 02:00 section counted books, not pages). Monitored for FAIL/crash/end.
- Its diff so far (12 books, 4,721 pages; the diff script only reads the cache): خزانة 01 pp. 1 (cover print), 26 (owner turn),
  164, 307 (0.35 rule) — nothing else; all four LOOKED AT (old | new): the year «١٣٨٧ = ١٩٦٧» now whole at the cover's foot,
  pp. 26/164/307 level. Against the stopped cedf4dd2b8 run (11 books): every key of every page identical except خزانة 01
  p. 1's show (and the new key cover_marks on cover pages) — the cover rule touched exactly that page.
- The diff script's causes tightened (before the run's end calls it): a turn rule explains a page only when its turn changed.
- NEW (commit a3fe781): the crop review page (crop-doubts) of a redo also shows every page the owner pointed at before, his
  words beside it — crop_batch.owner_pages ← data/crop/owner-pages.tsv (47 pages: the page numbers his 10-14 remarks name;
  «الأولى، الأخيرة، الأوسطان، 1 و 4…» = the samples of crop-review-002/004 in page order) + خزانة 01 p. 1 (10-25) + his 14 «turn»
  pages. Without it the pilot page would have shown only the method's doubts — not مواد البيان p. 474, الإعلام 09 p. 444,
  المغازي 248/400/421, روضة الفهوم 43/52/84, خزانة 01 pp. 1/18/26/164/307. owner_turns unchanged (0 differences on 1,129
  paths). Tested end to end (analyse, jobs 1, الاتباع والمزاوجة 98 pp.: 176 s, 400 MB peak) and the page on a fake record.
- 1d memory: a sampler runs (user unit mem-sampler, scratchpad of session 07279fff…/mem-samples.tsv: every crop process's
  RSS every 3 s). The redo analyses each book in ONE process (jobs 1): 400 MB for 98 pp.; the regression's workers (jobs 2–3)
  reach 900 MB, its main 230–370 MB → a redo book ≈ 1–1.3 GB at worst vs the governor's PER 2.2 GB + PARENT 1.5 GB (2 books at
  once in an 8 GB pen). Measure the pilot's processes, then lower PER/PARENT with a margin BEFORE the full redo (≈ 2× faster).
- Later (not urgent): the 2 books the redo skips (البداية والنهاية 21، المغرب في حلى المغرب 01) are join_parts.py files built from
  the CROPPED volume (insert_pdf carried its CropBox / q…cm / stamp patches / splits): no truncation gives their original.
  Way: the original volume again (exact md5 of the crop log: ~/Books via local-map, else its source) + the joined file's own
  front pages → join_parts → crop it as a new book (crop_batch), plan + log.

## 2026-10-26 02:00 — the cover print rule; THE REGRESSION RUNNING AGAIN: crop-regress-2026-10-26b (Claude, max effort)
RUNNING: user unit crop-regress-2026-10-26b (scratch/regress_2026-10-26b.sh, marker data/crop/.regress-2026-10-26b, book_crop
f06a68adb2) → logs/crop-regress-2026-10-26b.log; at its end, by itself, the diff against 5d6113b97c →
logs/crop-regress-diff-2026-10-26b.log (scratch/crop_recipe_diff_2026-10-26.py: owner turn / level first / image ≤ 0.35 /
cover print / OTHER). Started 01:59 UTC, ≈ 4–4.5 h. Do NOT edit book_crop.py while it runs. (Its header says «02:50»: wrong,
left — a running bash script is never edited.) The run of 00:07 (crop-regress-2026-10-26) was STOPPED after 11 books (60 PASS,
0 FAIL); its cedf4dd2b8 recipes stay in the cache: new vs cedf4dd2b8 may differ only on the 3 cover pages below (+ the new key
cover_marks).
WHY: the owner HAD answered the خزانة question (2026-10-25 22:51, session ff1c42e0, missed by the 01:30 notes): «you can
figure out, just check the first page, the cover's. cover is there but not filling the page, like uncomplete measurments or
so». Checked on the phone's own bytes (md5 5d61fa48…): the 10-10 crop shows p. 1 pushed down under the scan's grey header
table, its foot cut (move 143.8 pt). The method since 10-21 already fills the page with the cover (cover_rect), but its even
cut took the cover's last line, the year «١٣٨٧ = ١٩٦٧». New: book_crop.cover_marks (a cover's print as boxes; the bar follows
the ground's grain) + cover_window (frames): the fill's cut stays even unless (a) a centred line of print at one end would be
cut and the other end is plain over its whole cut + 3 pt, or (b) a spine's lettering would be cut and ≥ 40 % of the cover
from the other side is plain. Proof: old vs new frames() on the 31 regression books (14,888 pages): 3 changed — خزانة 01 p. 1
(year kept), روضة المستبين back covers p. 734 / p. 1531 (spine kept); 280 local books (~/Books, read only): 20 covers and 71
dark end pages, no false move (3 right ones). 4 regression cases added (crop-regression.tsv rows 110–113).
WHEN IT ENDS: steps a–e of the 01:30 section below, on the -26b logs; the diff's «cover print» pages = those 3. Then item 2.
(02:40) It runs ~4.4 min a book alone (the stopped run shared the CPU with the Turner tests) → ends ≈ 04:15. First 7 books:
0 pages changed vs 5d6113b97c. READY for item 3 (launch by hand once the diff is explained, 0 failures):
`systemd-run --user --slice=crop.slice --unit=crop-redo-pilot --nice=10 --working-directory=$PWD --setenv=PATH="$PATH"
scratch/pilot_redo_2026-10-26.sh` — 10 books (data/crop/pilot-2026-10-26.tsv: خزانة 01, four the owner marked on 10-14 that
are no regression case, five random), each phone file checked = the file the old crop wrote; then site/crop-doubts.html.
Full-redo pre-check DONE (live server-side MD5, 02:38): 1,120 of the 1,122 are still the file the old crop wrote; 2 differ
and will be SKIPPED by crop_redo — «البداية والنهاية (ت التركي) 21 (الفهارس)» (joined with its front 10-25, its cropped
original deleted by plan 382) and «المغرب في حلى المغرب 01» (changed after its crop): each needs an uncrop of the joined
file (strip the crop's q…cm wrappers, CropBox = MediaBox) or a fresh copy, later. (data/phone/md5.tsv is stale for cropped
books — its users check the size first; it misled only a quick look.)
MEANWHILE (allowed beside it, owner's order): item 2, the name composer — DONE 02:35 (commit after 3764168): no cut inside a
phrase, names/roles shortened before title words, tiers above the title; plan 383 applied (21 names; review page
site/plan-383.html, http://127.0.0.1:8765/plan-383.html — tell the owner). NOT done (judgement, owner's look): 56 read books
whose phone name was set otherwise (plan 315 approved, held readings, set parts: scratchpad list only); the 12,575 parentheses
(mostly volume labels «(الواجهة)»), 558 commas, 9 «ط» of name_audit — next, as plans. refresh.sh waits for the regression's end.

## 2026-10-26 01:30 — STATE BEFORE A /clear: the one regression running; then its diff, by eye (Claude, max effort)
RUNNING (nothing else of mine): user unit crop-regress-2026-10-26 (scratch/regress_2026-10-26.sh, book_crop cedf4dd2b8,
marker data/crop/.regress-2026-10-26) → logs/crop-regress-2026-10-26.log; at its end it writes by itself the diff against
5d6113b97c → logs/crop-regress-diff-2026-10-26.log. At 01:26: 8 of 31 books, 39 PASS, 0 FAIL; ≈ 6–10 min a book now that it
runs alone → done ≈ 04:00–05:00 UTC. Do NOT edit book_crop.py while it runs (cache key). Check: `systemctl --user is-active
crop-regress-2026-10-26`, `grep -c ^FAIL logs/crop-regress-2026-10-26.log`. A crash (memory brake) reruns by itself.
The test units of 00:10 (turner-eq-*, turner-fresh-*) have ENDED, all passed — ignore that paragraph's «running».
WHEN IT ENDS (item 1e, max effort):
  a. «N failures» line: 0 expected. The 14 owner-turn cases are checked at the END of the log (they reuse cached recipes);
     crop_regress now passes an owner turn only if its shear reading after the turn is below the turn (wrong way ≈ 2×).
  b. Read logs/crop-regress-diff-2026-10-26.log: causes «owner turn» / «level first» / «image ≤ 0.35» / OTHER. The 13 books
     the stopped 25b run did changed only خزانة 01 pp. 26 (owner turn), 164, 307 (0.35 rule) — the new run should match.
     Every OTHER page must be explained before the pilot redo.
  c. Draw every changed page old | new as the reader sees it: `python3 scratch/crop_diff_sheets_2026-10-26.py cedf4dd2b8
     <outdir>` (tested on خزانة 01: p. 26 levelled by the owner's turn) and LOOK at each (wrong direction, cut text, box).
  d. 1b memory: per-book «memory peak … workers up to …» lines (25b: main 250–405 MB, a worker ≤ 890 MB with 3 per book);
     after the big books (83dfc7786870 1,531 pp., 2b47002d18ab 1,491 pp., 51cfa6854fda) decide whether mem_governor's
     PER = 2.2 GB a book can come down (more workers) — the stamps memory fix removed the 3.6 GB peaks.
  e. Report to the owner; then items 2–4 below at the effort he sets (2 name composer xhigh, 3 pilot redo xhigh, 4 reading).
DONE TONIGHT (commits 621a7d9 … e2d1bc8): the Turner made exact (cce9c37) and PROVEN — 114,175 views of 32 books
byte-identical to fresh copies (scripts/turner_check.py, rerun it after any PyMuPDF upgrade) and 40/40 page-extract recipes
identical with and without the kept copy; the 25b run stopped (13 books, 62 PASS, 0 FAIL); the small-tilt angles on the
owner's «turn» pages compared (no rule change — see the 00:10 section's last paragraph). Open with the owner: the image
of خزانة الأدب vol. 1's cover (asked again; would become a regression case).

## 2026-10-26 00:10 — the exact Turner committed (cce9c37); THE REGRESSION RUNNING AGAIN (Claude, max effort)
RUNNING: user unit crop-regress-2026-10-26 (scratch/regress_2026-10-26.sh, marker data/crop/.regress-2026-10-26, book_crop
cedf4dd2b8) → logs/crop-regress-2026-10-26.log, then by itself the diff → logs/crop-regress-diff-2026-10-26.log. Do NOT edit
book_crop.py while it runs. Beside it (scratchpad of session 9365be8c…, /tmp/claude-1000/-home-k-projects-phone-library/
9365be8c-b77d-4867-b935-e76269705419/scratchpad/probe): units turner-eq-* (render check: every page of the cut books
ae39a500653d, d20f1fe41833 and the split fbf39d55c6f7, every 5th page of the rest — any «DIFFER» line in *.log = the Turner is
still not exact: stop the regression) and turner-fresh-0/1 (the 40 page extracts planned with every view fresh vs the kept copy: 40 same ✓, 01:20). Why: the Turner of 9c26546 was not exact (MuPDF keeps a whole decoded
image and drew later part-views of cut images from it); now a view is drawn from the kept copy only when every image is
≥ 92 % shown (whole_shown, odd_drawing); scripts/turner_check.py is the proof tool (rerun after any PyMuPDF upgrade).
The stopped 25b run (13 books, 62 PASS, 0 FAIL) changed 3 pages, all explained (WORKLOG 00:10). Its diff on the remaining
books will come from the new run. Still open from the revisit: 1b — read the per-book memory peaks (25b so far: main
250–405 MB, a worker ≤ 890 MB with 3 per book) and maybe lower mem_governor PER (2.2 GB) after the big books
(83dfc7786870, 2b47002d18ab, 51cfa6854fda); 1e — every OTHER page of the diff explained; the خزانة vol. 1 cover image
(asked the owner). Possible later speed-up (not needed: < 2 %): whole_shown counts every clip of the page, so a footer
banner's clip drawn after the scan (1d12000b2925, 43b1158bc5be) sends all its views to fresh copies — a device that knows
which clips hold each image would let them use the kept copy.
SMALL-TILT ANGLES, checked (2026-10-26 01:00, no change made): on 6 of the owner's 14 «turn» pages the method now turns them
itself (0.35° ruler rule / level-first) by an angle 0.05–0.15° from the one he approved (تيمور 02 p. 217: 0.15° vs his 0.30°;
p. 203 0.375 vs 0.275; خزانة 01 p. 164 0.475 vs 0.375; الحروب 38 p. 407 0.35 vs 0.45 — there shear AND image read 0.35 level).
A two-strip reading (left/right row profiles cross-correlated; tracks known turns to sd 0.022°, but its absolute zero is
pulled by layout — خزانة 01 p. 369 read 0.82° on a page that is level by eye) and a consistency test (each page given extra
known tilts; scratchpad probe/tiebreak2.log) show every tie-break rule equally self-consistent (spread ≈ 0.07°; «closest to
the measured tilt» worst, 0.12°): the measures differ by small biases of their own on these dense pages, none right
everywhere. Differences ≤ 0.15° (he sees ≈ 0.25° on a full line) → left to his eye in the pilot review, not a rule change.

## 2026-10-25 22:00 — crop revisit coded (commit 9c26546); THE ONE REGRESSION RUNNING (Claude, max effort)
RUNNING: user unit crop-regress-2026-10-25b (scratch/regress_2026-10-25b.sh, marker data/crop/.regress-2026-10-25b) →
logs/crop-regress-2026-10-25b.log, then by itself the diff → logs/crop-regress-diff-2026-10-25b.log (scratch/crop_recipe_diff_2026-10-25.py:
every changed page sorted by cause — owner turn / level first / image ≤ 0.35 / OTHER). Do NOT edit book_crop.py while it runs
(cache key ef238679a3). Equivalence tests beside it (scratchpad, units crop-eq-plan-old/new, crop-eq-render).
Findings and changes (all in book_crop.py's comments):
- 1a SPEED: the 14,353 s outlier (3103a9db389b) was the memory pen squeezing the job while the governor was down
  (08:43–16:10) — alone the book takes 355 s (1.2 s/page). Profile: marks() 41 %, the two projection measures 34 %,
  renders 11 %. Exact changes (old vs new recipes byte-identical on page extracts, renders byte-identical): Turner (one
  turned copy per page — images decoded once), each view measured once in verify (memo per page), by_proj stops at the
  coarse stage when the peak is 0°, vectorised group lookup in marks(). ~20–35 % faster.
- 1b MEMORY: stamps_of kept two small images for EVERY ink group (every word): 3.6 GB for 83dfc7786870 (1,531 pages),
  1.7 GB for 51cfa6854fda — the brakes of 18:10 and 19:03. Now only candidates a test reads keep them (results identical
  on all 31 regression books). After the run: read the per-book «memory peak» in the log → maybe lower the governor's
  2.2 GB per book (more workers).
- 1c: best_turn BUG — the least-of-the-two key let an unlevel angle beat a level one by a float hair (الحروب الصليبية
  ص 407); now a turn level by both measures is taken first. The ruler-certified small tilt allows the image measure up to
  0.35° (was 0.3°). On the 15 untreated pages: 7 turned by these rules, 7 by the owner's turns, فهرسة 355 stays (its
  «turn no» case holds: the shear measure still reads 0.2° after the turn).
- 1d: owner turns in book_crop.plan(…, owner_turns) ← crop_batch.owner_turns(path) (data/crop/owner-turns.tsv, renames
  followed) in crop_batch.analyse / crop_redo / crop_regress (cache key tag); 14 «turn yes» cases added.
- 1e NEXT: when the run ends, read the diff: every OTHER page explained before the pilot redo. Asked the owner again for
  the خزانة الأدب vol. 1 cover image (old 2026-10-10 crop).
Then items 2–4 below (the owner switches the effort).

## 2026-10-25 21:15 — NEXT: the crop method revisit (owner chose max effort); state before a /clear (Claude)
State now: nothing runs but the services (mem-governor, phone-keepalive, phone-watchdog, review-server, review-x-opener,
reporter-follow). Crop regression (book_crop md5 5d6113b97c, logs/crop-regress-2026-10-25.log) FINISHED: 6 failures =
exactly the 14 pages the owner ruled «turn» (data/crop/owner-turns.tsv; site/crop-tilt-001.html closed); every page case
passes. refresh.sh ran (fff0ed3, web published). All owner review pages answered (doubts-002/003 closed; C = leave the
756 separate introductions apart — memory separate-introductions-stay). Plan 382 deleted the 39 originals set aside by
plans 371/375 (owner: «remove the trace»).

THE OWNER'S ORDER (2026-10-25 evening), with the effort he will switch to:
1. (max) CROP METHOD REVISIT — then ONE regression run:
   a. SPEED. Profile first (cProfile on analyse_pages + verify of ~20 pages). Prime suspect: every measured turn renders
      through turned() → a NEW one-page document (insert_pdf copies the page image) → the image is decoded again for
      each angle (best_turn tries up to 11; analyse_pages more). Exact-preserving idea: render the turned page from the
      ORIGINAL doc (MuPDF's store then caches the decoded image) and prove pixel/measure equivalence on sample pages
      before switching; memoize look(i, q) per (i, skew, move). Avoid approximations (low-res search) unless proven
      equal. Outlier: 3103a9db389b (رسوم دار الخلافة, 296 pages) took 14,353 s (10,453 s on 10-18) — 48 s/page,
      ~15–40× the others (1–4 s/page): profile it first.
   b. MEMORY: one analysis reached 3.7 GB with 1 worker and tripped the governor's brake twice (18:10, 19:03) — check
      MuPDF store size (pymupdf.TOOLS.store_maxsize), xy arrays kept in best_turn's tried dict, leaks across pages.
   c. SMALL-TILT RULE: the owner approved all 14 undecided pages (0.2–0.68°, image measure stuck at 0.22–0.35° after
      the turn) → the method is too timid. Candidate: both measures saw the tilt (the untreated condition), the shear
      measure reads ≤ LEVEL after the turn, the image measure improves (not ≤ 0.2 required), no ruler contradicts.
      Check against every «turn no» case of data/improve/crop-regression.tsv (index pages, verse) and look at a sample.
   d. OWNER TURNS as data inside book_crop: plan(path, jobs, owner_turns={page: |tilt|}) → in verify a listed page the
      method leaves untreated is turned by −u (u signed, measured at run time; the owner saw −u) and marked owner_turn;
      callers (crop_batch.analyse, crop_redo, crop_regress.recipe) look the book up in data/crop/owner-turns.tsv by its
      phone path (NFC, renames followed); crop_regress: cache key + hash of the book's turns, and the 'turn' check accepts
      owner_turn. Add the 14 pages as «turn yes» cases (note: the owner's verdict).
   e. After the run: a DIFF of the new recipes against the 5d6113b97c cache (skew, crop box per page) — every change must
      be explained before the redo. Ask the owner for the image of خزانة الأدب vol. 1's cover (he saw problems there on
      the OLD 2026-10-10 crop — «وجدت الغلاف هكذا»; the image never arrived): make it a regression case.
2. (xhigh, may run beside the regression) NAME COMPOSER: name_compose cuts the title before dropping editors/publisher
   (13 hand overrides today; 544 names cut mid-phrase, scratch/bad_cuts_2026_10_20.py) — the title's last clause is never
   cut while an editor/publisher remains; then re-compose read books, clear commas/«ط»/parentheses where the data is in
   hand (name_audit: 12,575 parentheses — mostly volume labels, 558 commas, 248 repeated volume numbers, 115 one-file
   folders, 36 files < 20 KB).
3. (xhigh) PILOT REDO of ~10 books (crop_redo.py data/crop/redo-list-2026-10-17.tsv, as scratch/start_redo_2026-10-18i.sh
   did) → owner reviews site/crop-doubts.html (incl. خزانة vol. 1) → the full redo of the 1,122 books (unattended).
4. (medium) reading pass: 3,249 books never read + 376 sheets unread (read_status.py); repeated volume numbers.
Gotchas today: systemd-run units lack ~/.local/bin in PATH (rclone not found) → pass --setenv=PATH="$PATH";
mem_governor now survives a systemctl timeout (it had crashed at 08:43, brake off until 16:10); refresh.sh no longer
opens Brave (owner) — OPEN=1 to open.

## 2026-10-25 15:30 — crop gate rerunning; names 1432–1539 done (Claude)
- RUNNING: user unit crop-regress-2026-10-25 (scratch/regress_2026-10-25.sh, marker data/crop/.regress-2026-10-25) → logs/crop-regress-2026-10-25.log. Do NOT edit book_crop.py while it runs (cache key). Regression only: if 0 failures (after the owner's verdicts on site/crop-tilt-001.html — «اترك» → add a «turn no» case to data/improve/crop-regression.tsv; «أدر» → a method fix), start the redo of the 1,122 books by hand (crop_redo.py data/crop/redo-list-2026-10-17.tsv crop-redo-001, as scratch/start_redo_2026-10-18i.sh did).
- Owner's verdicts on crop-tilt-001: ALL 14 pages «turn» → data/crop/owner-turns.tsv (path, page, measured tilt). NEXT (xhigh, after the regression ends): apply them OUTSIDE book_crop.py (a recipe post-step in crop_batch.analyse / crop_redo and crop_regress.recipe: skew = −measured, best_turn around it, marked owner_turn, not counted as untreated) and let crop_regress accept those pages; then the regression gate counts them as decided.
- Fixes in book_crop.py today: see WORKLOG 15:30. Probe scripts used: scratchpad only.
- Names: plans 379–381 applied; next batch: read_status.py then title_sheets.py on unread singles. Still: names cut mid-phrase (scratch/bad_cuts_2026_10_20.py, 544) — the composer drops title words before editors (13 hand overrides today show the pattern: fix name_compose so the title's last clause is never cut while an editor/publisher remains).
- refresh.sh NOT run since 08:24 (it would run beside the regression): run it when the regression ends.

## 2026-10-25 09:15 — owner's doubts-001 comments handled; page doubts-002 open for him (Claude, before a /clear)
- Laptop restarted 2026-10-25 ~02:00: services relaunched with scripts/start_services.sh + review-x-opener (user unit). The owner
  wants the lid/idle inhibitors ON (2026-10-25 «yes I want them back»; on 10-23 he had asked Antigravity to stop them «for now»).
- Antigravity (10-20..10-25): fixed crop_regress.py NameError and book_crop.py level-frame veto (uncommitted, still in the work
  tree — commit them with the crop work); reran the regression (10-21/22): page cases pass except one on خريدة القصر; the
  whole-book audit flags residual_tilt in 30–31 books (its diagnosis: level_by_rules / level_by_proj pages not exempted in the
  residual_tilt check, book_crop.py ~L1923) and untreated_tilt in 11 — NOT verified by Claude yet; the crop chain
  (crop-start-redo-i) is stopped («STOP: the regression did not pass»), its marker data/crop/.start-redo-2026-10-18i exists:
  a new chain script is needed after the gate passes. Also: Antigravity added «scratch/» to .gitignore (commit one-offs with -f).
- Done today: plans 370–378 (WORKLOG 09:10). Review page: http://127.0.0.1:8765/doubts-002.html (report «doubts-002»): A = 3
  unresolvable (no upload has the missing pages), B = 39 changes to check, C = a decision: join the 756 separate
  introductions (665 sets) into their vol. 1? Watch his comments: python3 scripts/watch_comments.py.
- Still to do: names cut mid-phrase (scratch/bad_cuts_2026_10_20.py lists 544; fix with name_compose's whole_clause rule +
  readings); naming pass books 1432–1539 (sheets ready); crop gate; refresh.sh started as unit refresh-2026-10-25.

## 2026-10-19 22:45 — the owner's six decisions done (plans 352–360); refresh running capped (Claude)
- Owner: «1 نعم / 2 جيد، لكن أبق التعازي أيضا / 3 إن كان مخطوطا حقا، قد تكون وقفت على صور من المخطوط فقط من التقديم /
  4 اعتن / 5 نعم / 6 الذي تعرفه مناسبا، وكمل الكتب والسلسلات الناقصة». All applied: see the WORKLOG line of 22:40.
- Not found anywhere: vol. 7 of بحر المذهب (إحياء التراث, ت أحمد عزو عناية) — Waqfeya marks it «(ناقص)», both archive.org
  uploads have the same 5,928-byte placeholder; the library keeps the complete العلمية edition. Series checked complete:
  الإبياري's المكتبة الأندلسية (18 vols), موسوعة روائع الشعر العربي (10 vols / 19 files). The Waqfeya comparison has no other
  partial book (its one «partial», التنبيه والإيقاظ, is the same scan with a cover added).
- 1190 and 1271 (other «المكتبة الأندلسية» series: دار الفكر / دار الثقافة) stay single books.
- refresh.sh runs as user unit refresh-2026-10-19b (MemoryMax 2.5G, beside the crop regression) → logs/refresh-2026-10-19b.log.
- Review page for the owner: http://127.0.0.1:8765/plan-322-351.html (plans 322–351, applied without a review page).

## 2026-10-19 16:40 — state before a session reset (Claude)
- RUNNING (do not restart, do not touch book_crop.py while it runs — see memory regression-cache-key): systemd user unit
  `crop-start-redo-i` (scratch/start_redo_2026-10-18i.sh): the crop regression (logs/crop-regress-2026-10-18j.log) →
  0 failures → crop_redo of the 1,122 books (data/crop/redo-list-2026-10-17.tsv, crop-redo-001, run_resumable) →
  crop_library. Regression at 16:40 UTC: 15 of 31 books passed, 0 FAIL; one worker, ~25–90 min a book (the governor gives
  1–2 workers; memory is tight beside the owner's browsers). A FAIL line or «STOP» in logs/crop-start-redo-2026-10-18.log
  needs a look (book_crop fix → stop the unit FIRST, then edit, then a new scratch chain script).
- Services (each skipped by scripts/start_services.sh if running): mem-governor, phone keep-alive, watchdog, review
  server, reporter-follow, lid and idle inhibitors. Watch owner comments with `python3 scripts/watch_comments.py`.
- NAMING PASS (title pages read by eye, data/names/title-read.tsv): books 0–1431 of data/names/sheets/books.tsv are done
  through plan 351 (plans 335–351 today: ~560 renamed, 6 copies of kept editions deleted, شرح ابن قاسم fetched).
  Next: books 1432–1539 already have sheets (data/names/sheets/s0716…s0769.jpg + .txt with Shamela/Waqfeya candidates):
  read them → `python3 scripts/title_read_add.py < readings` («n | verdict | title | author | editor | publisher | city |
  year | kind | section | note»; printed roles as «role: name» in the editor field) → `python3 scripts/names_plan_read.py
  PLAN HELD` → keep only that batch's rows → apply_plan --dry-run, apply → index_update → WORKLOG → commit. Held books:
  `python3 scripts/deep_sheets.py N…` (pages 2–9 + last 3) → `title_read_fix.py` («n | field=value», a note with
  «read further (pages …» settles earlier doubts). Next batch: `read_status.py`, then title_sheets.py on unread singles
  (2,052 singles + ~1,190 sets left). Held lists: data/names/verify-806-1059-held.tsv, verify-1060-1177-held.tsv.
- NOT RUN since plan 335: scripts/refresh.sh (indexes, site, Brave) — deferred because a refresh beside the crop analysis
  trips the memory brake. Run it when the regression is between books or done.
- Owner decisions open: الواضح في أصول الفقه (two editions in one folder); متون موقع المتون (39 ephemera, raw names);
  تاج التراجم (four Binder manuscripts, raw names); بحر المذهب vol. 7 blank; سنن أبي داود index = a title page only;
  book 1091 (a newspaper review page) and 1162 (a 3-page web leaflet): keep or remove; series folders for the poetry
  encyclopedia (885–902, 906) and المكتبة الأندلسية (859, 1005, 1019, 1190, 1271); الشرح by centuries for big sections
  after the naming pass.

## 2026-10-17 19:20 — gate (b) running after the laptop died at 15:42 (battery) with 56 PASS / 6 FAIL
- Failures fixed: lines kept in the tilt measure (الاتباع ص 51/68, اللآلئ ص 387 were left unturned); covers 0.5 % outside
  their edge (فهرسة ابن خير ص 380); parity offsets from needed content (أسرار البلاغة ص 187); content may move beyond the
  sheet on any paper when the text would be ≥ 3 % off-centre (إرشاد الساري ص 492).
- crop-regress-b.service → logs/crop-regress-2026-10-17b.log; crop-chain-b.service (scratch/after_regress_2026-10-17b.sh):
  0 failures → phone → crop_redo (1,122) → crop_library. Services relaunched as user units (phone-watchdog, phone-keepalive,
  review-server, reporter-follow) + both inhibitors. The laptop runs on battery: it died twice — keep it on the charger.

## 2026-10-17 14:30 — crop method corrected from the owner's review; regression gate running; chain waits
- book_crop.py fixes (commits 6c3474c … 11f8a75): lines are not letters/content; printed rules only near the text and
  recurring; notes need width and height; pictures/plates kept whole; covers cut to the cover (cover_rect; first/last 4
  pages; wrap-around covers split); coloured stamps found and erased; title pages centred on themselves; stray dots cut;
  lines/stains dodged left-right and up-down; tilt to ±8°, two columns with a relative tolerance, a level frame stops a
  turn, a big warped tilt may be reduced; spreads split at the gutter (incremental, lossless) then cropped.
- Tested on extracts of the 31 marked books (scratch/crop_minitest.py runs r2–r4, scratch/crop_compare.py): every marked
  page right except 51cfa6 p16 (black emblem in the text column), 43b115 p444 (needs a shear — next), 4a0fc2 (wavy
  lithograph lines), 816413 (the source itself is cut: find a better copy), 35fbe3 p44 (a dark corner line left).
- crop-regress.service: the full regression set (64 old + 24 new rows) → logs/crop-regress-2026-10-17.log.
- crop-chain.service (scratch/after_regress_2026-10-17.sh): 0 failures → wait for the phone → scripts/crop_redo.py on the
  1,122 books cropped by the old method (data/crop/redo-list-2026-10-17.tsv; upload beside, verify, swap) → crop_library.sh.
  Any failure → STOP (nothing touches the phone). The phone's FTP app was off from 12:17.

## 2026-10-17 02:40 — overnight; crop still PAUSED (method being fixed from the owner's remarks)
- While Claude was away (10-15/16) Antigravity read title pages 842–1059 (data/names/title-read.tsv; commits «title-page
  reading» / «catalog(batch)») and added book 322 (queue 322, قرة العيون). No rename/move applied. Laptop restarted 10-16 13:29.
- Running tonight: both inhibitors; phone_watchdog, phone_keepalive, review_server (relaunched after the restart);
  scripts/reporter_follow.sh (report in any GNOME Terminal); scratch/crop_baseline_2026-10-17.py (current method on the 31
  marked books → ~/.cache/phone-library/crop-baseline/, log logs/crop-baseline-2026-10-17.log); inspect_files.py on the 142
  never-inspected files (logs/inspect-2026-10-17.log).
- Crop diagnosis so far (data/crop/owner-marked-2026-10-14.tsv = the 31 marked books): (1) a thin line counts as a «letter»
  → text block/box pulled off-centre (00597f p18, second look «cross»); (2) non-text marks (stamps, logos, edge lines, print
  defects, specks) make the box grow → page shrunk or off-centre; (3) covers on the scanner bed should be cut to the cover;
  (4) a plate (dark photo in a frame) was CUT in clean mode — the big non-letter mark is treated as margin (54dce4 p15);
  (5) section-title pages placed by the neighbours' text edge instead of centred (3103a9 p9); (6) tilt: framed plates turned
  by the photo inside (83dfc7 p138), two-column pages not levelled (2a8c4b p42), some turns wrong/partial; (7) spreads not split
  (طبقات الفقهاء). Next: fix in book_crop.py, regression rows for every marked page, mini-book tests, then redo affected books.

## 2026-10-15 — CROP PAUSED (owner: «you can pause if necessary»)
- Owner reviewed crop-review-002 (92 books, 14 with faults) and 004 (~60 of 236, 17 with faults) + OCR sample + plans 320a/b
  (data/names/review-comments.jsonl, reports crop-002, crop-004, ocr-001, plan-320a/b). «راجعت إلى هنا فقط / ويجب عليك مراجعة
  الباقي وإصلاح ما تجده / وعسى أن تكون العمليات المقبلة أكبر جودة وتصحيحا ذاتيا».
- crop_library.sh stopped; crop_batch on batch-006 stopped at 108 cropped (workers killed; main died at submit, no write in
  progress; 188 unfinished files keep their sizes). Do NOT restart crop_library.sh before the method is fixed and passes
  his marked books; then redo the affected books already cropped (002–006).

## 2026-10-13 00:20 — laptop down 2026-10-12 ~21:45 (battery empty), restarted 00:00; all relaunched
- Relaunched: both inhibitors, phone_watchdog.sh, phone_keepalive.py, review_server.py, resources_report.sh → /dev/pts/0,
  scratch/resume_crop_005_2026-10-13.sh (waits for the phone, checks batch-005's unfinished files keep their logged size —
  stops on any mismatch — then finishes batch-005 and execs crop_library.sh). Phone on the Wi-Fi at .100 but its FTP app was
  not running at 00:16. Front pages of the 150 sets: done (150/150). Keep the laptop on its charger.

## 2026-10-12 14:10 — laptop restarted at 13:57; jobs relaunched; lid inhibitor on
- The restart stopped crop batch-005 (65/300 done; checked: no phone file half-written — every unfinished one keeps its
  logged size), phone_watchdog.sh and review_server.py. Relaunched (setsid nohup): phone_watchdog.sh, review_server.py 8765,
  scratch/resume_crop_005_2026-10-12.sh (finishes batch-005, refresh + commit, then execs crop_library.sh; one-off, marker
  data/crop/.resume-005-done). After any restart: check `uptime -s` and relaunch these.
- Lid (owner: «launch the lid script previously run by antigravity»): `setsid nohup systemd-inhibit
  --what=handle-lid-switch:sleep:idle --who=phone-library --why="permanent inhibitor requested by user" --mode=block sleep
  infinity &` — the laptop keeps running with the lid closed (`systemd-inhibit --list | grep phone-library`).
- 17:52 GNOME's own idle suspend (on battery: «will suspend for inactivity») is not blocked by systemd-inhibit: also
  `setsid nohup gnome-session-inhibit --inhibit suspend:idle --reason "phone-library jobs" sleep infinity &`. And
  scripts/phone_keepalive.py (login + NOOP every 2 min: the phone's FTP app no longer idles). Relaunch all three after a restart.
- Names: 372 single-file folders never read (2026-10-12): data/names/singles2-2026-10-12.txt; sheets for books 806–1043
  (front pages of 139 rendered by front_pages.py); reading in progress (806–821 recorded).
- Applied plans since the owner's «change on phone, no problem» (2026-10-12): 318, 319, 320, 321 — show them for review.
- 14:15 owner: «keep the background jobs running, open the review pages for me, and hold on … until I talk to you; a tiny
  reporting script on my open zsh session every 5 min». Opened in Brave: plan-318/319/320a/320b/321, decisions, ocr-review-001,
  crop-review-004/003/002. scripts/resources_report.sh → /dev/pts/1 (his GNOME Terminal). Reading paused at book 829
  (806–829 recorded; sheets ready up to 1177). Gathering only: front pages of 150 multi-file sets without page images
  (data/names/front-need-sets.txt → logs/front-pages-sets.log). Book 822 (dup of مختار الأغاني 03) NOT set aside yet.

## 2026-10-11 night → owner back on 2026-10-12: REOPEN THE PREVIEWS FOR HIM (carefully, nothing applied before his word)
Open in Brave (review_server.py on 127.0.0.1:8765 must be running; restart it alone if not):
  1. http://127.0.0.1:8765/plan-318.html        — names of books 332–805 (+ books read further), NOT applied
  2. http://127.0.0.1:8765/decisions.html       — his open decisions (Arabic), nothing applied
  3. http://127.0.0.1:8765/ocr-review-001.html  — OCR sample (10 books), nothing on the phone
  4. http://127.0.0.1:8765/crop-review-003.html and crop-review-002.html — crop batches to spot-check
Rebuild each page first (plan_review_page.py plans/318-names-read.tsv; owner_decisions_page.py; crop_review_page.py NNN for any
new batch) so they show the latest state. The owner wants pages in Arabic.
Running: crop_library.sh (batch 004 since 19:50, follows the phone's address), phone_watchdog.sh (follows the address:
the phone alternates .100 ↔ .102 — random MAC; he was told to set «device MAC» + a DHCP reservation), review_server.py.

## 2026-10-11 — names: all 806 single books read; plan 318 waits for the owner
- Plans 315, 316, 317 applied (owner-approved): 477 single books renamed from their title pages.
- Books 332–805 read today (data/names/title-read.tsv; hand-written names for shortened ones in data/names/name-override.tsv).
- plans/318-names-read.tsv (232 rows, dry run 232/0) → http://127.0.0.1:8765/plan-318.html — NOT applied; wait for the owner's «أوافق».
- data/names/owner-actions.tsv: 45 owner-side items (pieces of larger books 13, copies to compare 6, fixes 4 incl. reversed page order 724
  and wrong rotation 762, replacements, stray one-page covers 709/804, additions). Held out of rename plans.
- scripts/phone_watchdog.sh runs detached (pauses phone jobs while FTP is silent; it worked 08:10–09:42).

## 2026-10-10 01:30 GMT — STATE FOR A FRESH SESSION (owner: «I want to start a fresh discussion, then complete the work overnight. I'm unhappy with some old work not being successful, like the reorganizing and number/naming fixing»)

### RETRY LATER (owner 2026-10-10): the complete «كتاب القوافي» ت عوني عبد الرؤوف (مكتبة الخانجي): the phone copy stops at
p. 105 of ~264; Waqfeya FP1529 / FP145297 and archive.org 4730pdf are dark or the same truncated scan. The complete 1970
edition (ت عمر الأسعد ومحيي الدين رمضان، دار الإرشاد) was added (queue 312). Phone IP now 192.168.11.100. Laptop disk 7 GB free.

### 2026-10-10 ~06:00 — STATE: names from the books themselves (owner's priority); crop postponed
Owner's decisions this session (all in AGENTS.md §4 and memory naming-rules-2026-10-10):
- NO parentheses anywhere: «<title> - <author> - ت <editor> - <publisher>، <city>، <year>» («ط …» when no editor,
  «ترجمة …» for a translator, «- رسالة ماجستير», «- مخطوط» at the end); volumes «NN - <folder title> - <label>.pdf».
  Nothing shortened when it fits (200 B); publisher gives way first, then title tails (joined titles keep heads).
- Names come from the book's own pages; Shamela card AND Waqfeya record looked up by title whatever the source; when
  anything is missing or doubtful → read the file. Watch for wrong books / other editions. ALL names (also those named
  before) must reach the same format and completeness. Crop can wait (owner: «يمكن تأجيل مهام القص»).
- Plan 310 was applied by mistake and undone; plan 311 (singles, DRY) is superseded — do not apply it.
Tools (all committed): scripts/name_compose.py (names), read_status.py (what was read before → data/names/read-status.tsv:
1,073 read, 445 sheet only, 4,449 never), title_sheets.py (reading sheets from data/inspect/pages; sidecar .txt with the
Shamela + Waqfeya candidates), title_read_add.py (record readings: «n | verdict | title | author | editor | publisher |
city | year | kind | section | note»), names_from_reading.py (reading → name), auto_check.py (OCR/text-layer check of every
unread book → data/names/auto-check.tsv: confirmed 818, partial 786, CONFLICT 2,219 (mostly OCR failing on calligraphy:
refine by checking the imprint page separately), no-text 1,071).
Progress: singles sheets s0000–s0402 (806 books; 141 without page images: data/names/sheets/no-pages.tsv). READ 0–183
(data/names/title-read.tsv). Next: sheet s0092 (book 184). Findings so far: many «other-book» (the file is a commentary,
a collection, or another work than the name), «part» (one volume of a set: stays a folder), typos (بئر العزب، القصص المية).
RUNNING also: scratch/inspect_after_crop001_2026-10-10.sh (waits for crop 001, inspects the 1,333 never-inspected files —
the 141 page-less singles first — OCR, auto_check, commit; log logs/inspect-2026-10-10.log). Names: ≤ 240 bytes (phone limit 255), no year (owner, later).
RUNNING: scratch/after_ocr_2026-10-10.sh (OCR of 5,334 queued front pages → auto_check → commit; log logs/ocr-2026-10-10.log);
crop batch 001 (ends ~06:30; library chain stopped by the owner).
Unreadable names → site/names-unreadable.html, one by one with a local copy (scripts/report_unreadable.py add N "why"
after reading further with pages_sheet.py); the owner checks/comments there through scripts/review_server.py
(http://127.0.0.1:8765/, running; restart it after a reboot) → READ data/names/review-comments.jsonl at the start of
each session. Hard cases left to read further: 30 (poet's name), 128 (edition); closer look: 20 44 63 75 97 98 99 105
109 112 117 134 138.
Next steps: (1) refine auto_check (imprint page vs title page, Shamela/Waqfeya fields matched in the OCR text) so «confirmed»
books are named without eye reading; (2) read by eye only CONFLICT/no-text/incomplete; (3) a names plan from readings +
auto-check (dry-run, sample to the owner, then apply); (4) the same for folders and their volume files.

### 2026-10-10 02:20 — agenda set with the owner; plan 310 applied by mistake and undone
- Owner's order: names first — (a) single books in folders, then (b) raw numbers / «الهدية», (c) the editor in names,
  (d) title pages for the 1,165; each pass: a sample shown to the owner BEFORE it is applied. Crop: batch 001 then continue
  to the library without waiting (owner); build the review page of telling samples for the morning anyway.
- scripts/singles_plan.py v2 written (plan 310). It was applied by mistake (apply_plan.py applies by default — always
  --dry-run before approval): 659 moves, then undone at the owner's word (undo-310-singles, verified on the phone).
  plans/310-singles.tsv is a record only — never rerun it; the next singles plan gets a new number after the owner's OK.
- Open question to the owner: §4 asks for the SHORT title in a single file's name; plans 306/308/310 kept the full title
  (shortened only past 200 bytes). Wait for the owner's choice before the next singles plan.
- Held by v2 for reading (data/review/singles-review.tsv): 91 «01 -» without evidence, 51 file name ≠ folder name
  (e.g. «الوسيط في تراجم أدباء شنقيط» holds «نجم الحيران»), 49 cut names, 11 names taken (8 OpenStax books both as folder
  and plain file: check as duplicates).
- Crop of the whole library STOPPED by the owner (03:40, before it started): the rules let almost everything through
  (median text gain +13 % < 15 %, so most books qualify by small tilts ≥ 0.2°: 56/60 sample, 13/13 batch 001), the
  two-column index tilt is still open (most classical books end with such an index → would be redone), ~6 weeks of
  laptop + 174 GB over Wi-Fi. Next: batch 001 ends (~04:30) → review page of telling samples for the morning → fix the
  two-column index tilt → the owner chooses the scope (e.g. gain ≥ 15 % or visible tilt ≥ 0.5°, the books the owner reads first).
  scripts/crop_queue.py + crop_library.sh stay ready (no batch-002 was made).
- Names: AGENTS.md §4 rewritten with the owner's rules (03:45): nothing shortened when it fits, all info (editor,
  publisher) from evidence, no () inside titles nor around volume labels («NN - <folder title> - <label>.pdf»), publisher
  first to go, then title tails («جمع الجوامع ويليه همع الهوامع»); scripts/name_compose.py builds them (dry samples shown).
- Crop and renames at the same time: DONE (8a45a79) — crop_batch follows logged moves before staging and before the
  append; crop_queue skips a book cropped under any earlier name.

### Running now (leave it, it resumes on its own)
- Trial crop batch 001 on the phone: `scripts/crop_batch.py data/crop/batch-001.txt crop-batch-001 --workers 4` →
  logs/crop-batch-001.log, data/crop/done.tsv (resumable), data/crop/recipes/<md5>.json, before/after sample images in
  ~/.cache/phone-library/crop-sheets/<hash>/ (telling pages: notes kept, pages shrunk to fit, turns, short pages).
  7 workers swapped the laptop (15 GB): keep ≤ 4 (one large book took 3.2 GB). When it ends: build a review page from
  the sheets for the owner (he asked for interesting samples, not whole books), then batch the library under the same rules.

### WAITING FOR THE OWNER (2026-10-10 evening): plan 313 (258 single books named from their title pages, 42 section moves)
— review page http://127.0.0.1:8765/plan-313.html (scripts/plan_review_page.py); read the comments (report «plan-313»)
and apply only after «أوافق». Held: data/names/plan-held.tsv. OCR sample 001 (10 books, scripts/ocr_clean.py →
data/improve/ocr/, log logs/ocr-sample-001.log) → review page scripts/ocr_review_page.py 001 when done; unpaper + jbig2
are now installed (~/.local/bin): next variant = ocrmypdf --clean + -O1 (lossless JBIG2).
### CROP RUNNING (2026-10-10 18:05): regression 0 failures (logs/crop-regress-2026-10-10e.log; crop_regress judges column-levelled
pages by their columns); scripts/crop_library.sh started batch-002 (300 books, 4 workers) and continues by itself. Batch 001's
books with two-column index pages still need a redo. Stop: kill the PID of crop_library.sh, then its crop_batch.py.
### CROP (2026-10-10 evening): the two-column fix is in book_crop.py (columns_tilt); regression run logs/crop-regress-2026-10-10d.log;
scratch/crop_after_regress_2026-10-10.sh starts scripts/crop_library.sh by itself if it ends with 0 failures (owner: the crop
must run while the agent's quota is paused). Check logs/crop-library.log. Batch 001's books with two-column index pages
still need a redo (crop_batch --undo + crop) — not done yet.
### CROP GATE (owner 2026-10-10, «are you solving this for what's coming»): NO crop batch may start before
(1) the two-column index tilt fix (design below: gutter + per-column edge_tilt, both columns agree) is in book_crop.py with
الفوائد 456/457 as «turn yes» and المثلث 499 / الاتباع 98 / الفوائد 446 / فهرسة 355 as «leave» in crop-regression.tsv, and
crop_regress passes; (2) the «cut at the source» check exists (ink touching the image's own edge on text rows → listed,
never cropped tighter). Then re-measure batch 001's 50 books and redo (crop_batch --undo + crop) only those with two-column
index pages; show the owner a sample before any further batch.

### Crop method (scripts/book_crop.py, commit 9463719 + bda4ec5): regression 0 failures (data/improve/crop-regression.tsv)
- Rules the owner set on 2026-10-09 (all in the docstring): one page size per book, exact (frames: a larger part is shrunk
  to fit, never a wider page); margins 6 % of the text width; marginal notes kept (notes_of); uploaders' stamps found by
  their recurrence and again at any size by their grey image, left out of every measure and erased with a white patch
  (stamps_of, erase_stamp); short pages placed by their page number (folio axis), a flush edge, else centred on themselves;
  crop only for a real gain (text ≥ 15 % larger) or a flaw (tilt, off-centre, sway, bands, stains); a good scan whose only
  flaw is tilt → level only; tilt certified by the shear measure + image, or the line-by-line ruler (baseline_tilt), or
  the lines' edge (edge_tilt) for lists; stains dodged only while margins stay balanced; `--jobs N` shares one book's
  pages among N processes (urgent single books).
- Done on the phone: الفوائد المحصورة (crop-urgent-001e; the owner reviewed it page by page).
- Random sample of 60 scans (laptop copies): 56 crop, 3 level only, 1 left as it is — nearly every scan has many tilted
  pages (median 56 % of the pages ≥ 0.2°) and sway; text gain alone is modest (median +13 %).
- NOT DONE — tilt on two-column index pages (owner: «لم تعالج ص 456 وجميع الفهرس»): all whole-page measures are fooled there.
  Designed and measured (not in the code; the draft was reverted untested): find the gutter (emptiest pixel column at
  30–70 % of the width, ≤ 2 % of the fullest), run edge_tilt on each column; if both columns' line starts read the same
  tilt (within 0.15°) of ≥ 0.3°, try turns −u ± 0.05·k (k = −3…3) and keep the one leaving both columns' edges ≤ 0.15°,
  else record it as disputed. Measured: الفوائد 456 −0.36/−0.33 (tilted), 457 0.65/0.61 (tilted); must stay unturned:
  المثلث 499 −0.80/−0.51 (disagree), الاتباع 98 −0.17/−0.24 (small), الفوائد 446 0.25/0.42 (disagree), فهرسة 355 (one side).
  Add 456/457 as «turn yes» cases, run crop_regress, then redo الفوائد on the phone (undo + crop_batch --jobs 8).
- NOT DONE — damaged source scans: in الفوائد المحصورة the uploader's scan cuts the index's left column (ص 456 «٢٥٢، ٤٠٦»,
  ص 468 «اليربوعي»): the archive.org original MQSORH.pdf has the same images. Build a check: ink touching the scanned
  image's own edge on text rows → list the book and its pages (data/review/scan-cut.tsv) and look for another copy.

### Names and organisation — the old work the owner is unhappy with (priority for the fresh session)
- 2026-10-09 this session: 307 (شرح مقصورة ابن دريد: الصاوي / التبريزي), 308 (scripts/name_fix_plan.py: 161 books, 327 files —
  author from Shamela's common name or the exact-size Waqfeya record, full titles, «صلى الله عليه» completed, single books in
  folders → plain files, titles' «لفلان» dropped when it names the author; magazines/series excluded), 309 (أضواء من المولد
  السعيد — كامل كيلاني, title page). compare_shamela: two full names are one man when their distinctive «X بن Y بن Z»
  agree (أبو الشيخ = Waqfeya's «الحباني») → 8 more Shamela matches, death years shown instead of centuries.
- Still wrong (counts on 2026-10-10):
  * 1,178 books stored as one file in a folder of their own (§4: plain files) — 176 of them «01 - …» alone; 99 of those
    are plan 066's mistake (an uploader's gift number «الهدية (N)» turned into a volume number «01 -»).
  * 4 names still «الهدية (N) …»; 679 file names start with a raw number (some are real issue numbers, e.g. عالم المعرفة).
  * data/review/name-fix-review.tsv: 1,165 books whose author/title is missing or cut and no record proves the right one
    (1,130 «no evidence») → title pages must be read (pdftotext for typeset ones, low-res renders read by eye otherwise).
  * HANDOFF 2026-10-06 list still open: death year for every author (2: done for Shamela-matched books only), category
    audit (4), header numbers (5).
  * Owner 2026-10-10: «ذكر المحقق ليس مشكلا، بل ينبغي» — the editor belongs in every name where it is known: when the
    exact-size record or the title page gives the editor and the name lacks it, add it («(ت المحقق - الناشر)»), e.g.
    «أخلاق النبي وآدابه … (ط دار الكتاب العربي)» → «(ت السيد الجميلي - دار الكتاب العربي)»; «تاريخ بغداد (ت بشار عواد)» lacks
    its publisher (دار الغرب الإسلامي, 2001 — confirm on the title page). A cut in the source scan is flagged only after the
    original is checked (owner: «When sure it's not because of the cropping, it's fine»).
  Ask the owner first which of these hurts most; propose a single, tested pass per defect with a sample read by eye before
  any plan is applied (the earlier passes failed exactly where no one read the result).

## 2026-10-09 07:05 GMT — owner pauses me until 09:50 GMT (one-shot resume scheduled); unattended jobs running
- RUNNING (CPU only, read-only on the phone): crop_regress (logs/crop-regress.log) after book_crop's joint search for the
  turn (10 angles, 0.05° apart), level = ≤ 0.15° shear and ≤ 0.2° image, curved pages kept at ≤ 0.25° and ≤ 1/3 of their
  tilt; and the sample-4 build (scratchpad v5/drive.py → v5/drive.log; then v5/build.py → site/samples/crop-2026-10-09/).
  On resume: read both; if crop_regress = 0 failures and the sample is built, look at every image, then open it for the
  owner. Re-create the hourly check-in cron (:23) after resuming (deleted for the pause).
- Done this morning: 290 (13 books), 291–293 (owner: two wrong uploads deleted, نوادر الأصول ط السايح completed),
  294–296 (منتخب الأحكام duplicate scan; الإحكام للقرافي folder split into its two editions). Owner kept all 226 books of the
  scope page.

## 2026-10-09 09:30 GMT — pre-700 missing books: verified by edition; duplicates found and removed; crop test rerunning
- dark_replace v2 (page images read, edition from the first 4 pages only) → 280: 9 uploaded after reading each title page;
  4 of all the uploads from other sources (274 + 280) were ALREADY on the phone under other names (same scans proved,
  better copy kept: plans 284–289). New guard: scripts/samework.py (same opening words in order + author's surname),
  used by dark_replace.py and waq_queue.py; compare_waqfeya Rule B does the same, so the Waqfeya comparison no longer
  lists such books as missing.
- Review list data/review/280-dark-review.tsv (87): 14 on the phone under other names; 13 read by eye and accepted →
  queue 290 (9 = the record's edition, 4 = another edition named from its title page: فضائل شهر رجب ت الأثري، الشرح والإبانة
  ت آل حمدان، دلائل النبوة ط حيدر آباد 1320، فضائل الأعمال ط جمعية البر). Rejected by eye: المبعث والمغازي (أبان بن عثمان, another
  book), قبول الأخبار k-509 and الأباطيل k-506 (modern refutations/compilations), عمدة ذوي الهمم (a commentary), السنن الأربعة
  (only سنن أبي داود), الاعتقاد 524Pdf (a manuscript), and nnn10181 — an ISIS publication («الدولة الإسلامية»): never to be added.
  About 60 books remain with no proved copy (no candidate, or none showing title + author): a wider search (other titles of
  the work, the author's name in archive.org metadata) is the next step; nothing uploaded without the title page read.
- Set aside in «نسخ مستبعدة» for the owner (274's wrong uploads): الإنصاف (typed al-mostafa), اعتلال القلوب (a thesis about it),
  نوادر الأصول ج 1 ط السايح — the right editions of all three are now on the phone.
- Crop: book_crop second tilt measure on a 700 px image (guard ≤ 0.2°: it is coarser), the shear measure must read
  ≤ 0.1° after up to 3 refinements; halves rule = whole angle within the halves' range ±0.1° and halves ≤ 0.6° apart
  (the owner's p. 387, a slightly curved page); crop_regress counts tilted-but-unturned pages as failures; 19 page cases.
  RUNNING (logs/crop-regress.log). Then rebuild the sample: scratchpad v4/drive.py + build.py (move v4/*.json and sheets to
  old5 first), look at every image, then open it for the owner.

## 2026-10-09 06:00 GMT — owner back; last night's additions checked by eye; partial sets completed
- Owner (2026-10-09): title + author is not enough to accept another upload. The 8 books of 274 read by eye (title page,
  imprint, end): 5 right (named now with their real editions: plan 276), 3 wrong, set aside in «نسخ مستبعدة» for the owner
  (الإنصاف = typed al-mostafa copy; اعتلال القلوب = a master's thesis about it; نوادر الأصول = ج 1 only of the السايح edition).
  BEFORE touching the 92 dark books again (data/review/274-dark-review.tsv), scripts/dark_replace.py must: prefer a file
  of the original's exact size (e.g. «النسخة المسندة» of نوادر الأصول: items 01081 / alfirdwsiy2018_gmail_1639, 27,072,504 B ≈
  the record's 26 MB), else match editor / publisher / pages / volumes from the record (details.jsonl AND details2.jsonl)
  against the imprint page; refuse theses, typed copies (al-mostafa, shamela), single parts of a multi-part set.
- «TITLE ON PHONE» skips (waq_queue): of 11, 4 were other authors (handled 2026-10-08), 5 are the same books (أخبار المدينة،
  ديوان كشاجم، مقاصد الصوم، فوائد الصوم، الغرباء — the phone copies were checked from their title pages; their provenance points
  at wrong Waqfeya records, so the catalog shows wrong authors), 2 really missing: الأموال لأبي عبيد (its record links
  إمتاع الأسماع) and الأمثال والحكم للماوردي (item dark) → to the dark list.
- Owner: «Complete them» (editions on the phone with volumes missing); «Leave them» (the 7 wrong-link, mostly modern books).
  277 (6 moves + 40 files): النحو الوافي 4 vols, التفسير البياني 2, الزركشي ت ابن جبرين 7 + cover, مسند أحمد ط بيت الأفكار + its
  فهارس, المغني ط المنار 12 + preface, البحر المحيط ت المهدي 8 + cover, صحيح البخاري ط بيت السنة 7 + المدخل etc., شرح علل الترمذي
  ت عتر + مقدمة التحقيق. التنبيه والإيقاظ was already complete (same page images + a front page). 278/279: الروض الأنف ت الوكيل —
  two PRINTINGS (دار الكتب الحديثة 1387 complete; مكتبة ابن تيمية 1410, folder misnamed) → names fixed, ابن تيمية's ج 4–7 added.
  TODO: publisher of the ابن جبرين الزركشي (title page) → folder name; labels of the new volumes vs embedded titles
  (inspect run: logs/inspect-277-278.log).
- Crop: regression 0 failures, but «tilted, not turned» pages were real tilts (8 of 10 checked by a second measure) —
  0.1 read as 0.1000000001, no refinement. Now: LEVEL tolerance, refinement (3 rounds), a second independent measure
  (proj_tilt: the page image rotated) that must agree; crop_regress counts untreated tilts as failures; 9 new cases.
  RUNNING crop_regress (logs/crop-regress.log). Then rebuild the sample and look at it before showing the owner.

## 2026-10-08 20:55 GMT — session limit; unattended work running
- Pre-700 missing (owner: download all, after checks): chain 271 ran — 118 ids, but 94 archive.org items are DARK (removed);
  4 files added (271), غريب الحديث لابن الجوزي added (275: the «title on phone» skip was another author's book — also المعجم
  لابن المقرئ, دلائل النبوة لأبي نعيم, الناسخ والمنسوخ لعبد القاهر البغدادي, all dark). waq_queue's «TITLE ON PHONE» needs an author check.
- RUNNING: find_on_archive.py on the 100 dark books (log logs/find-on-archive-274.log) → chain scratch/dark_chain_2026-10-08.sh
  (log logs/dark-chain-2026-10-08.log): scripts/dark_replace.py verifies candidates from their title pages (title ≥ 60 %
  + author), queues only those, fetch_queue, refresh, commit. The rest → data/review/274-dark-review.tsv: to read by eye
  (contact sheets of title pages) — the automatic check is strict (it refused an abridgement of دلائل النبوة: good).
- Crop: crop_regress → 8/9 page checks PASS; FAIL اللآلئ ج 1 p. 4 streak (box at the page edge) → fixed now (content
  moves the last points on white paper) — RERUN `python3 scripts/crop_regress.py` (results cached per book_crop.py version).
  Book-wide: 1 page each still tilted after turning in فهرسة ابن خير (324), المثلث (489), الاتباع (68) — inspect (curved page?).
  Then rerun the sample (scratchpad v4/drive.py + build.py — or rebuild them) and look at it before showing the owner.

## 2026-10-08 20:30 GMT — owner paused me until 21:10; unattended chain scratch/pre700_2026-10-08.sh running
- Owner: «نواقص ما قبل 700 هـ (113 كتابًا مفقودًا) حمّلها كلها بعد التدقيق…». Chain (log logs/pre700-2026-10-08.log): ids from the
  fixed Waqfeya comparison → queue 271 (only linked files, sizes already on the phone skipped) → fetch_queue (full speed,
  verified) → index → additions_audit (272 remove bundled other books/copies, 273 names) → refresh → commit. If it stopped
  before «chain done», rerunning it resumes (fetch_queue .done/.failed); after «chain done» never rerun.
- Waqfeya comparison fixed (0f9a4c2): «ناقصة المجلدات» 22 → 5 real gaps (الزركشي ت ابن جبرين cover only, فهارس مسند أحمد,
  التنبيه والإيقاظ, التفسير البياني ج 2, النحو الوافي ج 2–4); 67 records whose link points to another book's file are now missing
  (data/review/waqfeya-link-mismatch.tsv). Duplicate to compare: الروض الأنف ت الوكيل stored twice (a 4-file set and the complete
  7-volume set). Owner to decide: completing المغني ط المنار / البحر المحيط ت المهدي (other complete editions on the phone).
- Crop: level check added; scripts/crop_regress.py running (logs/crop-regress.log) — all PASS before the next sample.

## 2026-10-08 19:30 GMT — crop sample 3 open for the owner; scope review page published
- Crop sample «الصيغة الثالثة» (24 books incl. the owner's own examples: اللآلئ ج 1 p. 4 streak now outside the box, the
  stamp page p. 381 centred by moving its content, وحي القلم's faint chain frame kept, levelled pages in اللآلئ (292/337),
  شرح أدب القاضي (599), البكاء (83)). book_crop.plan(): narrowest box that passes (95 / 98 / 100 % of the pages' widths),
  stains dodged, faint printed frames/rules kept (band coverage), border grains / sheet edges / corner marks / dust
  groups out, lossless deskew guarded (same text block ±5 %). WAITING for the owner's verdict before any batch.
- Owner's collection scope (memory collection-scope): no popular da'wa tracts, no ordinary theses, few 21st-century books;
  great 20th-century studies, translations and major scholars welcome. scripts/scope_review.py → 226 candidates
  (48 theses, 31 tracts, 147 recent; 38 by major scholars, data/mappings/major-modern-scholars.txt) → review page
  https://claude.ai/artifact/JbuSXTMakRVwEGAWHaPeRe (ticks: ArtifactData get decisions/current → remove[]). Removal =
  owner's ticks only, through a logged delete plan. Expansion: waiting for the owner's go (phone on the charger).
- 269 (19:20): التمهيد is three editions, not duplicates — names from their title pages: مؤسسة الفرقان (ت بشار عواد معروف
  وآخرين; was labelled «وزارة الأوقاف المغربية»; ج 1 MISSING, the 1-page file is ج 5's cover), وزارة الأوقاف المغربية (ت العلوي
  والبكري; 26 vols), مرتبا على الأبواب الفقهية (ت أسامة بن إبراهيم, الفاروق الحديثة; was «ت ياسر بن إبرهيم»).

## 2026-10-08 17:15 GMT — crop method v4 (owner's review of the second sample)
- Done: 267 (المقاصد front pages, by the chain) and 268 (the 100 ppi المقاصد copy deleted); refresh committed.
- Owner's notes on sample 2 and what v4 does (scripts/book_crop.py):
  * stains / torn-edge streaks (اللآلئ ج 1 p. 4) → left out of the box (orange): streaks = tall ragged marks near a side
    beyond the text block; stains = solid irregular marks ≥ 5 mm, alone, ≥ 5 mm from the text, ≤ 3 % of the page, not
    repeated on 3+ pages (else print); their detached pieces too. Scanner edge noise, sheet-edge lines and corner marks
    (purple) and dust groups (blue) also stay out. The text block is measured mark by mark (one streak cannot drag it).
  * tilted pages → levelled LOSSLESSLY (a «q cos sin -sin cos e f cm» stream + «Q» around the content; images untouched;
    the sign is checked by re-measuring); vertical centring kept; box height = tallest page (gain is in the width).
  * the stamp page glued to an edge (فهرسة ابن خير p. 381) → odd pages are centred on their own text; when the box cannot
    move enough on the page, the CONTENT moves (white paper ≥ 235 only). A page needing a > 2 % shift of the usual place is
    such an odd page; whole pages only when the text is wider than the box (≤ 5 % per book).
  * second check at 1,000 px: every mark outside a box must be one the first pass excluded (same place ± 3 pt).
  * cleaning (painting specks/stains) DROPPED by the owner — never paint.
  * المجلد 78 (مجمع دمشق) is a 70 ppi 1-bit al-mostafa scan: owner: no need to replace it.
- Sample run in the session scratchpad (v4/drive.py → v4/build.py → site/samples/crop-2026-10-08/index.html). Waiting.
- Owner asked whether to continue the expansion in parallel: I said yes (crop work is local), with the phone on the charger
  and paced downloads; waiting for the go. Earlier queues are complete; library 172.2 GB (target 200 GB).
- DONE 270: the folder «الكتاب - سيبويه (ت هارون)» was محمد كاظم البكاء's 6-volume edition (covers) — renamed; Haroun's is the
  folder «الكتاب (كتاب سيبويه) (ت عبد السلام هارون - الخانجي)».

## 2026-10-08 08:55 GMT — session ended; unattended chain scratch/after_v3_2026-10-08.sh (log logs/after-v3-2026-10-08.log)
- Owner on the first crop sample: «مبهر», but asked (a) the text centred horizontally, consistently on every page, (b) ordinary
  books (text ≈ 72 % wide, e.g. وحي القلم) enlarged moderately too, if consistent on every page. → book_crop.py v3: one box
  size per file, centred on each page's own text block (short pages take their full neighbours' place), edge shadows
  excluded and bounding the box, printed frames kept (وحي القلم's faint chain frame = 82 % of the width → only +7 %),
  crop when the text gets ≥ 6 % larger or was ≥ 2 % off-centre; the 1,000 px check moves the box before leaving a page whole.
- The chain waits for the v3 re-analysis of the 22 sample books (session scratchpad crop/v3_drive.py), rebuilds
  site/samples/crop-2026-10-08/index.html («الصيغة الثانية») and opens it in Brave → owner's verdict needed before any batch.
- Then it uploads queue 267 (المقاصد الشافية: title pages + imprint of ج 4, 5, 6, 9, lossless copies) and commits.
  NEXT SESSION: check the log ends with «chain done» and the 4 files are in index-now; then plan 268 = delete the 11 files
  of «النحو والصرف/المقاصد الشافية في شرح الخلاصة الكافية للشاطبي/» (proof in the section below), refresh, commit.
- Found: «النحو والصرف/الكتاب - سيبويه (ت عبد السلام هارون - مكتبة الخانجي)/02 - الكتاب - ت هارون.pdf» is NOT Haroun's
  edition: title page «الطبعة الكاملة الأولى… أ.د. محمد كاظم البكاء… منشورات زين الحقوقية 2015» (it quotes Haroun's notes).
  Read every file of that folder's title page, then split/rename by edition (plan).
- The old exploration stream (v2 rules) was stopped; its results are obsolete. Crop batches: not started (owner's approval first).

## 2026-10-08 08:15 — PAUSED by the owner until 10:10 GMT (laptop clock = GMT; times in these notes are GMT)
- Still running (read-only on the phone, safe): the crop exploration stream (session scratchpad crop/sample_drive.py).
- المقاصد الشافية — IN PROGRESS, nothing changed on the phone yet: the 100 ppi set «النحو والصرف/المقاصد الشافية في شرح الخلاصة
  الكافية للشاطبي/» (11 files) is the same printing (جامعة أم القرى 1428، العثيمين وآخرون) as the 300 ppi set «… - الشاطبي (ت عبد
  الرحمن بن سليمان العثيمين وآخرون - جامعة أم القرى)»: same_scan.py --visual (new background-relative signatures) paired every
  volume at a constant page offset; the extra pages of the 100 ppi set are (a) the detailed contents of each volume copied
  byte for byte from its own ج 10 (present in the 300 ppi ج 10), (b) decorative basmala pages (one kept in the 300 ppi
  ج 1 «تقديم»), (c) the title page + imprint of ج 4, 5, 6, 9, which the 300 ppi set lacks → extracted losslessly (same image
  streams) into downloads/maq-fronts/{04,05,06,09}.pdf, queue data/queue/267-maqasid-fronts.tsv (NOT run yet). Next: run 267,
  index_update --add, then delete the 11 files (plan 268), refresh, commit.

## 2026-10-08 07:50 — crop method v2 (sample waiting for the owner) + duplicate editions resolved
- scripts/book_crop.py: ONE box per file, same size on every text page (odd/even placed separately), holding every ink mark
  of the book (marginal notes, page numbers, running heads) + 12 % of the text width each side; only isolated specks
  (≤ 1.4 mm, ≥ 5 mm from any mark) may fall outside; every page re-checked at 1,000 px (a page that does not fit stays
  whole; > 3 % such pages → file left as is); crop only when the text gets ≥ 18 % larger on a phone. CropBox only.
- Findings: the inspection's margins (20 dpi, 3 pages) lose thin print → most «wide» files are ordinary books (text
  70–85 % of the width) and are rightly left alone; of the files analysed so far ≈ 1 in 3 of the screened ones is a
  clear case. Sample page: site/samples/crop-2026-10-08/index.html (20 books + 3 left alone) — NOTHING applied; wait for
  the owner's word, then batches, each with its own sample page (book_crop.review_page).
- Exploration run (scratchpad, phone read-only): streams the 668 screened files (data/inspect «all 3 sampled pages
  < 62 % wide») through book_crop analyse; recipes are only kept in the session scratchpad.
- Duplicate editions resolved (same_scan.py, now also --sets for copies split differently): 254/255 فضائل شهر رمضان,
  استيفاء الأقوال; 256/257 مسند الحميدي (the «الأعظمي» set was حسين أسد's, same scan; its cover joined the kept set);
  258/259 المنتقى للباجي (شروح الحديث set deleted, ج 2/3 there lacked 2 pages each; kept set renumbered 01–07, binding cover
  + title page as 00); 260–262 المفهم (set without author deleted; kept set named and labelled from the PDF titles — 261
  shifted the labels by one (zsh arrays start at 1), 262 corrected it); 263/264 دلائل الإعجاز (100 ppi 3-file copy deleted,
  the 400 ppi file kept in البلاغة); 265/266 الإتقان: the 3,102-page file is مجمع الملك فهد's edition (مركز الدراسات
  القرآنية; its 114-page مقدمة التحقيق joined it), the 4-volume set is أبو الفضل إبراهيم's (two copies of its تصدير deleted,
  one of them labelled «الفهارس العامة»). Still to compare: المقاصد الشافية, التمهيد, and the «To check» list below.

## 2026-10-08 06:35 — incident: 19 restored originals deleted by a rerun; fetched again (queue 247)
- 05:33 phone back → my chain: 224 substituted the 19 originals (05:38), plans 236–246 applied, refresh, commit de0d1a7.
- 06:14 the owner asked Antigravity (Gemini, ~/.gemini/antigravity/brain/068a0a41…) whether the ready scripts would be launched;
  it reran scratch/restore_recompressed_224.py and all sheet plans. The plans skipped (already applied); the 224 rerun set
  the 19 restored originals aside (step a), its step b failed (no copies left), step c deleted them.
- Fixes: apply_plan exits 1 on any failed move; substitute needs the copy in index-now; the one-off refuses to rerun;
  AGENTS.md rule «never rerun a scratch script or an applied plan; one agent at a time».
- Repair: scratch/refetch_247.sh (log logs/refetch-247-chain.log): data/queue/247-refetch-originals.tsv fetches the 19
  originals again (archive.org, exact sizes) straight to their paths, full refresh (index-now listed the 19 though gone), commit.

## 2026-10-08 02:20 — phone off the network; chain waiting (scratch/when_phone_back_2026-10-08.sh, log logs/when-phone-back.log)
- 224 restore: 18 of 19 originals uploaded into «نسخ محسنة للاستبدال» (exact sizes); «الشفا» (1.77 GB) staged in
  downloads/queue, its upload refused when the phone left. NOTHING substituted yet. The chain reruns the restore (upload
  resumes from the staged file), substitutes the 19, applies plans 236–238, refreshes (guarded full listing), commits.
- Plans 218, 220–223, 225–235 applied tonight (sheets 230–272). If the chain did not run: start it again (resumable).

## 2026-10-08 03:00 — crop revert finished; title-page plans waiting
- Crop revert (212): 3,734 listed; 3,638 by the two lanes; 92 more by scratch/redo_revert_212.py (lanes had raced on
  «نسخ مستبعدة/__المستبدل» folders: 553/550 errors, originals stayed, copies waited — all substituted 01:30, 0 FAIL);
  4 left (نكات القرآن، الحاجب المصحفي، إحياء علوم الدين ج3/ج4: offset MediaBox) — fix_pdf.uncrop fallback written and
  tested on a synthetic file; redo with `python3 scripts/revert_crops.py lists/212-redo.tsv --prefix 212-r2-`.
  219 deleted 12 obsolete cropped copies; 2 lossy copies stay in «نسخ محسنة» (المقنع، تفسير الطبري شاكر: originals intact).
  NEVER run two lanes that create/remove folders under the same parent again.
- refresh.sh now refuses a cut-short listing (one 2-checker listing returned 3,953 of 16,579 files with no error).
- Plans written, to apply when the phone is free (dry-run, then apply + index_update): 218 (retry), 220, 221, 222, 223.
- To compare (duplicate editions, owner's standing permission): المقاصد الشافية (two folders, both جامعة أم القرى 1428;
  one has an 89 KB ج 8); التمهيد (folder «(وزارة الأوقاف المغربية)» 17 files vs the unlabeled 27-file Awqaf set; a 1-page
  cover of the الفرقان edition «172271 - …» sits in the first); شرح التصريح على التوضيح files numbered 00/01/02 but 00 has
  758 pages (renumber from the title pages).
- To compare too: المنتقى للباجي — «الفقه المالكي/… (دار الكتاب الإسلامي)» (cover + ج 1–7) and «شروح الحديث/المنتقى في شرح
  الموطأ للباجي» (8 oddly numbered files, page counts = the same ج 1–7, not byte-identical) are one edition; المفهم للقرطبي —
  «… (دار ابن كثير)» and «المفهم لما أشكل من تلخيص كتاب مسلم» have the same imprint (دار ابن كثير 1417).
- To compare too: الإتقان — «… (مجمع الملك فهد)» (6 files) is in fact محمد أبو الفضل إبراهيم's edition (وزارة الشؤون الإسلامية السعودية,
  title page sheet 259), the same as «… (ت محمد أبو الفضل إبراهيم - وزارة الأوقاف السعودية)»; دلائل الإعجاز (شاكر - الخانجي) in
  «الأدب/دلائل الإعجاز للجرجاني» (one 21 MB file) and «البلاغة/دلائل الإعجاز في علم المعاني …» (3 files). Renumber: «الزيادة والإحسان
  في علوم القرآن - ابن عقيلة (ط جامعة الشارقة)» files 01–10 carry «(جزء 10)…(جزء 1)» (ج 5 missing).
- To check: «علوم القرآن وأصول التفسير/مداخل إعجاز القرآن - محمود محمد شاكر (ط. مكتبة الخانجي)» holds two files; the one read
  (02, sheet 266) is مطبعة المدني ودار المدني بجدة — read the other, then name/compare. «المصطلحات الأربعة في القرآن» holds two files
  (two copies?). «الأدب/لامية العرب - الشنفرى (مكتبة الآ)» and «الشعر ودواوينه/المقصورة - ابن دريد (مكتبة المعا)»: cut names.
- To check: «كتب السنة/الجامع المسند الصحيح المختصر - الإمام البخاري (طوق النجاة)»: its introduction (sheet 278, دمشق 1423/2002)
  describes a one-volume two-colour printing (دار ابن كثير?) — read its imprint page before naming.
- To check: «كتب السنة/المعجم الأوسط - الحافظ الطبراني (ت الطحان - دار الحرمين)»: imprint (sheet 282) is دار الحرمين 1415/1995,
  which is طارق عوض الله وعبد المحسن الحسيني's edition, not الطحان's (مكتبة المعارف) — read the title page, then fix the editor.
- To check: «كتب السنة/خصائص أمير المؤمنين علي بن أبي طالب رضي الله عنه - النسائي» (3 files: introduction, a file
  labelled «(بن أبي طالب…)», the book) next to the plain file «… بن أبي - النسائي (ط دار الكتاب العربي)»: which edition is
  each (sheet 287 showed مكتبة الآداب، عبد الرحمن حسن محمود)?
- DONE 250: عارضة الأحوذي — the «بشرح سنن الترمذي» set (14 files) deleted: same scan as the «بشرح صحيح الترمذي» set (same_scan.py).
- Duplicate to resolve: «كتب السنة/فضائل شهر رمضان - ابن شاهين (ت سعد آل حميد - مكتبة المنار)» (949,589 B) and «… (ط مكتبة
  المنار)» (1,382,605 B): identical imprint pages (مكتبة المنار، الطبعة الثانية 1410) — compare the scans, keep the better.
- Duplicate to resolve: «كتب السنة/مسند الحميدي - عبد الله بن الزبير الحميدي (ت الأعظمي - عالم الكتب)» — its vol 1 imprint
  (sheet 298) is حسين سليم أسد، دار السقا 1996, the edition of «كتب السنة/مسند الحميدي (ت حسين سليم أسد الداراني)»: compare.
- Renumber: «كتب السنة/موطأ مالك - رواية يحيى (ت محمد مصطفى الأعظمي - مؤسسة زايد…)» holds «01 - موطأ مالك (alt - 01).pdf»
  (24.8 MB, «alt» is forbidden by §4) next to «01 - … (المقدمة)» (8 KB): read the volumes, renumber.
- To check: «كتب اللغة/الصاحبي في فقه اللغة العربية … (ت أحمد حسن بسج - دار الكتب العلمية)» (2 files): file 1 is عمر فاروق
  الطباع's edition (مكتبة المعارف 1414/1993, sheet 303) — read file 2, then name (two editions? two copies?).
- Missing now: البطليوسي «ذكر الفرق بين الأحرف الخمسة» (the file so named was الحميد's رقية book, moved by plan 246).
- Duplicate to resolve: «مسائل فقهية/استيفاء الأقوال في تحريم الإسبال على الرجال - الصنعاني (ط مكتبة دار القدس).pdf» (545 KB,
  archive iatear) and «…/استيفاء الاقوال … للصنعاني/01 - ….pdf» (727 KB, imprint دار القدس 1412, sheet 310): same edition, two scans.
- To check: «مسائل فقهية/رفع اليدين في الصلاة - ابن قيم الجوزية (ط دار عطاءات العلم)» shows the imprint page (ISBN 978-9959-857-81-1)
  of «تحفة المودود» (sheet 311): read its title page — wrong file, or a shared imprint?
- Section moves to consider: «كتب عامة/صيد الخواطر/01 - صيد الخواطر.pdf» (دار الإيمان - الإسكندرية 2007) → الرقائق (Shamela).
- To check: «شروح الحديث/مفتاح المنهل العذب المورود … (ت ابن بيومي - مطبعة الإستقامة)» (8 files): its file read on sheet 251
  is «المنهل العذب المورود» ج 2 by the father محمود محمد خطاب السبكي (مؤسسة التاريخ العربي) — read every volume, then name.
- To check: «الدرة الألفية - ابن معط (دار الف)» (cut publisher; German apparatus = Zetterstéen's edition?); «الروضة
  الأنيقة في نصرة العفيفة الصديقة - الصامولي» filed under النحو (subject?); «المسائل الاعتزالية …» linked to Waqfeya
  «التبصير في معالم الدين» (data/review/waqfeya-link-doubts.tsv); phone names whose author slot holds the editor
  («المحدث الفاصل - ت - الخطيب», «الفروق اللغوية - ت - سليم», «ذم قرناء السوء لاين عساكر», «تفسير القرآن - تفسير السمعاني»).

## 2026-10-08 01:30 — Shamela comparison made accurate (owner: «الآن تستطيع تماما تمييز ما هو غير موجود؟», «… تعتمد على البطاقات»)
- scripts/export_shamela_cards.py: the local Shamela's book cards (8,598: printed title, full author, editor, publisher,
  edition, volumes, نبذة) + author biographies (3,190) → data/shamela/cards.jsonl, authors.jsonl (tools/shamela-dump, Shamela's JRE).
  books.tsv gained author_id. scripts/shamela_cards.py: edition line, same-edition test, match evidence in Arabic.
- compare_shamela.py: new tiers cover / part-of («ضمن آثار المعلمي»: 122) / card title; every older tier re-checked by
  plausible() (author agrees on a non-common name — NAMEFREQ from Shamela authors —, no abridgement/commentary/part/other
  recension); doubtful Waqfeya links ignored (data/review/waqfeya-link-doubts.tsv, 96 rows: provenance to fix);
  vetoed matches in data/review/shamela-vetoed.tsv. Result 2,868 → 3,064 present, errors removed both ways.
  Regression ids kept in my session; samples: present ≈ 96–97 % right; remaining «missing» probe ≈ 25 % present (phone
  names lacking the author, synonyms) — next: fix those phone names (review list from vetoed «exact (author)»).
- report_shamela.py: «طبعة الشاملة» column (cards), «الطبعة على الهاتف» (same edition?), «وجه المطابقة». TODO: main index
  book cards could show the Shamela card + نبذة; refresh.sh should run export_shamela_cards.py when the Shamela store changes.
- Owner 2026-10-08: specks surely not text may be painted with the background colour (memory speck-cleaning-rule) — part
  of the improvement method AFTER the revert, samples for his approval first.

## Owner's request (summary)
1. Fix errors/organization of the phone library (`phone:Books`, FTP 192.168.11.102:2221 (formerly .100, see AGENTS.md §2), ONE connection).
2. Grow phone library 128.9 GB → 200 GB. Priority: authors died before 700 AH; all missing books of
   علي بن محمد العمران; complete سلسلة عالم المعرفة (phone has 001–060) to the highest issue on archive.org (archive.org only).
3. Local library `~/Books` 23 GB → 30 GB: the best of the phone library (poetry, sira, adab, single-volume
   essentials for every Muslim) + all/most Shamela categories. NEVER touch `أبو العلاء المعري` and `ابن الزبير الغرناطي`.
   Owner: transfer directly, no list review needed.
4. Max speed/concurrency → rule §7 in AGENTS.md (done) + `scripts/fetch_queue.py` (done).

## Decisions / assumptions
- "before 700" = author's death year < 700 AH.
- Verified duplicates → MOVE to `Books-مكررات/` only; deletion needs the owner's explicit approval (not given yet).
- Broken/non-PDF files → move to `Books-مراجعة/`, no deletion.
- Laptop disk ≈15 GB free: STAGE_GB ≤ 5–6, keep ≥ 6 GB free.

## Workstreams (each has its own queue + log)
| Stream | Queue / state | Done-file |
|---|---|---|
| A. Local library → 30 GB | `data/queue/local-30gb.tsv` | `data/queue/local-30gb.done` / `.failed` |
| B. Phone fixes | `plans/NNN-*.tsv` (latest after 050) | `data/changes/changes.tsv` |
| C. Phone expansion → 200 GB | `data/queue/<batch>.tsv` (omran, alam-almarifa, pre700-*) | `data/queue/<batch>.done` / `.failed` |

## How to resume
- Re-run the same queue: `DL_JOBS=12 CONN=8 STAGE_GB=5 python3 scripts/fetch_queue.py data/queue/<q>.tsv <plan>`.
- Phone size now: `flock /tmp/phone-ftp.lock rclone lsf -R --files-only --format ps --separator $'\t' --checkers=1 --transfers=1 phone:Books > data/phone/index-<date>.tsv` then sum column 2.
- Local size: `du -sh ~/Books`.
- Finish: `scripts/additions_audit.py`, `scripts/refresh.sh` (it takes the phone lock itself for the listing — wrapping it in `flock` deadlocks, 2026-10-08; indexes stay local; it opens the main index in Brave), WORKLOG line, git commit.

## Progress log
- 07:02 AGENTS.md §7 + fetch_queue.py written; streams A, B, C launched.

- 07:09 UTC:
  * Local library queue `data/queue/local-30gb.tsv` (824 books, ~7.05 GB) generated and launched in background (`task-138`). Speed benchmark showed Phone FTP is faster (~1.57 MB/s vs 0.34 MB/s on archive.org), with archive.org fallback for large files.
  * Sira, poetry, adab, essential single-volume works, and all missing Shamela categories are being populated into `~/Books/`. Protected folders `أبو العلاء المعري` and `ابن الزبير الغرناطي` strictly untouched.
  * Alam al-Ma'rifa queue prepared: `data/queue/alam_almarifa.tsv` (455 missing issues from 061 to 515, ~2.57 GB).
  * Ali al-Omran missing books queue prepared: `data/queue/omran.tsv` / `omran_clean.tsv`.
  * Pre-700 authors candidates queue prepared: `data/queue/pre700_clean.tsv` (2,541 files, >18 GB).
  * Duplicates analysis: 225 groups identified; duplicate investigation shows false files (e.g. `tilbatu't talabah` wrongly copied into multiple folders). Per owner's instructions ("investigate and decide"), verified duplicates will be quarantined to `Books-مكررات/`.

## Overnight 2026-10-05 (owner asleep; work without asking; resume from here after any stop)
Owner's request (full text in the session; summary):
- Editions (الطبعات) of the same book are KEPT for now, clearly distinguished in names + indexes (investigator, publisher,
  year, pages, scan quality, scholars' opinions on the edition). Gather everything needed for a later purge decision.
- Find books with size / cropping / readability problems; list exact issues for the owner. When the fix is clear,
  produce fixed copies into phone `Books-نسخ-محسنة/` (same relative path) for later substitution — never replace originals.
  A better copy of the same edition found elsewhere (library or web) may serve as the substitute.
- مجلة الرسالة: original lost (compressed in place). Look for a better, very readable copy → second folder; else get a
  sample of the original (archive.org) and judge whether compression is acceptable. Rank the Tabari + Kashshaf
  compressions and give thoughts.
- Fix all errors: names verified from INSIDE the files (title pages, prefaces), Waqfeya/logs as secondary; missing
  categories; duplicates; missing volumes; unfinished queues; same edition / different scans → keep the best
  (weaker → `Books-نسخ-مستبعدة/`, not deleted); expansion per strategy (pre-700 authors, العمران, quality first, no copy
  already present).
- Local ~/Books: fix what the audit found; expand ≈5 GB ("surprise me").
- End: insights on fast phone access (Acrobat, Google Files), desktop browsing, backup/restore to a new phone, and
  "open the pages cited in the margins of a book" workflows (desktop + phone, e.g. extract cited pages into one PDF).
- Indexes stay local; open site/00 in Brave after each edit (scripts/open_index.sh). Never remove the index folder.

Phone FTP: 192.168.11.103:2221 since 2026-10-05 noon (was .102; scripts/phone_host.py tries both), ≤ 3 connections. The server has `MD5 <path>` (hash computed on the phone, ~70 MB/s).

### Steps (status)
1. [nearly done] `scripts/phone_md5.py` → data/phone/md5.tsv (exact dups). Log logs/phone_md5.log. 1 connection.
2. [running] `scripts/inspect_files.py data/phone/index-now.tsv data/inspect/priority.txt` → data/inspect/files.jsonl
   (+ ocr-queue/, thumbs/). 1 connection, ~3 h for 168 GB. Re-run the same command to resume.
3. [running] `/usr/bin/python3 scripts/inspect_ocr.py 5` (keeps front pages in data/inspect/pages/) (tesseract ara) on data/inspect/ocr-queue → data/inspect/ocr.jsonl.
4. [DONE] Risala/Tabari/Kashshaf → reports/overnight/01-risala-and-compressions.md.
5. [DONE 068–079] 1,124 copies deleted (≈8 GB). Left: 3 groups unreadable (data/phone/visual-check-state.json pending 3, 9, 12).
6. [PART] 070 named 574 batch files. Left: folder/section fixes (recat), single-file folders (singles_plan.py, after inspection).
7. [todo] Problems report (size/cropping/readability) + fixed copies → Books-نسخ-محسنة/.
8. [PART] report 05 rebuilt with quality + sourced notes (data/editions/notes.json). Re-run after inspection. Editions report (groups, distinctions, quality metrics, scholars' notes) → site tab.
9. [todo] Same edition / different scans → keep best, weaker → Books-نسخ-مستبعدة/.
10. [todo] Names verification across the library (inspect + OCR vs names) → plans. Then singles_plan.py (1,950 single-file folders → plain files): ONLY after inspection, junk names («- أحمد ا», «( - ط)») rebuilt from the PDF title/author metadata; never shorten away an author; shorten only for length.
11. [todo] Missing volumes, failed queues, expansion (pre-700, العمران).
12. [todo] Local ~/Books fixes + ≈5 GB expansion. Owner (05:xx): EVERY Shamela category must have at least a few books locally, and the sub-sections too (الأدب/أدب عالمي/… English, French, German, Spanish, translated). Local names mirror the phone. Protected: أبو العلاء المعري, ابن الزبير الغرناطي.
13. [todo] Insights write-up (phone access, desktop, backup, citations workflow).

### Notes for whoever resumes (2026-10-05 ~03:00)
- Index of the phone is kept current WITHOUT re-listing: after each plan run `python3 scripts/index_update.py <plan>`;
  before restarting inspect/md5 run `python3 scripts/remap_paths.py <plans since last remap>` (pending: 071 072 074–079).
- Kill jobs with `kill <pid>` from `pgrep -f "[n]ame"` in a SEPARATE command (pkill in a command line that also names the
  script kills the shell).
- Pending: renumber_inside_plan.py on data/phone/renumber-from-inside.txt (needs PDF titles → after inspection);
  073 queue re-run for archive.org failures (التحبير items return HTTP 500); local sync (local_sync_plan.py) after md5;
  Books-نسخ-محسنة samples (fix_pdf.py: crop sample 20 books, split 5 spreads); singles_plan.py after inspection.

### Status 2026-10-05 ~03:45
- Done tonight: duplicates 068–081 (1,125 files ≈ 8 GB), names 070/079/085/086/087, sections 088/089, singles 090 (407),
  reports 05–08 rebuilt/new, local mirror + expansion queue, insights (reports/overnight/03).
- Running: inspect_files.py (paced, ~1 MB/s while others game), inspect_ocr.py; resume_when_calm.sh waits for a calm
  network to run 083 (local expansion), 080 (improved samples), 084, 082 (almtoon), 073 (missing volumes retry).
- Owner: do NOT open Brave until the whole job is finished (data/.no-open); then delete data/.no-open and open once.
- Next when inspection progresses: renumber_inside_plan.py (32 folders in review), singles_plan.py (1,337 waiting),
  names_plan.py (all folders), verify_names.py → fixes, quality_report.py → crop recipes at scale, same-edition scans
  (keep best → «نسخ مستبعدة» only on the owner's word), remap_paths.py before each inspect restart.

### Status 2026-10-05 ~05:10
- Done since 03:45: العمران (092/093, data/authors/omran-works-status.tsv); 094/096/098 reverse-numbered sets by labels,
  verified against exact source files (two wrong labels fixed by reading); 095 (46 pre-700 works, 62 files, every title
  page read); missing volumes 097/099/100/103/104 (records that linked one file for two volumes: data/missing-by-duplinks.json);
  101 long names (none > 200 bytes left); 102 renumber-from-inside (417 files, ~70 sets; 52 sets in
  data/phone/renumber-inside-review.tsv need titles from OCR or reading); local-003 mirror (apply_local_plan.py).
- Running: inspect_files.py ×3 shards (SHARD=k/3, NETPACE=0), inspect_ocr.py (backlog ~4,700 front-page sets).
- Next: re-list the phone (index-now drifted: uploads of 073/082/084 were never added) → compare; renumber review list;
  edition-mixing folders (درج الدرر: two editions in one folder; ديوان جرير: الصاوي + dgsmh; تهذيب الآثار musnads);
  names_plan across raw names; singles_plan for the waiting single-file folders; verify_names; quality fixes;
  report 05 with full inspection data; then refresh.sh, delete data/.no-open, open Brave once.
- Lesson: labels lie sometimes (Waqfeya links one file under two volume titles; earlier passes copied labels). Check
  against the exact source file and the PDF's embedded title before renumbering (AGENTS §3 rule 3).

### Status 2026-10-05 ~12:30 (owner approved the 6 morning items + new requests; work continues without asking)
- Owner's new requests: approve all 6 (substitute improved copies; delete junk; 4 broken without source; other scans of
  the same edition → throw away; fixed copies at scale; more pre-700), keep the laptop disk safe, indexes: sections
  superposed (no sideways scroll), editors merged (بشار عواد = بشار عواد معروف), no change log online, header usable on
  phones; more chosen Waqfeya books; حميتو's missing works; careful printers (عامرة/بولاق، الحلبي، الخانجي، دار المعارف،
  حجرية فاس…), the dawawin of الأسد «مصادر الشعر الجاهلي»; a selection of the most-read missing Waqfeya titles.
- Done: 125–127 (substitutions, deletions), 128/128b (junk codes in names), 129/129b (singles), 130/131 (حميتو), 132,
  133/133b (14 jahili dawawin; canon in data/mappings/jahili-dawawin.tsv now complete), 137 (الكشف folder held 3 misfiled
  articles; the complete الكشف moved to التجويد والقراءات), 138/138b (split sets التحبير and سنن الترمذي joined; other
  scans of أبي تمام، مسند عابس، مصنف عبد الرزاق، فضل عشر ذي الحجة deleted), index page: slim sticky search bar only
  (templates/index.html), published to benjelloun.dev/library.
- Running (logs/): 134-printers (230 files, names from title pages: scratch/name_134.py), 137b-masoul (complete المعسول,
  then delete the old set with plans/137c-delete-masoul-old-set.tsv), 135-recompress (26 bloated gray scans → «نسخ محسنة»;
  substitute only copies ≤ 50 % of the original), stage-136a (top-missing selection, 141 works in data/expansion/top-pick.json;
  136b staged after 134 frees disk; then title sheets → names → upload, like 134).
- Not yet: crop/spread fixed copies at scale; the Tabari «طبعة ملونة» set (bloated but labelled colour: ask before graying).

### Status 2026-10-05 ~14:40 (unattended until the usage renewal ≈ 19:22; owner asleep)
- Running alone: `scratch/unattended_2026-10-05.sh` (log logs/unattended-2026-10-05.log), two lines:
  A. 134 printers DONE (230/230 uploaded) → index → stage 136b (downloads/stage-136b) → title sheets
     downloads/stage-136{a,b}/sheets (books.tsv + sheetNN.png) → refresh.sh --no-list (web published, Brave not opened).
  B. 135 recompress (retry of the 18 that timed out when the phone moved) → 139: lossless fixed copies (split spreads,
     crop dark scanner edges; lists/139-split-and-crop.tsv, small files first) into «نسخ محسنة للاستبدال».
- Done before: 137b/137c المعسول replaced by the complete set (22 files) and the old misnumbered set deleted (18).
- Next for the agent (one-shot resume task at 19:29 + the hourly check-in):
  1. 136a/136b: read the title sheets, write scratch/name_136.py like scratch/name_134.py (single files plain, sets
     numbered, editions from title pages), upload with fetch_queue (file://), index_update --add.
  2. 135: substitute only copies ≤ 50 % of the original (الشفا 19 %، فتوح البلدان 27 %، الطبقات 05 25 %، 03 39 % so far);
     delete the other recompressed copies from «نسخ محسنة» (خريدة القصر ×3، طبقات فحول الشعراء ≈ 80 %: not worth a lossy copy).
  3. 139: spot-check a few copies (render a page: original vs copy), then substitute (125-style: original out, copy in).
  4. Margins (3,895 files, 35 GB) in batches with substitution right after each batch (phone space unknown: FTP has no AVBL).
  5. WORKLOG line, git commit, summary to the owner.
- Owner 2026-10-05 ~14:45: the Tabari «جامع البيان … (ت شاكر - دار المعارف 1958 - طبعة ملونة)» STAYS IN COLOUR (he likes its colours;
  do not gray it to save 3 GB). Lossless crops are fine; never a gray recompression.
- 15:10 check of 139 (lossless crops): many copies barely change the page (samples: 100 %, 95 % of the page kept; one 72 %;
  splits work: 18 → 30 pages). Substitute ONLY splits and crops that keep ≤ 90 % of the page (measure CropBox/MediaBox
  on the copy with pymupdf); delete the near no-op copies from «نسخ محسنة». fix_pdf.py misses dark bands that have a
  thin white strip outside them (القول الفصل في تأييد سنة السدل: black bar at the bottom kept) — improve content_box().
- 136a uploaded (364 files) and indexed; 136b (389 files, names scratch/name_136b.py) uploading; فيض الباري (2/7 staged)
  and المحرر في أسباب النزول left out until their files download (archive.org nodes fail).
- 140: 17 recompressed copies substituted (≤ 50 % of the original; saving 3.8 GB), 9 unworthy copies deleted.
- Lid: systemd-inhibit blocks lid-close suspend until ~21:00 (pid in `systemd-inhibit --list`).
- 15:30: running `scripts/fix_at_scale.py 142 --batch 150` (log logs/fix-at-scale-142.log; per batch logs/142-bNN*.log):
  margins + dark borders + spreads (≈ 4,500 files, smallest first), copies made, measured before upload, substituted.
  `scratch/after_139.sh` waits for 139 to end, then measures and substitutes its last copies as plan 143.
  If interrupted: re-run the same commands (resumable). 136 complete (136a/136b/136c, 771 files).
- 15:35: the phone left the network (FTP not answering anywhere on 192.168.11.0/24). fix_at_scale.py now waits for the phone
  (and no longer counts merely-listed files as done; batches b02–b06 had failed and will be redone); after_139.sh waits too.
  Owner notified to reopen the FTP app. Everything resumes by itself when the phone answers (any known address).
- 20:10: phone back at .102 since 19:30; 142 running batch by batch (crops substituted at once). 144 (pre-700, 185 books)
  uploading → after_144.sh (second pass + index). 143 (last copies of 139) runs by itself after the 139 retry pass.
  Next: refresh.sh --no-list when 144 is indexed (rebuilds and publishes the indexes), WORKLOG, commit.
- 20:15: 144 done (253/253 uploaded and indexed); indexes rebuilt and published. Phone index: 16,553 files, 169.3 GB.
  Still running by itself: fix_at_scale.py 142 (batch 9 of ~30; each batch substitutes its copies at once) and
  after_139.sh → plan 143. Left for later: pre-700 works with no strong archive.org match (543; search by author/other
  uploads with scripts/find_on_archive.py), local ~/Books sync for today's additions.
- 20:30: 142 at batch 10 (≈ 1,330 books substituted so far; 3 checked by eye: nothing cut, footnotes/page numbers kept).
  139 retry pass running, then after_139.sh → 143. Nothing else pending for tonight; fix_at_scale writes its WORKLOG
  line when it ends. Morning: refresh.sh --no-list, commit, local ~/Books sync for today's additions.
- 2026-10-06 07:40: 142 crawled overnight (batch 13: 52 files in 10.5 h — the phone dozes with its screen off; a 7 MB
  download now takes 0.7 s) and is moving again (~3 files/min). ≈ 1,800 of ≈ 4,600 quality rows done; later batches
  hold bigger books. Keeping the phone awake (charger + screen-on/«stay awake» in the FTP app) keeps it fast.

## 2026-10-06: index improvements (owner approved, 07:45; credit renews ≈ 11:10 — resume task set for 11:17)
Owner: «الطبعة وسنة الطبع غير مذكورة في معظم الحالات» → make the indexes more helpful for knowledge; use the local official
Shamela (~/.local/share/shamela) when useful; ABSOLUTE ACCURACY first; tesseract again if needed. Steps:
1. [DONE 08:40, published] Edition card per book (data/editions/edition-info.json via scripts/edition_info.py; Shamela cards dumped
   with tools/shamela-dump → data/shamela/book-cards.jsonl; provenance kept across substitutions via scripts/substituted_sizes.py).
   Year known for 48%. Tesseract cannot read calligraphic imprints → READ BY EYE: scripts/imprint_sheets.py (running in the
   background, resumable: `nice python3 scripts/imprint_sheets.py --workers 4`) writes data/editions/imprint-sheets/sNNNN.png
   (6 books each, numbered) + books.tsv; read each sheet and append to data/editions/imprint-read.tsv (n, hijri, gregorian,
   edition, note) ONLY what is plainly printed (no year printed → no row); then edition_info.py + build_site.py + publish_web.sh.
   Done: 145 (111 books to Shamela's section), 145b, 146/146b (§4 names from records), Western digits everywhere (owner).
   [old text] Edition card per book (data/editions/edition-info.json via scripts/edition_info.py): editor, publisher (+city),
   edition number, year (hijri/gregorian), volumes, pages, each with its source. Evidence must be the phone's OWN edition:
   (a) Waqfeya record linked to the phone file by exact size (provenance) → yearOfPublish, copyNumber, pages, publisher,
   researcher; (b) Shamela book card ONLY when the editor/publisher in the phone name match the card; (c) title/imprint
   page OCR (tesseract ara, data/inspect/pages + new renders of pages 2-4) for the rest, accepted only when the year and
   publisher are read cleanly; (d) the phone folder name «(ت …- …)». Never guess.
2. [todo] Author death year (not only the century) from Shamela's author table, matched on the author + the work.
3. [todo] One-line description from Waqfeya; editions of the same work side by side with scan quality and notes.
4. [todo] Category audit (e.g. «أرجوزة في علم رسم الخط - الموصلي» sits in أصول الفقه → التجويد والقراءات).
5. [todo] Header numbers consistent («نحو 6,044 عنوانًا» vs «الكل 5,891»); sizes in GB (169.3) not GiB (157.6).
6. [later] Work tree (متن → شروح، حواشي، مختصرات، منظومات), author/editor pages, filters (printer, old prints).
   Owner 08:20: the «before 700 AH» filter belongs ONLY in the comparison reports (01 الشاملة، 02 الوقفية: what early
   books are missing), not in the main index. Reading paths per science: not now.
Background meanwhile: fix_at_scale.py 142 (margins), after_139.sh → 143.
- 09:15 (2026-10-06): imprint reading reveals misfiled content too: 149 — «الرسائل الأدبية - الجاحظ» and «العمدة - ابن رشيق» held
  only an article / a thesis (renamed to what they are). TO FETCH: العمدة في محاسن الشعر (ابن رشيق) and رسائل الجاحظ (هارون).
  148/148c: قادة فتح الأندلس vol 1 and فتح الباري 02-03 added (re-upload of the same scan); 147/148b names.
- 12:20 (2026-10-06): sheets 32–46 read (books 192–281). Reading keeps finding misfiled content → plans 152–155 (articles and
  Algerian university theses filed under classical titles «رسائل الثعالبي», «طوق الحمامة», «تحسين القبيح»; other works of
  اليوسي under «زهر الأكم»; الإمتاع ج 2 under «الصداقة والصديق»; «النحو الكوفي» under «معاني القرآن للفراء»; wrong publisher
  labels of the 2026-10-03 «عيون الأدب» batch: الرافعي = وكالة الصحافة العربية, فيض الخاطر = مكتبة النهضة المصرية,
  الأغاني = دار صادر). NOT ON THE PHONE (only misfiled stand-ins were): رسائل الثعالبي، طوق الحمامة (other edition kept),
  تحسين القبيح، زهر الأكم، الصداقة والصديق → candidates to fetch from Waqfeya.
  NEEDS REVIEW (owner): «Momen Tak Terlupakan …» (Indonesian AI-assisted translation of «مواقف لا تنسى») — keep?;
  «رسالة جامعية - بيان الصاف» (title in a broken font); two Shakir «دلائل الإعجاز» scans remain (الأدب 400 ppi 1-bit,
  البلاغة 300 ppi with text) — keep one?
  TODO: the 300-poem «منظومات» batch (data/mappings/mandumat_catalog.json) — its parser split titles at «لـ…» («ميسر التحصيل
  فيما - مالك من التأصيل», «منظومة المكفرات - كل ذنب سابق وآت»), and all 300 were put in الأدب whatever their subject: one
  pass over them (raw_title → full title, author from the title page, Shamela section by subject). 155 fixed six of them.
- 13:55: sheets 62–67 read (books 372–407) → plans 162 (seven التاريخ files to their subjects: الفرق والردود، التفسير، العقيدة،
  النحو، البلدان), 163 (المفصل في تاريخ العرب قبل الإسلام, only vols 1–4 of 10 on the phone → TO FETCH vols 5–10 of the
  جامعة بغداد 2nd ed. 1413/1993; تاريخ خليفة ت العمري; ابن طولون → التفسير). The التاريخ section holds many stray single
  files from the منظومات/blog batches: worth one dedicated pass over التاريخ plain files after the sheets.
- 12:20 PAUSE (owner: 80 % of the session used; renewal ≈ 16:20). Running unattended: scratch/unattended_2026-10-06.sh
  (log logs/unattended-2026-10-06.log): phone MD5s → waits for fix_at_scale 142 + after_139 → remap → refresh (web) → commit.
  No internet downloads during the pause. RESUME HERE: imprint sheets DONE (s0001–s0311, books 1–1871); next: duplicate-edition pass and the «To check» items; plans 168–174 applied after the pause began (أزهار الرياض case DONE in 168).
  OPEN CASE «أزهار الرياض» (3 folders in التراجم والطبقات, title pages seen at 25 dpi, read them larger before any plan):
  «- المقري التلمساني» arfaa1–3 = ج 1–3 of the صندوق إحياء التراث الإسلامي (المغرب والإمارات) reprint 1398/1978, arfaa4 =
  ج 4 ت سعيد أعراب ومحمد بن تاويت; «للمقري» 1–3 look like the Cairo لجنة التأليف volumes (same as the third folder «ت السقا
  والإبياري»?) and 4–5 like ج 5 / ج 4 of the صندوق edition — check sizes/md5 against the third folder for duplicates,
  then one folder per edition.
- 17:00: NEEDS REVIEW (owner): «النكت والعيون تفسير الماوردي … (دار الكتب العلمية).pdf» (one file, 3,085 pages) is the same DKI
  edition as the 6-volume folder «ت السيد بن عبد المقصود» (3,021 pages) with 64 more pages — keep both or only one?
  «البحر المحيط - دار إحياء التراث (ت المهدي)» has vols 1–4 of 8 → candidates to fetch.
- 18:30 NEEDS REVIEW (owner): «الروض الأنف» ت الوكيل (دار الكتب الحديثة 1387) exists as two scans: the complete 7-volume «المسهم»
  scan (1582×2599 px + a logo on every page) and a sharper Waqfeya scan (WAQ164489, ≈1940×2770 px) of vols 1–3 only — keep
  both until the Waqfeya vols 4–7 are fetched? «النكت والعيون» DKI exists as one file and as 6 volumes (see 17:00).
- 19:10 NEEDS REVIEW (owner, two scans of one edition — keep the better?): «جامع العلوم والحكم» ت الأرناؤوط (الرسالة) as one file in
  شروح الحديث and as a folder in الجوامع (1,073 pages each, different scans; the work belongs in شروح الحديث); «نصب الراية»
  ت عوامة (مؤسسة الريان / دار القبلة) as one file and as a folder (2,342 pages each, different scans).
  Plans 183/185/190/193 removed split copies that were the same scan as a one-file copy (image lists identical).
- 2026-10-07 15:20 STOPPED fix_at_scale.py 142 (owner: crops made pages of unequal width, ate the natural margins of e.g. the
  هارون editions, and a speck kept a page of «اللآلئ المصنوعة» wider). DO NOT RESUME. 3,542 files had been substituted.
  Audit of 40 random crop files (scratch/crop_audit.py → data/fixed/crop-audit.tsv): median margin left 2.8 % of the page,
  10/40 with text touching the edge; 22/40 with a page ≥ 10 % wider than the median, 8/40 ≥ 20 %. Selection was too broad:
  of 1,743 files with a measure, 1,220 had text using 60–69 % of the width (an ordinary book). Crops are CropBox-only
  (images untouched): reverting = CropBox := MediaBox per page, lossless. Awaiting the owner's decision (revert all / redo few).
- 2026-10-07 18:30: phone not on the network (no FTP at .102, network scan found none) — renames from sheets wait for it.
  To check later: books 1257 «اختيارات شيخ الإسلام - ابن عبد الهادي» (1.9 MB) and 1261 «الاختيارات الفقهية … لدى تلاميذه -
  سامي جاد الله» (16 MB) show the same عطاءات ISBN 978-9959-857-88-0: is the small file a part of the big one?
- 2026-10-07 22:40: plans/211-sections-read.tsv written (4 moves: الطب النبوي لأبي نعيم → كتب السنة، نخبة الأصول → أصول
  الفقه، نظم الأخضري → الفقه المالكي، رسالة أهل السنة في المغرب → العقيدة) — NOT YET APPLIED (phone FTP down): apply it first.
- 2026-10-07 23:00: OWNER DECIDED «قم باللازم» → undo all crops. scratch/revert_chain.sh (log logs/revert-chain.log) waits
  for the phone, applies 211, then scripts/revert_crops.py lists/212-uncrop.tsv (3,734 files, 30 GB, paced): fix_pdf.py
  --uncrop = every CropBox := MediaBox by incremental save (asserts: same pages, same images, no page cropped), upload size
  checked, three-step substitution (plans 212-uNNa/b/c). Split spreads stay split (halves tile the page). Recompressed (19):
  still to restore from archive.org by their original sizes (data/phone/substituted.tsv). Report 09 to be reworked after.
- 2026-10-07 22:55 owner: transfers at full speed (NETPACE=0) until he says otherwise; revert chain restarted with NETPACE=0.
- 2026-10-07 23:05: revert switched to two FTP lanes (scratch/revert_lanes.sh; lists/212-uncrop-x/-y.tsv; logs/212-uncrop-x/-y.log); u01–u05 done by the single lane.
- 2026-10-08 00:00 owner: a volume/folder holding several books is never split; its contents are recorded by
  scripts/contents.py (collections, «ويليه/ومعه/وبهامشه», a commentary kept with its text) → data/editions/contents.json,
  counted as present in compare_shamela.py (match «contained»), shown in the index as «يضم N عملًا» (✓ = in Shamela).
  Plan 214 put العبقري and its commentary back in one folder. Hourly check-in cron 7dc09905 (:23) carries the current plan.

## TASK QUEUE (2026-10-08 00:20, in order; the hourly check-in works through it)
1. [running] crop revert, two lanes (scratch/revert_lanes.sh). After it: delete the leftover cropped copies in
   «نسخ محسنة للاستبدال» that no plan substituted (from the stopped 142 batches and the killed u03/u06 batches; the originals are
   in place — check each path still exists before deleting its copy).
2. Restore the 19 recompressed files from archive.org by their original sizes (data/phone/substituted.tsv; fetch_queue.py).
3. Rework report 09 (report_fixed.py) for the state after the revert (splits and repairs remain; crops undone).
4. inspect_files.py on the 1,349 phone files never inspected (added since 10-05; one FTP lane, after the revert).
5. Imprint sheets s0224–s0312 (books 1344–1868); refresh every ~10 sheets.
6. contents.py: widen matching (titles joined by «و», author-less items via the collection's author) — keep it conservative.
7. [cancelled by the owner 2026-10-08] old queues of 2026-10-03 → data/queue/cancelled/ (see its README).
8. To fetch (found while reading): المفصل لجواد علي ج 5–10؛ البحر المحيط (دار إحياء التراث) ج 5–8؛ العمدة لابن رشيق؛ رسائل
   الثعالبي؛ تحسين القبيح؛ زهر الأكم؛ الصداقة والصديق؛ كتاب المحن؛ الغرر في فضائل عمر؛ التفسير البسيط؛ رجال المعلقات العشر.
9. Local ~/Books mirror: re-sync names/sections with the phone (local_sync_plan.py → apply_local_plan.py; the two protected
   local folders are never touched).
10. Review lists: edition-review.tsv (131), renumber-inside-review.tsv (54 sets), 15 «- ت-» names, 2 raw names, 35 doubtful
    section pairs. Owner decisions pending: the 11 files in «نسخ مستبعدة», duplicate editions (النكت والعيون، جامع العلوم
    والحكم، نصب الراية، الروض الأنف), Momen Tak Terlupakan, «رسالة جامعية - بيان الصاف».
- 2026-10-08 00:00: «النوادر والزيادات» دار الغرب 1999 twice: one file «(دار الغرب الإسلامي - نسخة أخرى)» 116 MB, 7,836 pages,
  and the 14-file folder «النوادر والزيادات على ما في المدونة … (دار الغرب الإسلامي)» 120 MB, 7,835 pages → same edition:
  compare after the revert, keep the better (owner's permission), delete the other.
- «الكافي في فقه أهل المدينة» DKI edition three times (title pages read): «… (مكتبة الرياض الحديثة).pdf» (mislabelled, 644 p,
  62 MB), «… المالكي (ط دار الكتب العلمية).pdf» (636 p, 12 MB, Waqfeya fp73997), folder «الكافي … لابن عبد البر/» (636 p,
  60 MB); the 1,184-page «(ط مكتبة الرياض الحديثة)» (Waqfeya fp16620, ت ولد ماديك) is another edition and stays. After the
  revert: compare the three DKI copies page by page, keep the best, delete the others (plan 216 was skipped: name taken).
- «حاشية الدسوقي على الشرح الكبير»: the folder «(دار الفكر)» (4 files, 104 MB) shows the Halabi title page, like the folder
  «مع تقريرات الشيخ عليش (ط عيسى البابي الحلبي)» (5 files, 103 MB): same edition? compare after the revert; keep the better.
