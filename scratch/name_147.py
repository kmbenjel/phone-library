"""One-off (2026-10-06): names for the files still called «NN_<id>.pdf» (raw archive.org names), from the Waqfeya record
label of the very file (provenance by exact size) checked against the PDF's embedded title. → plans/147-raw-file-names.tsv"""
import csv, json, re, urllib.parse
prov={r['path']:r for r in csv.DictReader(open('data/phone/provenance.tsv'),delimiter='\t')}
wq={}
for fn in ('data/waqfeya/details.jsonl','data/waqfeya/details2.jsonl'):
    for l in open(fn): d=json.loads(l); wq[d['_id']]={**wq.get(d['_id'],{}),**d}
idx=[p for p,s in csv.reader(open('data/phone/index-now.tsv'),delimiter='\t')]
def lab(p):
    r=prov.get(p,{}); w=wq.get(r.get('waqfeya_id'),{})
    return next((x.get('title','').strip() for x in w.get('links',[]) if urllib.parse.unquote(x.get('url','')).endswith('/'+r.get('orig_name',''))), '')
def clean(s):
    s=re.sub(r'^(تحميل)\s*','',s); s=re.sub(r'(?<=\d)(?=[ء-ي])',' ',s); s=s.replace(':',' -').replace('*','-')
    s=re.sub(r'[\\/?"<>|]','',s); return re.sub(r'\s+',' ',s).strip(' -')
def fit(prefix, label, suffix='.pdf'):
    while label and len(f'{prefix} ({label}){suffix}'.encode())>200: label=label.rsplit(' ',1)[0].rstrip(' -،')
    return f'{prefix} ({label}){suffix}' if label else f'{prefix}{suffix}'
ORDW={'الأول':1,'الثاني':2,'الثالث':3,'الرابع':4,'الخامس':5,'السادس':6,'السابع':7,'الثامن':8,'التاسع':9,'العاشر':10,'الحادي عشر':11,'الثاني عشر':12,'الثالث عشر':13,'الرابع عشر':14,'الخامس عشر':15,'السادس عشر':16,'السابع عشر':17,'الثامن عشر':18,'التاسع عشر':19,'العشرون':20,'الحادي والعشرون':21,'الثاني والعشرون':22,'الثالث والعشرون':23,'الرابع والعشرون':24}
plan=[]; RAW=re.compile(r'^(\d{2})(?:-(\d))?_\d+([a-z]?)\.pdf$')
for p in idx:
    parts=p.split('/'); f=parts[-1]; m=RAW.match(f)
    if not m or len(parts)<3: continue
    folder='/'.join(parts[:-1]); v,k,suf=int(m.group(1)),m.group(2),m.group(3); L=clean(lab(p)); F=parts[1]
    if F.startswith('مؤلفات الشيخ الإمام محمد بن عبد الوهاب'): continue
    if F.startswith('فتح الباري'):
        if v==0: n='00 - فتح الباري (الواجهة).pdf'
        elif suf=='p': n='01 - فتح الباري (مقدمة التحقيق).pdf'
        elif v==1: n='01 - فتح الباري (هدى الساري مقدمة فتح الباري - الجزء 1).pdf'
        else:
            jm=re.match(r'الجزء (.+?) - (.*)$',L); j=ORDW[jm.group(1)]; assert j==v-2,(f,L)
            n=fit(f'{v:02d} - فتح الباري', f'الجزء {j} - {jm.group(2)}')
    elif F.startswith('نصب الراية'):
        n='00 - نصب الراية (الواجهة).pdf' if v==0 else ('01 - نصب الراية (التقديم).pdf' if suf=='p' else fit(f'{v:02d} - نصب الراية', re.sub(r'^المجلد \S+ - ','',L)))
    elif F.startswith('العبر في خبر'):
        if v==0: n='00 - العبر (الواجهة).pdf'
        elif suf=='p': n='01 - العبر (مقدمة التحقيق).pdf'
        elif suf=='i': n='05 - العبر (الفهارس).pdf'
        elif v==4: n='04 - العبر (ذيول العبر للذهبي والحسيني - 701 - 764).pdf'
        else: n=fit(f'{v:02d} - العبر', re.sub(r'^الجزء \S+ - ','',L))
    elif F.startswith('المنهل الصافي'):
        emb={5:'852 جلال - 1072 سعيد',8:'1533 عجلان - 1815 فيروزشاه',10:'2103 محمد بن جابر - 2329 محمد بن محمد بن عبد البر',12:'2587 ناصر - 2828 الكنى',13:'الكشافات التحليلية'}
        n=fit(f'{v:02d} - المنهل الصافي والمستوفي بعد الوافي', emb[v])
    elif F.startswith('سلم الوصول'):
        if v==0: n='00 - سلم الوصول (الواجهة).pdf'
        elif suf=='e': n='01 - سلم الوصول (Foreword).pdf'
        elif suf=='p': n='01 - سلم الوصول (مقدمة التحقيق).pdf'
        else: n=fit(f'{v:02d} - سلم الوصول', re.sub(r'^المجلد \S+ - ','',L))
    elif F.startswith('قادة فتح الأندلس'): n='00 - قادة فتح الأندلس (الواجهة).pdf'
    elif F.startswith('مجموعة فتاوى ابن تيمية'): continue   # numbered below with the «NN_id-k» files of the same set
    elif F.startswith('المحرر، ومعه'): n='03 - المحرر - ابن تيمية (الأطعمة - الإقرار).pdf'      # like its siblings 01, 02
    else: print('??',p); continue
    plan.append((p,f'{folder}/{n}'))
