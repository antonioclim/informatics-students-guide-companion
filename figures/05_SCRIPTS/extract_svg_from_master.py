#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, zipfile
from pathlib import Path

MAPPING={
'image_ch01_01.svg':'Figure_1_1_Evidence_to_Defence_Architecture.svg','image_ch01_02.svg':'Figure_1_2_Advice_Authority_and_Authorship_Map.svg',
'image_ch02_01.svg':'Figure_2_1_Topic_Decision_Path.svg','image_ch02_02.svg':'Figure_2_2_SCOPE_Framing_Canvas.svg',
'image_ch03_01.svg':'Figure_3_1_Evidence_Identity_Chain.svg','image_ch03_02.svg':'Figure_3_2_CORPUS_Records_Cycle.svg',
'image_ch04_01.svg':'Figure_4_1_Reversible_Driver_to_Test_Chain.svg','image_ch04_02.svg':'Figure_4_2_DECIDE_Conditional_Commitment_Cycle.svg',
'image_ch05_01.svg':'Figure_5_1_Candidate_to_Admission_Chain.svg','image_ch05_02.svg':'Figure_5_2_Bounded_Execution_Loop.svg',
'image_ch06_01.svg':'Figure_6_1_Evidence_to_Claim_Ladder.svg','image_ch06_02.svg':'Figure_6_2_Claim_Stress_Test_and_Gate_Returns.svg',
'image_ch07_01.svg':'Figure_7_1_Gate_Records_to_Answer_Architecture.svg','image_ch07_02.svg':'Figure_7_2_Section_and_Paragraph_Contract.svg',
'image_ch08_01.svg':'Figure_8_1_Semantic_First_Revision_and_Proof_Control.svg','image_ch08_02.svg':'Figure_8_2_One_Study_Consistency_and_Metadata_Lock.svg',
'image_ch09_01.svg':'Figure_9_1_Author_Side_Closure_to_Defence_Ready_Record.svg','image_ch09_02.svg':'Figure_9_2_One_Bounded_Contribution_Across_Defence_Interfaces.svg'}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('master',type=Path);ap.add_argument('output',type=Path);ap.add_argument('--expected-master-sha256',default='');a=ap.parse_args()
 h=hashlib.sha256(a.master.read_bytes()).hexdigest()
 if a.expected_master_sha256 and h!=a.expected_master_sha256:raise SystemExit('master hash mismatch')
 a.output.mkdir(parents=True,exist_ok=True)
 with zipfile.ZipFile(a.master) as z:
  for source,target in MAPPING.items():
   path='word/media/'+source
   if path not in z.namelist():raise SystemExit('missing '+path)
   (a.output/target).write_bytes(z.read(path))
 print(f'Extracted {len(MAPPING)} SVG files from master {h}')
if __name__=='__main__':main()
