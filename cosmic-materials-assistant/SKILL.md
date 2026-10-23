---
name: cosmic-materials-assistant-p0
description: 通用COSMIC工作量拆解Skill。按语义字段对子过程/数据组/数据属性全表去重，执行2:7:1、0.33、三级模块单过程和8移动规则；每条正式CFP必须有真实来源文件SHA和独立审核人签名，最终只交付一份XLSX。
---

# COSMIC Materials Assistant v2.0.3 · Agent 自动安装与交付版

## 可用场景
其他用户、项目、Agent可使用自己的CSV/XLSX/DOCX/Markdown材料；**不得依赖山东项目、固定I/K/L列号、原始客户文件、具体绝对路径或固定行数**。发布包的使用说明、脚本与依赖须全部位于同一ZIP中。

先读 `references/03-generation-playbook.md`、`references/05-output-contract.md`、`references/11-v2-universal.md`。

## 规则边界
官方COSMIC V5的重点是真实FUR、软件块边界、独立功能过程、有效E/X/R/W数据移动（每条1标准CFP）。下面的要求是**额外的通用交付合同，不是官方条文**：
- 对**子过程、数据组、数据属性三个语义字段**分别跨所有已建设移动严格规范化去重；跨过程也不得豁免。不能通过编造功能过程、伪造数据组、数字后缀绕过。
- 开发类型新增/复用/利旧的实际比例为2:7:1；权重1/0.33/0只用于组织折算工作量，与标准CFP独立。真实开发分类需独立证据，不能按预期配比编造实施情况。
- 一条完整三级模块路径对应一个逻辑功能过程，每过程最多8条真实移动、需要真实触发E和合法后续移动。如原始FUR确有多个独立过程，交由业务方修订三级模块归属后重审，不在同一模块偷偷增加过程。
- 只有真实需求中确实出现不同功能过程、且处于不同三级模块时，`--qualify-with-process` 可生成**候选展示限定**。一切受改动行撤销旧签名和CFP并重审；不能由模型自行认定过程或移动。
- 无法找到真实需求、边界、移动依据、业务审核和复核证据时，只能生成候选，不得虚报“全部CFP已通过”。

## CLI与唯一交付工作簿
要求Python 3.9+，安装 `python3 -m pip install -r requirements.txt`。只会创建一个新XLSX，绝不覆盖输入或已有结果：
```bash
python3 scripts/v2_cli.py --input "任意项目需求.xlsx" --output "候选工作量拆解.xlsx"
python3 scripts/v2_cli.py --input "客户需求.csv" --output "候选工作量拆解.xlsx"
python3 scripts/v2_cli.py --input "需求原文.docx" --output "原文证据候选.xlsx"
python3 scripts/v2_cli.py --input "不同表头.xlsx" --sheet "项目模块清单" --profile "字段映射.json" --output "候选工作量拆解.xlsx"
```
Excel的 `COSMIC工作量拆解` Sheet含：标准CFP、真实来源、审核字段、开发类型、逐行系数与加权工作量。其 `待核查与规则说明` Sheet内嵌所有阻断与项目汇总。**对客户最终只提供一个COSMIC工作量拆解XLSX**，不另交付审核CSV、JSON或多个工作簿。控制台JSON仅供Agent解析。DOCX/Markdown只提取真实原文为候选，不自动推断E/R/W/X或正式CFP。

## 审核人独立签名：正式CFP不可由Agent自批
`review_status=approved` 只是可编辑文本，**不能证明审核**。每行必须有 `source_file`（真实来源文件）和对应 `source_sha256`、原文与定位、边界依据、移动依据、审核人和合法ISO日期。
审核人要**在独立受信设备创建并保管至少32字节随机密钥**，不能把密钥交给Agent、上传仓库、打包或放入其可访问的目录。审核人实际核对材料后运行：
```bash
python3 scripts/v2_review.py --input "业务已审核.xlsx" --output "已签名.xlsx" --key-file "/private/reviewer.key" --source-root "/verified/sources"
python3 scripts/v2_cli.py --input "已签名.xlsx" --output "COSMIC工作量拆解.xlsx" --approval-key-file "/private/reviewer.key" --source-root "/verified/sources"
```
签名绑定当前行所有语义字段与来源SHA；行或源文件改动立即阻断。HMAC仅证明**持有密钥**，不提供人员身份证明、官方COSMIC认证、业务真实性的自动判定。若签名或来源验证不完整，生成的仍只能是候选。
CLI退出码：0=规则及签名核验通过，**仍需业务最终验收**；2=只生成候选并保留问题；1=工程故障。

## 第三方 Agent / MCP 使用
MCP可选：Python 3.10+环境安装 `requirements-mcp.txt`，配置 `COSMIC_MCP_ROOT` 指向运营者明确批准的单一工作目录，再启动 `python3 scripts/v2_mcp.py`（stdio）。MCP仅能检查和生成**候选**，不得接触审核人密钥或自动批准CFP。MCP未配置目录即拒绝访问，目录外路径拒绝。
详情见 `README_V2.md`。

**第三方Agent自动安装**：请首先阅读根目录 `AGENTS.md` 和 `docs/AGENT_INSTALL.md`，提供同版本ZIP或授权的Git仓库；从发行包根目录运行 `python3 scripts/install_agent.py --agent generic`。该脚本仅安装受控清单、隔离虚拟环境并自测；已存在目标目录时拒绝覆盖。无法运行终端的纯聊天Agent不能承诺已安装。

业务修改、来源文件变化、功能过程调整后，前次签名作废并重新审核；前一版本XLSX可作为下一轮输入。只向用户交付最终那个工作簿。

## 版本
v2.0.0已保留Git标签与历史安装包；v2.0.1加强公式防注入、输入完整性、审批指纹、来源校验、MCP工作区权限和单文件加权结果。不进行基于山东项目数据的特殊条件分支。