ma=[p for p in idx if p.split('/')[1].startswith('مؤلفات الشيخ الإمام محمد بن عبد الوهاب') and p.count('/')==2]
def key(p):
    m=re.match(r'^(\d{2})(?:-(\d))?_',p.split('/')[-1]); return (int(m.group(1)), int(m.group(2) or 0))
ma.sort(key=key)
for i,p in enumerate(ma):
    v,k=key(p); L=clean(lab(p))
    if v==0: n='00 - مؤلفات الإمام محمد بن عبد الوهاب (الواجهة).pdf'
    else:
        L2=re.sub(r'^المجلد \S+( عشر)? - ','',L)
        L2=re.sub(r'^(العقيدة والآداب الإسلامية|الفقه 2|مختصر السيرة والفتاوى|التفسير|ملحق المصنفات) - ','',L2)
        L2=re.sub(r'^\d+ ?','',L2)
        n=fit(f'{i:02d} - مؤلفات الإمام محمد بن عبد الوهاب', f'المجلد {v}' + (f' - {L2}' if L2 else ''))
    plan.append((p,'/'.join(p.split('/')[:-1])+'/'+n))
ft=[p for p in idx if p.split('/')[1].startswith('مجموعة فتاوى ابن تيمية - مجموع الفتاوى - ط. العلمية') and p.count('/')==2]
def fkey(p):
    m=re.match(r'^(\d{2})_\d+(?:-(\d))?\.pdf$',p.split('/')[-1]); return (int(m.group(1)), int(m.group(2) or 0))
ft.sort(key=fkey)
for i,p in enumerate(ft):
    v,k=fkey(p); L=clean(lab(p))
    L2=re.sub(r'^المجلد \S+ ?','',L); L2=re.sub(r'^القسم (الأول|الثاني|الثالث) ?-? ?','',L2)
    if v==0: n='00 - مجموعة فتاوى ابن تيمية (الواجهة).pdf'
    else: n=fit(f'{i:02d} - مجموعة فتاوى ابن تيمية', f'المجلد {v}' + (f' - القسم {k}' if k else '') + (f' - {L2}' if L2 else ''))
    plan.append((p,'/'.join(p.split('/')[:-1])+'/'+n))
dst=[d for s,d in plan]; assert len(dst)==len(set(dst))
with open('plans/147-raw-file-names.tsv','w') as w:
    for s,d in plan: w.write(f"Books/{s}\tBooks/{d}\tname from the Waqfeya record label of the very file and the PDF's embedded title (§4)\n")
print(len(plan))
for s,d in plan: print(d.split('/')[-1][:120])
