from pathlib import Path
import zipfile,re,copy
from lxml import etree
srcdir = Path(__file__).resolve().parents[1] / '03_PPTX_NATIVE_EDITABLE'
out=srcdir/'All_18_Figures_v4.3.pptx'
files=sorted(srcdir.glob('Figure_*.pptx'))
P='http://schemas.openxmlformats.org/presentationml/2006/main'; R='http://schemas.openxmlformats.org/officeDocument/2006/relationships'; PR='http://schemas.openxmlformats.org/package/2006/relationships'; CT='http://schemas.openxmlformats.org/package/2006/content-types'; EP='http://schemas.openxmlformats.org/officeDocument/2006/extended-properties'; VT='http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes'; CP='http://schemas.openxmlformats.org/package/2006/metadata/core-properties'; DC='http://purl.org/dc/elements/1.1/'
with zipfile.ZipFile(files[0]) as z: payload={n:z.read(n) for n in z.namelist()}
parser=etree.XMLParser(remove_blank_text=False)
pres=etree.fromstring(payload['ppt/presentation.xml'],parser); sldlst=pres.find(f'{{{P}}}sldIdLst')
prels=etree.fromstring(payload['ppt/_rels/presentation.xml.rels'],parser)
ct=etree.fromstring(payload['[Content_Types].xml'],parser)
# Keep slide1. Add slides 2..18 from source packages.
for i,p in enumerate(files[1:],2):
 with zipfile.ZipFile(p) as z:
  payload[f'ppt/slides/slide{i}.xml']=z.read('ppt/slides/slide1.xml')
  payload[f'ppt/slides/_rels/slide{i}.xml.rels']=z.read('ppt/slides/_rels/slide1.xml.rels')
 rid=f'rId{i+2}' # rId4 onwards, but rId4 currently presProps -> move presProps later
 # We'll rebuild presentation rels cleanly later.
# rebuild rels: theme rId1, master rId2, slides rId3..rId20, presProps rId21
for e in list(prels): prels.remove(e)
def rel(rid,typ,target):
 e=etree.SubElement(prels,f'{{{PR}}}Relationship');e.set('Id',rid);e.set('Type',typ);e.set('Target',target)
rel('rId1','http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme','theme/theme1.xml')
rel('rId2','http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster','slideMasters/slideMaster1.xml')
for i in range(1,19): rel(f'rId{i+2}','http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide',f'slides/slide{i}.xml')
rel('rId21','http://schemas.openxmlformats.org/officeDocument/2006/relationships/presProps','presProps.xml')
# rebuild slide list
for e in list(sldlst): sldlst.remove(e)
for i in range(1,19):
 e=etree.SubElement(sldlst,f'{{{P}}}sldId');e.set('id',str(255+i));e.set(f'{{{R}}}id',f'rId{i+2}')
# Add content types for all added slides and rels.
existing={e.get('PartName') for e in ct.findall(f'{{{CT}}}Override')}
for i in range(2,19):
 for part,ctype in [(f'/ppt/slides/slide{i}.xml','application/vnd.openxmlformats-officedocument.presentationml.slide+xml'),(f'/ppt/slides/_rels/slide{i}.xml.rels','application/vnd.openxmlformats-package.relationships+xml')]:
  if part not in existing:
   e=etree.SubElement(ct,f'{{{CT}}}Override');e.set('PartName',part);e.set('ContentType',ctype)
# metadata
if 'docProps/app.xml' in payload:
 app=etree.fromstring(payload['docProps/app.xml'],parser)
 slides=app.find(f'{{{EP}}}Slides')
 if slides is not None: slides.text='18'
 payload['docProps/app.xml']=etree.tostring(app,xml_declaration=True,encoding='UTF-8')
if 'docProps/core.xml' in payload:
 core=etree.fromstring(payload['docProps/core.xml'],parser)
 title=core.find(f'{{{DC}}}title')
 if title is not None:title.text='Student’s Guide - All 18 Author-Corrected Native Editable Figures v4.3'
 payload['docProps/core.xml']=etree.tostring(core,xml_declaration=True,encoding='UTF-8')
payload['ppt/presentation.xml']=etree.tostring(pres,xml_declaration=True,encoding='UTF-8',standalone='yes')
payload['ppt/_rels/presentation.xml.rels']=etree.tostring(prels,xml_declaration=True,encoding='UTF-8')
payload['[Content_Types].xml']=etree.tostring(ct,xml_declaration=True,encoding='UTF-8')
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
 for n,b in payload.items():z.writestr(n,b)
print(out)
