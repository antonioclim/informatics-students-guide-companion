#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, json, re, subprocess, sys, zipfile
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
errors=[]

SKIP_DIRS={'.git','__pycache__','_qa','_build'}

def is_repo_file(path: Path) -> bool:
    try:
        rel=path.relative_to(ROOT)
    except ValueError:
        return False
    return path.is_file() and not any(part in SKIP_DIRS for part in rel.parts)

def repo_files():
    return (path for path in ROOT.rglob('*') if is_repo_file(path))

def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
    return h.hexdigest()

def need(rel):
    p=ROOT/rel
    if not p.exists(): errors.append(f'missing {rel}')
    return p

for rel in [
    'README.md','VERSION.txt','CITATION.cff','PUBLIC_RELEASE_HOLD.md','RIGHTS_AND_RELEASE_STATUS.md',
    'PRIVACY_AND_SECURITY.md','REPOSITORY_CONTENT_POLICY.md','ZENODO_DEPOSIT_HOLD.md',
    'companion/00_READ_FIRST','companion/01_WORKBOOK','companion/02_TEMPLATES_MINIMUM',
    'companion/03_TEMPLATES_FULL','companion/04_ROUTE_KITS','companion/05_REGISTRIES','companion/06_MAINTENANCE',
    'figures/01_SVG_AUTHORITATIVE','figures/02_PNG_TECHNICAL_FALLBACK','figures/03_METADATA',
    'figures/06_ODG_NATIVE_EDITABLE_INDIVIDUAL','figures/07_ODG_NATIVE_EDITABLE_CONSOLIDATED',
    'figures/08_PPTX_NATIVE_EDITABLE_INDIVIDUAL','figures/09_PPTX_NATIVE_EDITABLE_CONSOLIDATED',
    'figures/10_NATIVE_EDITABILITY_QA','figures/NATIVE_FORMATS_SUPERSESSION_NOTICE.md',
    'figures/05_SCRIPTS/validate_native_editability.py',
    'manifests/REPOSITORY_MANIFEST.csv','manifests/ASSET_RIGHTS_PRIVACY_REGISTER.csv',
    'manifests/EXCLUSIONS_REGISTER.csv','SHA256SUMS.txt']:
    need(rel)

if (ROOT/'LICENSE_AND_RIGHTS.md').exists(): errors.append('superseded root LICENSE_AND_RIGHTS.md still present')
prohibited_names={'LICENSE','LICENSE.txt','LICENSE.md'}
for p in repo_files():
    if p.name in prohibited_names: errors.append(f'public licence file prohibited during hold: {p.relative_to(ROOT)}')
    lower=p.name.lower()
    if ('authoritative_master' in lower or lower.endswith('.pdf') and 'report' not in lower):
        errors.append(f'possible prohibited manuscript/proof payload: {p.relative_to(ROOT)}')
for prohibited in ['companion/07_ARCHIVED_RESOURCES','companion/08_PROVENANCE']:
    if (ROOT/prohibited).exists(): errors.append(f'excluded directory present: {prohibited}')

cff=(ROOT/'CITATION.cff').read_text(encoding='utf-8')
for required in ['Antonio','Clim','Martino','Aldrigo','1.1.1-rc.3','unpublished candidate','Native Editable Figures']:
    if required.lower() not in cff.lower(): errors.append(f'CITATION.cff missing {required}')
for forbidden in ['date-released:', 'doi:', 'license:', 'repository-code:']:
    if forbidden in cff.lower(): errors.append(f'CITATION.cff prematurely contains {forbidden}')

version=(ROOT/'VERSION.txt').read_text(encoding='utf-8')
if not version.startswith('1.1.1-rc.3\n'): errors.append('VERSION.txt is not 1.1.1-rc.3')

CANONICAL_TITLE='The Informatics Student’s Guide to Research Projects, Theses and Dissertations'
DUPLICATED_TITLE=CANONICAL_TITLE+' to Research Projects, Theses and Dissertations'
for path in repo_files():
    if path.name=='SHA256SUMS.txt': continue
    if path.suffix.lower() in {'.md','.txt','.csv','.json','.cff','.yml','.yaml','.py','.sh'} or path.name in {'.gitignore','.gitattributes'}:
        content=path.read_text(encoding='utf-8',errors='replace')
        if DUPLICATED_TITLE in content: errors.append(f'duplicated canonical title in {path.relative_to(ROOT)}')
        relpath=path.relative_to(ROOT).as_posix()
        if '1.1.1-rc.2' in content and relpath not in {'scripts/validate_repository.py','companion/06_MAINTENANCE/DEPRECATION_AND_SUPERSESSION_LOG.csv'}: errors.append(f'superseded rc.2 reference in active file {relpath}')
