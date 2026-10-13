"""A tiny review server on this laptop only (127.0.0.1), so the owner can check and comment from the HTML reports
(owner 2026-10-10: «for html report gimme tools to check and comment from there»).
  GET  /                      → the report of unreadable names (site/names-unreadable.html)
  GET  /<page>.html           → any page of site/
  GET  /copies/<file>         → the local copy of a book (data/names/copies/), opened in the browser's PDF viewer
  GET  /ocr/<book>/<file>     → the original and the cleaned copy of an OCR sample book (data/improve/ocr/)
  GET  /api/comments?r=REPORT → the latest check/comment per item of that report
  POST /api/comment           → {report, n, checked, comment} appended to data/names/review-comments.jsonl (with the time)
Comments are read back by the agent from data/names/review-comments.jsonl. Nothing else is served or written.
Prints one line per page opened and per comment saved (run it in a Terminal to watch, or tail -f logs/review-server.log).
Usage: python3 scripts/review_server.py [port]   (default 8765; open http://127.0.0.1:8765/)"""
import json, os, sys, time, urllib.parse
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE, COPIES = os.path.join(ROOT, 'site'), os.path.join(ROOT, 'data', 'names', 'copies')
OCR = os.path.join(ROOT, 'data', 'improve', 'ocr')            # /ocr/<book>/orig.pdf|final.pdf (ocr_clean.py)
LOG = os.path.join(ROOT, 'data', 'names', 'review-comments.jsonl')

def latest(report):
    out = {}
    if os.path.exists(LOG):
        for l in open(LOG, encoding='utf-8'):
            try: d = json.loads(l)
            except ValueError: continue
            if d.get('report') == report: out[str(d.get('n'))] = d
    return out

say = lambda *a: print(time.strftime('%H:%M:%S'), *a, flush=True)    # one line per page opened / comment saved

class H(SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
    def send_json(self, obj, code=200):
        b = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(code); self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(b))); self.end_headers(); self.wfile.write(b)
    def translate_path(self, path):
        p = urllib.parse.unquote(urllib.parse.urlsplit(path).path)
        base, rel = (COPIES, p[len('/copies/'):]) if p.startswith('/copies/') else \
                    (OCR, p[len('/ocr/'):]) if p.startswith('/ocr/') else (SITE, p.lstrip('/') or 'names-unreadable.html')
        full = os.path.realpath(os.path.join(base, rel))
        return full if full.startswith(os.path.realpath(base) + os.sep) else os.path.join(SITE, '__nope__')
    def do_GET(self):
        u = urllib.parse.urlsplit(self.path)
        if u.path == '/api/comments':
            return self.send_json(latest(urllib.parse.parse_qs(u.query).get('r', [''])[0]))
        if u.path == '/':
            self.send_response(302); self.send_header('Location', '/names-unreadable.html'); self.end_headers(); return
        if u.path.endswith('.html'): say('opened', urllib.parse.unquote(u.path).lstrip('/'))
        return super().do_GET()
    def do_POST(self):
        if urllib.parse.urlsplit(self.path).path != '/api/comment': return self.send_json({'error': 'not found'}, 404)
        try:
            d = json.loads(self.rfile.read(int(self.headers.get('Content-Length', 0) or 0)) or b'{}')
            rec = {'time': time.strftime('%F %T'), 'report': str(d.get('report', ''))[:60], 'n': str(d.get('n', ''))[:20],
                   'checked': bool(d.get('checked')), 'comment': str(d.get('comment', ''))[:4000]}
        except (ValueError, TypeError):
            return self.send_json({'error': 'bad request'}, 400)
        with open(LOG, 'a', encoding='utf-8') as w: w.write(json.dumps(rec, ensure_ascii=False) + '\n')
        say(f"saved  {rec['report']} #{rec['n']}" + (' ✓' if rec['checked'] else '') + (f" — {rec['comment'][:100]}" if rec['comment'] else ''))
        return self.send_json({'ok': True, 'time': rec['time']})

if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
    srv = ThreadingHTTPServer(('127.0.0.1', port), H)
    say(f'review server on http://127.0.0.1:{port}/ — comments → data/names/review-comments.jsonl (Ctrl+C stops it)')
    srv.serve_forever()
