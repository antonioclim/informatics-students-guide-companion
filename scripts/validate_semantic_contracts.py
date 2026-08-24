#!/usr/bin/env python3
from __future__ import annotations
import csv, re, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
errors=[]

def read(rel):
    with (ROOT/rel).open(encoding='utf-8-sig',newline='') as f: return list(csv.DictReader(f))

def rows(path):
    with path.open(encoding='utf-8-sig',newline='') as f: return list(csv.reader(f))

def key(name):
    return re.sub(r'[^a-z0-9]+','_', (name or '').lower()).strip('_')

cat=read('companion/09_CHANGE_AND_SUPERSESSION/RECORD_CATALOGUE_v1.2.0.csv')
fd=read('schemas/CSV_DATA_DICTIONARIES/TEMPLATE_FIELD_DICTIONARY.csv')
audit=read('companion/09_CHANGE_AND_SUPERSESSION/TEMPLATE_SEMANTIC_AUDIT_REGISTER_v1.2.0.csv')
gates=read('companion/09_CHANGE_AND_SUPERSESSION/GATE_CHAIN_REGISTRY_v1.2.0.csv')
criteria=read('companion/09_CHANGE_AND_SUPERSESSION/GATE_CRITERIA_REGISTRY_v1.2.0.csv')
routes=read('companion/05_ROUTE_KITS/ROUTE_KIT_CATALOGUE.csv')
vocab=read('schemas/CSV_DATA_DICTIONARIES/CONTROLLED_VOCABULARY.csv')
example_audit=read('manifests/WORKED_EXAMPLE_COMPLETENESS_AUDIT.csv')
vocab_map={}
for r in vocab: vocab_map.setdefault(r['vocabulary'],[]).append(r['value'])
gate_names=[r['control_or_gate'] for r in gates]

if len([r for r in cat if r['level']=='minimum'])!=12: errors.append('record catalogue does not contain 12 minimum records')
if len([r for r in cat if r['level']=='full'])!=40: errors.append('record catalogue does not contain 40 full records')
if len(audit)!=52: errors.append(f'expected 52 template audit rows, found {len(audit)}')
if len(gates)!=9: errors.append(f'expected 9 gate rows, found {len(gates)}')
if len(criteria)<55: errors.append(f'gate criteria registry too small: {len(criteria)}')
if len(routes)!=8: errors.append(f'expected 8 route kits, found {len(routes)}')
if len(example_audit)!=72: errors.append(f'expected 72 completed-record audit rows, found {len(example_audit)}')
if any(r.get('status')!='PASS' for r in example_audit): errors.append('worked-example completeness audit contains FAIL')
if sum(int(r.get('blank_cells') or 0) for r in example_audit)!=0: errors.append('worked examples contain blank cells')
if sum(int(r.get('controlled_value_violations') or 0) for r in example_audit)!=0: errors.append('worked examples violate controlled vocabularies')

def vocabulary_for(filename, field):
    k=key(field); f=(filename or '').upper()
    if k in {'route','dominant_route','provisional_route'}: return 'route'
    if k=='gate_decision': return 'gate_decision'
    if f.startswith('GATE_RECORD') and k=='decision': return 'gate_decision'
    if f.startswith('TRACE_RECORD') and k in {'decision','student_decision'}: return 'ai_disposition'
    if f.startswith('CLAIM_EVIDENCE_MAP') and k=='status': return 'claim_status'
    if f in {'CURRENT_SESSION_AUTHORITY_RECORD_FULL.CSV','AUTHORITY_MATRIX_FULL.CSV'} and k=='status': return 'source_status'
    if k=='inclusion_status': return 'inclusion_status'
    if k=='evidence_status': return 'evidence_status'
    if k in {'privacy_status','confidentiality_class'}: return 'privacy_class'
    if k=='disposition': return 'work_disposition'
    if k=='rights_status': return 'rights_status'
    if k in {'render_status','proof_state'}: return 'render_status'
    if k=='submission_status': return 'submission_status'
    if f=='ACCESSIBILITY_RENDER_AUDIT_FULL.CSV' and k=='result': return 'audit_result'
    if k=='rehearsal_result': return 'rehearsal_result'
    if k in {'access_status','full_text_status'}: return 'access_status'
    if k in {'status','review_status','rehearsal_status'}: return 'lifecycle_status'
    return ''

def expected_controlled(filename, field):
    k=key(field); v=vocabulary_for(filename,field)
    if v: return '; '.join(vocab_map[v])
    if k in {'gate','gate_name','earliest_return_gate','current_gate','return_route','gate_reopened','gate_reopened_if_failed'}: return '; '.join(gate_names)
    if k=='decision_consequence': return 'continue; narrow; pivot; stop'
    if k=='severity': return 'low; medium; high; blocking'
    return ''

