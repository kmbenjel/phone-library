"""Verify doubtful size matches by comparing the first 64 KB of the phone file and the archive.org file.
Input: data/phone/provenance-suspect.tsv (path, size, archive_id, orig_name)
Output: data/phone/provenance-verified.tsv (path, archive_id, orig_name, same|different|error)
provenance.py drops 'different' pairs on its next run."""
import csv, hashlib, os, subprocess, urllib.parse
from concurrent.futures import ThreadPoolExecutor
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
from phone_host import FTP
def head(url, extra=()):
    r = subprocess.run(['curl', '-s', '-L', '--max-time', '90', '-r', '0-65535', *extra, url], capture_output=True)
    return r.stdout[:65536] if r.returncode == 0 else b''
def check(row):
    path, size, aid, orig = row
    a = head(FTP + urllib.parse.quote(path))
    b = head(f'https://archive.org/download/{urllib.parse.quote(aid)}/{urllib.parse.quote(orig)}', ('-A', 'personal-library-catalog/1.0', '--fail', '--retry', '2'))
    if not a or not b: return [path, aid, orig, 'error']
    return [path, aid, orig, 'same' if hashlib.sha1(a).digest() == hashlib.sha1(b).digest() else 'different']
rows = list(csv.reader(open(os.path.join(ROOT, 'data/phone/provenance-suspect.tsv')), delimiter='\t'))
with ThreadPoolExecutor(4) as ex:
    res = list(ex.map(check, rows))
csv.writer(open(os.path.join(ROOT, 'data/phone/provenance-verified.tsv'), 'w'), delimiter='\t').writerows(res)
from collections import Counter
print(Counter(r[3] for r in res))
