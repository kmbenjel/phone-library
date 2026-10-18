#!/usr/bin/env python3
"""Review Plan books one by one in Brave in an independent window.
Preloads 3-4 books ahead from the phone into /tmp/review_<plan>/
When a book's window is closed by the user, immediately deletes its local file and temp profile,
then opens the next book.
Cleans up everything on exit.
Usage:
  python3 scripts/review_brave_flow.py [plan_number_or_file] [start_row]
  e.g.: python3 scripts/review_brave_flow.py 314 1
"""
import atexit
import glob
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

def resolve_plan(arg):
    if os.path.isfile(arg):
        return arg
    p = os.path.join(ROOT, 'plans', f"{arg}-names-read.tsv")
    if os.path.isfile(p):
        return p
    # Try finding matching file in plans/
    matches = glob.glob(os.path.join(ROOT, 'plans', f"*{arg}*.tsv"))
    if matches:
        return matches[0]
    raise FileNotFoundError(f"Plan file not found for: {arg}")

def main():
    plan_arg = sys.argv[1] if len(sys.argv) > 1 else '314'
    start_k = int(sys.argv[2]) if len(sys.argv) > 2 else 1

    plan_path = resolve_plan(plan_arg)
    plan_num = os.path.basename(plan_path).split('-')[0]
    cache_dir = f'/tmp/review_{plan_num}'

    def cleanup_all():
        if os.path.exists(cache_dir):
            shutil.rmtree(cache_dir, ignore_errors=True)
        for d in glob.glob(f'/tmp/brave-rev-{plan_num}-*'):
            shutil.rmtree(d, ignore_errors=True)

    atexit.register(cleanup_all)
    signal.signal(signal.SIGINT, lambda s, f: sys.exit(0))
    signal.signal(signal.SIGTERM, lambda s, f: sys.exit(0))

    rows = []
    for line in open(plan_path, encoding='utf-8'):
        line = line.strip()
        if line:
            rows.append(line.split('\t'))

    total = len(rows)
    os.makedirs(cache_dir, exist_ok=True)

    def file_for(idx):
        k = idx + 1
        name = os.path.basename(rows[idx][1])
        return os.path.join(cache_dir, f"{k} - {name}")

    def download_book(idx):
        if idx >= total: return None
        dst = file_for(idx)
        if os.path.exists(dst) and os.path.getsize(dst) > 0:
            return dst
        src = rows[idx][0].removeprefix('Books/')
        part = dst + '.part'
        try:
            with Phone() as ph:
                ph.get(src, part)
            os.rename(part, dst)
            return dst
        except Exception as e:
            if os.path.exists(part):
                try: os.remove(part)
                except OSError: pass
            print(f"[Error downloading {idx+1}]: {e}", file=sys.stderr)
            return None

    # Background preloader keeping 3-4 books ahead
    current_idx_box = [start_k - 1]
    stop_event = threading.Event()

    def preloader():
        while not stop_event.is_set():
            c = current_idx_box[0]
            # preload from c up to c + 4
            for target in range(c, min(c + 4, total)):
                if stop_event.is_set(): break
                if not os.path.exists(file_for(target)):
                    download_book(target)
            time.sleep(0.5)

    th = threading.Thread(target=preloader, daemon=True)
    th.start()

    # Sequential review loop
    for idx in range(start_k - 1, total):
        current_idx_box[0] = idx
        k = idx + 1
        dst = file_for(idx)

        # Clean up any files older than current index
        for f in os.listdir(cache_dir):
            n = f.split(' - ')[0]
            if n.isdigit() and int(n) < k:
                try: os.remove(os.path.join(cache_dir, f))
                except OSError: pass

        # Wait if file is still downloading
        waited = 0
        while not os.path.exists(dst) and waited < 60:
            time.sleep(0.5)
            waited += 0.5
        if not os.path.exists(dst):
            download_book(idx)

        if not os.path.exists(dst) or os.path.getsize(dst) == 0:
            print(f"Skipping book {k} (could not download)")
            continue

        print(f"[{k}/{total}] Opening in Brave: {os.path.basename(dst)}", flush=True)

        tmp_profile = tempfile.mkdtemp(prefix=f'brave-rev-{plan_num}-{k}-')
        try:
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
            # Wait for user to close this window
            p.wait()
        finally:
            # IMMEDIATELY delete this book and its profile - leave nothing behind!
            if os.path.exists(dst):
                try: os.remove(dst)
                except OSError: pass
            shutil.rmtree(tmp_profile, ignore_errors=True)

    stop_event.set()
    cleanup_all()
    print("All books in the review loop completed.", flush=True)

if __name__ == '__main__':
    main()
