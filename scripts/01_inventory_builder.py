import ftplib, json, os
from datetime import datetime

from phone_host import HOST
FTP_HOST = os.environ.get('PHONE_FTP_HOST') or HOST
FTP_PORT = int(os.environ.get('PHONE_FTP_PORT', 2221))
FTP_ROOT = '/Books'

inventory = {
    'last_updated': datetime.now().isoformat(),
    'categories': {},
    'total_books': 0,
    'total_files': 0,
    'total_size_bytes': 0
}

def walk_ftp(ftp, path, category_name=None, book_name=None):
    try:
        ftp.cwd(path)
        items = []
        ftp.retrlines('LIST', items.append)
    except Exception as e:
        print(f"Error accessing {path}: {e}")
        return

    for item in items:
        # Example LIST output (varies by server, usually Unix style):
        # drwxr-xr-x   2 user group            0 Oct  3 19:16 FolderName
        # -rw-r--r--   1 user group      2897896 Oct  3 19:16 file.pdf
        parts = item.split(None, 8)
        if len(parts) < 9: continue
        
        perms = parts[0]
        size = int(parts[4])
        name = parts[8]
        
        if name in ['.', '..']: continue
        
        is_dir = perms.startswith('d')
        full_path = f"{path}/{name}"
        
        if path == FTP_ROOT:
            # We are at the category level
            if is_dir:
                if name not in inventory['categories']:
                    inventory['categories'][name] = {'books': {}}
                walk_ftp(ftp, full_path, category_name=name)
        
        elif category_name and not book_name:
            # We are inside a category, looking at books
            if is_dir:
                # Multi-volume book in its own folder
                inventory['categories'][category_name]['books'][name] = {
                    'type': 'folder',
                    'path': full_path,
                    'files': [],
                    'total_size': 0,
                    'status': 'unverified'
                }
                inventory['total_books'] += 1
                walk_ftp(ftp, full_path, category_name=category_name, book_name=name)
            elif name.lower().endswith('.pdf'):
                # Single-volume book (PDF directly in category)
                b_name = name.rsplit('.pdf', 1)[0]
                inventory['categories'][category_name]['books'][b_name] = {
                    'type': 'file',
                    'path': full_path,
                    'files': [{'name': name, 'size': size}],
                    'total_size': size,
                    'status': 'unverified'
                }
                inventory['total_books'] += 1
                inventory['total_files'] += 1
                inventory['total_size_bytes'] += size
                
        elif category_name and book_name:
            # We are inside a multi-volume book folder
            if not is_dir and name.lower().endswith('.pdf'):
                inventory['categories'][category_name]['books'][book_name]['files'].append({'name': name, 'size': size})
                inventory['categories'][category_name]['books'][book_name]['total_size'] += size
                inventory['total_files'] += 1
                inventory['total_size_bytes'] += size


try:
    print(f"Connecting to {FTP_HOST}:{FTP_PORT}...")
    ftp = ftplib.FTP()
    ftp.connect(FTP_HOST, FTP_PORT, timeout=15)
    ftp.login()
    print("Connected! Scanning library structure...")
    walk_ftp(ftp, FTP_ROOT)
    ftp.quit()
    
    with open('data/phone_master_catalog.json', 'w', encoding='utf-8') as f:
        json.dump(inventory, f, ensure_ascii=False, indent=2)
        
    mb = inventory['total_size_bytes'] / (1024*1024)
    print(f"\nInventory Complete!")
    print(f"Total Categories: {len(inventory['categories'])}")
    print(f"Total Books: {inventory['total_books']}")
    print(f"Total PDF Files: {inventory['total_files']}")
    print(f"Total Size: {mb:.2f} MB")
    
except Exception as e:
    print(f"Critical Error: {e}")

