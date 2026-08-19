#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, json, re, sys, zipfile
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
errors=[]

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
    'README.md','VERSION.txt','CITATION.cff','PUBLIC_RELEASE_HOLD.md','LICENSE_AND_RIGHTS.md',
    'PRIVACY_AND_SECURITY.md','REPOSITORY_CONTENT_POLICY.md','ZENODO_DEPOSIT_HOLD.md',
    'companion/00_READ_FIRST','companion/01_WORKBOOK','companion/02_TEMPLATES_MINIMUM',
    'companion/03_TEMPLATES_FULL','companion/04_ROUTE_KITS','companion/05_REGISTRIES','companion/06_MAINTENANCE',
    'figures/01_SVG_AUTHORITATIVE','figures/02_PNG_TECHNICAL_FALLBACK','figures/03_METADATA',
    'manifests/REPOSITORY_MANIFEST.csv','manifests/ASSET_RIGHTS_PRIVACY_REGISTER.csv',
    'manifests/EXCLUSIONS_REGISTER.csv','SHA256SUMS.txt']:
    need(rel)

prohibited_names={'LICENSE','LICENSE.txt','LICENSE.md'}
for p in ROOT.rglob('*'):
    if p.is_file() and p.name in prohibited_names: errors.append(f'public licence file prohibited during hold: {p.relative_to(ROOT)}')
    lower=p.name.lower()
    if p.is_file() and ('authoritative_master' in lower or lower.endswith('.pdf') and 'report' not in lower):
        errors.append(f'possible prohibited manuscript/proof payload: {p.relative_to(ROOT)}')
for prohibited in ['companion/07_ARCHIVED_RESOURCES','companion/08_PROVENANCE']:
    if (ROOT/prohibited).exists(): errors.append(f'excluded directory present: {prohibited}')

cff=(ROOT/'CITATION.cff').read_text(encoding='utf-8')
for required in ['Antonio','Clim','Martino','Aldrigo','1.1.1-rc.2','unpublished candidate']:
    if required.lower() not in cff.lower(): errors.append(f'CITATION.cff missing {required}')

# Canonical-title and active-document consistency.
CANONICAL_TITLE = 'The Informatics Student’s Guide to Research Projects, Theses and Dissertations'
DUPLICATED_TITLE = CANONICAL_TITLE + ' to Research Projects, Theses and Dissertations'
for path in ROOT.rglob('*'):
    if not path.is_file() or path.name == 'SHA256SUMS.txt':
        continue
    if path.suffix.lower() in {'.md','.txt','.csv','.json','.cff','.yml','.yaml','.py','.sh'} or path.name in {'.gitignore','.gitattributes'}:
        content=path.read_text(encoding='utf-8',errors='replace')
        if DUPLICATED_TITLE in content:
            errors.append(f'duplicated canonical title in {path.relative_to(ROOT)}')
if '33 full CSV records' not in (ROOT/'companion/00_READ_FIRST/README.md').read_text(encoding='utf-8'):
    errors.append('companion README does not declare 33 full CSV records')
for absent in ['companion/07_ARCHIVED_RESOURCES','companion/08_PROVENANCE']:
    if absent in (ROOT/'companion/00_READ_FIRST/README.md').read_text(encoding='utf-8'):
        errors.append(f'companion README incorrectly lists excluded directory {absent}')

for forbidden in ['date-released:', 'doi:', 'license:', 'repository-code:']:
    if forbidden in cff.lower(): errors.append(f'CITATION.cff prematurely contains {forbidden}')

svgs=sorted((ROOT/'figures/01_SVG_AUTHORITATIVE').glob('*.svg'))
pngs=sorted((ROOT/'figures/02_PNG_TECHNICAL_FALLBACK').glob('*.png'))
if len(svgs)!=18: errors.append(f'expected 18 SVG files, found {len(svgs)}')
if len(pngs)!=18: errors.append(f'expected 18 PNG files, found {len(pngs)}')
for svg in svgs:
    try:
        tree=ET.parse(svg)
        tags={el.tag.rsplit('}',1)[-1] for el in tree.iter()}
        bad=tags & {'script','foreignObject','image'}
        if bad: errors.append(f'unsafe/raster tags {bad} in {svg.name}')
    except Exception as e: errors.append(f'bad SVG {svg.name}: {e}')

mins=list((ROOT/'companion/02_TEMPLATES_MINIMUM').glob('*.csv'))
fulls=list((ROOT/'companion/03_TEMPLATES_FULL').glob('*.csv'))
routes=[p for p in (ROOT/'companion/04_ROUTE_KITS').iterdir() if p.is_dir()]
if len(mins)!=12: errors.append(f'expected 12 minimum templates, found {len(mins)}')
if len(fulls)!=33: errors.append(f'expected 33 full templates, found {len(fulls)}')
if len(routes)!=4: errors.append(f'expected 4 route kits, found {len(routes)}')

# Verify SHA256SUMS.
sums=ROOT/'SHA256SUMS.txt'
if sums.exists():
    for line in sums.read_text(encoding='utf-8').splitlines():
        if not line.strip(): continue
        expected, rel=line.split('  ',1)
        p=ROOT/rel
        if not p.exists(): errors.append(f'SHA256SUMS missing file {rel}')
        elif sha(p)!=expected: errors.append(f'SHA256 mismatch {rel}')

# CSV parsability.
for p in ROOT.rglob('*.csv'):
    try:
        with p.open(encoding='utf-8-sig', newline='') as f: list(csv.reader(f))
    except Exception as e: errors.append(f'CSV parse error {p.relative_to(ROOT)}: {e}')

if errors:
    print('\n'.join('ERROR: '+x for x in errors)); sys.exit(1)
print(f'PASS: repository structure, 18 figure pairs, companion counts, CFF hold and hashes')
