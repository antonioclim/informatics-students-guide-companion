#!/usr/bin/env python3
from pathlib import Path
import json, subprocess, sys
ROOT=Path(__file__).resolve().parents[1]
steps=[
 [sys.executable,str(ROOT/'scripts/validate_repository.py')],
 [sys.executable,str(ROOT/'scripts/verify_manifest.py')],
 [sys.executable,str(ROOT/'scripts/check_internal_links.py')],
 [sys.executable,str(ROOT/'scripts/scan_sensitive_content.py'),'--fail-on','medium'],
 [sys.executable,str(ROOT/'scripts/validate_data_files.py')],
 [sys.executable,str(ROOT/'scripts/validate_semantic_contracts.py')],
 [sys.executable,str(ROOT/'scripts/validate_appendix_migration.py')],
]
res=[]
for cmd in steps:
 cp=subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True)
 res.append({'command':cmd,'returncode':cp.returncode,'stdout':cp.stdout,'stderr':cp.stderr})
status='PASS' if all(x['returncode']==0 for x in res) else 'FAIL'
print(json.dumps({'status':status,'steps':res},ensure_ascii=False,indent=2)); sys.exit(0 if status=='PASS' else 1)
