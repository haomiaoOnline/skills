#!/usr/bin/env python3
"""Local independent reviewer-only signing step.

The key must be kept by the reviewer outside Agent-accessible input folders.
This creates exactly one signed workload XLSX. It cannot authenticate the real
person or prove COSMIC classification is true; it prevents accidental stale
approvals and enforces source-file integrity.
"""
import argparse,json,sys
from pathlib import Path
import v2_auth,v2_core,v2_io

def sign_file(input_file,output_file,key_file,source_root=None,sheet="COSMIC工作量拆解"):
    original=Path(input_file)
    root=Path(source_root) if source_root else original.parent
    key=v2_auth.read_key(key_file)
    rows=v2_io.read_source(original,sheet=sheet)
    completed=0
    for r in rows:
        if r.get("status") in ("未建设","unbuilt","excluded"):continue
        if r.get("review_status") not in ("approved","已审批"):
            r["approval_signature"]=""
            continue
        if not all(r.get(field) for field in ("reviewer","reviewed_at","evidence_text",
                 "source_locator","source_file","boundary_basis","movement_basis")):
            raise ValueError("Incomplete human-reviewed row "+r.get("row_id",""))
        if not v2_auth.review_date_valid(r):
            raise ValueError("Invalid or future review date")
        if not v2_auth.source_valid(r,root):
            raise ValueError("Source file does not match declared SHA: "+r.get("row_id",""))
        r["approval_signature"]=v2_auth.signature(r,key)
        completed+=1
    report=v2_core.validate(rows,approval_key=key,source_base=root)
    v2_io.export_workbook(rows,report,output_file)
    return {"file":str(output_file),"signed_rows":completed,
            "status":"READY_FOR_USER_ACCEPTANCE" if report["passed"] else "BLOCKED_CANDIDATE_ONLY",
            "issues":len(report["issues"]),"approved_cfp":report["approved_cfp"]}

def main():
    p=argparse.ArgumentParser(description="Independent reviewer signs the current workbook")
    p.add_argument("--input",required=True,type=Path)
    p.add_argument("--output",required=True,type=Path)
    p.add_argument("--key-file",required=True,type=Path)
    p.add_argument("--source-root",type=Path)
    p.add_argument("--sheet",default="COSMIC工作量拆解")
    a=p.parse_args()
    print(json.dumps(sign_file(a.input,a.output,a.key_file,a.source_root,a.sheet),ensure_ascii=False))
if __name__=="__main__":
    try:main()
    except Exception as exc:
        print(json.dumps({"state":"ERROR","message":str(exc)},ensure_ascii=False),file=sys.stderr)
        sys.exit(1)
