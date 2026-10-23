# COSMIC Materials Assistant v2.0.3 — Portable Third-Party Skill

完整包支持不依赖WebCodex的CLI，默认Python 3.9+。第三方Agent按 `AGENTS.md` 与 `docs/AGENT_INSTALL.md` 运行 `python3 scripts/install_agent.py --agent generic` 可在获授权目录隔离安装，并自动检测依赖和测试；不具备本地终端或文件访问权限的Agent需要先获得授权。仅依赖`requirements.txt`中列出的库（DOCX要求python-docx，XLSX要求openpyxl）。第三方可以单独解压、运行测试和从自己的资料生成一个工作量拆解 XLSX。

## 快速开始

```bash
python3 -m pip install -r requirements.txt
python3 scripts/v2_cli.py --input "客户需求.xlsx" --output "候选.xlsx"
python3 scripts/v2_cli.py --input "客户需求.csv" --profile "列映射.json" --output "候选.xlsx"
python3 scripts/v2_cli.py --input "需求.docx" --output "原文待审核.xlsx"
python3 -B -m unittest discover -s tests -p 'test_v2_*.py' -v
```

缺少真实源文件、校验SHA、独立人工签名时，生成一个候选文件，返回退出码2、零已批准CFP。绝不将“review_status=approved”字样直接当作可信审批。绝不改动来源文件。一次命令只生成一个工作簿，质量问题与开发类型比例在同一工作簿内的第二Sheet。

## 由独立审核人签署

业务审核人保管密钥并验证真实FUR、软件边界及E/X/R/W与开发分类。在审核后的工作簿中填写：`source_file`、`source_sha256`、`source_locator`、`evidence_text`、`boundary_basis`、`movement_basis`、`review_status=approved`、`reviewer`、`reviewed_at`。原始文件SHA可使用系统 `sha256sum` 或 `shasum -a256` 获取；路径可相对 `--source-root`。

使用审核人**本地可信环境**生成至少32字节随机密钥，例如 `python3 -c 'import secrets; open("reviewer.key","wb").write(secrets.token_bytes(32))'`，随后保存在Agent**无法读取**的受限目录（不应在聊天发送密钥、不要进Git）；首次签名与再次核验：

```bash
python3 scripts/v2_review.py --input "已人工复核.xlsx" --output "已签名.xlsx" --key-file "/private/reviewer.key" --source-root "/verified/sources"
python3 scripts/v2_cli.py --input "已签名.xlsx" --output "COSMIC工作量拆解.xlsx" --approval-key-file "/private/reviewer.key" --source-root "/verified/sources"
```

仅最终 `COSMIC工作量拆解.xlsx` 对外交付；运行过程中产生的候选与签名版由审核人内部保留。输入修改后重新签名，否则老签名被判为无效。密钥签名无法核验审核人真实身份，不能替代客户签章或业务真实性审核。

## 可选Agent/MCP

MCP Python SDK v1使用Python 3.10+。安装 `requirements-mcp.txt`（固定MCP主版本1，不能安装2.x后仍沿用FastMCP接口）。**只有运营者已明确批准该目录时**：

```bash
export COSMIC_MCP_ROOT="/path/to/approved/workspace"
python3 -m pip install -r requirements-mcp.txt
python3 scripts/v2_mcp.py
```

默认stdio接口：`cosmic_schema`、`cosmic_inspect`、`cosmic_generate_workload`。仅可访问配置目录内文件，不提供密钥认证接口，不允许擅自读其他路径、写已有文件，所有Agent侧生成仅候选。其他MCP宿主的实时接入必须在对应系统单独验收；单元测试通过不等于所有宿主已真实连接。

## 版本和完整性
构建：`python3 scripts/build_release.py`。可以从v2.0.0 Git标签回滚；本地项目的客户专用历史资料、范例和外部规范PDF都不随通用ZIP发布。阅读 `references/03-generation-playbook.md` 与 `references/05-output-contract.md` 可执行全部示例，不再依赖旧脚本。源代码分发条款见随包 LICENSE；官方COSMIC内容仅以引用和描述为主，未附任何官方PDF或声称有官方认证。
