"""Fix B5 (2026-10-28, the benches of B2–B4 on خريدة القصر 01 0648): THE BAND'S OWN EDGE PIXELS ARE THE BAND. band_mask turns
the band's edge as a straight line (one pixel's allowance in), but a scanner band's edge wobbles by a pixel: where it steps out,
its last pixels stay on the page as slivers one or two pixels across, of any length — and each became something: ص 71 a 16-pt
sliver at the foot counted as a letter, the text block grew 23 pt down and the page sat 11 pt high in its frame; ص 389, 579,
585, 637 slivers of 47–56 pt at the top corner were «lines» and were dodged (fix B4 stops the dodge, not the reading). A mark
lying WHOLLY within 2.4 pt of a band the turned page lost is the band (two pixels at 500 px, four at the second look's 1,000:
an edge 2.4 pt off the straight line leaves one pixel at 500 px, three at 1,000). REJECTED (single-page first looks): the band grown
two pixels through the ink joined to it — it ate the paper's grey rim beside the band (ص 694: the rim a blot again, the line
ends «٣١٠»، «٢٨٨» out of the text block, 32 pt) and a table's border rule touching the band (ص 637: the text block 8.5 pt
short). A rim, a table's grid, a letter reach further from the band than that and stay as they were.
Usage: patch_b5.py SRC DST   (SRC = book_crop with fixes L, B, B2, B3 and B4: code2/bc_lbb4.py)"""
import sys
src, dst = sys.argv[1:3]
s = open(src, encoding='utf-8').read()

def sub(old, new):
    global s
    assert s.count(old) == 1, old[:80]
    s = s.replace(old, new)

sub('''        band = (band & lost) != 0
        if band.any(): mask = mask & ~band
        else: band = None
''', '''        band = (band & lost) != 0
        if band.any():
            mask = mask & ~band
            # (fix B5) the band's own edge pixels a straight edge misses: a mark wholly within 2.4 pt of the band is the band
            # (two pixels at the first look's 500 px, four at the second look's 1,000)
            ring = ndimage.binary_dilation(band, iterations=max(2, int(round(2.4 * scale)))) & ~band
            if (mask & ring).any():
                lb5, n5 = ndimage.label(mask, structure=np.ones((3, 3), bool))
                tot, inr = np.bincount(lb5.ravel(), minlength=n5 + 1), np.bincount(lb5[ring], minlength=n5 + 1)
                sl = tot == inr; sl[0] = False
                if sl.any(): band |= sl[lb5]; mask = mask & ~band
        else: band = None
''')

open(dst, 'w', encoding='utf-8').write(s)
print('patched', dst)
