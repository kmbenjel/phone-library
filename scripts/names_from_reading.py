"""Names from the title-page readings (data/names/title-read.tsv) under AGENTS.md §4 (scripts/name_compose.py):
«<title> - <author> - ت <editor> - <publisher> <city> <year>», no parentheses or commas; a thesis or a manuscript says so at the
end; a translator is «ترجمة X»; «part» (one volume of a set) stays a folder: «<folder>/NN - <title> - <label>.pdf».
Usage: python3 scripts/names_from_reading.py [N…]   (prints old → new for the readings N, or all)"""
import csv, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from name_compose import compose, B
from rename_plan import redundant

def year_of(y):
    """«1408 هـ / 1988» → «1988»; «1346 هـ» stays; no «/» in a name"""
    y = (y or '').replace('?', '').strip()
    g = re.search(r'\b(1[5-9]\d\d|20\d\d)\b', y)
    if g and not re.fullmatch(r'\d{3,4}\s*هـ', y): return g.group(1)
    h = re.search(r'\b(\d{3,4})\s*هـ', y)
    return f'{h.group(1)} هـ' if h else ''

def name_of(r):
    """publisher, city and year stay separate fields until name_compose renders them (no commas, no repeated city)"""
    t, au, ed, pub, city = r['title'], r['author'], r['editor'], r['publisher'], r['city']
    kind = r.get('kind', '')
    place = '، '.join(x for x in (pub, city.replace('، ', ' و') if city and pub else '') if x)
    if ed and kind == 'ترجمة': edition = f'ت {ed}' + (f' - {place}' if place else '')
    elif ed: edition = f'ت {ed}' + (f' - {place}' if place else '')
    else: edition = f'ط {place}' if place else ''          # «ط» only marks the field for name_compose; not rendered
    extra = [kind] if kind and kind not in ('نظم', 'متن', 'ترجمة') else []
    n = compose(t, '' if (au and redundant(au, t)) else au, edition, year=year_of(r['year']), kinds_extra=extra)
    return n.replace(' - ت ', ' - ترجمة ', 1) if kind == 'ترجمة' and ed else n

if __name__ == '__main__':
    want = set(sys.argv[1:])
    for r in csv.DictReader(open(os.path.join(ROOT, 'data', 'names', 'title-read.tsv'), encoding='utf-8'), delimiter='\t'):
        if want and r['n'] not in want: continue
        print(f"[{r['n']}] {r['verdict']:10} {r['book']}\n      → {name_of(r)}.pdf  [{B(name_of(r))} B]")
