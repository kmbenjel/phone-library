"""Upload the indexes, reports, guide and data to the phone: Books/فهارس الويب/ (overwrites only these generated files)."""
import os, shutil, subprocess, glob
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J = lambda p: os.path.join(ROOT, p)
OUT = J('build/فهارس الويب'); shutil.rmtree(J('build'), ignore_errors=True)
os.makedirs(OUT + '/data'); os.makedirs(OUT + '/md')
for f in glob.glob(J('site/*.html')): shutil.copy(f, OUT)
for f in glob.glob(J('reports/*.md')): shutil.copy(f, OUT + '/md')
shutil.copy(J('AGENTS.md'), OUT)
for f in ('data/catalog.json', 'data/catalog.tsv', 'data/compare/waqfeya-matches.tsv', 'data/compare/shamela-matches.tsv',
          'data/changes/changes.tsv', 'data/phone/rename-review.tsv', 'data/mappings/shamela-to-phone.tsv', 'data/mappings/waqfeya-to-phone.tsv'):
    if os.path.exists(J(f)): shutil.copy(J(f), OUT + '/data')
# copy (not sync): never deletes anything already in the phone folder
r = subprocess.run(['rclone', 'copy', OUT, 'phone:Books/فهارس الويب', '--inplace', '--no-update-modtime', '-q'], capture_output=True, text=True)
print('published' if r.returncode == 0 else 'ERROR ' + r.stderr[-500:])
