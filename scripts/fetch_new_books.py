"""Download new books (chosen archive.org items) into the library: parallel downloads, ZIP extraction,
%PDF check on every file, upload with ≤2 FTP connections, every file logged (action 'add', plan 026-new-books).
Edit BOOKS: (section, folder name, short title, archive.org id, label for single-file items or None)."""
import csv, os, re, subprocess, sys, threading, time, urllib.parse, urllib.request, zipfile, xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J = lambda p: os.path.join(ROOT, p)
PLAN = '026-new-books'
DIW, ADAB, TAR = 'الدواوين الشعرية', 'الأدب والبلاغة ونقد الشعر', 'التراجم والطبقات والأعلام'
BOOKS = [
 (DIW, 'شرح القصائد التسع المشهورات - أبو جعفر النحاس', 'شرح القصائد التسع المشهورات', '0539_20191225', None),
 (DIW, 'منتهى الطلب من أشعار العرب - ابن ميمون', 'منتهى الطلب من أشعار العرب', 'bahajarrar_yahoo_201506', None),
 (DIW, 'مختارات شعراء العرب (حماسة ابن الشجري) - ابن الشجري', 'مختارات شعراء العرب', 'ar102arab04', None),
 (DIW, 'الحماسة - البحتري (ت كمال مصطفى)', 'الحماسة - البحتري', 'hm2201', None),
 (DIW, 'الحماسة الشجرية - ابن الشجري', 'الحماسة الشجرية', '20191217_20191217_1707', None),
 (DIW, 'الأشباه والنظائر من أشعار المتقدمين والجاهلية والمخضرمين (حماسة الخالديين) - الخالديان', 'الأشباه والنظائر (حماسة الخالديين)', '0081_20191221', None),
 (DIW, 'مختارات البارودي - محمود سامي البارودي', 'مختارات البارودي', 'barodi00', None),
 (TAR, 'معجم الشعراء - المرزباني (ت عبد الستار فراج)', 'معجم الشعراء', 'animetake00_gmail_201901', None),
 (TAR, 'روضة الآس العاطرة الأنفاس في ذكر من لقيته من أعلام الحضرتين مراكش وفاس - المقري', 'روضة الآس العاطرة الأنفاس', 'ar101dzair22', None),
 (ADAB, 'تتمة اليتيمة - الثعالبي', 'تتمة اليتيمة', 'AAlexandrina-115117', None),
 (ADAB, 'دمية القصر وعصرة أهل العصر - الباخرزي (دار الجيل)', 'دمية القصر وعصرة أهل العصر', '20230321_20230321_1121', None),
 (ADAB, 'خريدة القصر وجريدة العصر - العماد الأصفهاني', 'خريدة القصر', '2-1955_202103', 'قسم شعراء العراق'),
 (ADAB, 'خريدة القصر وجريدة العصر - العماد الأصفهاني', 'خريدة القصر', 'ar103anda82', 'قسم شعراء المغرب'),
 (ADAB, 'قلائد العقيان ومحاسن الأعيان - الفتح بن خاقان', 'قلائد العقيان ومحاسن الأعيان', 'ar103anda83', None),
 (ADAB, 'ريحانة الألبا وزهرة الحياة الدنيا - الشهاب الخفاجي', 'ريحانة الألبا وزهرة الحياة الدنيا', '0775pdf1500', None),
 (ADAB, 'سلافة العصر في محاسن الشعراء بكل مصر - ابن معصوم', 'سلافة العصر في محاسن الشعراء بكل مصر', 'AAlexandrina-166982', None),
 (ADAB, 'نفحة الريحانة ورشحة طلاء الحانة - المحبي', 'نفحة الريحانة', 'nafhat.arryhanah', None),
 (ADAB, 'زاد المسافر وغرة محيا الأدب السافر - صفوان بن إدريس', 'زاد المسافر وغرة محيا الأدب السافر', 'Zad.Al-musafir', None),
 (ADAB, 'مجاني الأدب في حدائق العرب - لويس شيخو', 'مجاني الأدب', '6_20230327', None),
 (ADAB, 'شعراء النصرانية - لويس شيخو', 'شعراء النصرانية', 'BBib-Alex-03084', 'قبل الإسلام'),
 (ADAB, 'شعراء النصرانية - لويس شيخو', 'شعراء النصرانية', 'AAlexandrina-119623', 'بعد الإسلام'),
 (ADAB, 'مختار الأغاني في الأخبار والتهاني - ابن منظور', 'مختار الأغاني', 'hm2971', None),
]
DL = J('downloads/new'); os.makedirs(DL, exist_ok=True)
done = {r[3] for r in csv.reader(open(J('data/changes/changes.tsv')), delimiter='\t') if r and r[1] == 'add' and r[5] == PLAN}
lock = threading.Lock(); stats = {'ok': 0, 'bad': 0}
log = csv.writer(open(J('data/changes/changes.tsv'), 'a', newline=''), delimiter='\t')

