#!/usr/bin/env python3
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
catalog_path = root / "skills.json"
data = json.loads(catalog_path.read_text(encoding="utf-8"))

assert data.get("schema_version") == 1, "schema_version must be 1"
skills = data.get("skills")
assert isinstance(skills, list) and skills, "skills must be a non-empty list"

required = {"id", "name", "path", "summary", "kind", "status", "tags"}
ids = set()
paths = set()

for item in skills:
    missing = required - item.keys()
    assert not missing, f"{item.get('id', '<unknown>')}: missing {sorted(missing)}"
    assert item["id"] not in ids, f"duplicate id: {item['id']}"
    assert item["path"] not in paths, f"duplicate path: {item['path']}"
    ids.add(item["id"])
    paths.add(item["path"])

    skill_dir = root / item["path"]
    assert skill_dir.is_dir(), f"missing skill directory: {item['path']}"
    assert isinstance(item["tags"], list), f"{item['id']}: tags must be a list"

    entrypoint = item.get("entrypoint")
    if entrypoint:
        assert (root / entrypoint).is_file(), f"missing entrypoint: {entrypoint}"

print(f"catalog ok: {len(skills)} skills")
