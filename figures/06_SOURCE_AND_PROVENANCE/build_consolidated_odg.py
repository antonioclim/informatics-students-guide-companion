from __future__ import annotations
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED, ZIP_STORED
from lxml import etree
from copy import deepcopy
from datetime import datetime, timezone
import re, shutil, tempfile

SRC_DIR = Path(__file__).resolve().parents[1] / '01_ODG_NATIVE_EDITABLE'
OUT=SRC_DIR/'All_18_Figures_v4.3.odg'
files=sorted(SRC_DIR.glob('Figure_*.odg'), key=lambda p: tuple(map(int,re.findall(r'Figure_(\d+)_(\d+)',p.name)[0])))
assert len(files)==18

OFF='urn:oasis:names:tc:opendocument:xmlns:office:1.0'
STYLE='urn:oasis:names:tc:opendocument:xmlns:style:1.0'
DRAW='urn:oasis:names:tc:opendocument:xmlns:drawing:1.0'
TEXT='urn:oasis:names:tc:opendocument:xmlns:text:1.0'
PRES='urn:oasis:names:tc:opendocument:xmlns:presentation:1.0'
XML='http://www.w3.org/XML/1998/namespace'
NS={'office':OFF,'style':STYLE,'draw':DRAW,'text':TEXT,'presentation':PRES}

def q(ns,local): return f'{{{ns}}}{local}'

def parse_member(path,name):
    with ZipFile(path) as z:
        return etree.fromstring(z.read(name))

def named_values(root, sections=None):
    vals=set()
    for e in root.iter():
        for k,v in e.attrib.items():
            ns=etree.QName(k).namespace; loc=etree.QName(k).localname
            if loc=='name' and ns in {STYLE,DRAW,PRES}:
                vals.add(v)
    return vals

def prefix_tree(tree, prefix, style_map, id_map=None):
    t=deepcopy(tree)
    allmap=dict(style_map)
    if id_map: allmap.update(id_map)
    # exact value replacements, plus #fragment and whitespace lists
    for e in t.iter():
        for k,v in list(e.attrib.items()):
            if v in allmap:
                e.set(k,allmap[v]); continue
            if v.startswith('#') and v[1:] in allmap:
                e.set(k,'#'+allmap[v[1:]]); continue
            parts=v.split()
            if len(parts)>1 and any(p in allmap for p in parts):
                e.set(k,' '.join(allmap.get(p,p) for p in parts))
    return t

# Load first package as container
base=files[0]
with ZipFile(base) as z:
    members={n:z.read(n) for n in z.namelist()}
    compress={n:z.getinfo(n).compress_type for n in z.namelist()}

base_content=parse_member(base,'content.xml')
base_styles=parse_member(base,'styles.xml')

# Clear target style/content sections
c_font=base_content.find(q(OFF,'font-face-decls'))
c_auto=base_content.find(q(OFF,'automatic-styles'))
c_body=base_content.find(q(OFF,'body'))
c_draw=c_body.find(q(OFF,'drawing'))
for e in list(c_auto): c_auto.remove(e)
for e in list(c_draw): c_draw.remove(e)

s_font=base_styles.find(q(OFF,'font-face-decls'))
s_styles=base_styles.find(q(OFF,'styles'))
s_auto=base_styles.find(q(OFF,'automatic-styles'))
s_master=base_styles.find(q(OFF,'master-styles'))
# retain default styles only; clear all named style children
for e in list(s_styles):
    if etree.QName(e).localname!='default-style':
        s_styles.remove(e)
for sec in [s_auto,s_master]:
    for e in list(sec): sec.remove(e)

# union font faces by name+attrs; start with first
seen_fonts=set()
for sec in [c_font,s_font]:
    if sec is not None:
        for e in list(sec):
            key=(etree.QName(e).localname,tuple(sorted(e.attrib.items())))
            seen_fonts.add(key)

