#!/usr/bin/env python3
"""
Batch PDF Optimizer for Majallat al-Risala using the Optimal setting (150 DPI Bicubic Grayscale).
Reduces volume size from ~319 MB to ~196 MB while preserving font sharpness and contrast.
Safe in-place atomic replace with integrity checks.
"""
import os, sys, subprocess, shutil, time

SRC_DIR = os.path.expanduser('~/Books/الجوامع/مجلة الرسالة')
LOG_FILE = os.path.expanduser('~/projects/phone-library/data/changes/risala_opt.log')

def check_pdf(p):
    try:
        if not os.path.exists(p) or os.path.getsize(p) < 1000: return False
        with open(p, 'rb') as f:
            if f.read(4) != b'%PDF': return False
            f.seek(max(0, os.path.getsize(p) - 2048))
            if b'%%EOF' not in f.read(): return False
        return subprocess.run(['pdfinfo', p], capture_output=True).returncode == 0
    except Exception:
        return False

def optimize_vol(src_path):
    orig_sz = os.path.getsize(src_path)
    tmp_out = src_path + '.opt.tmp'
    cmd = [
        'gs', '-sDEVICE=pdfwrite', '-dCompatibilityLevel=1.4',
        '-sColorConversionStrategy=Gray', '-dProcessColorModel=/DeviceGray',
        '-dDownsampleColorImages=true', '-dColorImageDownsampleType=/Bicubic', '-dColorImageResolution=150',
        '-dDownsampleGrayImages=true', '-dGrayImageDownsampleType=/Bicubic', '-dGrayImageResolution=150',
        '-sOutputFile=' + tmp_out, '-dNOPAUSE', '-dQUIET', '-dBATCH', src_path
    ]
    t0 = time.time()
    print(f"Optimizing: {os.path.basename(src_path)} ({orig_sz/(1024*1024):.1f} MB)...", flush=True)
    res = subprocess.run(cmd)
    if res.returncode == 0 and check_pdf(tmp_out):
        new_sz = os.path.getsize(tmp_out)
        reduction = (1 - new_sz / orig_sz) * 100
        elapsed = time.time() - t0
        print(f"  -> SUCCESS: {new_sz/(1024*1024):.1f} MB (-{reduction:.1f}%) in {elapsed:.1f}s", flush=True)
        os.replace(tmp_out, src_path)
        with open(LOG_FILE, 'a') as lf:
            lf.write(f"{time.strftime('%F %T')}\t{os.path.basename(src_path)}\t{orig_sz}\t{new_sz}\n")
        return orig_sz - new_sz
    else:
        print(f"  -> FAILED for {os.path.basename(src_path)}", flush=True)
        if os.path.exists(tmp_out):
            try: os.remove(tmp_out)
            except OSError: pass
        return 0

def main():
    total_saved = 0
    done_files = set()
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r') as lf:
            for line in lf:
                parts = line.strip().split('\t')
                if len(parts) >= 2:
                    done_files.add(parts[1])
    print(f"Already optimized {len(done_files)} files. Skipping them.", flush=True)

    targets = [
        os.path.expanduser('~/Books/الجوامع/مجلة الرسالة'),
        os.path.expanduser('~/Books/التفسير/جامع البيان عن تأويل آي القرآن - الطبري (ت التركي - هجر)'),
        os.path.expanduser('~/Books/التفسير/الكشاف عن حقائق التنزيل - الزمخشري (دار المعرفة)'),
    ]
    for target_dir in targets:
        if not os.path.exists(target_dir):
            continue
        print(f"\n=== STARTING TARGET DIRECTORY: {os.path.basename(target_dir)} ===", flush=True)
        files = sorted([os.path.join(target_dir, f) for f in os.listdir(target_dir) if f.endswith('.pdf') and not f.endswith('.opt.tmp')])
        for f in files:
            fname = os.path.basename(f)
            if fname in done_files:
                continue
            saved = optimize_vol(f)
            total_saved += saved
            done_files.add(fname)
            print(f"Running saved disk: {total_saved/(1024*1024*1024):.2f} GB", flush=True)
    print(f"\nALL 3 TARGETS COMPLETED! Total disk space saved: {total_saved/(1024*1024*1024):.2f} GB", flush=True)

if __name__ == '__main__':
    main()
