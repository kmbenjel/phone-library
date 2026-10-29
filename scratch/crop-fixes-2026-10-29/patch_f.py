"""Fix F (2026-10-29, the review of regression 27m's diff): THE OWNER'S «LEAVE AS SCANNED» STANDS. The pages he saw left as
scanned for their two angles and kept so — crop-tilt-002 (2026-10-27, «Leave as scanned»: 4 pages) and crop-tilt-003
(2026-10-29, «mark all ok»: 82 pages) — were his verdicts on the method's output, not part of the method: a later change of
reading could turn them again. 27m did: fix L (a line is thin by its ink) narrowed صبح الأعشى 05 ص 367's text block as
scanned by 3.6 pt (a thin mark at its left edge now a line), line_tracks then read its short foot lines otherwise (y 680:
−0.18° → −0.41°, no longer read alike in both views; y 654 short of «made worse» by 0.007°), guard W saw one line made to
lean instead of three and the page was turned −0.625° — the page of crop-tilt-003 row 21 («a warped page: the tilt grows
line by line, leaving it is right»). His verdict becomes data: a turn of 0 in data/crop/owner-turns.tsv (crop_batch.
owner_turns, already passed to plan/verify and in the regression's cache key) = the page stays as scanned, whatever a reading
finds; the turn the method would have made is kept for the record (owner_flat). Guard W and the baselines' late turn already
skip a page the owner ruled on; the owner's turn itself applies to a non-zero turn only.
Usage: patch_f.py SRC DST   (SRC = scripts/book_crop.py 4fcdf11f58, regression 27m)"""
import sys
src, dst = sys.argv[1:3]
s = open(src, encoding='utf-8').read()

def sub(old, new):
    global s
    assert s.count(old) == 1, old[:80]
    s = s.replace(old, new)

sub('''    owner_turns: {page (1-based, as in the recipe): |tilt|} — pages the owner ruled «turn» (verify)"""''',
    '''    owner_turns: {page (1-based, as in the recipe): |tilt|} — pages the owner ruled «turn» (verify); a tilt of 0: a page he
    ruled «leave as scanned» (fix F)"""''')

sub('''        ot = (owner_turns or {}).get(i + 1)
        if ot is not None and not p.get('skew'):
''', '''        ot = (owner_turns or {}).get(i + 1)
        # THE OWNER'S «LEAVE AS SCANNED» (fix F, 2026-10-29: his turn of 0 — the pages he saw left as scanned for their two
        # angles and kept so, crop-tilt-002 «Leave as scanned», crop-tilt-003 «mark all ok»): never turned, whatever a later
        # reading finds — 27m's fix L narrowed صبح الأعشى 05 ص 367's text block as scanned by 3.6 pt, its short foot lines read
        # 0.2° otherwise, guard W saw one line made to lean instead of three and turned the page he had kept −0.625°. The turn
        # the method would make is kept for the record (owner_flat)
        if ot is not None and not ot:
            if p.get('skew'):
                p['owner_flat'] = p.pop('skew')
                for k in ('after_tilt', 'after_tilt_image', 'turned_in_check'): p.pop(k, None)
                mk = look(i, {k: v for k, v in p.items() if k != 'skew'})
            ot = None
        if ot is not None and not p.get('skew'):
''')

open(dst, 'w', encoding='utf-8').write(s)
print('patched', dst)
