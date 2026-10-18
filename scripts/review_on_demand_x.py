#!/usr/bin/env python3
"""Watch data/names/review-comments.jsonl.
Whenever the owner types 'x' in the comment for a row of plan-314,
immediately fetch that book and open it in Brave in an independent window.
When closed by the user, delete the local file and temporary profile immediately.
"""
import atexit
import glob
import json
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from crop_batch import Phone

PLAN_FILE = os.path.join(ROOT, 'plans', '314-names-read.tsv')
COMMENTS_LOG = os.path.join(ROOT, 'data', 'names', 'review-comments.jsonl')
CACHE_DIR = '/tmp/review_314_x'

def cleanup_all():
    if os.path.exists(CACHE_DIR):
        shutil.rmtree(CACHE_DIR, ignore_errors=True)
    for d in glob.glob('/tmp/brave-rev-x-*'):
        shutil.rmtree(d, ignore_errors=True)

atexit.register(cleanup_all)
signal.signal(signal.SIGINT, lambda s, f: sys.exit(0))
signal.signal(signal.SIGTERM, lambda s, f: sys.exit(0))

import re

def find_plan_file(report):
    token = re.sub(r'^[^\d]*', '', report).strip()
    if not token:
        return None
    matches = glob.glob(os.path.join(ROOT, 'plans', f'{token}-*.tsv'))
    if not matches:
        matches = glob.glob(os.path.join(ROOT, 'plans', f'{token}*.tsv'))
    if not matches:
        m = re.search(r'\d+', token)
        if m:
            num = m.group(0)
            matches = glob.glob(os.path.join(ROOT, 'plans', f'{num}-*.tsv')) or glob.glob(os.path.join(ROOT, 'plans', f'{num}*.tsv'))
    if matches:
        matches.sort()
        return matches[0]
    return None

def get_plan_row(report, k):
    plan_file = find_plan_file(report)
    if not plan_file or not os.path.exists(plan_file):
        return None, 0, plan_file
    rows = []
    with open(plan_file, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(line.split('\t'))
    if 1 <= k <= len(rows):
        return rows[k - 1], len(rows), plan_file
    return None, len(rows), plan_file

def safe_cache_filename(report, k, proposed_name):
    prefix = f"{report}-row{k} - "
    ext = os.path.splitext(proposed_name)[1] or '.pdf'
    base = os.path.splitext(proposed_name)[0]
    # Linux NAME_MAX is 255 bytes. Keep plenty of headroom for prefix, ext, and '.part'
    max_title_bytes = 210 - len(prefix.encode('utf-8')) - len(ext.encode('utf-8'))
    if max_title_bytes < 30:
        max_title_bytes = 40
    safe_base = base.encode('utf-8')[:max_title_bytes].decode('utf-8', errors='ignore')
    return f"{prefix}{safe_base}{ext}"

def main():
    os.makedirs(CACHE_DIR, exist_ok=True)

    # Record current file position of comments log to only process NEW comments
    last_pos = 0
    if os.path.exists(COMMENTS_LOG):
        last_pos = os.path.getsize(COMMENTS_LOG)

    currently_open = set()
    lock = threading.Lock()

    def open_book_worker(report, k):
        key = (report, k)
        with lock:
            if key in currently_open:
                return
            currently_open.add(key)

        try:
            row_info, total, plan_file = get_plan_row(report, k)
            if not row_info:
                print(f"[{report} Row {k}] Not found in plan (total rows: {total}, file: {plan_file})", file=sys.stderr, flush=True)
                return

            src = row_info[0].removeprefix('Books/')
            alt_src = row_info[1].removeprefix('Books/') if len(row_info) > 1 else None
            proposed_name = os.path.basename(row_info[1])
            cached_filename = safe_cache_filename(report, k, proposed_name)
            dst = os.path.join(CACHE_DIR, cached_filename)

            print(f"[Triggered {report} row {k}/{total}] Downloading: {proposed_name}\n  Source on phone: {src}", flush=True)
            if not os.path.exists(dst) or os.path.getsize(dst) == 0:
                part = dst + '.part'
                candidates = [src]
                if alt_src and alt_src != src:
                    candidates.append(alt_src)

                downloaded = False
                last_err = None
                for cand in candidates:
                    for attempt in range(2):
                        try:
                            with Phone() as ph:
                                ph.get(cand, part)
                            os.rename(part, dst)
                            downloaded = True
                            break
                        except Exception as err:
                            last_err = err
                            if os.path.exists(part):
                                try: os.remove(part)
                                except OSError: pass
                            if attempt == 0 and len(candidates) == 1:
                                print(f"[{report} Row {k}] FTP attempt 1 failed: {err}. Retrying in 1s...", flush=True)
                                time.sleep(1)
                    if downloaded:
                        break
                if not downloaded:
                    raise last_err

            tmp_profile = tempfile.mkdtemp(prefix=f'brave-rev-x-{k}-')
            try:
                print(f"[{report} Row {k}] Opening in Brave...", flush=True)
                file_url = f"file://{os.path.abspath(dst)}"
                env = dict(os.environ)
                p = subprocess.Popen([
                    'brave-browser',
                    f'--user-data-dir={tmp_profile}',
                    '--no-first-run',
                    '--no-default-browser-check',
                    '--new-window',
                    file_url
                ], env=env)
                p.wait()
                print(f"[{report} Row {k}] Closed by user. Cleaning up...", flush=True)
            finally:
                if os.path.exists(dst):
                    try: os.remove(dst)
                    except OSError: pass
                if os.path.exists(dst + '.part'):
                    try: os.remove(dst + '.part')
                    except OSError: pass
                shutil.rmtree(tmp_profile, ignore_errors=True)
        except Exception as e:
            print(f"[Error opening {report} row {k}]: {e}", file=sys.stderr, flush=True)
        finally:
            with lock:
                currently_open.discard(key)

    print("Watching review-comments.jsonl for 'x' on plans (317, 314, etc.)...", flush=True)

    while True:
        if os.path.exists(COMMENTS_LOG):
            cur_size = os.path.getsize(COMMENTS_LOG)
            if cur_size < last_pos: # truncated/rotated
                last_pos = 0
            if cur_size > last_pos:
                with open(COMMENTS_LOG, 'r', encoding='utf-8') as f:
                    f.seek(last_pos)
                    new_lines = f.readlines()
                    last_pos = f.tell()

                for line in new_lines:
                    line = line.strip()
                    if not line: continue
                    try:
                        d = json.loads(line)
                    except ValueError:
                        continue

                    report = d.get('report', '')
                    if report.startswith('plan-'):
                        cmt = d.get('comment', '').strip().lower()
                        # If comment starts with x or is x
                        if cmt == 'x' or cmt.startswith('x'):
                            n_str = str(d.get('n', ''))
                            if n_str.isdigit():
                                k = int(n_str)
                                t = threading.Thread(target=open_book_worker, args=(report, k), daemon=True)
                                t.start()
        time.sleep(0.2)

if __name__ == '__main__':
    main()
