"""The Shamela book cards (data/shamela/cards.jsonl, scripts/export_shamela_cards.py) for the reports and the index:
the edition line of a card, whether a phone book is the card's edition, and how a Shamela book was matched (owner,
2026-10-08: «معلومات الشاملة في الفهرس يجب أن تكون أغنى وتعتمد على البطاقات التي عندي في الشاملة المحلية»)."""
import json, os, re
from textnorm import norm
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEST = str.maketrans('٠١٢٣٤٥٦٧٨٩', '0123456789')          # Western digits everywhere (owner, 2026-10-06)

def load():
    p = os.path.join(ROOT, 'data/shamela/cards.jsonl')
    if not os.path.exists(p): return {}
    return {c['id']: c for c in map(json.loads, open(p, encoding='utf-8'))}

def first(v, n=60):
    v = re.sub(r'\s*\[ت [^\]]*\]', '', (v or '').translate(WEST)).strip()        # «[ت ١٤٣٨ هـ]» after an editor's name
    v = re.split(r'\s*[؛]\s*', v)[0]
    return v if len(v) <= n else v[:n].rsplit(' ', 1)[0] + ' …'

def ed_line(c):
    """«ت محمود الأرناؤوط · دار الثقافة العربية، دمشق · ط 2، 1408 هـ · 282 ص»"""
    if not c: return ''
    out = []
    if c.get('editor'): out.append('ت ' + first(c['editor']))
    if c.get('publisher'): out.append(first(c['publisher']))
    if c.get('edition'): out.append('ط ' + first(c['edition'], 40))
    elif c.get('year'): out.append(first(c['year'], 30))
    if c.get('volumes_n'): out.append(f"{c['volumes_n']} ج")
    elif c.get('pages_n'): out.append(f"{c['pages_n']} ص")
    return ' · '.join(out)

GENERIC = set(norm('دار مكتبة مكتبه مؤسسة مؤسسه مطبعة مطبعه المطبعة الكتب العلمية للنشر والتوزيع النشر التوزيع للطباعة الطباعة '
                   'بيروت لبنان القاهرة مصر الرياض دمشق جدة مكة المكرمة المدينة المنورة الكويت عمان الأردن السعودية سوريا '
                   'الإسلامي الإسلامية العربي العربية الطبعة الأولى الثانية الثالثة شركة ومكتبة ومطبعة وأولاده بن ابن عبد '
                   'محمد أحمد علي الله الرحمن تحقيق ت ط').split())
def _toks(s): return {w for w in norm(s).split() if len(w) > 2 and w not in GENERIC}

def phone_edition(folder):
    """the edition part of a phone name: «(ت عبد الله التركي - مؤسسة الرسالة)», «- ط. بيت الأفكار»"""
    m = re.findall(r'\(([^()]*)\)', folder)
    tail = ' '.join(x for x in m if re.match(r'\s*(?:ت|ط|دار|مكتبة|مؤسسة|مطبعة)[\s.]', x) or ' - ' in x)
    m2 = re.search(r'\s-\s(?:ت|ط)[\s.\-]+(.+)$', folder)
    return (tail + ' ' + (m2.group(1) if m2 else '')).strip()

def same_edition(c, folder):
    """'same' (the card's editor, or its publisher when no editor is named, is in the phone name), 'publisher' (only the
    publisher agrees), 'other' (the phone name names another edition), '' (the phone name says nothing)"""
    pe = phone_edition(folder)
    if not c or not pe: return ''
    P = _toks(pe)
    ed, pub = _toks(c.get('editor', '')), _toks(c.get('publisher', '') or '')
    m = re.search(r'(?:^|[\s(])ت[\s.\-]+([^()]+?)(?:\s-\s|\)|$)', pe)
    ped = _toks(m.group(1)) if m else set()                    # the editor the phone name gives
    if ed and ed & P: return 'same'
    if ed and ped: return 'other'                              # two different editors: another edition, whatever the publisher
    if pub and pub & P: return 'same' if not ed else 'publisher'
    return 'other'

SAME = {'same': 'طبعة الشاملة نفسها', 'publisher': 'ناشر الشاملة نفسه', 'other': 'طبعة أخرى', '': ''}

def how_ar(how):
    """the evidence of a match, in words"""
    card = ' (بعنوانه المطبوع في بطاقة الشاملة)' if 'card title' in how else ''
    h = how.replace(' (card title)', '')
    return {'exact': 'العنوان نفسه', 'prefix': 'العنوان مع زيادة أو نقص في آخره', 'prefix+author': 'العنوان والمؤلف',
            'smart-tokens': 'كلمات العنوان والمؤلف', 'cover': 'كلمات العنوان المميِّزة والمؤلف',
            'in-collection': 'مطبوع مع كتاب آخر على الهاتف', 'contained': 'مضمَّن في مجموع أو مجلد على الهاتف',
            'part-of': 'من مجموعه الذي تذكره الشاملة («ضمن …») وهو على الهاتف'}.get(h, h) + card
