"""Fix N2 (2026-10-30, the review of regression 27n's diff): FIX N ONLY FOR LINES READ AND REFUSED FOR THEIR SPREAD, as its
note says — not for a page whose lines the tracks cannot read at all. 8109 (108 pages) p. 102, a warped page whose lines
lie at many angles — the prose at its head level as scanned, the body 0.2–0.45°, the footnotes 0.65–0.75° (rowtilt and
line_tracks agree): its first look's turn −0.7° (the tracks' −0.694°, read on 5 lines, 4 of them footnotes) is unread on
the turned page because only 3 lines are read there (< 5), not for their spread; fix N then took −0.675°, where 5 lines
(4 footnotes) read a median −0.025° while the body line read +0.44°: the printed rule under the text left leaning 0.29°,
the body ~0.3°, the head ~0.5° (/tmp/claude-1000/r27n/turnrows.py). Without N: −0.45° (27l, 27m — the rule level, −0.06°).
إرشاد الساري 10 ص 477, N's own page, reads 34 lines at −0.575° (spread 0.325°): N still takes −0.6° there.
Usage: patch_n2.py SRC DST   (SRC = scripts/book_crop.py a0e20119c2 = code/bc_fn.py)"""
import sys
src, dst = sys.argv[1:3]
s = open(src, encoding='utf-8').read()

def sub(old, new):
    global s
    assert s.count(old) == 1, old[:80]
    s = s.replace(old, new)

sub('''    an = [t[1] for t in T if t[3] <= 1.0 and t[4] >= 6 and t[2] >= 0.3 and not t[5]]
    if len(an) < 5: return None
''', '''    an = tracks_read(T)
    if len(an) < 5: return None
''')
sub('''def tracks_tilt(T):
''', '''def tracks_read(T):
    """(tracks_tilt) the angles of the lines read well: ≤ 1 px from their straight line at 1,000 px, ≥ 6 strips, ≥ 30 % of
    the block, printed rules left out"""
    return [t[1] for t in T if t[3] <= 1.0 and t[4] >= 6 and t[2] >= 0.3 and not t[5]]

def tracks_tilt(T):
''')
sub('''            # the last word)
            if tk is None and mk.get('paper') and not (
''', '''            # the last word) — only when the lines were read and refused for their spread (≥ 5 read: fix N2, 2026-10-30,
            # 8109 p. 102, a warped page: 3 lines read at −0.7°, N took −0.675° where 4 footnotes of 5 lines read level and the
            # body leaned 0.3–0.5°)
            if tk is None and mk.get('paper') and len(tracks_read(mk['tracks']())) >= 5 and not (
''')

open(dst, 'w', encoding='utf-8').write(s)
print('patched', dst)
