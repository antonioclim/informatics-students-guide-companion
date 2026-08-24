#!/usr/bin/env python3
from pathlib import Path
import argparse, hashlib, json, re, sys, zipfile
ROOT=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser(); ap.add_argument('--fail-on',choices=['low','medium','high'],default='medium'); a=ap.parse_args()
levels={'low':1,'medium':2,'high':3}; findings=[]
patterns=[
 ('high','private_key',re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----')),
 ('high','github_token',re.compile(r'\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{30,}\b')),
 ('high','credential_assignment',re.compile(r'(?i)\b(?:password|passwd|api[_-]?key|secret|token)\s*[:=]\s*["\'][^"\']{8,}["\']')),
 ('medium','romanian_phone',re.compile(r'(?<!\d)(?:\+40|0040|0)7\d{8}(?!\d)')),
 ('medium','email_address',re.compile(r'(?i)(?<![\w.+-])[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}(?![\w.-])')),
 ('medium','windows_private_path',re.compile(r'(?i)\b[A-Z]:\\(?:Users|Documents and Settings)\\[^\\\s]+')),
 ('medium','unix_private_path',re.compile(r'/(?:home|Users|mnt/data)/[^\s"\']+')),
]
allowed_domains={'example.com','example.org','invalid.example'}
text_ext={'.md','.txt','.csv','.json','.yaml','.yml','.cff','.html','.xml','.svg','.tsv','.py','.sh','.rels'}
archive_ext={'.docx','.pptx','.odg','.xlsx'}
def scan(name,text):
 for lineno,line in enumerate(text.splitlines(),1):
  for sev,label,rx in patterns:
   for m in rx.finditer(line):
    value=m.group(0)
    if label=='email_address' and value.rsplit('@',1)[-1].lower() in allowed_domains: continue
    findings.append({'severity':sev,'type':label,'path':name,'line':lineno,'value_sha256':hashlib.sha256(value.encode()).hexdigest()})
for p in sorted(ROOT.rglob('*')):
 if not p.is_file() or '__pycache__' in p.parts: continue
 rel=p.relative_to(ROOT).as_posix()
 if p.suffix.lower() in text_ext or p.name in {'.gitignore','.gitattributes','VERSION','LICENSE-CODE'}:
  try: scan(rel,p.read_text(encoding='utf-8',errors='replace'))
  except Exception: pass
 elif p.suffix.lower() in archive_ext:
  try:
   with zipfile.ZipFile(p) as z:
    for n in z.namelist():
     if Path(n).suffix.lower() in text_ext:
      scan(rel+'::'+n,z.read(n).decode('utf-8','replace'))
  except Exception as e:
   findings.append({'severity':'high','type':'invalid_archive','path':rel,'line':0,'value_sha256':hashlib.sha256(str(e).encode()).hexdigest()})
threshold=levels[a.fail_on]; failing=[x for x in findings if levels[x['severity']]>=threshold]
print(json.dumps({'status':'FAIL' if failing else 'PASS','findings':findings,'failing_count':len(failing)},ensure_ascii=False,indent=2)); sys.exit(1 if failing else 0)
