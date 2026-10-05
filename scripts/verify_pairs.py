"""Verify that pairs of phone files are identical: same size + identical 64 KB samples at 0/25/50/75%/end."""
import ftplib, sys, csv
from phone_host import HOST as H
def sample(f, path, size, off):
    out = bytearray()
    class Stop(Exception): pass
    def cb(b):
        out.extend(b)
        if len(out) >= 65536: raise Stop
    try: f.retrbinary('RETR ' + path, cb, rest=off)
    except Stop:
        f.abort() if False else None
        f.close(); f2 = conn(); return bytes(out[:65536]), f2
    return bytes(out[:65536]), f
def conn():
    f = ftplib.FTP(); f.encoding = 'utf-8'; f.connect(H, 2221, timeout=60); f.login(); return f
f = conn()
for a, b in csv.reader(open(sys.argv[1]), delimiter='\t'):
    sa, sb = f.size(a), f.size(b)
    same = sa == sb
    if same:
        for frac in (0, .25, .5, .75, None):
            off = max(0, sa - 65536) if frac is None else int(sa * frac)
            x, f = sample(f, a, sa, off); y, f = sample(f, b, sb, off)
            if x != y: same = False; break
    print('IDENTICAL' if same else 'DIFFERENT', sa, sb, a, b, sep='\t')
