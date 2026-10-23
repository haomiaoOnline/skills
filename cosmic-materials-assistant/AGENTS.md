# Instructions for any coding Agent — COSMIC Materials Assistant

This is a portable **local AI Agent Skill**. The project's only customer-facing result is **one COSMIC workload XLSX**, never extra review/JSON/CSV deliverables. You must not pretend to have certified COSMIC measures or sign as the customer's reviewer.

## Agent: install this Skill from a ZIP or cloned repository

1. Read `docs/AGENT_INSTALL.md` then `README.md` and `SKILL.md` **before** running scripts.
2. Confirm your host allows local file writes, Python execution, and optional dependency downloads. If it does not, explain that limitation rather than claiming success. Do not require OpenAI/WebCodex plugins.
3. Choose an **authorized installation target** (default `~/.agents/skills/cosmic-materials-assistant-p0` for generic Agent Skills; choose `--agent codex` or `--agent claude` only when appropriate). Never install into the user's project/source data folder.
4. Run `python3 scripts/install_agent.py --agent generic` from the unpacked ZIP. It copies **only the curated release manifest** into a new path, creates an isolated Python virtual environment, installs dependencies, and runs tests. The target is never overwritten. If already installed, inspect it; never silently remove or replace a user's installation.
5. If your environment is offline, use `--skip-deps`, report that dependencies are not installed and functionality is not yet verified. Running tests or activating tools still requires dependencies.
6. Read the output JSON `status`, `location`, and `python`. Only report success after `status=installed` and the exit status is 0.
7. To try it, use `python3 scripts/v2_cli.py --input /approved/input.csv --output /approved/candidate.xlsx` from the installed Skill. Exit 2 means **a candidate was generated but is not approved**, not an installation error. Exit 1 means execution failed.
8. If using MCP, install with `--with-mcp` in a Python 3.11 environment, configure `COSMIC_MCP_ROOT` to a **user-approved working folder**, then launch `scripts/v2_mcp.py`. MCP is for generating candidates only.
9. **Never** request, read, create, upload or store the human reviewer's private signing key in an Agent-readable directory. Final CFP approvals require independently held credentials, real evidence and real human judgment.
10. Never access, publish, upload or commit customer requirements, workbook data, credentials, or local private directories without the owner's authorization.

## Default non-negotiable delivery contract

- Three independent globally unique semantic fields: `subprocess` (子过程), `data_group` (数据组), `attributes` (数据属性), regardless of worksheet letters.
- Actual new/reused/legacy development classification ratio 2:7:1; organizational weights 1/0.33/0, **not** official CFP weights.
- One genuine logical functional process per full Level1/Level2/Level3 module; no more than eight genuine E/X/R/W movements per process; don't fabricate to satisfy formatting constraints.
- A document of requirements alone only yields **a candidate**; every officially counted movement must be supported by real FUR, software boundary and independent reviewer-controlled row signature, which is not a legal identity certificate.

## Repository scope
`scripts/v2_*.py`, `scripts/install_agent.py` and the 2.0.x documentation form the generic product. This public subdirectory contains only vetted generic Skill files. Do not fetch legacy customer code or historical private documents from separate repositories.

## Useful references
- `docs/AGENT_INSTALL.md` — agent-driven installation
- `docs/USAGE.md` — candidate workflow and human sign-off
- `docs/ARCHITECTURE.md` — module responsibilities
- `docs/SECURITY.md` — key custody and GitHub publishing protection
- `docs/TROUBLESHOOTING.md` — failure diagnosis
- `CHANGELOG.md` — releases
