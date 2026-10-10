"""Pages FIRST..LAST of a PDF as one numbered sheet, for reading further into a book whose first pages do not name it
(no title page, a cut-off scan, a dark cover). Usage: python3 scripts/pages_sheet.py FILE FIRST LAST OUT.jpg [height]"""
import os, subprocess, sys, tempfile
from PIL import Image, ImageDraw, ImageFont

def main(pdf, first, last, out, h=900):
    with tempfile.TemporaryDirectory() as d:
        subprocess.run(['pdftoppm', '-gray', '-r', '70', '-f', str(first), '-l', str(last), '-jpeg', pdf, os.path.join(d, 'p')], check=True)
        files = sorted(os.listdir(d))
        ims = []
        for f in files:
            im = Image.open(os.path.join(d, f)); ims.append(im.resize((max(1, im.width * h // im.height), h)))
        per = 4
        rows = [ims[i:i + per] for i in range(0, len(ims), per)]
        W = max(sum(i.width + 8 for i in r) for r in rows); sheet = Image.new('L', (W, len(rows) * (h + 40)), 255)
        try: font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 28)
        except OSError: font = ImageFont.load_default()
        d_ = ImageDraw.Draw(sheet); k = first
        for y, r in enumerate(rows):
            x = 0
            for im in r:
                sheet.paste(im, (x, y * (h + 40) + 36)); d_.text((x + 4, y * (h + 40)), f'p {k}', fill=0, font=font); x += im.width + 8; k += 1
        sheet.save(out, quality=80)
    print(out)

if __name__ == '__main__':
    a = sys.argv[1:]
    main(a[0], int(a[1]), int(a[2]), a[3], int(a[4]) if len(a) > 4 else 900)
