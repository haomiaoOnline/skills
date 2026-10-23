# Changelog

## 公开个人Skills仓库目录迁移（2026-10-23）
- 通用 v2.0.3 Agent Skill 的 35 个正式发行文件迁入公开 `haomiaoOnline/skills/cosmic-materials-assistant/` 独立子目录。
- `skills.json` 成为未来个人 Skill 的统一目录；原私有开发仓库和旧客户专用资料不参与迁移。
- 仅替换公开仓库的路径/发布说明，不修改 COSMIC 功能逻辑与验收规则。

## v2.0.1 · 2026-10
- 通用COSMIC拆解引擎与安全交付基础，保持标准CFP和组织加权工作量分开。
- 增加来源SHA与审核签名绑定、跨Agent目录权限、公式防注入、输入缺失/重复核查、单XLSX输出。
- 提供CLI及MCP接口，发布ZIP不包含历史山东专用脚本。

## v2.0.3 · 2026-10
- 安装器优先使用已存在的 uv 创建 Python 虚拟环境和安装依赖；无 uv 时回退 pip，并提供有上限的超时/重试，避免自动安装长期无响应。
- 独立 Python 3.11 与 uv 完整安装验收通过，32 个发行包测试成功；保留 v2.0.2 既有Git标签与ZIP不修改。

## v2.0.2 · Agent onboarding, installer and GitHub · 2026-10
- 新增可交付给Agent的 `AGENTS.md`、`docs/AGENT_INSTALL.md`、公开使用与安全说明。
- 增加 `scripts/install_agent.py` 隔离自动安装入口和无数据依赖回归测试。
- GitHub远程同步默认采用私有仓库，公共售卖使用精选发行包而非历史开发库。