if '33 full CSV records' not in (ROOT/'companion/00_READ_FIRST/README.md').read_text(encoding='utf-8'):
    errors.append('companion README does not declare 33 full CSV records')

svgs=sorted((ROOT/'figures/01_SVG_AUTHORITATIVE').glob('*.svg'))
pngs=sorted((ROOT/'figures/02_PNG_TECHNICAL_FALLBACK').glob('*.png'))
if len(svgs)!=18: errors.append(f'expected 18 SVG files, found {len(svgs)}')
if len(pngs)!=18: errors.append(f'expected 18 PNG files, found {len(pngs)}')
for svg in svgs:
    try:
        tree=ET.parse(svg); tags={el.tag.rsplit('}',1)[-1] for el in tree.iter()}; bad=tags & {'script','foreignObject','image'}
        if bad: errors.append(f'unsafe/raster tags {bad} in {svg.name}')
    except Exception as e: errors.append(f'bad SVG {svg.name}: {e}')

mins=list((ROOT/'companion/02_TEMPLATES_MINIMUM').glob('*.csv'))
fulls=list((ROOT/'companion/03_TEMPLATES_FULL').glob('*.csv'))
routes=[p for p in (ROOT/'companion/04_ROUTE_KITS').iterdir() if p.is_dir()]
if len(mins)!=12: errors.append(f'expected 12 minimum templates, found {len(mins)}')
if len(fulls)!=33: errors.append(f'expected 33 full templates, found {len(fulls)}')
if len(routes)!=4: errors.append(f'expected 4 route kits, found {len(routes)}')

# Native package validation.
proc=subprocess.run([sys.executable,str(ROOT/'figures/05_SCRIPTS/validate_native_editability.py')],capture_output=True,text=True)
if proc.returncode: errors.append('native editability validation failed: '+(proc.stdout+proc.stderr).strip())

# Verify SHA256SUMS.
sums=ROOT/'SHA256SUMS.txt'
if sums.exists():
    declared=set()
    for line in sums.read_text(encoding='utf-8').splitlines():
        if not line.strip(): continue
        expected,rel=line.split('  ',1); declared.add(rel); p=ROOT/rel
        if not p.exists(): errors.append(f'SHA256SUMS missing file {rel}')
        elif sha(p)!=expected: errors.append(f'SHA256 mismatch {rel}')
    actual={p.relative_to(ROOT).as_posix() for p in repo_files() if p.name!='SHA256SUMS.txt'}
    if declared!=actual:
        for rel in sorted(actual-declared): errors.append(f'SHA256SUMS undeclared file {rel}')
        for rel in sorted(declared-actual): errors.append(f'SHA256SUMS stale file {rel}')

# Repository manifest coverage, excluding self-generated manifest files and SHA list.
manifest_excluded={'manifests/REPOSITORY_MANIFEST.csv','manifests/REPOSITORY_MANIFEST.json','SHA256SUMS.txt'}
actual_manifest={p.relative_to(ROOT).as_posix() for p in repo_files() if p.relative_to(ROOT).as_posix() not in manifest_excluded}
try:
    with (ROOT/'manifests/REPOSITORY_MANIFEST.csv').open(encoding='utf-8-sig',newline='') as f: mrows=list(csv.DictReader(f))
    declared={r['path'] for r in mrows}
    if declared!=actual_manifest: errors.append(f'repository manifest coverage mismatch: declared={len(declared)} actual={len(actual_manifest)}')
    for r in mrows:
        p=ROOT/r['path']
        if p.exists() and (int(r['bytes'])!=p.stat().st_size or r['sha256']!=sha(p)): errors.append(f'repository manifest mismatch {r["path"]}')
except Exception as e: errors.append(f'repository manifest parse error: {e}')

# CSV parsability and no absolute private paths.
for p in (path for path in repo_files() if path.suffix.lower()=='.csv'):
    try:
        with p.open(encoding='utf-8-sig',newline='') as f: list(csv.reader(f))
    except Exception as e: errors.append(f'CSV parse error {p.relative_to(ROOT)}: {e}')
for p in repo_files():
    if p.suffix.lower() in {'.md','.txt','.csv','.json','.cff','.yml','.yaml','.py','.sh'}:
        t=p.read_text(encoding='utf-8',errors='replace')
        if re.search(r'/(?:mnt/data|home|Users)/',t): errors.append(f'absolute private path in {p.relative_to(ROOT)}')

if errors:
    print('\n'.join('ERROR: '+x for x in errors)); sys.exit(1)
print('PASS: rc.3 structure, hashes, 18 SVG/PNG pairs, 18 native ODG/PPTX pairs, consolidated native files, companion counts, rights hold and CFF hold')
