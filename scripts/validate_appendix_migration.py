#!/usr/bin/env python3
from pathlib import Path
import csv, json, sys
ROOT=Path(__file__).resolve().parents[1]; errors=[]
def read(rel):
 with (ROOT/rel).open(encoding='utf-8-sig',newline='') as f: return list(csv.DictReader(f))
amp=read('companion/09_CHANGE_AND_SUPERSESSION/APPENDIX_MIGRATION_REGISTER.csv')
aom=read('companion/09_CHANGE_AND_SUPERSESSION/APPENDIX_OBJECT_MIGRATION_REGISTER_PHASE14C.csv')
spr=read('companion/10_BOOK_RESOURCE_MAP/STABLE_PRINCIPLE_RETENTION_REGISTER.csv')
if len(spr)!=21: errors.append(f'expected 21 stable principles, found {len(spr)}')
if any(r.get('status')!='INTEGRATED_IN_BOOK_v3.9.0' for r in spr): errors.append('stable-principle register is not closed for v3.9.0')
if any('COMPANION_v1.2.0_RELEASED' not in r.get('status','') for r in amp): errors.append('appendix migration register is not closed for companion v1.2.0')
for r in aom:
 p=r.get('current_companion_path') or r.get('companion_path') or r.get('target_companion_path') or ''
 if p and not (ROOT/p).exists(): errors.append('missing mapped path '+p)
for rel in ['companion/08_INSTITUTIONAL_LINKS/DC_A_REQUIREMENTS_AND_RECOMMENDATIONS.md','companion/08_INSTITUTIONAL_LINKS/DC_B_OFFICIAL_ROUTE_AND_CURRENT_SESSION.md','companion/08_INSTITUTIONAL_LINKS/DC_C_MILESTONE_EVIDENCE_AND_DOSSIER.md','companion/06_AI_TRACE_AND_DISCLOSURE/DC_D_GENERATIVE_AI_USE_DISCLOSURE_AND_RESPONSIBILITY.md','companion/07_SUBMISSION_AND_DEFENCE/DC_E_SUBMISSION_AND_DEFENCE.md']:
 if not (ROOT/rel).is_file(): errors.append('missing DC module '+rel)
status=(ROOT/'companion/10_BOOK_RESOURCE_MAP/BOOK_INTEGRATION_STATUS.md').read_text(encoding='utf-8')
if 'Formal Appendices A–E are absent from book v3.9.0' not in status: errors.append('final appendix-free architecture not asserted')
print(json.dumps({'status':'FAIL' if errors else 'PASS','appendix_rows':len(amp),'object_rows':len(aom),'stable_principles':len(spr),'errors':errors},ensure_ascii=False,indent=2)); sys.exit(1 if errors else 0)
