"""One-off: for each front part to join (argv[1]/targets.json, rows not skipped), fetch its volume from the phone, render the
part's pages 1–8 and the volume's pages 1–5 at 30 dpi, and measure which leading volume pages repeat a page of the part
(normalised correlation of 80×112 gray thumbnails) → argv[1]/match.json: per row the volume's local copy and, for each of
its first 5 pages, the best-matching part page and score."""
import json, os, subprocess, sys, unicodedata
import numpy as np
from PIL import Image
S = sys.argv[1]; SKIP = {2, 10, 19, 27}
t = json.load(open(f'{S}/targets.json'))
os.makedirs(f'{S}/vol', exist_ok=True); os.makedirs(f'{S}/m', exist_ok=True)
def thumb(pdf, p, pre):
    f = f'{pre}.png'
    if not os.path.exists(f):
        subprocess.run(['pdftoppm', '-gray', '-png', '-r', '30', '-f', str(p), '-l', str(p), '-singlefile', pdf, pre], capture_output=True)
    if not os.path.exists(f): return None
    a = np.asarray(Image.open(f).convert('L').resize((80, 112)), float); a -= a.mean(); n = np.linalg.norm(a)
    return a / n if n else None
out = []
for x in t:
    if x['i'] in SKIP or not x['volume']: continue
    vol = f"{S}/vol/{x['i']}.pdf"
    if not os.path.exists(vol):
        subprocess.run(['flock', '/tmp/phone-ftp.lock', 'rclone', 'copyto', '--bwlimit', '6M', '--retries', '3', 'phone:Books/' + x['volume'], vol], check=True)
    P = [thumb(x['local'], p, f"{S}/m/p{x['i']}_{p}") for p in range(1, min(8, x['pages']) + 1)]
    V = [thumb(vol, p, f"{S}/m/v{x['i']}_{p}") for p in range(1, 6)]
    rows = []
    for j, v in enumerate(V, 1):
        best = max(((float((v * q).sum()), k) for k, q in enumerate(P, 1) if v is not None and q is not None), default=(0, None))
        rows.append({'vol_page': j, 'best_part_page': best[1], 'score': round(best[0], 3)})
    out.append({'i': x['i'], 'file': x['file'], 'part_pages': x['pages'], 'volume': x['volume'], 'vol_local': vol, 'match': rows})
    print(x['i'], x['file'], [(r['vol_page'], r['best_part_page'], r['score']) for r in rows], flush=True)
json.dump(out, open(f'{S}/match.json', 'w'), ensure_ascii=False, indent=1)
