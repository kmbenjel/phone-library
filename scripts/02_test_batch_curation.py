import json, random, os, ftplib
import pymupdf as fitz  # PyMuPDF
import google.generativeai as genai
from PIL import Image

# Configure Gemini
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel('models/gemini-3.5-flash')

from phone_host import HOST as FTP_HOST
FTP_PORT = 2221
FTP_ROOT = '/Books'

def get_test_sample(catalog_path, sample_size=5):
    with open(catalog_path, 'r', encoding='utf-8') as f:
        catalog = json.load(f)
    
    candidates = []
    for cat_name, cat_data in catalog['categories'].items():
        for book_name, book_data in cat_data['books'].items():
            if book_data['type'] == 'file':
                candidates.append({
                    'category': cat_name,
                    'book_name': book_name,
                    'path': book_data['path'],
                    'size': book_data['total_size']
                })
    
    # Filter for reasonable sizes (< 50MB) for faster testing
    candidates = [c for c in candidates if c['size'] < 50_000_000]
    return random.sample(candidates, min(sample_size, len(candidates)))

def process_book(ftp, book_info):
    remote_path = book_info['path']
    local_path = f"/tmp/{os.path.basename(remote_path)}"
    
    print(f"\n[{book_info['category']}] Processing: {book_info['book_name']}")
    
    # 1. Download File
    print("  Downloading from phone...")
    with open(local_path, 'wb') as f:
        ftp.retrbinary(f"RETR {remote_path}", f.write)
        
    # 2. PyMuPDF Analysis
    print("  Analyzing PDF structure...")
    doc = fitz.open(local_path)
    page_count = len(doc)
    
    # Check text layer
    text_sample = ""
    if page_count > 5:
        text_sample = doc[5].get_text()
    is_searchable = len(text_sample.strip()) > 50
    print(f"  Pages: {page_count}, Searchable (Text Layer): {is_searchable}")
    
    # Render cover images
    print("  Extracting cover images for Vision AI...")
    cover_paths = []
    for p_num in range(min(3, page_count)):
        page = doc[p_num]
        pix = page.get_pixmap(dpi=150)
        img_path = f"/tmp/cover_{p_num}.jpg"
        pix.save(img_path)
        cover_paths.append(img_path)
        
    doc.close()
    
    # 3. Vision AI Extraction
    print("  Asking Gemini Vision to extract metadata...")
    try:
        images = [Image.open(p) for p in cover_paths]
        prompt = """
        أنت محقق تراثي وخبير في مكتبات الـ PDF العربية. 
        اقرأ هذه الصفحات الأولى من الكتاب بدقة واستخرج البيانات التالية حصراً بصيغة JSON:
        {
          "title": "العنوان الفعلي كما هو مكتوب",
          "author": "اسم المؤلف",
          "editor": "اسم المحقق إن وجد",
          "publisher": "دار النشر",
          "edition": "رقم الطبعة أو سنتها",
          "volumes": "عدد الأجزاء المكتوبة على الغلاف إن وجدت"
        }
        إذا لم تجد المعلومة، اكتب "غير مذكور".
        """
        response = model.generate_content([prompt] + images)
        print("  [AI Output]:")
        print(response.text.strip())
    except Exception as e:
        print(f"  AI Error: {e}")
        
    # 4. Cleanup
    for p in cover_paths:
        if os.path.exists(p): os.remove(p)
    if os.path.exists(local_path):
        os.remove(local_path)

if __name__ == "__main__":
    print("Connecting to FTP...")
    ftp = ftplib.FTP()
    ftp.connect(FTP_HOST, FTP_PORT, timeout=10)
    ftp.login()
    
    print("Selecting 5 random books for the test batch...")
    sample_books = get_test_sample('data/phone_master_catalog.json', 5)
    
    for book in sample_books:
        process_book(ftp, book)
        
    ftp.quit()
    print("\nTest batch complete!")
