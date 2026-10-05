import csv, ftplib, os, re, sys, time, urllib.parse
import requests
from concurrent.futures import ThreadPoolExecutor

from phone_host import FTP, HOST
FTP_URL = FTP
parsed_ftp = urllib.parse.urlparse(FTP_URL)
FTP_HOST = parsed_ftp.hostname or HOST
FTP_PORT = parsed_ftp.port or 2221
FTP_ROOT = parsed_ftp.path if parsed_ftp.path else '/Books'

def get_waqfeya_pdfs(url):
    try:
        html = requests.get(url, timeout=15).text
        # Extract archive.org direct download links (pdf)
        links = re.findall(r'href=["\'](https?://(?:www\.)?archive\.org/download/[^"\']+\.pdf)["\']', html, re.I)
        return list(set(links))
    except:
        return []

def get_shamela_pdf(url):
    try:
        html = requests.get(url, timeout=15).text
        # Typically looks like /index.php/book/export_pdf/... or similar
        m = re.search(r'href=["\']([^"\']+/export_pdf/[^"\']+)["\']', html)
        if m:
            link = m.group(1)
            if not link.startswith('http'): 
                link = 'https://shamela.ws' + link
            return [link]
    except:
        pass
    return []

def ftp_ensure_dir(ftp, path):
    parts = [p for p in path.split('/') if p]
    curr = ''
    for p in parts:
        curr += '/' + p
        try:
            ftp.cwd(curr)
        except:
            try:
                ftp.mkd(curr)
                ftp.cwd(curr)
            except:
                pass

def process_book(row):
    title = row['title'].replace('/', '-').replace(':', '-')
    cat = row['category']
    url = row['url']
    
    pdfs = []
    if url.lower().endswith('.pdf'):
        pdfs = [url]
    elif 'shamela.ws' in url:
        pdfs = get_shamela_pdf(url)
    else:
        pdfs = get_waqfeya_pdfs(url)
        
    if not pdfs:
        print(f"FAILED (No PDF links found): {title} ({url})")
        return
        
    try:
        ftp = ftplib.FTP()
        ftp.connect(FTP_HOST, FTP_PORT, timeout=30)
        ftp.login()
    except Exception as e:
        print(f"FTP Connect Error for {title}: {e}")
        return
        
    # If a book has multiple PDFs (volumes), it gets its own subfolder.
    # Otherwise, it goes straight into the category folder.
    target_dir = f"{FTP_ROOT}/{cat}/{title}" if len(pdfs) > 1 else f"{FTP_ROOT}/{cat}"
    ftp_ensure_dir(ftp, target_dir)
    
    for link in pdfs:
        fname = link.split('/')[-1]
        # Rename the file nicely if it's a single volume
        if len(pdfs) == 1: 
            fname = f"{title}.pdf"
            
        try:
            size = ftp.size(fname)
            if size and size > 50000: # Exists and > 50KB
                print(f"SKIPPED (Exists): {title} -> {fname}")
                continue
        except:
            pass # Does not exist yet
            
        print(f"DOWNLOADING: {title} ({fname})")
        local_path = f"/tmp/{fname}"
        
        success = False
        for attempt in range(3):
            try:
                with requests.get(link, stream=True, timeout=45) as r:
                    r.raise_for_status()
                    with open(local_path, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=65536): 
                            f.write(chunk)
                success = True
                break
            except Exception as e:
                print(f"Attempt {attempt+1} failed for {fname}: {e}")
                time.sleep(3)
                
        if not success:
            print(f"ERROR on {title} ({fname}): All download attempts failed.")
            if os.path.exists(local_path): os.remove(local_path)
            continue
            
        try:
            print(f"UPLOADING: {fname} to {target_dir}")
            with open(local_path, 'rb') as f:
                ftp.storbinary(f'STOR {fname}', f)
            os.remove(local_path)
            print(f"SUCCESS: {title} -> {fname}")
        except Exception as e:
            print(f"FTP ERROR on {title} ({fname}): {e}")
            if os.path.exists(local_path): os.remove(local_path)
            
    try:
        ftp.quit()
    except:
        pass

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/download_missing.py plans/download_batch.tsv")
        return
        
    plan = list(csv.DictReader(open(sys.argv[1]), delimiter='\t'))
    print(f"Starting dynamic download of {len(plan)} books with 4 threads...")
    
    with ThreadPoolExecutor(max_workers=4) as ex:
        ex.map(process_book, plan)
        
    print("Download batch completed.")

if __name__ == '__main__':
    main()
