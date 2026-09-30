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

CORE_DOCS = [
    "做平台要办哪些证.md",
    "家庭应急装备清单.md",
    "生物钟和夜班.md",
    "结婚划不划算.md",
    "遇到陌生人出事该不该停.md",
]

EXPECTED_SCORING_MARKERS = [
    "const COST_W = { money:{'0':0,'少':1,'多':2}, time:{'少':0,'中':1,'多':2}, will:{'否':0,'些':1,'是':2} };",
    "e.ratio = e.level === '大' ? (e.cs === 0 ? '极高' : (e.cs <= 2 ? '高' : '一般'))",
    ": e.level === '中' ? (e.cs === 0 ? '高' : '一般') : '一般';",
]

MAINTENANCE_REPLACEMENTS = [
    (
        "https://www.gov.cn/zwgk/2006-06/27/content_320458.htm",
        "https://www.nhc.gov.cn/bgt/pw10609/200702/6faca6dc60a248ab963bd7477bf65a5e.shtml",
    ),
    (
        "广东省疾病预防控制中心. 艾滋病检测窗口期科普. <https://cdcp.gd.gov.cn/jkjy/kpydjwjxz/content/post_3441820.html>",
        "中国疾病预防控制中心. HIV 检测窗口期资料（依据 WS 293—2019）. <https://ncaids.chinacdc.cn/zlk/clly/guangds/202508/P020250820524907154831.pdf>",
    ),
    (
        "广东省疾控中心的口径是：核酸检测约 1 周、第四代抗原抗体联合检测约 2 周、第三代抗体检测约 3 周可以检出。建议至少 2 周后再查，间隔 2 至 4 周复查一次。最后一次高危行为满 3 个月后，99.99% 以上可以排除感染。",
        "中国疾控资料给出的现有诊断技术窗口期约为：核酸 1 周、抗原 2 周、抗体 3 周。具体该在什么时候复查，要结合暴露时间、所用检测方法和医生建议。",
    ),
    (
        "<https://jcy.heyuan.gov.cn/node/142>（河源市人民检察院转载）",
        "<https://www.gd.jcy.gov.cn/xwzx/ajjj/201704/t20170411_1975028.shtml>",
    ),
]

FORBIDDEN_SNAPSHOT_MARKERS = [
    "4.mcyyy.com",
    "ads/mcyyy.webp",
    "ads/mcyyy-side.webp",
    "ads/wechat-reward.png",
]


def run(*args: str, cwd: Path | None = None) -> str:
    return subprocess.check_output(args, cwd=cwd, text=True).strip()


def validate_source(src: Path) -> None:
    required = [
        src / "book",
        src / "docs",
        src / "index.html",
        src / "LICENSE",
    ]
    missing = [str(p) for p in required if not p.exists()]
    if missing:
        raise SystemExit("invalid source checkout, missing: " + ", ".join(missing))

    index_text = (src / "index.html").read_text(encoding="utf-8")
    missing_scoring = [m for m in EXPECTED_SCORING_MARKERS if m not in index_text]
    if missing_scoring:
        raise SystemExit(
            "upstream scoring formula changed; review before updating snapshot"
        )


def apply_maintenance_replacements(snapshot: Path) -> int:
    changed = 0
    for path in [*sorted((snapshot / "book").glob("*.md")), *sorted((snapshot / "docs").glob("*.md"))]:
        text = path.read_text(encoding="utf-8")
        updated = text
        for old, new in MAINTENANCE_REPLACEMENTS:
            updated = updated.replace(old, new)
        if updated != text:
            path.write_text(updated, encoding="utf-8")
            changed += 1
    return changed


def validate_snapshot(snapshot: Path) -> None:
    expected_docs = set(CORE_DOCS)
    actual_docs = {p.name for p in (snapshot / "docs").glob("*.md")}
    if actual_docs != expected_docs:
        raise SystemExit(
            f"unexpected snapshot docs: expected {sorted(expected_docs)}, got {sorted(actual_docs)}"
        )

    forbidden_paths = [
        snapshot / "README.md",
        snapshot / "index.html",
        snapshot / "ads",
    ]
    present = [str(p) for p in forbidden_paths if p.exists()]
    if present:
        raise SystemExit("forbidden presentation assets copied: " + ", ".join(present))

    for path in snapshot.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in {".md", ".json", ".txt", ".html"}:
            continue
        text = path.read_text(encoding="utf-8")
        for marker in FORBIDDEN_SNAPSHOT_MARKERS:
            if marker in text:
                raise SystemExit(f"forbidden promotional marker {marker!r} in {path}")


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
    for name in CORE_DOCS:
        doc = src / "docs" / name
        if not doc.is_file():
            raise SystemExit(f"missing core upstream document: {doc}")
        shutil.copy2(doc, tmp_dest / "docs" / name)
    shutil.copy2(src / "LICENSE", tmp_dest / "LICENSE")
    maintenance_files_changed = apply_maintenance_replacements(tmp_dest)
    validate_snapshot(tmp_dest)

    meta = {
        "name": "高性价比人生指南",
        "repository": DEFAULT_REPO.removesuffix(".git"),
        "commit": commit,
        "retrieved_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "license_file": "LICENSE",
        "snapshot_scope": ["book/", *[f"docs/{name}" for name in CORE_DOCS], "LICENSE"],
        "excluded_upstream_presentation": ["README.md", "index.html", "ads/", "docs/引用对照.md"],
        "snapshot_policy": "Filtered distribution: core decision content is retained; promotional, donation, star-history, site UI and internal maintenance assets are excluded. Confirmed-dead evidence links may be repointed to current official sources.",
        "maintenance_files_changed": maintenance_files_changed,
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
