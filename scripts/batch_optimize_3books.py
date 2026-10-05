#!/usr/bin/env python3
"""
Batch PDF Optimizer for Risala, Tabari, and Zamakhshari.
Converts bloat RGB scan PDFs into high-clarity 150 DPI DeviceGray PDFs.
Performs verification (%PDF, %%EOF, pdfinfo, size check) before in-place swap.
"""
import os, sys, subprocess, shutil, tempfile

TARGET_DIRS = [
    os.path.expanduser('~/Books/الجوامع/مجلة الرسالة'),
    os.path.expanduser('~/Books/التفسير/جامع البيان عن تأويل آي القرآن - الطبري (ت التركي - هجر)'),
    os.path.expanduser('~/Books/التفسير/الكشاف عن حقائق التنزيل - الزمخشري (دار المعرفة)')
]

def check_pdf(p):
    try:
        if not os.path.exists(p) or os.path.getsize(p) < 1000:
            return False
        with open(p, 'rb') as f:
            if f.read(4) != b'%PDF': return False
            f.seek(max(0, os.path.getsize(p) - 2048))
            if b'%%EOF' not in f.read(): return False
        r = subprocess.run(['pdfinfo', p], capture_output=True)
        return r.returncode == 0
    except Exception:
        return False

def optimize_file(src_path):
    orig_sz = os.path.getsize(src_path)
    tmp_out = src_path + '.opt.tmp'
    cmd = [
        'gs', '-sDEVICE=pdfwrite', '-dCompatibilityLevel=1.4',
        '-sColorConversionStrategy=Gray',
        '-dProcessColorModel=/DeviceGray',
        '-dDownsampleColorImages=true', '-dColorImageDownsampleType=/Bicubic', '-dColorImageResolution=150',
        '-dDownsampleGrayImages=true', '-dGrayImageDownsampleType=/Bicubic', '-dGrayImageResolution=150',
        '-sOutputFile=' + tmp_out,
        '-dNOPAUSE', '-dQUIET', '-dBATCH',
        src_path
    ]
    print(f"Optimizing: {os.path.basename(src_path)} ({orig_sz/(1024*1024):.1f} MB)...", flush=True)
    res = subprocess.run(cmd)
    if res.returncode == 0 and check_pdf(tmp_out):
        new_sz = os.path.getsize(tmp_out)
        reduction = (1 - new_sz / orig_sz) * 100
        print(f"  -> SUCCESS: {new_sz/(1024*1024):.1f} MB (-{reduction:.1f}%)", flush=True)
        # Atomic replace
        os.replace(tmp_out, src_path)
        return orig_sz - new_sz
    else:
        print(f"  -> FAILED optimization or verification for {os.path.basename(src_path)}", flush=True)
        if os.path.exists(tmp_out):
            try: os.remove(tmp_out)
            except OSError: pass
        return 0

def main():
    total_saved = 0
    for d in TARGET_DIRS:
        if not os.path.exists(d):
            continue
        print(f"\n=== Processing folder: {os.path.basename(d)} ===", flush=True)
        files = sorted([os.path.join(d, f) for f in os.listdir(d) if f.endswith('.pdf') and not f.endswith('.opt.tmp')])
        for f in files:
            saved = optimize_file(f)
            total_saved += saved
            print(f"Running total disk saved: {total_saved/(1024*1024*1024):.2f} GB", flush=True)
    print(f"\nALL COMPLETED. Total space saved: {total_saved/(1024*1024*1024):.2f} GB", flush=True)

if __name__ == '__main__':
    main()
