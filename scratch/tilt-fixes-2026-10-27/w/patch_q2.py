"""Fix Q, step 2 (2026-10-27, the smoke test of P+Q+R+W+W3 on أنساب الأشراف المقدمة): when the baselines cannot read the
turned page at all (base_tilt: fewer than 6 lines, or their spread ≥ 0.3° — on ص 44 turned −0.525° the clean lines read
0.00 to +0.10° but the row profile merged a few pairs into readings of −2.4°, +9.1°, +4.3°), the turn the baselines set
is confirmed as the projection's turns were before fix Q — the page's shear ≤ 0.2° once turned — instead of falling to the
ordinary checks, which undid it (the page left 0.52° tilted and listed). Applied on a copy of book_crop.py with fixes P,
Q, R and guard W (patch_w.py, patch_w3.py). Usage: patch_q2.py SRC DST"""
import sys
src, dst = sys.argv[1:3]
s = open(src, encoding='utf-8').read()

def sub(old, new):
    global s
    assert s.count(old) == 1, old[:80]
    s = s.replace(old, new)

sub("""        # A TURN ITS LINES' BASELINES SET (tilt_by_base): read again by them on the page as the reader sees it, corrected once
        # when they still read more than 0.05° (the ruler is linear; never below 0.2°), kept when they read ≤ 0.1°; else the
        # ordinary checks below decide — not the shear measure's ≤ 0.2°, which such pages pass at almost any turn
""", """        # A TURN ITS LINES' BASELINES SET (tilt_by_base): read again by them on the page as the reader sees it, corrected once
        # when they still read more than 0.05° (the ruler is linear; never below 0.2°), kept when they read ≤ 0.1°; else the
        # ordinary checks below decide — not the shear measure's ≤ 0.2°, which such pages pass at almost any turn. Only when
        # the baselines cannot read the turned page at all (fewer than 6 lines, or a spread ≥ 0.3°: أنساب الأشراف المقدمة
        # ص 44 turned −0.525°, its clean lines 0.00 to +0.10° but a few pairs merged into −2.4°, +9.1°, +4.3°) is their turn
        # confirmed as the projection's were — the page's shear ≤ 0.2° (level_by_proj): the angle stays the baselines'
""")
sub("""        if not lbr and p.get('skew') and p.get('tilt_by_proj') is not None and p.get('tilt_by_base') is None and mk.get('xy') is not None:   # turned by the
""", """        if not lbr and p.get('skew') and p.get('tilt_by_proj') is not None and mk.get('xy') is not None \\
           and (p.get('tilt_by_base') is None or base(i, p, mk) is None):                                      # turned by the
""")
open(dst, 'w', encoding='utf-8').write(s)
print('patched', dst)
