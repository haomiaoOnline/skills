#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "assets" / "upstream"
DEFAULT_REPO = "https://github.com/eternity4719/HowToLiveBetter.git"


def run(*args: str, cwd: Path | None = None) -> str:
    return subprocess.check_output(args, cwd=cwd, text=True).strip()


def validate_source(src: Path) -> None:
    required = [
        src / "book",
        src / "docs",
        src / "README.md",
        src / "index.html",
        src / "LICENSE",
    ]
    missing = [str(p) for p in required if not p.exists()]
    if missing:
        raise SystemExit("invalid source checkout, missing: " + ", ".join(missing))


def copy_tree(src: Path) -> str:
    validate_source(src)
    commit = "unknown"
    try:
        commit = run("git", "rev-parse", "HEAD", cwd=src)
    except Exception:
        pass

    tmp_dest = DEST.with_name(DEST.name + ".new")
    if tmp_dest.exists():
        shutil.rmtree(tmp_dest)
    tmp_dest.mkdir(parents=True)

    shutil.copytree(src / "book", tmp_dest / "book")
    (tmp_dest / "docs").mkdir()
    for doc in sorted((src / "docs").glob("*.md")):
        shutil.copy2(doc, tmp_dest / "docs" / doc.name)
    for name in ["README.md", "index.html", "LICENSE"]:
        shutil.copy2(src / name, tmp_dest / name)

    meta = {
        "name": "高性价比人生指南",
        "repository": DEFAULT_REPO.removesuffix(".git"),
        "commit": commit,
        "retrieved_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "license_file": "LICENSE",
        "note": "Bundled snapshot for deterministic local retrieval. Current facts may require fresh official verification."
    }
    (tmp_dest / "SOURCE.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    backup = DEST.with_name(DEST.name + ".bak")
    if backup.exists():
        shutil.rmtree(backup)
    if DEST.exists():
        DEST.rename(backup)
    tmp_dest.rename(DEST)
    if backup.exists():
        shutil.rmtree(backup)
    return commit


def main() -> int:
    parser = argparse.ArgumentParser(description="Update bundled HowToLiveBetter snapshot.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--source", type=Path, help="existing local checkout")
    group.add_argument("--remote", action="store_true", help="clone latest upstream main branch")
    args = parser.parse_args()

    if args.source:
        commit = copy_tree(args.source.expanduser().resolve())
        print(f"updated from local source at commit {commit}")
        return 0

    with tempfile.TemporaryDirectory(prefix="hltb-update-") as td:
        src = Path(td) / "repo"
        subprocess.check_call(["git", "clone", "--depth", "1", DEFAULT_REPO, str(src)])
        commit = copy_tree(src)
        print(f"updated from remote at commit {commit}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
