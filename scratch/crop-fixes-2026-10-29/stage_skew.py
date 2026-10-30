"""stage_skew.py [--apply] — the «skew» case (2026-10-30, the review of regression 27n's diff): a turn looked at by eye and
measured, held at X ± T degrees. The level check cannot hold these pages: base_angles reads too few lines on القوافي للتنوخي
p. 102 and الفوائد المحصورة p. 457, and fails both turns on معجم تيمور الكبير 02 p. 166 — fix N moved all three in 27n, each
for the worse or a trade-off (HANDOFF 2026-10-30 00:36–01:34). Without --apply: shows what it would write. Run only after
27n has ended (crop_regress.py and crop-regression.tsv are read by its check phase)."""
import os, sys
ROOT = '/home/k/projects/phone-library'
CR, TSV = ROOT + '/scripts/crop_regress.py', ROOT + '/data/improve/crop-regression.tsv'
s = open(CR, encoding='utf-8').read()
OLD = """    if what == 'cropped':                              # cropped, not left whole (a book without print in its margins)
"""
NEW = """    if what == 'skew':                                 # the page's turn at X ± T° (a turn looked at by eye and measured, on a
        x, t = (float(v) for v in expect.split('±'))   # page the level check cannot read: too few lines, or lines at two
        d = p.get('skew') or 0                         # angles — القوافي للتنوخي p. 102, 2026-10-30)
        return abs(d - x) <= t + 1e-6, f'turned {p.get("skew")} (expected {x}±{t}), tracks beside {p.get("tracks_near")}'
""" + OLD
assert s.count(OLD) == 1 and "what == 'skew'" not in s
t = open(TSV, encoding='utf-8').read()
HOLD = """# 6 lines within an IQR of 0.3° — a turn too far fails it as surely as one left undone; 2026-10-27).
"""
HNEW = HOLD + """# skew = the page's turn at X±T degrees: a turn looked at by eye and measured, on a page the level check cannot read (too few
# lines, or lines at two angles; 2026-10-30).
"""
assert t.count(HOLD) == 1 and '\tskew\t' not in t
P1 = 'العروض والقوافي/القوافي للتنوخي - أبو يعلى التنوخي/1824 كتاب اقرا اونلاين pdf القوافي للتنوخي.pdf'
P2 = 'كتب اللغة/معجم تيمور الكبير في الألفاظ العامية - أحمد تيمور باشا/02 - معجم تيمور الكبير (الألف - التاء).pdf'
P3 = 'الأدب/الفوائد المحصورة في شرح المقصورة لابن هشام اللخمي/الفوائد المحصورة في شرح المقصورة لابن هشام اللخمي.pdf'
rows = [
    (P1, 102, '-0.45±0.1', 'a warped page — head prose level as scanned, body 0.2–0.45°, footnotes 0.65–0.75°: at −0.45° the rule '
     'under the text reads −0.06°; fix N (27n) took −0.675° (4 footnotes of 5 lines read level), the rule then −0.29° — worse, '
     'looked at by eye (2026-10-30)'),
    (P2, 166, '-0.65±0.1', '18 lines: at −0.65° the head rule −0.07° (27m: after 0.125°, image 0.1°); fix N (27n) took −0.875° '
     '(the lines\' spread squeaking under 0.3°), the head rule then −0.29° — worse (2026-10-30)'),
    (P3, 457, '-0.629±0.1', 'a sheared index page, two columns of short entries: at −0.629° the columns\' right edges 0.03/0.00°; '
     'fix N (27n) took −0.25° by the lines (≈ 0.1°), the columns then 0.41/0.36° — 4 pt of drift over 570 pt shows more '
     'than the short entries\' 1 pt: 27m\'s turn kept (2026-10-30)'),
]
add = ''.join(f'{p}\t{pg}\tskew\t{x}\t{n}\n' for p, pg, x, n in rows)
if '--apply' in sys.argv:
    open(CR, 'w', encoding='utf-8').write(s.replace(OLD, NEW))
    open(TSV, 'w', encoding='utf-8').write(t.replace(HOLD, HNEW) + ('' if t.endswith('\n') else '\n') + add)
    print('applied: crop_regress.py «skew» check, header lines, 3 rows')
else:
    print(NEW); print(HNEW); print(add)
