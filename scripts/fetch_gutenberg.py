"""Add public-domain books from Project Gutenberg as phone-friendly PDFs.

Gutenberg gives EPUB/HTML, not PDF, so each book's EPUB (with its illustrations) is converted locally with calibre's
ebook-convert: A5 pages, serif 13 pt, page numbers, the book's own table of contents as PDF bookmarks.
Every PDF is checked (%PDF + page count) before upload; uploads use one FTP connection; every file is logged
(action 'add', plan 035-gutenberg). Already-added targets are skipped, so the script can be re-run.
Edit BOOKS: (section, folder, file name, Gutenberg ebook number). Usage: python3 scripts/fetch_gutenberg.py"""
import csv, os, subprocess, sys, threading, time
from concurrent.futures import ThreadPoolExecutor
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J = lambda p: os.path.join(ROOT, p)
PLAN = os.environ.get('PLAN', '035-gutenberg')
FR, EN = 'أدب عالمي - فرنسي (Littérature française)', 'أدب عالمي - إنجليزي (English Literature)'
DE, ES = 'أدب عالمي - ألماني (Deutsche Literatur)', 'أدب عالمي - إسباني (Literatura en español)'
MIS, MC = 'Les Misérables - Victor Hugo', 'Le Comte de Monte-Cristo - Alexandre Dumas'
BOOKS = [
 (FR, MIS, '01 - Les Misérables (Tome I - Fantine).pdf', 17489),
 (FR, MIS, '02 - Les Misérables (Tome II - Cosette).pdf', 17493),
 (FR, MIS, '03 - Les Misérables (Tome III - Marius).pdf', 17494),
 (FR, MIS, "04 - Les Misérables (Tome IV - L'Idylle rue Plumet et l'Épopée rue Saint-Denis).pdf", 17518),
 (FR, MIS, '05 - Les Misérables (Tome V - Jean Valjean).pdf', 17519),
 (FR, MC, '01 - Le Comte de Monte-Cristo (Tome I).pdf', 17989),
 (FR, MC, '02 - Le Comte de Monte-Cristo (Tome II).pdf', 17990),
 (FR, MC, '03 - Le Comte de Monte-Cristo (Tome III).pdf', 17991),
 (FR, MC, '04 - Le Comte de Monte-Cristo (Tome IV).pdf', 17992),
 (FR, 'Le Rouge et le Noir - Stendhal', 'Le Rouge et le Noir.pdf', 798),
 (FR, 'Madame Bovary - Gustave Flaubert', 'Madame Bovary.pdf', 14155),
 (FR, 'Fables - Jean de La Fontaine', 'Fables (illustrées par Grandville).pdf', 56327),
 (EN, 'Wuthering Heights - Emily Brontë', 'Wuthering Heights.pdf', 768),
 (DE, 'Der Struwwelpeter - Heinrich Hoffmann', 'Der Struwwelpeter.pdf', 24571),
 (DE, 'Max und Moritz - Wilhelm Busch', 'Max und Moritz.pdf', 17161),
 (DE, 'Deutsche Märchen - Brüder Grimm', 'Deutsche Märchen gesammelt durch die Brüder Grimm.pdf', 77905),
 (DE, 'Fabeln und Erzählungen - Christian Fürchtegott Gellert', 'Fabeln und Erzählungen.pdf', 9335),
 (DE, 'Einige Gedichte - Friedrich Schiller', 'Einige Gedichte (mit Das Lied von der Glocke).pdf', 6649),
 (ES, 'Fábulas - Félix María Samaniego', 'Fábulas.pdf', 55206),
 (ES, 'Fábulas literarias - Tomás de Iriarte', 'Fábulas literarias.pdf', 29497),
 (ES, 'La Edad de Oro - José Martí', 'La Edad de Oro.pdf', 19898),
 (ES, 'Fábulas y cuentos en verso - selección de María Goyri (Biblioteca Literaria del Estudiante)', 'Fábulas y cuentos en verso.pdf', 64058),
]
DL = J('downloads/gutenberg'); os.makedirs(DL, exist_ok=True)
done = {r[3] for r in csv.reader(open(J('data/changes/changes.tsv')), delimiter='\t') if r and r[1] == 'add'}
lock = threading.Lock(); stats = {'ok': 0, 'bad': 0}
CONVERT = ['--paper-size', 'a5', '--pdf-default-font-size', '13', '--pdf-mono-font-size', '11', '--pdf-serif-family', 'Noto Serif',
           '--pdf-page-margin-left', '30', '--pdf-page-margin-right', '30', '--pdf-page-margin-top', '30', '--pdf-page-margin-bottom', '30',
           '--pdf-page-numbers', '--preserve-cover-aspect-ratio', '--embed-all-fonts']

def pages(p):
    out = subprocess.run(['pdfinfo', p], capture_output=True, text=True).stdout
    return next((int(l.split()[-1]) for l in out.splitlines() if l.startswith('Pages:')), 0)

def book(b):
    sec, folder, name, gid = b
    target = f'Books/{sec}/{folder}/{name}'
    if target in done: return
    epub, pdf = os.path.join(DL, f'{gid}.epub'), os.path.join(DL, f'{gid}.pdf')
    url = f'https://www.gutenberg.org/ebooks/{gid}.epub3.images'
    if not os.path.exists(epub) or os.path.getsize(epub) < 1000:
        subprocess.run(['curl', '-sL', '--fail', '--retry', '3', '-A', 'personal-library/1.0', '-o', epub, url])
    if not os.path.exists(pdf) or pages(pdf) == 0:
        r = subprocess.run(['ebook-convert', epub, pdf] + CONVERT, capture_output=True, text=True)
        if r.returncode:
            with lock: print('CONVERT FAIL', gid, r.stderr[-300:], flush=True); stats['bad'] += 1
            return
    n = pages(pdf)
    if open(pdf, 'rb').read(5) != b'%PDF-' or n < 2:
        with lock: print('BAD PDF', gid, flush=True); stats['bad'] += 1
        return
    with lock:                                     # one FTP connection at a time
        r = subprocess.run(['rclone', 'copyto', pdf, f'phone:{target}', '--inplace', '--ftp-concurrency', '1', '-q'], capture_output=True, text=True)
        if r.returncode: print('UPLOAD FAIL', target, r.stderr[-200:], flush=True); stats['bad'] += 1; return
        with open(J('data/changes/changes.tsv'), 'a', newline='') as f:
            csv.writer(f, delimiter='\t').writerow([time.strftime('%F %T'), 'add', '', target,
                f'Project Gutenberg #{gid} (public domain), EPUB → A5 PDF with calibre, {n} pages: https://www.gutenberg.org/ebooks/{gid}', PLAN])
        stats['ok'] += 1; print(f'added ({n} p, {os.path.getsize(pdf) / 2**20:.1f} MB)', target.split('/', 1)[1][:110], flush=True)

with ThreadPoolExecutor(4) as ex: list(ex.map(book, BOOKS))
print('added:', stats['ok'], '| problems:', stats['bad'], flush=True)
