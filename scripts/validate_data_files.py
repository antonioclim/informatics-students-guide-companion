#!/usr/bin/env python3
from __future__ import annotations
import csv, json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
errors=[]; csv_n=0; json_n=0
for p in sorted(ROOT.rglob('*.csv')):
    csv_n+=1
    try:
        with p.open(encoding='utf-8-sig',newline='') as f: rows=list(csv.reader(f))
        if not rows or not rows[0]: errors.append(f'empty CSV {p.relative_to(ROOT)}'); continue
        if any(not h.strip() for h in rows[0]): errors.append(f'blank CSV header {p.relative_to(ROOT)}')
        if len(set(rows[0]))!=len(rows[0]): errors.append(f'duplicate CSV header {p.relative_to(ROOT)}')
        width=len(rows[0])
        for i,r in enumerate(rows[1:],2):
            if len(r)!=width: errors.append(f'width mismatch {p.relative_to(ROOT)} row {i}: {len(r)} != {width}')
    except Exception as e: errors.append(f'CSV parse error {p.relative_to(ROOT)}: {e}')
for p in sorted(ROOT.rglob('*.json')):
    json_n+=1
    try: json.loads(p.read_text(encoding='utf-8-sig'))
    except Exception as e: errors.append(f'JSON parse error {p.relative_to(ROOT)}: {e}')
if errors:
    print('\n'.join('ERROR: '+e for e in errors)); sys.exit(1)
print(f'PASS: {csv_n} CSV and {json_n} JSON files parsed with consistent structure')
