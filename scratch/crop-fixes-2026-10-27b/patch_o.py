"""Fix O (2026-10-27, regression 26i's diff on فهرسة ابن خير acb87508dd15): (1) AN ORNAMENT THE BOOK REPEATS — the
end-of-section fleuron, a 59 pt square under the text — was read as a stain (blots) on 12 pages: the repeat rule wants a
stain at the same place (height too) on ≥ 3 % of the text pages, and a section ends anywhere on the page (12 of ≈ 370
pages). Now a «stain» at least M across both ways whose twin (same width and height ± 10 %, its centre on the same vertical
line ± 3 % of the page) stands on 3 other text pages or more, at any height, within the text's columns (punch holes repeat alike in the margin), is
print: content again (p['ornament']), part
of the text block when its centre lies within the text's columns. Surveyed on the 26h recipes of all 31 regression books:
ornament-sized stains repeat only there. (2) A DODGE THAT GAINS NOTHING: the vertical dodge slid those pages' boxes to the
page's top (crop y0 = 0) while the box still held the whole fleuron — the page number 120 pt lower than on the pages
around. A slide that leaves as much of the mark (with its 0.6 % blur room) in the box as before is not made
(p['stain_kept']). The same futile slide on 10 more pages of 5 books in 26h (أسرار البلاغة pp. 82–107, مناقب الإمام أحمد
p. 710, f134344a7421 p. 167, 435bf8357444 p. 96, c63a21351cba p. 441). (3) A PAGE NUMBER READ AS DUST — «- ٥ -» (ابن خير
ص 4: three grains each under SPECK, alone above a chapter's first lines; the «(١)» under it taken for the number and the page
placed on itself, 30 pt off), مناقب الإمام أحمد ص 500–601 (at the foot, 5 pt from the box's edge): specks sitting together
where the book prints its page number (the folio of max(3, 3 %) other pages, same place and size as the folio-stain rule)
are the page's number when its own was not found there. Usage: patch_o.py SRC DST"""
import sys
src, dst = sys.argv[1:3]
s = open(src, encoding='utf-8').read()

def sub(old, new):
    global s
    assert s.count(old) == 1, old[:80]
    s = s.replace(old, new)

sub("""            if not p.get('folio'): p['folio'] = list(bl[:4]) + ['foot' if (bl[1] >= t[3] - 1 if t else bl[1] > h / 2) else 'head']
""", """            if not p.get('folio'): p['folio'] = list(bl[:4]) + ['foot' if (bl[1] >= t[3] - 1 if t else bl[1] > h / 2) else 'head']
    # AN ORNAMENT THE BOOK REPEATS (2026-10-27, فهرسة ابن خير: the end-of-section fleuron, a 59 pt square under the text,
    # read as a stain on 12 pages — a section ends anywhere on the page, so its place never repeats, and 12 pages are
    # fewer than 3 % of the book): a «stain» at least M across both ways whose twin — the same width and height ± 10 %, its
    # centre on the same vertical line ± 3 % of the page — stands on 3 other text pages or more, at any height, is that
    # print: content again (the box had slid to the page's top to dodge it), and part of the page's box and text block
    # (within the text's columns) once its pages are sorted full or short below — a section's end stays a short page.
    # A stain is never so alike from page to page; thin bars and specks are not M across; and it stands within the text's
    # columns, as a fleuron does — punch holes repeat alike too, but in the margin
    def same_block(a, b, w):
        aw, ah, bw_, bh_ = a[2] - a[0], a[3] - a[1], b[2] - b[0], b[3] - b[1]
        return abs((a[0] + a[2]) - (b[0] + b[2])) / 2 <= 0.03 * w and 0.9 <= (aw + 1) / (bw_ + 1) <= 1.1 \\
            and 0.9 <= (ah + 1) / (bh_ + 1) <= 1.1
    allo = [(i, bl) for i in text for bl in pages[i].get('blots', [])
            if min(bl[2] - bl[0], bl[3] - bl[1]) >= M * pages[i]['w'] / REF and bl[3] - bl[1] < 0.25 * pages[i]['h']
            and pages[i].get('text') and pages[i]['text'][0] <= (bl[0] + bl[2]) / 2 <= pages[i]['text'][2]]
    for i, bl in [(i, bl) for i, bl in allo if sum(1 for j, c in allo if j != i and same_block(bl, c, pages[i]['w'])) >= 3]:
        pages[i]['blots'].remove(bl); pages[i].setdefault('ornament', []).append([round(v, 1) for v in bl])
    # A PAGE NUMBER READ AS DUST (2026-10-27, فهرسة ابن خير ص 4: «- ٥ -», three grains each under SPECK alone above a
    # chapter's first lines — marks() takes such a group outside the text block for dust; turned 0.15° in 26h its grains
    # merged and it was read, unturned in 26i the «(١)» under it was taken for the number and the page placed on itself, the
    # box 30 pt off; مناقب الإمام أحمد ص 500–601: the number at the foot 5 pt from the box's edge): specks that together sit
    # where the book prints its page number — the folio of 3 other pages or more (3 %), the same place and size as for a
    # stain above — are that number when the page's own was not found there: print again, the page's folio, part of the
    # text block when it lies within the text's columns
    fols = [(j, pages[j]['folio']) for j in text if pages[j].get('folio')]
    for i in text:
        p = pages[i]; w, h = p['w'], p['h']; sp = p.get('specks') or []
        at = lambda u: [f for j, f in fols if j != i and same_place(u, f, w, h)]
        if not sp or (p.get('folio') and len(at(p['folio'])) >= max(3, int(0.03 * len(text)))): continue
        g_, groups = M * w / REF, []
        for s in sp:
            for gr in groups:
                if any(s[0] - g_ <= u[2] and u[0] - g_ <= s[2] and s[1] - g_ <= u[3] and u[1] - g_ <= s[3] for u in gr): gr.append(s); break
            else: groups.append([s])
        for gr in groups:
            u = union(gr); f_ = at(u)
            if len(f_) < max(3, int(0.03 * len(text))): continue
            for s in gr: p['specks'].remove(s)
            p['box'] = union([p['box'], u]); t = p.get('text'); p['folio_specks'] = [round(v, 1) for v in u]
            if t and t[0] <= (u[0] + u[2]) / 2 <= t[2]: p['text'] = union([t, u])
            k_ = [f[4] for f in f_]; p['folio'] = list(u) + [max(set(k_), key=k_.count)]
            break
""")

