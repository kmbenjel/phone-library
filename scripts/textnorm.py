"""Arabic normalization + title/author keys shared by the comparison scripts."""
import re
STOP_AUTH = set('بن ابن ابي ابو ابا عبد الله محمد احمد علي الامام الحافظ الشيخ العلامه القاضي الدين شيخ الاسلام ت ط'.split())
def norm(s):
    s = re.sub(r'[ً-ْٰـ]', '', s or '')
    for a, b in (('أ', 'ا'), ('إ', 'ا'), ('آ', 'ا'), ('ٱ', 'ا'), ('ة', 'ه'), ('ى', 'ي'), ('ؤ', 'و'), ('ئ', 'ي'), ('ء', ''), ('ـ', '')):
        s = s.replace(a, b)
    s = re.sub(r'[^ء-ي0-9 ]', ' ', s)
    return ' '.join(s.split())
def title_key(t):
    t = re.sub(r'\([^)]*\)|\[[^\]]*\]', ' ', t or '')
    t = re.split(r'\s+-\s+|\s+ط\s|\s+ت\s', ' ' + t + ' ')[0]
    w = norm(t).split()
    if w and w[0] == 'كتاب' and len(w) > 1: w = w[1:]
    return ' '.join(w)
def author_tokens(a):
    return {w for w in norm(a).split() if w not in STOP_AUTH and len(w) > 2}
