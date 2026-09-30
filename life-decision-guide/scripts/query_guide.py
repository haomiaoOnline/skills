#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOOK_DIR = ROOT / "assets" / "upstream" / "book"

ENTRY_RE = re.compile(r"^###\s+(\d+)\.\s+(.+?)\s*$")
SECTION_RE = re.compile(r"^(\d+)-(.+)\.md$")
COST_RE = re.compile(r"<!--\s*成本标签:\s*(.*?)\s*-->")
FIELD_RE = re.compile(r"^- (成本|说人话|收益|证据等级|来源|备注)：(.*)$")


def load_entries() -> list[dict]:
    entries: list[dict] = []
    if not BOOK_DIR.exists():
        raise FileNotFoundError(f"book directory not found: {BOOK_DIR}")

    for path in sorted(BOOK_DIR.glob("*.md")):
        sm = SECTION_RE.match(path.name)
        section = int(sm.group(1)) if sm else None
        section_title = sm.group(2) if sm else path.stem
        lines = path.read_text(encoding="utf-8").splitlines()

        starts: list[tuple[int, int, str]] = []
        for i, line in enumerate(lines):
            m = ENTRY_RE.match(line)
            if m:
                starts.append((i, int(m.group(1)), m.group(2).strip()))

        for idx, (start, item_no, title) in enumerate(starts):
            end = starts[idx + 1][0] if idx + 1 < len(starts) else len(lines)
            block_lines = lines[start:end]
            block = "\n".join(block_lines).strip()
            fields: dict[str, str] = {}
            cost_tags = ""
            for line in block_lines:
                cm = COST_RE.search(line)
                if cm:
                    cost_tags = cm.group(1).strip()
                fm = FIELD_RE.match(line)
                if fm:
                    fields[fm.group(1)] = fm.group(2).strip()

            entries.append(
                {
                    "section": section,
                    "section_title": section_title,
                    "item": item_no,
                    "title": title,
                    "file": str(path.relative_to(ROOT)),
                    "line": start + 1,
                    "cost_tags": cost_tags,
                    "cost": fields.get("成本", ""),
                    "human": fields.get("说人话", ""),
                    "benefit": fields.get("收益", ""),
                    "evidence": fields.get("证据等级", ""),
                    "source": fields.get("来源", ""),
                    "note": fields.get("备注", ""),
                    "block": block,
                }
            )
    return entries


def searchable_text(e: dict) -> str:
    return "\n".join(
        [
            e["title"],
            e["section_title"],
            e["cost_tags"],
            e["cost"],
            e["human"],
            e["benefit"],
            e["evidence"],
            e["source"],
            e["note"],
        ]
    ).lower()


def score_entry(e: dict, terms: list[str]) -> int:
    title = e["title"].lower()
    human = e["human"].lower()
    benefit = e["benefit"].lower()
    note = e["note"].lower()
    source = e["source"].lower()
    section_title = e["section_title"].lower()

    score = 0
    for t in terms:
        if t in title:
            score += 8
        if t in section_title:
            score += 5
        if t in human:
            score += 4
        if t in benefit:
            score += 3
        if t in note:
            score += 2
        if t in source:
            score += 1
    return score


def excerpt(e: dict, limit: int = 240) -> str:
    text = e["human"] or e["benefit"] or e["note"] or e["title"]
    text = re.sub(r"\s+", " ", text).strip()
    return text if len(text) <= limit else text[: limit - 1] + "…"


def list_sections(entries: list[dict]) -> None:
    seen = {}
    for e in entries:
        seen[e["section"]] = e["section_title"]
    for sec in sorted(k for k in seen if k is not None):
        print(f"{sec:02d}\t{seen[sec]}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Search the bundled 高性价比人生指南 snapshot deterministically."
    )
    parser.add_argument("terms", nargs="*", help="search terms")
    parser.add_argument("--section", type=int, help="restrict to one section number")
    parser.add_argument("--mode", choices=["any", "all"], default="any")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--json", action="store_true", help="emit JSON")
    parser.add_argument("--full", action="store_true", help="include full matched entry")
    parser.add_argument("--list-sections", action="store_true")
    args = parser.parse_args()

    try:
        entries = load_entries()
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 2

    if args.list_sections:
        list_sections(entries)
        return 0

    if not args.terms:
        parser.error("provide at least one search term, or use --list-sections")

    terms = [t.lower().strip() for t in args.terms if t.strip()]
    if args.section is not None:
        entries = [e for e in entries if e["section"] == args.section]

    matches = []
    for e in entries:
        hay = searchable_text(e)
        checks = [t in hay for t in terms]
        ok = all(checks) if args.mode == "all" else any(checks)
        if not ok:
            continue
        item = dict(e)
        item["score"] = score_entry(e, terms)
        item["excerpt"] = excerpt(e)
        if not args.full:
            item.pop("block", None)
        matches.append(item)

    matches.sort(key=lambda x: (-x["score"], x["section"] or 999, x["item"]))
    matches = matches[: max(1, args.limit)]

    if args.json:
        print(json.dumps(matches, ensure_ascii=False, indent=2))
    else:
        for e in matches:
            print(
                f"[{e['score']:02d}] 第{e['section']}节第{e['item']}条 "
                f"{e['title']} | 证据 {e['evidence'] or '未知'}"
            )
            print(f"  {e['excerpt']}")
            print(f"  {e['file']}:{e['line']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
