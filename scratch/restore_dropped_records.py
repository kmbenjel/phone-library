"""One-off (2026-10-06): put back the md5.tsv / files.jsonl records that remap_paths.py dropped today by following substituted
files into the deletion of their set-aside originals (fixed in remap_paths.py). Takes the records of commit 74708d7 (09:00)
whose paths are gone and whose file is not already represented now; remap_paths.py then carries them to their current paths."""
import csv, json, os, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.argv = ['x']; os.chdir(ROOT)
ns = {}
ns['__file__'] = os.path.join(ROOT, 'scripts/remap_paths.py')
exec(open('scripts/remap_paths.py', encoding='utf-8').read().split('rows = [r for r')[0], ns)   # idx, follow, fix, subs
idx, follow = ns['idx'], ns['follow']
old_md5 = [l.split('\t') for l in subprocess.run(['git', 'show', '74708d7:data/phone/md5.tsv'], capture_output=True, text=True).stdout.split('\n') if l]
cur_md5 = [r for r in csv.reader(open('data/phone/md5.tsv', encoding='utf-8'), delimiter='\t') if len(r) == 3]
have = {r[0] for r in cur_md5}
add = [r for r in old_md5 if len(r) == 3 and r[0] not in have and follow(r[0]) and follow(r[0]) not in have and follow(r[0]) in idx]
with open('data/phone/md5.tsv', 'a', encoding='utf-8') as w:
    for r in add: w.write('\t'.join(r) + '\n')
old_f = [json.loads(l) for l in subprocess.run(['git', 'show', '74708d7:data/inspect/files.jsonl'], capture_output=True, text=True).stdout.split('\n') if l]
cur_f = {json.loads(l)['path'] for l in open('data/inspect/files.jsonl', encoding='utf-8')}
addf = [d for d in old_f if d['path'] not in cur_f and follow(d['path']) and follow(d['path']) not in cur_f and follow(d['path']) in idx]
with open('data/inspect/files.jsonl', 'a', encoding='utf-8') as w:
    for d in addf: w.write(json.dumps(d, ensure_ascii=False) + '\n')
print('restored', len(add), 'md5 records,', len(addf), 'inspection records')
