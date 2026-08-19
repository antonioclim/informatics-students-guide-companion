#!/usr/bin/env python3
from pathlib import Path
from lxml import etree
import csv, hashlib, sys
root = Path(__file__).resolve().parents[1]
rows = list(csv.DictReader((root/'03_METADATA'/'FIGURE_MANIFEST.csv').open(encoding='utf-8-sig')))
errors=[]
for row in rows:
    svg=root/'01_SVG_AUTHORITATIVE'/(row['file_stem']+'.svg')
    png=root/'02_PNG_TECHNICAL_FALLBACK'/(row['file_stem']+'.png')
    for p, key in [(svg,'svg_sha256'),(png,'png_sha256')]:
        if not p.exists(): errors.append(f'missing {p}')
        elif hashlib.sha256(p.read_bytes()).hexdigest()!=row[key]: errors.append(f'hash mismatch {p}')
    try:
        t=etree.fromstring(svg.read_bytes(), parser=etree.XMLParser(resolve_entities=False,no_network=True))
        tags={etree.QName(n).localname for n in t.iter() if isinstance(n.tag,str)}
        if tags & {'script','foreignObject','image'}: errors.append(f'unsafe or raster tag in {svg}')
    except Exception as e: errors.append(f'XML error {svg}: {e}')
if len(rows)!=18: errors.append(f'expected 18 figures, found {len(rows)}')
if errors:
    print('\n'.join(errors)); sys.exit(1)
print('PASS: 18 figures, hashes and SVG safety checks')
