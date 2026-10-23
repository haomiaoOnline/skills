# Agent 自动安装与使用交接（可直接发给任何有本地终端能力的 Agent）

**请 Agent 执行本页步骤，不需要用户懂 Python；遇到登录、权限或外部安装阻碍时仅报告必要操作。**

## 交付给 Agent 的材料
1. 此文档 `docs/AGENT_INSTALL.md`。
2. 同版本的 `cosmic-materials-assistant-v2.0.3.zip`，**或** Agent 可访问的本项目 Git 仓库。
3. 如需马上分析业务材料，附上用户授权的 DOCX/XLSX/CSV 文件，并指明希望的**候选结果输出目录**。无数据时也能完成安装和健康检查。

只给本文档而不给源码、ZIP 或访问仓库权限，Agent **无法可靠完成安装**，必须先获得软件包。Agent 不得伪造安装结果或向互联网上传客户源文件。

## Agent 的自动化执行步骤
1. 确认宿主系统能执行 `python3`，版本至少 3.9；MCP 推荐 3.11。确认目标安装目录为用户已授权的路径。若已经存在，先停止，不要清理/覆盖旧安装。
2. 如果是 ZIP，安全解压并切换到其根目录，确认至少存在 `SKILL.md`、`AGENTS.md`、`scripts/install_agent.py`、`requirements.txt` 和 `scripts/v2_cli.py`。
3. 推荐执行：
   ```bash
   python3 scripts/install_agent.py --agent generic
   # 已安装 uv 时优先快速安装；或显式指定 Python 3.11：
   # python3 scripts/install_agent.py --agent generic --python /path/to/python3.11
   ```
   目标 Agent 有专属技能目录时，使用 `--agent codex` 或 `--agent claude`；未知宿主使用 `--target "/approved/agent/skills/cosmic-materials-assistant-p0"`。自动安装程序**只复制发布清单**，创建隔离 venv，安装所需依赖和运行测试；目标已存在就拒绝覆盖。
4. 观察退出码和 JSON `status`。只有 `status=installed` 才能报告安装成功。缺网络时可执行 `--skip-deps`，但只能报告“文件已安装，依赖和功能尚未验证”。
5. 切换到安装目录，调用安装 JSON 返回的 Python：
   ```bash
   .venv/bin/python -B -m unittest discover -s tests -p 'test_v2_*.py' -v
   ```
   Windows 路径改用 `.venv\\Scripts\\python.exe`。确认全部测试通过。
6. 用户提供源材料时，运行：
   ```bash
   .venv/bin/python scripts/v2_cli.py --input "/authorized/project.xlsx" --output "/authorized/COSMIC-candidate.xlsx"
   ```
   - Exit 0：已具备所有签名与核查条件，**仍须业务方最终验收**。
   - Exit 2：**成功生成候选结果**，工作簿中含待核查事项；不能宣称正式CFP成功。
   - Exit 1：执行错误；查看错误说明修复环境/字段映射。
7. 对不同 Excel 表头与工作表使用 `--profile` 和 `--sheet`；不能为运行通过改写客户真实FUR或强行凑比例。
8. 人工正式审批不由 Agent 执行：审核人本机独立持有密钥、验证SHA和业务证据，按 `docs/USAGE.md` 执行 `v2_review.py`，不能向 Agent 分享私钥。
9. MCP 可选：用 Python3.11 安装 `--with-mcp`；设 `COSMIC_MCP_ROOT` 为**明确授权目录**后启动 `scripts/v2_mcp.py` stdio；不配置时应拒绝访问。
10. 回报安装目录、Python版本、依赖是否已安装、测试数、执行命令和结果状态；不要回报或展示任何密钥/私有客户数据。

## 正确的成功定义
- **安装验收**：文件齐全、依赖安装、测试通过。
- **候选工作量输出**：一个XLSX，含拆解和待审核说明。
- **正式业务CFP核验**：独立审核人签名+真实来源材料一致性+所有门禁通过，仍由客户最终验收。

## Agent 专用复制提示词

> 你是我的本地软件安装助手。请阅读随附的 AGENT_INSTALL.md 和 AGENTS.md，读取同版本 Skill ZIP 或可访问的项目仓库，检查 Python 版本和授权目录，按文档使用 scripts/install_agent.py 创建隔离安装及安装依赖，执行完整的 v2 回归测试，检查 SKILL.md 和 CLI 入口。不要覆盖已有文件、不上传我的工作资料、不访问私钥。若安装成功，告诉我安装目录、验收结果及示例命令；若因权限、Python版本或网络失败，请告诉我具体阻碍和最小手工操作。不得将候选 CFP 宣传为已审核。
