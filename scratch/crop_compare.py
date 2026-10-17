"""Side by side for the pages the owner marked: the page as scanned | the old crop (crop-sheets) | the new crop (minitest run).
Usage: python3 scratch/crop_compare.py RUN OUT.jpg sheet-id[:page,page] …"""
import sys, os, json
from PIL import Image, ImageDraw, ImageFont
S = os.path.expanduser('~/.cache/phone-library/crop-sheets'); R = os.path.expanduser(f'~/.cache/phone-library/crop-minitest/{sys.argv[1]}')
font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 20); H = 520; rows = []
for item in sys.argv[3:]:
    n, _, pgs = item.partition(':')
    mp = json.load(open(os.path.join(R, n, 'map.json')))['marked']
    for pg in (pgs.split(',') if pgs else sorted(mp, key=int)):
        ims = []
        for f in (os.path.join(S, n, f'p{int(pg):04d}-before.jpg'), os.path.join(S, n, f'p{int(pg):04d}-after.jpg'),
                  os.path.join(R, n, f'p{mp[pg] + 1:04d}-after.jpg')):
            if os.path.exists(f): im = Image.open(f).convert('RGB'); ims.append(im.resize((max(1, int(im.width * H / im.height)), H)))
            else: ims.append(Image.new('RGB', (300, H), (200, 200, 200)))
        row = Image.new('RGB', (sum(i.width for i in ims) + 30 * len(ims) + 120, H + 30), 'white'); d = ImageDraw.Draw(row)
        d.text((4, 8), f'{n[:6]}\np{pg}', fill='black', font=font); x = 120
        for t, im in zip(('scan', 'OLD', 'NEW'), ims): d.text((x, 4), t, fill='red', font=font); row.paste(im, (x, 28)); x += im.width + 30
        rows.append(row)
W = max(r.width for r in rows); out = Image.new('RGB', (W, sum(r.height for r in rows)), (120, 120, 120)); y = 0
for r in rows: out.paste(r, (0, y)); y += r.height
out.save(sys.argv[2], quality=85)
