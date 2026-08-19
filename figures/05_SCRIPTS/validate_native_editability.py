#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import argparse, csv, json, sys, zipfile
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[2]
ODG_NS={'draw':'urn:oasis:names:tc:opendocument:xmlns:drawing:1.0','text':'urn:oasis:names:tc:opendocument:xmlns:text:1.0','office':'urn:oasis:names:tc:opendocument:xmlns:office:1.0'}
P_NS={'p':'http://schemas.openxmlformats.org/presentationml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main'}

def odg_stats(path: Path):
    with zipfile.ZipFile(path) as z:
        names=z.namelist()
        root=ET.fromstring(z.read('content.xml'))
        images=len(root.findall('.//draw:image',ODG_NS))
        frames=len(root.findall('.//draw:frame',ODG_NS))
        texts=len(root.findall('.//draw:text-box',ODG_NS))
        groups=len(root.findall('.//draw:g',ODG_NS))
        pages=len(root.findall('.//draw:page',ODG_NS))
        pictures=sum(1 for n in names if n.startswith('Pictures/') and not n.endswith('/'))
        return {'images':images,'frames':frames,'texts':texts,'groups':groups,'pages':pages,'pictures':pictures}

def pptx_stats(path: Path):
    with zipfile.ZipFile(path) as z:
        names=z.namelist()
        slides=sorted(n for n in names if n.startswith('ppt/slides/slide') and n.endswith('.xml') and '/_rels/' not in n)
        pictures=0; shapes=0; texts=0
        for name in slides:
            root=ET.fromstring(z.read(name))
            pictures += len(root.findall('.//p:pic',P_NS))
            shapes += len(root.findall('.//p:sp',P_NS))
            texts += sum(1 for sp in root.findall('.//p:sp',P_NS) if sp.findall('.//a:t',P_NS))
        media=sum(1 for n in names if n.startswith('ppt/media/') and not n.endswith('/'))
        return {'slides':len(slides),'pictures':pictures,'shapes':shapes,'texts':texts,'media':media}

def validate():
    errors=[]; rows=[]
    svg_dir=ROOT/'figures/01_SVG_AUTHORITATIVE'
    odg_dir=ROOT/'figures/06_ODG_NATIVE_EDITABLE_INDIVIDUAL'
    pptx_dir=ROOT/'figures/08_PPTX_NATIVE_EDITABLE_INDIVIDUAL'
    odgs=sorted(odg_dir.glob('*_NATIVE_EDITABLE.odg'))
    pptxs=sorted(pptx_dir.glob('*_NATIVE_EDITABLE.pptx'))
    if len(odgs)!=18: errors.append(f'expected 18 individual ODG files, found {len(odgs)}')
    if len(pptxs)!=18: errors.append(f'expected 18 individual PPTX files, found {len(pptxs)}')
    for odg in odgs:
        stem=odg.name.replace('_NATIVE_EDITABLE.odg','')
        svg=svg_dir/f'{stem}.svg'; pptx=pptx_dir/f'{stem}_NATIVE_EDITABLE.pptx'
        if not svg.exists(): errors.append(f'missing canonical SVG for {stem}')
        if not pptx.exists(): errors.append(f'missing PPTX for {stem}'); continue
        try: os=odg_stats(odg)
        except Exception as e: errors.append(f'bad ODG {odg.name}: {e}'); continue
        try: ps=pptx_stats(pptx)
        except Exception as e: errors.append(f'bad PPTX {pptx.name}: {e}'); continue
        if os['images'] or os['pictures']: errors.append(f'ODG contains embedded image object: {odg.name}')
        if os['groups']: errors.append(f'ODG contains grouped objects: {odg.name}')
        if os['texts']<1 or os['frames']<1: errors.append(f'ODG lacks native text/frames: {odg.name}')
        if os['pages']!=1: errors.append(f'individual ODG page count {os["pages"]}: {odg.name}')
        if ps['pictures'] or ps['media']: errors.append(f'PPTX contains picture/media objects: {pptx.name}')
        if ps['shapes']<1 or ps['texts']<1: errors.append(f'PPTX lacks native shapes/text: {pptx.name}')
        if ps['slides']!=1: errors.append(f'individual PPTX slide count {ps["slides"]}: {pptx.name}')
        rows.append({'stem':stem,'odg':os,'pptx':ps})
    codg=ROOT/'figures/07_ODG_NATIVE_EDITABLE_CONSOLIDATED/TISG_RPTD_ALL_18_FIGURES_NATIVE_EDITABLE.odg'
    cpptx=ROOT/'figures/09_PPTX_NATIVE_EDITABLE_CONSOLIDATED/TISG_RPTD_ALL_18_FIGURES_NATIVE_EDITABLE.pptx'
    if not codg.exists(): errors.append('missing consolidated ODG')
    else:
        try:
            s=odg_stats(codg)
            if s['pages']!=18 or s['images'] or s['pictures']: errors.append(f'consolidated ODG invalid: {s}')
        except Exception as e: errors.append(f'bad consolidated ODG: {e}')
    if not cpptx.exists(): errors.append('missing consolidated PPTX')
    else:
        try:
            s=pptx_stats(cpptx)
            if s['slides']!=18 or s['pictures'] or s['media']: errors.append(f'consolidated PPTX invalid: {s}')
        except Exception as e: errors.append(f'bad consolidated PPTX: {e}')
    return errors,rows

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--json',default=''); args=ap.parse_args()
    errors,rows=validate()
    if args.json: Path(args.json).write_text(json.dumps({'status':'FAIL' if errors else 'PASS','errors':errors,'figures':rows},indent=2),encoding='utf-8')
    if errors:
        print('\n'.join('ERROR: '+e for e in errors)); return 1
    print('PASS: 18 native ODG, 18 native PPTX and both consolidated files are object-level editable packages without embedded picture objects')
    return 0
if __name__=='__main__': raise SystemExit(main())