for idx,path in enumerate(files,1):
    prefix=f'f{idx:02d}_'
    content=parse_member(path,'content.xml')
    styles=parse_member(path,'styles.xml')

    # union font faces into both documents
    for srcsec, dstsec in [(content.find(q(OFF,'font-face-decls')),c_font),(styles.find(q(OFF,'font-face-decls')),s_font)]:
        if srcsec is None or dstsec is None: continue
        for e in srcsec:
            key=(etree.QName(e).localname,tuple(sorted(e.attrib.items())))
            if key not in seen_fonts:
                dstsec.append(deepcopy(e)); seen_fonts.add(key)

    # collect all style/resource names from both docs
    style_names=named_values(content.find(q(OFF,'automatic-styles')))
    for secname in ['styles','automatic-styles','master-styles']:
        sec=styles.find(q(OFF,secname))
        if sec is not None: style_names |= named_values(sec)
    style_map={n:prefix+n for n in style_names}

    # collect object/page ids and names for uniqueness within copied page
    srcdrawing=content.find(f'{{{OFF}}}body/{{{OFF}}}drawing')
    assert srcdrawing is not None and len(srcdrawing)==1
    page=srcdrawing[0]
    idvals=set()
    for e in page.iter():
        for k,v in e.attrib.items():
            ns=etree.QName(k).namespace; loc=etree.QName(k).localname
            if loc=='id' or (loc=='name' and ns==DRAW):
                idvals.add(v)
    id_map={v:prefix+v for v in idvals}

    # content automatic styles
    srcauto=content.find(q(OFF,'automatic-styles'))
    for e in srcauto:
        c_auto.append(prefix_tree(e,prefix,style_map,id_map))

    # named styles, excluding default styles
    srcstyles=styles.find(q(OFF,'styles'))
    if srcstyles is not None:
        for e in srcstyles:
            if etree.QName(e).localname=='default-style': continue
            s_styles.append(prefix_tree(e,prefix,style_map,id_map))
    # styles automatic and master
    for srcsec,dstsec in [(styles.find(q(OFF,'automatic-styles')),s_auto),(styles.find(q(OFF,'master-styles')),s_master)]:
        if srcsec is not None:
            for e in srcsec:
                dstsec.append(prefix_tree(e,prefix,style_map,id_map))

    newpage=prefix_tree(page,prefix,style_map,id_map)
    m=re.match(r'Figure_(\d+)_(\d+)',path.stem)
    newpage.set(q(DRAW,'name'),f'Figure {m.group(1)}.{m.group(2)}')
    c_draw.append(newpage)

# Update metadata
meta=parse_member(base,'meta.xml')
meta_node=meta.find(q(OFF,'meta'))
# remove existing title/subject/description/user-defined/generator/editing stats except creator/date maybe
DC='http://purl.org/dc/elements/1.1/'
META='urn:oasis:names:tc:opendocument:xmlns:meta:1.0'
for local,text in [('title','All 18 Figures — Student’s Guide — v4.3 author-corrected native editable ODG'),('subject','Author-corrected figure authority v4.3 — public release'),('description','Consolidated 18-page native editable ODG assembled from the author-corrected individual ODG sources supplied on 23 August 2026. Released under CC BY 4.0.')]:
    tag=q(DC,local)
    el=meta_node.find(tag)
    if el is None: el=etree.SubElement(meta_node,tag)
    el.text=text
for el in meta_node.findall(q(META,'generator')): el.text='Controlled reconstruction Phase 17B-redir'
for el in meta_node.findall(q(META,'editing-duration')): el.text='PT0S'
for el in meta_node.findall(q(META,'editing-cycles')): el.text='1'

members['content.xml']=etree.tostring(base_content,xml_declaration=True,encoding='UTF-8',standalone=True)
members['styles.xml']=etree.tostring(base_styles,xml_declaration=True,encoding='UTF-8',standalone=True)
members['meta.xml']=etree.tostring(meta,xml_declaration=True,encoding='UTF-8',standalone=True)
# write ODF mimetype first and uncompressed
with ZipFile(OUT,'w') as zout:
    mt=members.pop('mimetype')
    zout.writestr('mimetype',mt,compress_type=ZIP_STORED)
    for n,b in members.items():
        zout.writestr(n,b,compress_type=ZIP_DEFLATED)
print(OUT,OUT.stat().st_size)