sub("""    full_h = [i for i in text if bh[i] >= 0.9 * q(bh.values(), 0.5)]
""", """    full_h = [i for i in text if bh[i] >= 0.9 * q(bh.values(), 0.5)]
    # an ornament (above) joins its page's box and text block only now: a page ending in a section's fleuron stays a short
    # page that takes its neighbours' place — counted full by it, ابن خير ص 304 was centred on itself, its number 15 pt low
    for i in text:
        for o in pages[i].get('ornament') or []:
            p = pages[i]; p['box'] = union([p['box'], o]); t = p.get('text')
            if t and t[0] <= (o[0] + o[2]) / 2 <= t[2]: p['text'] = union([t, o])
""")

sub("""        px_, py_ = 0.006 * p['w'], 0.006 * p['h']
        avoid = [[v[0] - px_, v[1] - py_, v[2] + px_, v[3] + py_] for v in avoid]
""", """        px_, py_ = 0.006 * p['w'], 0.006 * p['h']
        avoid = [[v[0] - px_, v[1] - py_, v[2] + px_, v[3] + py_] for v in avoid]
        # a slide that leaves as much of the mark in the box as before gains nothing and costs the page its place (2026-10-27,
        # فهرسة ابن خير ص 167: slid to the page's top, the fleuron still whole in the box, the page number 120 pt low)
        def seen(m, c): return max(0.0, min(m[2], c[2]) - max(m[0], c[0])) * max(0.0, min(m[3], c[3]) - max(m[1], c[1]))
""")

sub("""                        if min(ml, mr) < 0.6 * max(ml, mr): p['stain_kept'] = True; continue
                        want = nx; nx = cand; b = [round(nx, 1), b[1], round(nx + b[2] - b[0], 1), b[3]]; p['dodged'] = True
""", """                        if min(ml, mr) < 0.6 * max(ml, mr): p['stain_kept'] = True; continue
                        s_ = nx - cand; s_ = -s_ if s_ and p.get('paper', 0) >= 235 and abs(s_) <= 0.03 * p['w'] else 0.0
                        if seen([bl[0] + s_, bl[1], bl[2] + s_, bl[3]], [cand, b[1], cand + b[2] - b[0], b[3]]) >= 0.999 * seen(bl, b):
                            p['stain_kept'] = True; continue
                        want = nx; nx = cand; b = [round(nx, 1), b[1], round(nx + b[2] - b[0], 1), b[3]]; p['dodged'] = True
""")

sub("""                        if min(mt, mbm) < 0.35 * max(mt, mbm): p['stain_kept'] = True; continue
""", """                        if min(mt, mbm) < 0.35 * max(mt, mbm): p['stain_kept'] = True; continue
                        if seen(bl, [b[0], cand, b[2], cand + b[3] - b[1]]) >= 0.999 * seen(bl, b): p['stain_kept'] = True; continue
""")
open(dst, 'w', encoding='utf-8').write(s)
print('patched', dst)
