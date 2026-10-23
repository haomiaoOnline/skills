#!/usr/bin/env python3
"""Safe, non-interactive, local Agent Skill installer.

Install only the release manifest, never the developer repository or source data.
Requires Python 3.9+. Use --skip-deps only for offline/CI validation.
"""
import argparse,json,os,shutil,subprocess,sys,tempfile
from pathlib import Path
from build_release import FILES,ROOT

def default_target(agent):
    home=Path.home()
    base={"generic":home/".agents"/"skills","codex":home/".codex"/"skills",
          "claude":home/".claude"/"skills"}[agent]
    return base/"cosmic-materials-assistant-p0"

def install(target,with_mcp=False,skip_deps=False,python=None):
    target=Path(target).expanduser()
    if target.exists() or target.is_symlink():
        raise FileExistsError("Skill destination already exists; choose a fresh --target: "+str(target))
    executable=str(Path(python).expanduser()) if python else sys.executable
    if with_mcp:
        check=subprocess.run([executable,"-c",
               "import sys;sys.exit(0 if sys.version_info >= (3,10) else 4)"],
               check=False)
        if check.returncode:
            raise RuntimeError("MCP installer requires selected Python 3.10+; Python 3.11 recommended.")
    for name in FILES:
        if not (ROOT/name).is_file():
            raise FileNotFoundError("Incomplete source Skill package: "+name)
    target.parent.mkdir(parents=True,exist_ok=True)
    stage=Path(tempfile.mkdtemp(prefix=".cosmic-stage-",dir=target.parent))
    try:
        for name in FILES:
            destination=stage/name
            destination.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(ROOT/name,destination)
        if not skip_deps:
            uv=shutil.which("uv")
            if uv:
                subprocess.run([uv,"venv","--python",executable,str(stage/".venv")],
                               check=True,timeout=60)
            else:
                subprocess.run([executable,"-m","venv",str(stage/".venv")],
                               check=True,timeout=80)
            vpython=stage/".venv"/("Scripts/python.exe" if os.name=="nt" else "bin/python")
            depfile="requirements-mcp.txt" if with_mcp else "requirements.txt"
            if uv:
                subprocess.run([uv,"pip","install","--python",str(vpython),"-r",str(stage/depfile)],
                               check=True,timeout=120)
            else:
                subprocess.run([str(vpython),"-m","pip","install","--disable-pip-version-check",
                               "--retries","1","--timeout","8","-r",str(stage/depfile)],
                               check=True,timeout=120)
            subprocess.run([str(vpython),"-B","-m","unittest","discover","-s",str(stage/"tests"),
                            "-p","test_v2_*.py"],cwd=stage,check=True,timeout=90)
        if target.exists() or target.is_symlink():
            raise FileExistsError("Target appeared while installing; refusing to replace")
        stage.rename(target)
    except BaseException:
        shutil.rmtree(stage,ignore_errors=True)
        raise
    return {"status":"installed","location":str(target),"dependencies_installed":not skip_deps,
            "python":str(target/".venv"/("Scripts/python.exe" if os.name=="nt" else "bin/python")) if not skip_deps else None,
            "usage":"See AGENTS.md and docs/AGENT_INSTALL.md in the target directory"}

def main():
    p=argparse.ArgumentParser(description="Install portable COSMIC Skill in a clean Agent-owned directory")
    p.add_argument("--agent",choices=("generic","codex","claude"),default="generic")
    p.add_argument("--target",type=Path,help="Explicit Agent skill installation path; never overwritten")
    p.add_argument("--with-mcp",action="store_true",help="Include optional MCP SDK, requires Python 3.10+")
    p.add_argument("--skip-deps",action="store_true",help="Offline install: copy only; dependencies must be provided separately")
    p.add_argument("--python",help="Interpreter to use to create isolated virtualenv")
    a=p.parse_args()
    dest=a.target or default_target(a.agent)
    try:
        print(json.dumps(install(dest,a.with_mcp,a.skip_deps,a.python),ensure_ascii=False,indent=2))
    except Exception as ex:
        print(json.dumps({"status":"failed","reason":str(ex)},ensure_ascii=False),file=sys.stderr)
        return 1
    return 0
if __name__=="__main__":
    sys.exit(main())