# Template path, headers and field dictionary.
fd_by={}
for r in fd: fd_by.setdefault(r['record_id'],[]).append(r)
for r in cat:
    p=ROOT/r['template_path']
    if not p.exists(): errors.append('missing template '+r['template_path']); continue
    data=rows(p)
    expected=[x['field_name'] for x in sorted(fd_by.get(r['record_id'],[]), key=lambda x:int(x['field_order']))]
    if data and data[0][:5]==['field','entry','evidence_or_basis','review_status','guidance']:
        actual=[x[0] for x in data[1:]]
    else: actual=data[0] if data else []
    if actual!=expected: errors.append(f'field dictionary mismatch {r["filename"]}')
    for field_row in fd_by.get(r['record_id'],[]):
        expected_vocab=vocabulary_for(r['filename'],field_row['field_name'])
        if field_row.get('controlled_vocabulary','')!=expected_vocab:
            errors.append(f'controlled vocabulary name mismatch {r["filename"]}:{field_row["field_name"]}')
        expected_values=expected_controlled(r['filename'],field_row['field_name'])
        if field_row.get('controlled_values','')!=expected_values:
            errors.append(f'contextual controlled-value mismatch {r["filename"]}:{field_row["field_name"]}')
        if not field_row.get('requiredness','').strip() or not field_row.get('validation_rule','').strip():
            errors.append(f'incomplete field contract {r["filename"]}:{field_row["field_name"]}')
    for required in ['purpose','when_to_use','completion_test','book_anchor','data_sensitivity','semantic_status']:
        if not r.get(required,'').strip(): errors.append(f'blank catalogue {required} for {r["filename"]}')
    if 'Provide the v1.2.0 record required' in r['purpose']: errors.append('generic purpose remains for '+r['filename'])

# Route-kit completeness and exact worked-example schemas.
expected_dirs={'build_and_evaluate','algorithmic_simulation','predictive_machine_learning','quantitative_empirical','qualitative_inquiry','case_study','formal_evidence_synthesis','hybrid_route'}
actual_dirs={p.name for p in (ROOT/'companion/05_ROUTE_KITS').iterdir() if p.is_dir()}
if actual_dirs!=expected_dirs: errors.append(f'route directory mismatch: {actual_dirs ^ expected_dirs}')
source_map={
 '02_SCOPE_CANVAS_MIN_COMPLETED.csv':'companion/03_TEMPLATES_MINIMUM/SCOPE_CANVAS_MIN.csv',
 '03_DECIDE_RECORD_MIN_COMPLETED.csv':'companion/03_TEMPLATES_MINIMUM/DECIDE_RECORD_MIN.csv',
 '04_EXECUTION_PROVENANCE_FULL_COMPLETED.csv':'companion/04_TEMPLATES_FULL/EXECUTION_PROVENANCE_RECORD_FULL.csv',
 '05_EVALUATION_DESIGN_FULL_COMPLETED.csv':'companion/04_TEMPLATES_FULL/EVALUATION_DESIGN_RECORD_FULL.csv',
 '06_CLAIM_EVIDENCE_MAP_MIN_COMPLETED.csv':'companion/03_TEMPLATES_MINIMUM/CLAIM_EVIDENCE_MAP_MIN.csv',
 '07_DEMONSTRATION_RUNBOOK_MIN_COMPLETED.csv':'companion/03_TEMPLATES_MINIMUM/DEMONSTRATION_RUNBOOK_MIN.csv',
 '08_DEFENCE_QUESTION_MATRIX_MIN_COMPLETED.csv':'companion/03_TEMPLATES_MINIMUM/DEFENCE_QUESTION_MATRIX_MIN.csv',
 '09_GATE_RECORD_MIN_COMPLETED.csv':'companion/03_TEMPLATES_MINIMUM/GATE_RECORD_MIN.csv',
}
def shape(p):
    data=rows(p)
    if data and data[0][:5]==['field','entry','evidence_or_basis','review_status','guidance']:
        return ('form',data[0],[r[0] for r in data[1:]])
    return ('ledger',data[0] if data else [],[])
for d in sorted(actual_dirs):
    base=ROOT/'companion/05_ROUTE_KITS'/d
    for name in ['README.md','ROUTE_GATE_PLAN.csv','ROUTE_RECORD_SELECTION.csv','RISK_AND_BOUNDARY_REGISTER.csv','worked_example/README.md','worked_example/EXAMPLE_MANIFEST.csv']:
        if not (base/name).exists(): errors.append(f'missing {d}/{name}')
    gp=read((base/'ROUTE_GATE_PLAN.csv').relative_to(ROOT).as_posix())
    if len(gp)!=9: errors.append(f'{d} gate plan has {len(gp)} rows')
    manifest=read((base/'worked_example/EXAMPLE_MANIFEST.csv').relative_to(ROOT).as_posix())
    listed={r['filename'] for r in manifest}
    actual_csv={p.name for p in (base/'worked_example').glob('*.csv') if p.name!='EXAMPLE_MANIFEST.csv'}
    if listed!=actual_csv: errors.append(f'example manifest mismatch {d}: {listed ^ actual_csv}')
    for example,source in source_map.items():
        ep=base/'worked_example'/example; sp=ROOT/source
        if not ep.exists(): errors.append(f'missing {d}/worked_example/{example}'); continue
        if shape(ep)!=shape(sp): errors.append(f'schema mismatch {d}/{example}')

# Crosswalk links to old worked-example path are forbidden.
for p in ROOT.rglob('*'):
    if p.name == 'validate_semantic_contracts.py':
        continue
    if p.is_file() and p.suffix.lower() in {'.md','.csv','.json','.txt','.py','.yml','.yaml','.cff'}:
        t=p.read_text(encoding='utf-8',errors='replace')
        if 'companion/05_WORKED_EXAMPLES' in t: errors.append('superseded worked-example path in '+p.relative_to(ROOT).as_posix())
if errors:
    print('\n'.join('ERROR: '+e for e in errors)); sys.exit(1)
print(f'PASS: semantic contracts for 52 templates, {len(fd)} fields, 9 gates, {len(criteria)} gate criteria, 8 route kits and 72 complete worked-example records')
