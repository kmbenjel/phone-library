"""Check every book not yet read by eye against its own first pages, with no human (and no model) in the loop
(owner 2026-10-10: automate, spend fewer tokens). The text of pages 1–4 comes from the OCR already made
(data/inspect/ocr.jsonl, tesseract ara+eng) or the PDF's text layer (data/inspect/files.jsonl). For each book:
  title    — share of the name's title words found in that text; author — the name's author words found;
  lines    — the lines that state the author, editor, publisher, edition, year («تأليف، تحقيق، الناشر، دار، الطبعة، 14xx هـ»);
  verdict  — confirmed (title ≥ 0.7 and the author found or none named), partial, CONFLICT (enough text, title < 0.3:
             maybe another book or edition), no-text (no OCR/text: read by eye or OCR first).
→ data/names/auto-check.tsv. Only «CONFLICT», «no-text» and books whose editor/publisher is still missing go to the
reading sheets (scripts/title_sheets.py); the rest is named from these lines and the catalogues.
Usage: python3 scripts/auto_check.py"""
import csv, json, os, re, sys, unicodedata, collections
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from textnorm import norm, title_key, author_tokens
J = lambda *p: os.path.join(ROOT, *p)
N = lambda s: unicodedata.normalize('NFC', s)
INFO = re.compile(r'تأليف|تاليف|تحقيق|حققه|تحقيق وتعليق|شرح|الناشر|دار |مكتبة|مطبعة|المطبعة|الطبعة|طبع|منشورات|جامعة|رسالة|\b1[34]\d\d\s*هـ|\b(19|20)\d\d\b')

def main():
    st = {r['book']: r['status'] for r in csv.DictReader(open(J('data', 'names', 'read-status.tsv'), encoding='utf-8'), delimiter='\t')}
    idx = [N(l.split('\t', 1)[0]) for l in open(J('data', 'phone', 'index-now.tsv'), encoding='utf-8') if l.strip()]
    files_of = collections.defaultdict(list)
    for p in idx:
        parts = p.split('/')
        files_of['/'.join(parts[:2]) if len(parts) >= 3 else p.removesuffix('.pdf')].append(p)
    key, layer = {}, {}
    for l in open(J('data', 'inspect', 'files.jsonl'), encoding='utf-8'):
        d = json.loads(l); key[N(d['path'])] = d.get('key'); layer[d.get('key')] = d.get('text_first') or ''
    ocr = collections.defaultdict(dict)
    for l in open(J('data', 'inspect', 'ocr.jsonl'), encoding='utf-8'):
        try: d = json.loads(l)
        except ValueError: continue
        if int(d.get('page', 99)) <= 4: ocr[d['key']][int(d['page'])] = d.get('text', '')
    c = collections.Counter()
    with open(J('data', 'names', 'auto-check.tsv'), 'w', encoding='utf-8') as w:
        w.write('book\tverdict\ttitle\tauthor\ttext_chars\tlines\n')
        for b, s in sorted(st.items()):
            if s == 'read': continue
            fs = sorted(files_of.get(b, []))
            f = next((x for x in fs if re.search(r'/0*1 - |\(الواجهة\)|- الواجهة', x)), fs[0] if fs else None)
            k = key.get(f) if f else None
            text = '\n'.join(ocr.get(k, {}).get(p, '') for p in sorted(ocr.get(k, {}))) + '\n' + (layer.get(k) or '')
            nt = norm(text)
            name = b.split('/', 1)[1]
            base = re.sub(r'\([^()]*\)', ' ', name)
            parts = [x.strip() for x in base.split(' - ')]
            tk = [x for x in title_key(parts[0]).split() if len(x) > 2]
            au = author_tokens(parts[1]) if len(parts) > 1 and not re.match(r'^(ت|ط)\s', parts[1]) else set()
            words = set(nt.split())
            tr = sum(1 for x in tk if x in words) / max(1, len(tk))
            af = (sum(1 for x in au if x in words) / len(au)) if au else None
            if len(nt) < 40: v = 'no-text'
            elif tr >= 0.7 and (af is None or af >= 0.5): v = 'confirmed'
            elif tr < 0.3: v = 'CONFLICT'
            else: v = 'partial'
            c[v] += 1
            lines = [x.strip() for x in text.split('\n') if INFO.search(x) and 4 < len(x.strip()) < 120][:8]
            w.write(f"{b}\t{v}\t{tr:.2f}\t{'' if af is None else f'{af:.2f}'}\t{len(nt)}\t{' ¦ '.join(lines)}\n")
    print(dict(c), '→ data/names/auto-check.tsv')

if __name__ == '__main__':
    main()
