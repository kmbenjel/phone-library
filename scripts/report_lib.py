"""Tiny report builder: the same content rendered to phone-friendly HTML (site/) and Markdown (reports/)."""
import html, os, time
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CSS = """
:root{--bg:#f7f4ee;--card:#fffdf8;--ink:#1f1b16;--muted:#6b6358;--line:#e4ddd0;--accent:#7a4b1e;--good:#2f6b3a;--warn:#9a5a00;--bad:#9b2c2c;--bar:#d9c7a6}
@media (prefers-color-scheme:dark){:root{--bg:#16140f;--card:#1f1c16;--ink:#ece6da;--muted:#a59c8d;--line:#332e25;--accent:#e0a86a;--good:#7bc48a;--warn:#e0b060;--bad:#e08a8a;--bar:#5a4a30}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.75 "Noto Naskh Arabic","Amiri","Scheherazade New","Traditional Arabic",serif}
main{max-width:980px;margin:auto;padding:14px 14px 70px}
a{color:var(--accent)}
h1{font-size:1.35rem;margin:.2em 0}
h2{font-size:1.12rem;margin:1.6em 0 .4em;padding-top:.4em;border-top:1px solid var(--line)}
h3{font-size:1rem;margin:1.1em 0 .3em}
.sub{color:var(--muted);font-size:.88rem}
.back{font-size:.85rem}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:8px;margin:12px 0}
.kpi{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:8px 12px}
.kpi b{display:block;font-size:1.3rem}
.kpi span{color:var(--muted);font-size:.8rem}
.tw{overflow-x:auto;border:1px solid var(--line);border-radius:10px;background:var(--card);margin:8px 0}
table{border-collapse:collapse;width:100%;font-size:.88rem}
th,td{padding:5px 8px;border-bottom:1px solid var(--line);text-align:right;vertical-align:top}
th{position:sticky;top:0;background:var(--card);font-weight:700;white-space:nowrap}
td.n{white-space:nowrap;font-variant-numeric:tabular-nums}
.bar{display:inline-block;height:.55em;background:var(--bar);border-radius:3px;vertical-align:middle;margin-inline-start:4px}
details{background:var(--card);border:1px solid var(--line);border-radius:10px;margin:6px 0;padding:4px 10px}
summary{cursor:pointer;font-weight:700}
.note{background:var(--card);border-inline-start:3px solid var(--accent);padding:6px 10px;border-radius:6px;margin:8px 0;font-size:.92rem}
.good{color:var(--good)} .warn{color:var(--warn)} .bad{color:var(--bad)}
ul{padding-inline-start:1.3em}
"""

class Report:
    def __init__(self, title, subtitle=''):
        self.title, self.subtitle = title, subtitle
        self.h, self.m = [], [f'# {title}', '', subtitle, ''] if subtitle else [f'# {title}', '']

    def h2(self, t, anchor=None):
        a = f' id="{anchor}"' if anchor else ''
        self.h.append(f'<h2{a}>{esc(t)}</h2>'); self.m += ['', f'## {t}', '']

    def h3(self, t):
        self.h.append(f'<h3>{esc(t)}</h3>'); self.m += ['', f'### {t}', '']

    def p(self, t, raw_html=None):
        self.h.append(f'<p>{raw_html or esc(t)}</p>'); self.m += [t, '']

    def note(self, t):
        self.h.append(f'<div class="note">{esc(t)}</div>'); self.m += [f'> {t}', '']

    def ul(self, items):
        self.h.append('<ul>' + ''.join(f'<li>{esc(i)}</li>' for i in items) + '</ul>'); self.m += [f'- {i}' for i in items] + ['']

    def kpis(self, pairs):
        self.h.append('<div class="kpis">' + ''.join(f'<div class="kpi"><b>{esc(v)}</b><span>{esc(k)}</span></div>' for k, v in pairs) + '</div>')
        self.m += [f'- **{k}:** {v}' for k, v in pairs] + ['']

    def table(self, head, rows, numeric=(), links=None, bar_col=None, fold=None, md_limit=None):
        """rows: list of lists. links: {col: row->url}. bar_col: (col, max). fold: summary text -> wrap in <details>."""
        th = ''.join(f'<th>{esc(h)}</th>' for h in head)
        body = []
        for r in rows:
            tds = []
            for i, c in enumerate(r):
                txt = esc(fmt(c))
                if links and i in links and links[i](r): txt = f'<a href="{esc(links[i](r))}">{txt}</a>'
                if bar_col and i == bar_col[0] and bar_col[1]:
                    w = max(1, round(80 * float(c or 0) / bar_col[1])); txt += f'<span class="bar" style="width:{w}px"></span>'
                tds.append(f'<td class="n">{txt}</td>' if i in numeric else f'<td>{txt}</td>')
            body.append('<tr>' + ''.join(tds) + '</tr>')
        t = f'<div class="tw"><table><thead><tr>{th}</tr></thead><tbody>{"".join(body)}</tbody></table></div>'
        self.h.append(f'<details><summary>{esc(fold)}</summary>{t}</details>' if fold else t)
        if fold: self.m += [f'**{fold}**', '']
        mrows = rows if md_limit is None else rows[:md_limit]
        self.m += ['| ' + ' | '.join(head) + ' |', '|' + '---|' * len(head)]
        for r in mrows:
            cells = []
            for i, c in enumerate(r):
                s = fmt(c).replace('|', '/')
                if links and i in links and links[i](r): s = f'[{s}]({links[i](r)})'
                cells.append(s)
            self.m.append('| ' + ' | '.join(cells) + ' |')
        if md_limit is not None and len(rows) > md_limit: self.m.append(f'| … {len(rows) - md_limit} more rows in the TSV data file |' + ' |' * (len(head) - 1))
        self.m.append('')

    def write(self, name):
        stamp = time.strftime('%Y-%m-%d %H:%M')
        page = (f'<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8">'
                f'<meta name="viewport" content="width=device-width, initial-scale=1"><title>{esc(self.title)}</title>'
                f'<style>{CSS}</style></head><body><main><div class="back"><a href="00 - الفهرس العام.html">→ الفهرس العام</a></div>'
                f'<h1>{esc(self.title)}</h1><div class="sub">{esc(self.subtitle)} · أُنشئ {stamp}</div>' + '\n'.join(self.h) + '</main></body></html>')
        os.makedirs(os.path.join(ROOT, 'site'), exist_ok=True); os.makedirs(os.path.join(ROOT, 'reports'), exist_ok=True)
        open(os.path.join(ROOT, 'site', name + '.html'), 'w').write(page)
        open(os.path.join(ROOT, 'reports', name + '.md'), 'w').write('\n'.join(self.m + ['', f'_Generated {stamp}_', '']))
        return name

def esc(s): return html.escape(str(s if s is not None else ''))

def fmt(c):
    if isinstance(c, float): return f'{c:,.1f}'
    if isinstance(c, int): return f'{c:,}'
    return str(c if c is not None else '')

def pct(a, b): return f'{(100.0 * a / b):.1f}%' if b else '—'

def gb(b): return f'{b / 2**30:,.1f} GB' if b >= 2**30 else f'{b / 2**20:,.0f} MB'
