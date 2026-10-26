"""Fix P (a sheet's line read by the projection) on a copy of book_crop.py. Usage: patch_p.py SRC DST"""
import sys
src, dst = sys.argv[1:3]
s = open(src, encoding='utf-8').read()

def sub(old, new):
    global s
    assert s.count(old) == 1, old[:80]
    s = s.replace(old, new)

sub("""            rec['proj_level_rule'] = round(t, 2); return ang, gain
        rec['tilt_by_proj'] = t; return t, 1.1
""", """            rec['proj_level_rule'] = round(t, 2); return ang, gain
        # A SHEET'S LINE (2026-10-26, الموسوعة الشاملة 38 ص 438: the copier's dark bar across the whole sheet above a contents
        # table, slanting 0.64°, drew the projection to 0.475° while every line of the table lay level — turned 0.675°, ten
        # of them leaned 0.5–1°; pp. 423 and 437 alike): a long straight line across most of the sheet (≥ 70 % of its width)
        # and well past the text on both sides (≥ 5 % of the width beyond its core) is the sheet's or the copier's edge, not
        # print — the projection is read again without it, and the page is turned only if its lines still line up at a
        # tilt (a printed head rule spans the text it heads and tilts with it: خريدة القصر 01 ص 658–705, خزانة الأدب ج 4 ص 78)
        c, W = mk.get('core'), rec.get('w')
        sl = [h for h in mk.get('hrules') or [] if c and W and h[3] - h[1] >= 0.7 * W and c[0] - h[1] >= 0.05 * W and h[3] - c[2] >= 0.05 * W]
        if sl:
            b = a.copy(); z = a.shape[1] / W
            for h in sl: b[max(0, int(h[2] * z) - 3):int(h[4] * z) + 4, max(0, int(h[1] * z) - 3):int(h[3] * z) + 4] = 255
            t2, s2 = proj_signed(b, mk.get('paper') or 255, need=0.3)
            if t2 is None or abs(t2) < 0.3 or s2 < 1.5: rec['proj_sheet_line'] = round(t, 2); return ang, gain
        rec['tilt_by_proj'] = t; return t, 1.1
""")
open(dst, 'w', encoding='utf-8').write(s)
print('patched', dst)
