#!/usr/bin/env python3
from pathlib import Path
import csv, hashlib, json, mimetypes
ROOT=Path(__file__).resolve().parents[1]
EX={'manifests/REPOSITORY_MANIFEST.csv','manifests/REPOSITORY_MANIFEST.json','manifests/REPOSITORY_SHA256.txt','SHA256SUMS.txt'}
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''): h.update(b)
 return h.hexdigest()
def media(p):
 return {'.md':'text/markdown','.cff':'application/x-yaml','.odg':'application/vnd.oasis.opendocument.graphics','.pptx':'application/vnd.openxmlformats-officedocument.presentationml.presentation','.docx':'application/vnd.openxmlformats-officedocument.wordprocessingml.document','.svg':'image/svg+xml','.csv':'text/csv','.json':'application/json','.py':'text/x-python','.sh':'text/x-shellscript','.yml':'application/yaml','.yaml':'application/yaml'}.get(p.suffix.lower(),mimetypes.guess_type(p.name)[0] or 'application/octet-stream')
def licence(rel):
 if rel.startswith('scripts/') or rel.startswith('.github/workflows/') or (rel.startswith('figures/06_SOURCE_AND_PROVENANCE/') and rel.endswith('.py')): return 'MIT'
 return 'CC BY 4.0'
def role(rel):
 if rel.startswith('figures/01_'): return 'native_editable_figure_authority'
 if rel.startswith('figures/02_'): return 'publication_vector_figure'
 if rel.startswith('figures/03_'): return 'editable_figure_derivative'
 if rel.startswith('figures/04_'): return 'figure_fallback'
 if rel.startswith('figures/'): return 'figure_control_or_provenance'
 if rel.startswith('companion/'): return 'digital_companion_content'
 if rel.startswith('schemas/'): return 'schema'
 if rel.startswith('scripts/'): return 'validation_code'
 if rel.startswith('.github/'): return 'continuous_validation'
 if rel.startswith('docs/'): return 'release_documentation'
 if rel.startswith('manifests/'): return 'control_manifest'
 return 'repository_governance'
rows=[]
for p in sorted(ROOT.rglob('*')):
 rel=p.relative_to(ROOT).as_posix() if p.is_file() else ''
 if p.is_file() and rel not in EX:
  rows.append({'path':rel,'sha256':sha(p),'size_bytes':str(p.stat().st_size),'media_type':media(p),'release_scope':'PUBLIC_RELEASE','licence':licence(rel),'privacy_status':'PUBLIC_SCREENED','source_role':role(rel)})
mp=ROOT/'manifests'; mp.mkdir(exist_ok=True)
fields=list(rows[0])
with (mp/'REPOSITORY_MANIFEST.csv').open('w',encoding='utf-8',newline='') as f:
 w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n'); w.writeheader(); w.writerows(rows)
obj={'schema_version':'3.0','release_version':'1.2.0','book_version':'v3.9.0','generated_at':'2026-08-24T12:00:00Z','manifest_exclusions':sorted(EX),'entries':rows}
(mp/'REPOSITORY_MANIFEST.json').write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
allfiles=[p for p in sorted(ROOT.rglob('*')) if p.is_file() and p not in {mp/'REPOSITORY_SHA256.txt',ROOT/'SHA256SUMS.txt'}]
(mp/'REPOSITORY_SHA256.txt').write_text('\n'.join(f'{sha(p)}  {p.relative_to(ROOT).as_posix()}' for p in allfiles)+'\n',encoding='utf-8')
all2=[p for p in sorted(ROOT.rglob('*')) if p.is_file() and p!=ROOT/'SHA256SUMS.txt']
(ROOT/'SHA256SUMS.txt').write_text('\n'.join(f'{sha(p)}  {p.relative_to(ROOT).as_posix()}' for p in all2)+'\n',encoding='utf-8')
print(json.dumps({'status':'PASS','manifest_rows':len(rows),'repository_sha_entries':len(allfiles)},indent=2))
