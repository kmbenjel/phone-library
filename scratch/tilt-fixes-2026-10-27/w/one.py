"""one.py BOOK PAGE[,PAGE…] — the new book_crop's verdict on chosen pages (verify with only=…), every flag printed, beside 26h's"""
import sys, json
sys.path.insert(0, '/home/k/projects/phone-library/scripts')
import book_crop as bc
C = '/home/k/.cache/phone-library/crop-regress/'
h = sys.argv[1]; pages = [int(x) for x in sys.argv[2].split(',')]
old = json.load(open(C + h + '.20d30c2020.json'))
skip = ('crop', 'show', 'cut_specks', 'specks', 'blots', 'edge', 'lines', 'rules', 'allowed', 'core', 'text', 'stains',
        'edge_letters', 'move', 'scale', 'w', 'h', 'paper')
rec = bc.plan(C + h + '.pdf', 1, owner_turns={})
for g in pages:
    p, q = old['pages'][g - 1], rec['pages'][g - 1]
    print(g, '26h:', {k: v for k, v in p.items() if k not in skip})
    print(g, 'new:', {k: v for k, v in q.items() if k not in skip})
