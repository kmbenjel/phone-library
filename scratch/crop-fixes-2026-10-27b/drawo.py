"""drawo.py BOOK [A B] OUTDIR — every page whose crop/show/turn/move/scale/kind differs between the bench recipes
<book>.<A>.json and <book>.<B>.json, drawn as the reader sees it (book_crop.sheet): A (left) | B (right) with neighbours
for comparison: the page before and after (B) — so a page's place can be judged against the pages around it"""
import sys, os, json, tempfile, textwrap
S = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, '/home/k/projects/phone-library/scripts')
import book_crop as bc
from PIL import Image, ImageDraw, ImageFont
h = sys.argv[1]; a_, b_ = (sys.argv[2:4] if len(sys.argv) >= 5 else ('base', 'o')); out = sys.argv[-1]; os.makedirs(out, exist_ok=True)
A = json.load(open(f'{S}/{h}.{a_}.json')); B = json.load(open(f'{S}/{h}.{b_}.json'))
K = ('crop', 'show', 'skew', 'move', 'scale', 'kind')
ch = [i for i, (p, q) in enumerate(zip(A['pages'], B['pages'])) if any(p.get(k) != q.get(k) for k in K)]
nb = sorted({j for i in ch for j in (i - 1, i + 1) if 0 <= j < len(B['pages'])} - set(ch))
font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 14)
src = f'{S}/books/{h}.pdf'
with tempfile.TemporaryDirectory() as td:
    ma = {m['page']: m for m in bc.sheet(src, A, os.path.join(td, 'a'), [(i, '') for i in ch])}
    mb = {m['page']: m for m in bc.sheet(src, B, os.path.join(td, 'b'), [(i, '') for i in ch + nb])}
    for i in ch:
        ims = [Image.open(mb[j + 1]['after']) for j in (i - 1,) if j + 1 in mb] + [Image.open(ma[i + 1]['after']), Image.open(mb[i + 1]['after'])] \
              + [Image.open(mb[j + 1]['after']) for j in (i + 1,) if j + 1 in mb]
        tags = ([f'p.{i} (new)'] if i in mb else []) + [f'p.{i + 1} OLD', f'p.{i + 1} NEW'] + ([f'p.{i + 2} (new)'] if i + 2 in mb else [])
        p, q = A['pages'][i], B['pages'][i]
        cap = f'{h} p. {i + 1}  old crop {p.get("crop")} skew {p.get("skew")}  new crop {q.get("crop")} skew {q.get("skew")}  ' + \
              ' '.join(f'{k}={q.get(k)}' for k in ('ornament', 'folio_specks', 'stain_kept', 'tilt_by_tracks', 'level_by_tracks', 'tilt_by_base', 'level_by_base') if q.get(k) is not None)
        lines = textwrap.wrap(cap, 150)[:3]; top = 8 + 18 * len(lines) + 18
        W = sum(im.width for im in ims) + 20 * (len(ims) - 1); Hh = max(im.height for im in ims) + top
        sheet = Image.new('RGB', (W, Hh), 'white'); d = ImageDraw.Draw(sheet); x = 0
        for im, t in zip(ims, tags):
            sheet.paste(im, (x, top)); d.text((x + 4, top - 18), t, fill='red' if 'OLD' in t or 'NEW' in t else 'grey', font=font)
            d.rectangle([x, top, x + im.width - 1, top + im.height - 1], outline='black'); x += im.width + 20
        for k, l in enumerate(lines): d.text((6, 4 + 18 * k), l, fill='black', font=font)
        sheet.save(os.path.join(out, f'{h}-p{i + 1:04d}.jpg'), quality=80)
print(h, len(ch), 'pages drawn')
