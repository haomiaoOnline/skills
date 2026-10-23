# 完整操作手册

## 候选工作量拆解
在已解压/安装的Skill根目录运行：
```bash
python3 scripts/v2_cli.py --input "/authorized/requirements.xlsx" --output "/authorized/COSMIC-candidate.xlsx"
# 指定工作表
python3 scripts/v2_cli.py --input "source.xlsx" --sheet "需求明细" --output "candidate.xlsx"
# 非标准列名
python3 scripts/v2_cli.py --input "source.csv" --profile "custom-map.json" --output "candidate.xlsx"
```
`templates/profile.example.json` 展示字段映射。不要因一份只有 DOCX 原文的需求材料缺少 E/X/R/W 证据而虚构数据移动；当前DOCX读取属于**原文提取**，不是从零自动确认完整CFP。

## 结构检查
- 数据移动类型：E、X、R、W；每个有效移动的标准 CFP 与组织折算区分。
- `subprocess`、`data_group`、`attributes`分别跨建成的完整表严格去重。
- 额外交付比率为新增:复用:利旧 = 2:7:1，复用经验系数0.33，三级模块单过程，最多8真实移动/过程。
- 正式数据来自可靠FUR、软件块边界、过程触发、对象和开发分类依据，不得假造。
- 输出 `COSMIC工作量拆解` 与 `待核查与规则说明` 位于**同一个XLSX文件**内。

## 只有独立审核人员才能进行的最终签署
1. 业务审核人员核对真实来源、FUR和边界数据、开发分类，补全 `source_file`、`source_sha256`、`reviewer`、ISO `reviewed_at`、`review_status=approved`、`boundary_basis`、`movement_basis`。
2. 审核人员将至少32字节随机 HMAC 密钥保存到**仅自己能读取**的目录，禁止交给Agent或仓库。由审核人员本人执行：
   ```bash
   python3 scripts/v2_review.py --input reviewed.xlsx --output signed.xlsx --key-file /private/reviewer.key --source-root /approved/sources
   python3 scripts/v2_cli.py --input signed.xlsx --output COSMIC工作量拆解.xlsx --approval-key-file /private/reviewer.key --source-root /approved/sources
   ```
3. 修改原文来源或拆解行会使签名失效。签名只能验证内容与密钥一致，不能证明审核人的法律身份或FUR业务判断正确。

## CLI结果
`0`：工程门禁通过，可交用户业务终验；
`2`：**成功创建候选工作簿**，但尚无可承诺的正式CFP；
`1`：工程错误，如文件不存在、表头冲突、输出文件已存在、Python依赖缺失。

## MCP
在 Python 3.11 环境安装 `requirements-mcp.txt`，由服务运营者明确授权 `COSMIC_MCP_ROOT`，通过stdio启动 `scripts/v2_mcp.py`。提供 `cosmic_schema`、`cosmic_inspect`、`cosmic_generate_workload`。MCP不提供人工审批签名能力。
