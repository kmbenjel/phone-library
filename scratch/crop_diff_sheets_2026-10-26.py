"""One-off (2026-10-26, the crop revisit's diff): every page whose turn, box, shown part, scale, move or kind changed
between the recipes of book_crop 5d6113b97c and the new regression's, drawn as the reader sees it — old (left) | new
(right), the cause and the after-turn readings in the caption — so each change is checked by eye before the pilot redo.
Usage: crop_diff_sheets_2026-10-26.py NEWMD5 OUTDIR [HASH …]"""
import glob, json, os, sys, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'scripts'))
import book_crop as bc
from PIL import Image, ImageDraw, ImageFont

C = os.path.expanduser('~/.cache/phone-library/crop-regress/')
KEYS = ('skew', 'crop', 'show', 'scale', 'move', 'kind')
new, out = sys.argv[1][:10], sys.argv[2]; os.makedirs(out, exist_ok=True)
only = set(sys.argv[3:])
try: font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 15)
except OSError: font = ImageFont.load_default()

def cause(q):
    for k, v in (('owner_turn', 'owner turn'), ('level_first', 'level first'), ('image_loose', 'image ≤ 0.35')):
        if q.get(k) is not None: return v
    return 'OTHER'

for f in sorted(glob.glob(C + '*.5d6113b97c.json')):
    h = os.path.basename(f)[:12]
    if only and h not in only: continue
    nf = sorted(glob.glob(C + f'{h}.{new}*.json'))
    if not nf: continue
    A, B = json.load(open(f)), json.load(open(nf[-1]))
    ch = [i for i, (p, q) in enumerate(zip(A['pages'], B['pages'])) if any(p.get(k) != q.get(k) for k in KEYS)]
    if not ch: continue
    src = C + h + '.pdf'
    with tempfile.TemporaryDirectory() as td:
        ma = {m['page']: m for m in bc.sheet(src, A, os.path.join(td, 'a'), [(i, '') for i in ch])}
        mb = {m['page']: m for m in bc.sheet(src, B, os.path.join(td, 'b'), [(i, '') for i in ch])}
        for i in ch:
            a, b = Image.open(ma[i + 1]['after']), Image.open(mb[i + 1]['after'])
            q = B['pages'][i]; p = A['pages'][i]
            cap = (f'{h} p. {i + 1} [{cause(q)}]  old: skew {p.get("skew")} crop {p.get("crop")}   new: skew {q.get("skew")} '
                   f'crop {q.get("crop")}  after {q.get("after_tilt")}/{q.get("after_tilt_image")} lines {q.get("level_by_lines")}')
            import textwrap
            lines = textwrap.wrap(cap, 110)[:4]; top = 8 + 20 * len(lines)
            W, H = a.width + b.width + 30, max(a.height, b.height) + top
            im = Image.new('RGB', (W, H), 'white'); im.paste(a, (0, top)); im.paste(b, (a.width + 30, top))
            d = ImageDraw.Draw(im)
            for k, l in enumerate(lines): d.text((6, 4 + 20 * k), l, fill='black', font=font)
            im.save(os.path.join(out, f'{h}-p{i + 1:04d}.jpg'), quality=80)
    print(h, len(ch), 'pages drawn', flush=True)
