"""Books whose Waqfeya archive.org items went dark: verify the other uploads find_on_archive.py proposed, and queue the right
ones (owner, 2026-10-08: «حمّل هذه الكتب كلها بعد التدقيق وأخضعها لما يلزم من فحص وعناية»).
For each Waqfeya record, its candidates in score order:
  - refused at once: more PDFs than the record's volumes allow (a bundle of other books: > 2 × volumes + 2), over 2 GB;
  - the first PDF (natural order) is downloaded (aria2c, kept for the upload) and read: its text layer, else tesseract
    (ara) on its first 6 pages at 150 dpi;
  - accepted when the title page carries the record's title (≥ 60 % of its distinctive words) and, when the record names
    an author, the author's name; otherwise the next candidate; none → listed for review (nothing uploaded).
Accepted items are queued for scripts/fetch_queue.py (verified first file as file:///, the other PDFs by URL) under
Books/<phone section>/<title - author>/NN - <short title>.pdf (one PDF → a plain file), with the evidence as reason.
Usage: python3 scripts/dark_replace.py candidates.json queue.tsv review.tsv"""
import csv, json, os, re, subprocess, sys, tempfile, unicodedata, urllib.parse
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from textnorm import title_key, author_tokens
J = lambda p: os.path.join(ROOT, p)
STAGE = J('downloads/dark-replace'); os.makedirs(STAGE, exist_ok=True)
STOP = {'كتاب', 'رساله', 'جزء', 'شرح', 'مختصر', 'في', 'علي', 'من', 'الي', 'عن', 'ومعه', 'ويليه', 'ط', 'ت', 'المسمي'}

def words(t): return [w for w in title_key(t).split() if len(w) > 2 and w not in STOP]
def nat(s): return [int(x) if x.isdigit() else x for x in re.split(r'(\d+)', s)]
def safe(s): return re.sub(r'\s+', ' ', re.sub(r'[\\/:*?"<>|]', ' ', s)).strip(' .')

def read_front(pdf):
    """the first pages' text: the text layer when it has Arabic, else OCR"""
    t = subprocess.run(['pdftotext', '-l', '6', pdf, '-'], capture_output=True, text=True).stdout
    if len(re.findall(r'[؀-ۿ]', t)) > 200: return t
    with tempfile.TemporaryDirectory() as d:
        subprocess.run(['pdftoppm', '-r', '150', '-l', '6', '-gray', pdf, os.path.join(d, 'p')], capture_output=True)
        out = []
        for f in sorted(os.listdir(d)):
            out.append(subprocess.run(['tesseract', os.path.join(d, f), '-', '-l', 'ara'], capture_output=True, text=True).stdout)
    return '\n'.join(out)

def main(cands_json, queue_tsv, review_tsv):
    cands = json.load(open(cands_json, encoding='utf-8'))
    cat = {r['waqfeya_id']: r['phone_category'] for r in csv.DictReader(open(J('data/compare/waqfeya-matches.tsv'), encoding='utf-8'), delimiter='\t')}
    have = {int(l.rstrip('\n').split('\t')[1]) for l in open(J('data/phone/index-now.tsv'), encoding='utf-8') if l.rstrip('\n').split('\t')[1].isdigit()}
    q, review = [], []
    for wid, rec in cands.items():
        title = re.split(r'\s+-\s+(?:ط|ت)[\s.:]', rec['waqfeya'])[0].strip()
        au = re.split(r'[؛;]', rec.get('author') or '')[0].strip()
        vols = int(re.sub(r'\D', '', str(rec.get('volumes') or '1')) or 1)
        tw = words(title); aw = author_tokens(au)
        done = False; notes = []
        for c in rec.get('candidates', []):
            pdfs = sorted(c['pdfs'], key=lambda x: nat(x[0]))
            if len(pdfs) > 2 * vols + 2: notes.append(f'{c["id"]}: {len(pdfs)} PDFs for {vols} volumes (a bundle?)'); continue
            if sum(z for _, z in pdfs) > 2e9: notes.append(f'{c["id"]}: too large'); continue
            if all(z in have for _, z in pdfs): notes.append(f'{c["id"]}: already on the phone (same sizes)'); continue
            first, fsize = pdfs[0]
            local = os.path.join(STAGE, f'{c["id"]}__{re.sub(r"[^A-Za-z0-9._-]", "_", first)}')
            url = f'https://archive.org/download/{c["id"]}/{urllib.parse.quote(first)}'
            if not (os.path.exists(local) and os.path.getsize(local) == fsize):
                subprocess.run(['aria2c', '-q', '-x8', '-s8', '-k1M', '--allow-overwrite=true', '--auto-file-renaming=false',
                                '-d', STAGE, '-o', os.path.basename(local), url], capture_output=True)
            if not (os.path.exists(local) and os.path.getsize(local) == fsize):
                notes.append(f'{c["id"]}: first file not downloaded'); continue
            text = title_key(read_front(local))
            found = [w for w in tw if w in text]
            a_ok = not aw or any(t in text for t in aw)
            score = len(found) / max(1, len(tw))
            if score >= 0.6 and a_ok:
                sec = cat.get(wid) or 'كتب عامة'
                name = safe(title) + (f' - {safe(au)}' if au and safe(au) not in title else '')
                short = safe(re.split(r'\s+(?:=|-|ويليه|ومعه|المسمى|الموسوم)\s+|،', title)[0])
                why = f'«{rec["waqfeya"]}»: Waqfeya item dark; archive.org {c["id"]} — title page read: {len(found)}/{len(tw)} title words' + (', author found' if aw else '')
                if len(pdfs) == 1:
                    q.append([f'file://{local}', fsize, f'Books/{sec}/{name[:150]}.pdf', why])
                else:
                    for n, (f, z) in enumerate(pdfs, 1):
                        src = f'file://{local}' if f == first else f'https://archive.org/download/{c["id"]}/{urllib.parse.quote(f)}'
                        q.append([src, z, f'Books/{sec}/{name[:150]}/{n:02d} - {short[:80]}.pdf', why])
                print(f'OK  {rec["waqfeya"][:60]} ← {c["id"]} ({score:.0%}{", author" if aw else ""}, {len(pdfs)} PDFs)', flush=True)
                done = True; break
            notes.append(f'{c["id"]}: title words {len(found)}/{len(tw)}, author {"yes" if a_ok else "no"}')
            os.remove(local)
        if not done:
            review.append([wid, rec['waqfeya'], au, ' | '.join(notes) or 'no candidate'])
            print(f'--  {rec["waqfeya"][:60]}: {"; ".join(notes)[:150] or "no candidate"}', flush=True)
    with open(queue_tsv, 'w', encoding='utf-8', newline='') as f: csv.writer(f, delimiter='\t').writerows(q)
    with open(review_tsv, 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f, delimiter='\t'); w.writerow(['waqfeya_id', 'name', 'author', 'why not added']); w.writerows(review)
    print(len(q), 'files queued;', len(review), 'books for review')

if __name__ == '__main__':
    main(*sys.argv[1:4])
