"""Closes an item of a review page in data/names/review-closed.tsv after the agent acted on the owner's remark (a tick closes by
itself). For «crop-doubts» the row also records the book's recipe md5, so the book stays closed through later redos as long
as its crop is the one he saw (crop_doubts_page.py; owner 2026-11-07 «كثيرا من ملاحظاتي السابقة ألغيت»).
THE NOTE QUOTES HIM OR SAYS IT IS MINE (owner 2026-11-07, audit rule 3: «الأخير نازل» was closed as «he says it seems alright»
with no such words on record): a note must hold his words in «…» or the words «my judgment»; «REOPEN …» cancels the closes
before it (crop_doubts_page.py).
Usage: python3 scripts/review_close.py REPORT ITEM "note"      (ITEM = the card's data-n, e.g. 0022362994e5-3ba75eb)"""
import csv, hashlib, os, re, sys, time
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J = lambda *p: os.path.join(ROOT, *p)

def recipe_md5(h):
    """the md5 of the recipe file of the latest crop of the book whose path hashes to h (changes.tsv), or None"""
    rf = None
    for r in csv.reader(open(J('data', 'changes', 'changes.tsv'), encoding='utf-8'), delimiter='\t'):
        if len(r) > 5 and r[1] == 'crop' and hashlib.md5(r[2].removeprefix('Books/').encode()).hexdigest()[:12] == h:
            o = re.search(r'original \d+ B md5 (\w+)', r[4]); rf = J('data', 'crop', 'recipes', o.group(1) + '.json') if o else rf
    return hashlib.md5(open(rf, 'rb').read()).hexdigest() if rf and os.path.exists(rf) else None

if __name__ == '__main__':
    report, item, note = sys.argv[1], sys.argv[2], ' '.join(sys.argv[3:])
    if not (re.search(r'«[^»]{2,}»', note) or 'my judgment' in note or note.startswith('REOPEN')):
        sys.exit('the note must quote the owner in «…», or say «my judgment», or start with REOPEN')
    f = [report, item, time.strftime('%Y-%m-%d'), note.replace('\t', ' ').replace('\n', ' ')]
    if report == 'crop-doubts':
        m = recipe_md5(item.split('-')[0])
        if m: f.append('recipe=' + m)
    with open(J('data', 'names', 'review-closed.tsv'), 'a', encoding='utf-8') as out: out.write('\t'.join(f) + '\n')
    print('\t'.join(f))
