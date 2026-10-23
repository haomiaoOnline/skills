#!/usr/bin/env python3
"""COSMIC v2: one input -> one end-user deliverable XLSX.

Stdout only prints JSON status, no additional report files.
"""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
import v2_core,v2_io
import v2_auth

def run(input_path,output_path,sheet=None,profile=None,qualify_with_process=False,approval_key_file=None,source_root=None):
 cfg={}
 if Path(input_path).resolve()==Path(output_path).resolve():
  raise ValueError("Output must be separate from source input")
 if profile:
  cfg=json.loads(Path(profile).read_text(encoding="utf8"))
  if not isinstance(cfg,dict):raise ValueError("Profile must be a JSON object")
  if cfg.get("policy") not in (None,v2_core.POLICY_VERSION):
   raise ValueError("Unsupported universal policy version")
 records=v2_io.read_source(input_path,sheet, cfg.get("column_mapping"))
 if qualify_with_process:
  records=v2_core.qualify_with_evidenced_process(records)
 # Every deliverable holds candidate details + all issue explanations.
 key=v2_auth.read_key(approval_key_file) if approval_key_file else None
 assessed=v2_core.validate(records,approval_key=key,source_base=(source_root or Path(input_path).parent))
 v2_io.export_workbook(records,assessed,output_path)
 return {"state":"READY_FOR_USER_ACCEPTANCE" if assessed["passed"] else "BLOCKED_CANDIDATE_ONLY",
         "file":str(output_path),"file_count":1,"rows":len(records),
         "approved_cfp":assessed["approved_cfp"],
         "issues":len(assessed["issues"]),"policy":v2_core.POLICY_VERSION}
def main(argv=None):
 p=argparse.ArgumentParser(description="COSMIC v2 universal single deliverable")
 p.add_argument("--input",required=True,type=Path)
 p.add_argument("--output",required=True,type=Path)
 p.add_argument("--sheet")
 p.add_argument("--approval-key-file",type=Path,help="Optional reviewer-held HMAC key for verifying current signed rows")
 p.add_argument("--source-root",type=Path,help="Base directory for relative source_file references")
 p.add_argument("--profile",type=Path,help="JSON input column mapping")
 p.add_argument("--qualify-with-process",action="store_true",
                help="Suggest source-evidenced functional-process qualifiers for duplicates; resets changed rows to pending")
 a=p.parse_args(argv)
 if a.input.resolve()==a.output.resolve():p.error("output must differ from source")
 result=run(a.input,a.output,a.sheet,a.profile,a.qualify_with_process,a.approval_key_file,a.source_root)
 print(json.dumps(result,ensure_ascii=False,indent=2))
 return 0 if result["state"]=="READY_FOR_USER_ACCEPTANCE" else 2
if __name__=="__main__":
 try:sys.exit(main())
 except Exception as ex:
  print(json.dumps({"state":"ERROR","message":str(ex)},ensure_ascii=False),file=sys.stderr)
  sys.exit(1)
