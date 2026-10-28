"""stage_tools.py — the tool edits that go with fixes O and Q3 (for regression 26j), applied in place to scripts/crop_regress.py,
crop_recipe_diff.py, crop_batch.py, crop_doubts_page.py and data/improve/crop-regression.tsv (+5 cases on فهرسة ابن خير). Run
from the repo root, only after 26i (done) and before 26j. Asserts every anchor once; refuses to run twice"""
import os
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))

def edit(fn, pairs):
    s = open(fn, encoding='utf-8').read()
    for old, new in pairs:
        assert s.count(old) == 1, (fn, old[:70]); s = s.replace(old, new)
    open(fn, 'w', encoding='utf-8').write(s); print('edited', fn)

assert 'ycentre' not in open('scripts/crop_regress.py', encoding='utf-8').read(), 'already staged'
edit('scripts/crop_regress.py', [
("""             or (p.get('level_by_base') is not None and abs(p['level_by_base']) <= 0.1 + 1e-6)
""", """             or (p.get('level_by_base') is not None and abs(p['level_by_base']) <= 0.1 + 1e-6)
             # (a projection page the baselines could not read, turned by its lines followed across it and read level by
             # them once turned: book_crop fix Q3, 2026-10-27)
             or (p.get('tilt_by_tracks') is not None and p.get('level_by_tracks') is not None and abs(p['level_by_tracks']) <= 0.1 + 1e-6)
"""),
("""    if what == 'centred':
""", """    if what == 'ycentre':                              # the shown part's middle lies at Y ± T pt: a page placed where its
        if not p.get('show'): return False, 'no frame'   # neighbours are (its page number where theirs is: فهرسة ابن خير)
        y, t = (float(v) for v in expect.split('±')); s = p['show']; c = (s[1] + s[3]) / 2
        return abs(c - y) <= t, f'middle {c:.1f} (expected {y}±{t}), anchored {p.get("anchored_y")}'
    if what == 'centred':
"""),
])
edit('scripts/crop_recipe_diff.py', [
("""                     ('tilt_by_base', 'baselines'),
""", """                     ('tilt_by_tracks', "lines' tracks"),
                     ('tilt_by_base', 'baselines'),
"""),
("""    if q.get('folio_blot') is not None or p.get('folio_blot') is not None: return 'folio stain'
""", """    if q.get('folio_blot') is not None or p.get('folio_blot') is not None: return 'folio stain'
    if q.get('folio_specks') is not None or p.get('folio_specks') is not None: return 'folio specks'
    if q.get('ornament') != p.get('ornament'): return 'ornament'
    if p.get('dodged') and not q.get('dodged') and q.get('stain_kept'): return 'no futile dodge'
"""),
])
edit('scripts/crop_batch.py', [
("""                   'folio' if p.get('folio_blot') else
""", """                   'folio' if p.get('folio_blot') or p.get('folio_specks') else
                   # (2026-10-27: an ornament the book repeats, read as a stain before — print again, the box no longer
                   # dodging it)
                   'orn' if p.get('ornament') else
"""),
("""                 'cut': 10, 'folio': 11, 'base': 12, 'tracks': 13}
""", """                 'cut': 10, 'folio': 11, 'orn': 12, 'base': 13, 'tracks': 14}
"""),
("""                                                               'two_angles', 'turn_by_tracks', 'level_by_tracks', 'level_by_print') if p.get(k)}
""", """                                                               'two_angles', 'turn_by_tracks', 'level_by_tracks', 'level_by_print',
                                                               'tilt_by_tracks', 'base_robust', 'ornament', 'folio_specks') if p.get(k)}
"""),
])
edit('scripts/crop_doubts_page.py', [
("""'folio': 'رقم الصفحة قُرئ بقعةً فأعيد إلى النص',
""", """'folio': 'رقم الصفحة قُرئ بقعةً أو نُقَطًا متفرقة فأعيد إلى النص',
       'orn': 'زخرفة مطبوعة يكررها الكتاب (حلية آخر الفصل) كانت تُقرأ بقعة: أعيدت إلى النص، ولم يعد الإطار يتحرك ليتفاداها',
"""),
])
fn = 'data/improve/crop-regression.tsv'; s = open(fn, encoding='utf-8').read()
old = "# page's content centred in its box (±2 %); xcentre = the shown part's centre at X±T pt (a measured anchor: page number, heading);\n"
assert s.count(old) == 1
s = s.replace(old, old + "# ycentre = the shown part's middle at Y±T pt (a page placed where its neighbours are: its page number where theirs is);\n")
P = 'فهارس الكتب والأدلة/فهرسة ابن خير الإشبيلي/1 - فهرسة ابن خير الإشبيلي.pdf'
rows = [
 (P, 167, 'ycentre', '430.9±8', "a chapter's end with the book's fleuron under its last line (a 59 pt square, on 12 pages): read as a stain, the box slid to the page's top to dodge it while still holding it — the page number 120 pt lower than on the pages around (26i). A «stain» repeated as the same block is print; a dodge that takes nothing of the mark out is not made (fix O, 2026-10-27)"),
 (P, 167, 'in', '230,557,289,617', 'the fleuron itself: print, wholly shown (fix O)'),
 (P, 11, 'ycentre', '440.1±8', 'the same fleuron under a short page: the box slid to the page top for it (fix O)'),
 (P, 4, 'ycentre', '433.9±8', "the page number «- ٥ -» above a chapter's first lines: three grains under 6 pt read as dust, the «(١)» under it taken for the number and the page centred on itself, 30 pt off (26i). Specks where the book prints its page number are that number (fix O)"),
 (P, 4, 'xcentre', '275.4±5', 'the same page across: centred on its page number like the pages around (fix O)'),
]
s = s.rstrip('\n') + '\n' + ''.join('\t'.join(map(str, r)) + '\n' for r in rows)
open(fn, 'w', encoding='utf-8').write(s); print('cases added', len(rows))
