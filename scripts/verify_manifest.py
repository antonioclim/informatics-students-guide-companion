#!/usr/bin/env python3
from pathlib import Path
import csv, hashlib, json, sys
ROOT=Path(__file__).resolve().parents[1]; MP=ROOT/'manifests'
EX={'manifests/REPOSITORY_MANIFEST.csv','manifests/REPOSITORY_MANIFEST.json','manifests/REPOSITORY_SHA256.txt','SHA256SUMS.txt'}
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''): h.update(b)
 return h.hexdigest()
errors=[]
def payload_files():
 return [p for p in ROOT.rglob('*') if p.is_file() and '.git' not in p.relative_to(ROOT).parts]
with (MP/'REPOSITORY_MANIFEST.csv').open(encoding='utf-8-sig',newline='') as f: r=csv.DictReader(f); rows=list(r); cols=r.fieldnames
expected=['path','sha256','size_bytes','media_type','release_scope','licence','privacy_status','source_role']
if cols!=expected: errors.append(f'CSV schema mismatch: {cols}')
obj=json.loads((MP/'REPOSITORY_MANIFEST.json').read_text(encoding='utf-8')); jrows=obj.get('entries',[])
if rows!=jrows: errors.append('CSV and JSON entries differ')
physical={p.relative_to(ROOT).as_posix() for p in payload_files()}-EX; listed={r['path'] for r in rows}
if physical!=listed: errors.append(f'manifest coverage mismatch missing={sorted(physical-listed)[:10]} extra={sorted(listed-physical)[:10]}')
for r in rows:
 p=ROOT/r['path']
 if p.is_file() and (str(p.stat().st_size)!=r['size_bytes'] or sha(p)!=r['sha256']): errors.append('manifest mismatch '+r['path'])
reg={}
for line in (MP/'REPOSITORY_SHA256.txt').read_text(encoding='utf-8').splitlines():
 if line.strip(): h,path=line.split('  ',1); reg[path]=h
exp={p.relative_to(ROOT).as_posix() for p in payload_files() if p not in {MP/'REPOSITORY_SHA256.txt',ROOT/'SHA256SUMS.txt'}}
if set(reg)!=exp: errors.append('REPOSITORY_SHA256 coverage mismatch')
for rel,h in reg.items():
 if sha(ROOT/rel)!=h: errors.append('REPOSITORY_SHA256 mismatch '+rel)
reg2={}
for line in (ROOT/'SHA256SUMS.txt').read_text(encoding='utf-8').splitlines():
 if line.strip(): h,path=line.split('  ',1); reg2[path]=h
exp2={p.relative_to(ROOT).as_posix() for p in payload_files() if p!=ROOT/'SHA256SUMS.txt'}
if set(reg2)!=exp2: errors.append('root SHA256 coverage mismatch')
for rel,h in reg2.items():
 if sha(ROOT/rel)!=h: errors.append('root SHA mismatch '+rel)
print(json.dumps({'status':'FAIL' if errors else 'PASS','manifest_rows':len(rows),'errors':errors},indent=2)); sys.exit(1 if errors else 0)
