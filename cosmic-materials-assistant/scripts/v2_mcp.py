#!/usr/bin/env python3
"""Optional MCP stdio adapter for generic COSMIC v2 tools.

No WebCodex requirement; server startup requires external package 'mcp'.
The library-level inspect/generate functions are testable without it.
"""
from __future__ import annotations
import json
import os
from pathlib import Path
import v2_cli,v2_core,v2_io

def _authorized(path,output=False):
    """Grant least privilege under operator-owned COSMIC_MCP_ROOT only."""
    base=os.getenv("COSMIC_MCP_ROOT")
    if not base:
        raise PermissionError("Set COSMIC_MCP_ROOT to an explicitly authorized workspace before starting MCP")
    root=Path(base).expanduser().resolve(strict=True)
    location=Path(path).expanduser().resolve(strict=not output)
    if location != root and root not in location.parents:
        raise PermissionError("MCP file access outside authorized workspace")
    if output and (location.exists() or location.is_symlink()):
        raise FileExistsError("Refusing existing output")
    return location


def inspect(input_path,sheet=None,profile=None):
    cfg={}
    if profile:
        cfg=json.loads(_authorized(profile).read_text(encoding="utf8"))
        if cfg.get("policy") not in (None,v2_core.POLICY_VERSION):
            raise ValueError("Unsupported policy")
    rows=v2_io.read_source(_authorized(input_path),sheet,cfg.get("column_mapping"))
    result=v2_core.validate(rows)
    return {"schema":result["schema"],"policy":result["policy"],
            "rows":len(rows),"ready":result["passed"],
            "issue_total":len(result["issues"]),"issues_preview":result["issues"][:25],
            "note":"This is an inspection only; not a human approval or CFP certification"}

def generate(input_path,output_path,sheet=None,profile=None,qualify_with_process=False):
    """Produces exactly one workbook, with issues embedded in the same XLSX."""
    return v2_cli.run(_authorized(input_path),_authorized(output_path,True),sheet,
                      _authorized(profile) if profile else None,qualify_with_process)

def schema():
    return {"semantic_fields":v2_io.SEMANTIC_COLUMNS,
            "default_policy":v2_core.sample_profile(),
            "single_deliverable":".xlsx","supported_inputs":["csv","xlsx","xlsm","docx","md","txt"],
            "status":["READY_FOR_USER_ACCEPTANCE","BLOCKED_CANDIDATE_ONLY"]}

def server():
    if not os.getenv("COSMIC_MCP_ROOT"):
        raise PermissionError("COSMIC_MCP_ROOT is mandatory for MCP server")
    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError as exc:
        raise RuntimeError("Optional MCP server requires: pip install -r requirements-mcp.txt") from exc
    instance=FastMCP("cosmic-materials-assistant-v2")
    instance.tool(name="cosmic_inspect")(inspect)
    instance.tool(name="cosmic_generate_workload")(generate)
    instance.tool(name="cosmic_schema")(schema)
    return instance

if __name__=="__main__":
    server().run(transport="stdio")
