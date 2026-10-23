#!/usr/bin/env python3
"""Reproducible portable COSMIC v2 Skill package."""
import argparse,hashlib,json,re
from pathlib import Path
from zipfile import ZipFile,ZipInfo,ZIP_DEFLATED
ROOT=Path(__file__).resolve().parents[1]
FILES=("SKILL.md","AGENTS.md","README.md","README_V2.md","CHANGELOG.md","LICENSE","requirements.txt","requirements-mcp.txt",
       "docs/AGENT_INSTALL.md","docs/ARCHITECTURE.md","docs/USAGE.md","docs/SECURITY.md",
       "docs/TROUBLESHOOTING.md","docs/REPOSITORY_POLICY.md",
       "references/01-official-method-v5.md","references/03-generation-playbook.md",
       "references/05-output-contract.md","references/11-v2-universal.md",
       "templates/intake.md","templates/master-columns.csv","templates/profile.example.json",
       "scripts/v2_core.py","scripts/v2_io.py","scripts/v2_auth.py","scripts/v2_review.py","scripts/v2_cli.py","scripts/v2_mcp.py","scripts/build_release.py","scripts/install_agent.py",
       "tests/test_v2_core.py","tests/test_v2_io.py","tests/test_v2_mcp.py","tests/test_v2_security.py","tests/test_v2_install.py","tests/test_v2_package.py")
def build(output,name):
 output=Path(output);output.parent.mkdir(parents=True,exist_ok=True)
 with ZipFile(output,"w",compression=ZIP_DEFLATED) as z:
  for filename in FILES:
   contents=(ROOT/filename).read_bytes()
   if filename=="SKILL.md":
    text=contents.decode("utf8")
    text,n=re.subn(r'(?m)^name:[^\n]+$',"name: "+name,text,count=1)
    if n!=1:raise ValueError("Skill name frontmatter missing")
    contents=text.encode("utf8")
   info=ZipInfo(filename,date_time=(2026,10,21,0,0,0));info.compress_type=ZIP_DEFLATED;info.external_attr=0o644<<16
   z.writestr(info,contents)
 with ZipFile(output) as z:
  if z.testzip() is not None or len(z.namelist())!=len(FILES):raise ValueError("Broken release")
 return {"path":str(output),"sha256":hashlib.sha256(output.read_bytes()).hexdigest(),"files":len(FILES),"version":"2.0.3","skill":name}
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--out",type=Path,default=ROOT/"packages/cosmic-materials-assistant-v2.0.3.zip")
 p.add_argument("--name",default="cosmic-materials-assistant-p0")
 args=p.parse_args()
 if not re.fullmatch(r"[A-Za-z0-9_.-]{1,96}",args.name):p.error("Invalid skill name")
 print(json.dumps(build(args.out,args.name),ensure_ascii=False))
if __name__=="__main__":main()
