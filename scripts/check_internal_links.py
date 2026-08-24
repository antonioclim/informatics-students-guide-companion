#!/usr/bin/env python3
from pathlib import Path
from urllib.parse import unquote
import json,re,sys
ROOT=Path(__file__).resolve().parents[1]
errors=[]; checked=0
pat=re.compile(r'!?(?:\[[^\]]*\])\(([^)]+)\)')
for p in ROOT.rglob('*.md'):
 try: txt=p.read_text(encoding='utf-8')
 except Exception: continue
 for raw in pat.findall(txt):
  target=raw.strip().split()[0].strip('<>')
  if not target or target.startswith(('#','http://','https://','mailto:')): continue
  target=unquote(target.split('#',1)[0])
  if not target: continue
  checked+=1
  q=(p.parent/target).resolve()
  try: q.relative_to(ROOT.resolve())
  except Exception: errors.append(f'link escapes repository: {p.relative_to(ROOT)} -> {target}'); continue
  if not q.exists(): errors.append(f'broken link: {p.relative_to(ROOT)} -> {target}')
if errors:
 print(json.dumps({'status':'FAIL','checked':checked,'errors':errors},ensure_ascii=False,indent=2));sys.exit(1)
print(json.dumps({'status':'PASS','checked':checked},indent=2))
