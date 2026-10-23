# COSMIC Materials Assistant

**通用 COSMIC 工作量拆解与质量核验 Agent Skill** · Python CLI · Optional MCP · One XLSX deliverable

A reusable tool for FUR-based functional-process / E-X-R-W movement review, semantic duplicates, 2:7:1 development category validation and an independent audit trail. The tool makes **no claim of official COSMIC certification**. Actual business FUR and approvals are required before reporting approved CFP.

## Give this document to an Agent for guided automatic setup

Give an Agent **`docs/AGENT_INSTALL.md` + the release ZIP** (or this repository if it has access). A coding Agent with terminal access can use `AGENTS.md`, inspect its Python environment, install to a user-approved directory, install dependencies in an isolated venv and run included tests.

```bash
# From the extracted release ZIP or the repository root
python3 scripts/install_agent.py --agent generic
# Or choose an explicit safe path for another Agent
python3 scripts/install_agent.py --target "$HOME/.agents/skills/cosmic-materials-assistant-p0"
```

Defaults: generic `~/.agents/skills/cosmic-materials-assistant-p0`, Codex `~/.codex/skills/cosmic-materials-assistant-p0`, Claude `~/.claude/skills/cosmic-materials-assistant-p0`. Consult the target Agent's actual installation guidelines. The installer **never overwrites an existing target**; dependencies and self-tests are installed/run unless `--skip-deps` is specified.

## Direct CLI quick start

```bash
python3 -m pip install -r requirements.txt
python3 scripts/v2_cli.py --input "project.xlsx" --output "candidate.xlsx"
```

`candidate.xlsx` contains an analysis worksheet and an embedded list of unmet rules. Exit code 2 means candidate/not formally approved. Normal Agents cannot approve CFP; **signing is performed independently on the reviewer's trusted device** per `docs/USAGE.md`.

## Included functionality

| Component | Behavior |
| --- | --- |
| Semantic field validation | Globally unique subprocess, data group and attributes across built rows; never tied to I/K/L positions |
| Business delivery policy | 2:7:1, 0.33 reuse weighting, one logical process per 3-level module, <=8 genuine movements |
| COSMIC-related review | E/X/R/W candidate validation based on real FUR and boundaries, distinct from extra delivery rules |
| Input | XLSX/CSV, semantic column-mapping profiles; DOCX/Markdown/TXT as **evidence-only candidates** |
| Output | One XLSX with detailed rows, reasons for blocking, and weighted work basis |
| Review integrity | Source-file SHA-256, signed row content, invalidation on source or row changes |
| Agent interfaces | `SKILL.md` + Python CLI, optional stdio MCP (three tools), constrained to an authorized workspace |

## Docs index
`AGENTS.md` · `docs/AGENT_INSTALL.md` · `docs/USAGE.md` · `docs/ARCHITECTURE.md` · `docs/SECURITY.md` · `docs/TROUBLESHOOTING.md` · `docs/REPOSITORY_POLICY.md` · `CHANGELOG.md` · `README_V2.md` · `SKILL.md`.

## Tested and licensed
Python 3.9+ CLI with `openpyxl` and `python-docx`; MCP requires compatible Python 3.11 and MCP SDK 1.x. Unit tests:

```bash
python3 -B -m unittest discover -s tests -p 'test_v2_*.py' -v
python3 scripts/build_release.py
```

MIT license covers **original** code and docs only, not third-party COSMIC method books or customer source data. This public monorepo folder contains only the curated portable Skill files. Historical client-specific material remains in a separate PRIVATE developer repository and is never imported here.

**Current release:** v2.0.3. The repository root may contain older customer-specific code for maintenance and tests; only the ZIP manifest is the generic product.