def files_of(i):
    x = urllib.request.urlopen(urllib.request.Request(f'https://archive.org/download/{i}/{i}_files.xml', headers={'User-Agent': 'personal-library/1.0'}), timeout=90).read()
    return [(f.get('name'), int(f.findtext('size') or 0)) for f in ET.fromstring(x).findall('file') if f.get('source') == 'original']

def fetch(url, local, size):
    if not (os.path.exists(local) and os.path.getsize(local) == size):
        subprocess.run(['curl', '-sL', '--fail', '--retry', '3', '--max-time', '3600', '-A', 'personal-library/1.0', '-o', local, url])
    return os.path.exists(local) and (not size or os.path.getsize(local) == size)

def vol_no(name, k):
    m = re.search(r'(?:ج|جزء|الجزء|n\.|vol)\s*\.?\s*0*(\d{1,2})(?!\d)', name, re.I) or re.search(r'(?<!\d)0*(\d{1,2})(?=\D*\.pdf$)', name)
    return int(m.group(1)) if m else k

def upload(local, target, url):
    if target in done: return
    r = subprocess.run(['rclone', 'copyto', local, f'phone:{target}', '--inplace', '--ftp-concurrency', '1', '-q'], capture_output=True, text=True)
    with lock:
        if r.returncode: print('UPLOAD FAIL', target, r.stderr[-200:], flush=True); stats['bad'] += 1; return
        log.writerow([time.strftime('%F %T'), 'add', '', target, f'new book from archive.org: {url}', PLAN]); stats['ok'] += 1
        print('added', target.split('/', 2)[2][:110], flush=True)

uploader = ThreadPoolExecutor(2)
def book(b):
    sec, folder, short, ident, label = b
    try: fs = files_of(ident)
    except Exception as e:
        with lock: print('LIST FAIL', ident, e, flush=True); stats['bad'] += 1
        return []
    pdfs = sorted([(n, s) for n, s in fs if n.lower().endswith('.pdf') and not n.lower().endswith('_text.pdf')])
    zips = [(n, s) for n, s in fs if n.lower().endswith('.zip')]
    got = []                                            # (local pdf path, original name)
    for n, s in pdfs:
        local = os.path.join(DL, f'{ident}__{re.sub(r"[^A-Za-z0-9._-]", "_", n)}')
        if fetch(f'https://archive.org/download/{urllib.parse.quote(ident)}/{urllib.parse.quote(n)}', local, s): got.append((local, n))
    if not pdfs:
        for n, s in zips:
            local = os.path.join(DL, f'{ident}__archive.zip')
            if not fetch(f'https://archive.org/download/{urllib.parse.quote(ident)}/{urllib.parse.quote(n)}', local, s): continue
            with zipfile.ZipFile(local) as z:
                for m in z.namelist():
                    if m.lower().endswith('.pdf'):
                        out = os.path.join(DL, f'{ident}__z__{re.sub(r"[^A-Za-z0-9._-]", "_", os.path.basename(m))}')
                        with open(out, 'wb') as w: w.write(z.read(m))
                        got.append((out, os.path.basename(m)))
    got = [(p, n) for p, n in got if open(p, 'rb').read(5) == b'%PDF-']
    if not got:
        with lock: print('NO PDF', ident, flush=True); stats['bad'] += 1
        return []
    futs = []
    url = f'https://archive.org/details/{ident}'
    if len(got) == 1:
        name = short + (f' ({label})' if label else '') + '.pdf'
        futs.append(uploader.submit(upload, got[0][0], f'Books/{sec}/{folder}/{name}', url))
    else:
        width = 2
        ordered = sorted(got, key=lambda x: x[1])
        nums = [vol_no(n, k) for k, (p, n) in enumerate(ordered, 1)]
        if len(set(nums)) < len(nums): nums = list(range(1, len(ordered) + 1))   # never two files with one name
        for v, (p, n) in zip(nums, ordered):
            name = f'{v:0{width}d} - {short}' + (f' ({label})' if label else '') + '.pdf'
            futs.append(uploader.submit(upload, p, f'Books/{sec}/{folder}/{name}', url))
    return futs

with ThreadPoolExecutor(5) as ex:
    allf = [f for fs in ex.map(book, BOOKS) for f in fs]
for f in allf: f.result()
uploader.shutdown(wait=True)
print('uploaded:', stats['ok'], '| problems:', stats['bad'], flush=True)
