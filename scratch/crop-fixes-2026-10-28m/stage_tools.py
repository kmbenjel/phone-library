"""stage_tools.py — the tool edits that go with book_crop fixes L, B, B2 and B3 (2026-10-28), applied once to the working tree:
crop_recipe_diff.py names their causes («band: box kept»: the off-band slide stopped at the page's box — p['band_box'];
«band no ink»: the scanner bands as scanned read as no ink on the turned page changed its box or text — p['band_ink'],
p['band_ink2']; «band: second look off»: the second look placed the frame off a band, 4 pt beside the print —
p['band_slide'] (fix B3); «slant line»: the lines found by their ink changed — p['slant_lines']; «band carried»: the scanner bands
as scanned bound the turned page — p['band_carried']), and the case rows (case-rows.tsv) join
data/improve/crop-regression.tsv. Refuses to run twice (each edit is checked first)."""
import os, sys
ROOT = '/home/k/projects/phone-library'; S = os.path.dirname(os.path.abspath(__file__))

def edit(path, old, new):
    s = open(path, encoding='utf-8').read()
    if new in s: sys.exit(f'already applied: {path}')
    assert s.count(old) == 1, (path, old[:80])
    open(path, 'w', encoding='utf-8').write(s.replace(old, new))

d = os.path.join(ROOT, 'scripts/crop_recipe_diff.py')
edit(d, """loop's turn, the lines' turn not kept — fix Q5) (turns); a page number read as a stain
restored (folio stain);""", """loop's turn, the lines' turn not kept — fix Q5) (turns); the off-band slide held back by the page's box (band: box
kept — fix B2); the scanner bands as scanned no ink on the turned page (band no ink — fix B2); a thin line at a slant
taken for a line by its ink, not its box (slant line — fix L); the scanner bands read before the turn bounding the
turned page (band carried — fix B); the second look's frame slid off a scanner band, 4 pt beside the print (band: second
look off — fix B3); a page number read as a stain restored (folio stain);""")
edit(d, """        return None
    if q.get('folio_blot') is not None""", """        return None
    if q.get('band_slide') is not None: return 'band: second look off'
    if q.get('band_box') is not None: return 'band: box kept'
    if q.get('band_ink') or q.get('band_ink2'): return 'band no ink'
    if q.get('slant_lines') != p.get('slant_lines'): return 'slant line'
    if (q.get('band_carried') or p.get('band_carried')) and q.get('allowed') != p.get('allowed'): return 'band carried'
    if q.get('folio_blot') is not None""")

rows = open(os.path.join(S, 'case-rows.tsv'), encoding='utf-8').read()
t = os.path.join(ROOT, 'data/improve/crop-regression.tsv'); s = open(t, encoding='utf-8').read()
if rows.splitlines()[0] in s: sys.exit('case rows already there')
open(t, 'a', encoding='utf-8').write(('' if s.endswith('\n') else '\n') + rows)
print('staged: crop_recipe_diff causes, case rows', len(rows.splitlines()))
