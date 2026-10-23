# COSMIC 通用单XLSX交付合同 v2.0.1

## 权威分界
COSMIC V5 计量依据是真实软件边界、FUR、功能用户、功能过程和E/X/R/W数据移动，每有效移动1标准CFP。子过程/数据组/数据属性各自全表唯一，新增/复用/利旧2:7:1、复用系数0.33、三级模块单过程和每过程8条，是用户额外规定的通用交付要求，不能伪称官方要求。

## 统一文件
对外交付**一个** `COSMIC工作量拆解.xlsx`。Sheet 1完整写出FUR、过程、移动、标准CFP、开发类型、组织折算系数与每行折算工作量，Sheet 2包含全部阻断项、实际/目标开发类型比例及组织加权工作量基数。CLI的标准输出JSON供Agent读取而非交付。不得将独立的审计CSV/JSON作为客户交付内容。

退出码0=证据完整、独立审核签名及全部规则验证通过，仍需客户最终验收；2=候选阻断但一个工作簿已创建；1=执行错误。

## 安全与来源证据
- 无原始文件、文件SHA256不一致、人工签名缺失/过期、非法审核日期，均不能确认CFP。
- 来源 `source_file` 可相对 `--source-root`；`source_sha256` 必须匹配真实字节；`approval_signature` 对行语义字段及原始来源SHA进行HMAC-SHA256绑定。
- 独立审核人须在本人控制、Agent无法接触的目录保存密钥，用 `scripts/v2_review.py` 签名；再次运行 `scripts/v2_cli.py --approval-key-file` 核验。密钥签名不是国家认可的身份证明，也不能自动证明FUR本身正确。
- 不得将客户的 `=HYPERLINK(...)`、`=cmd(...)` 等文本直接输出为活动Excel公式。
- 禁止静默忽略非空数据行、重复表头或误选择其他Sheet；已有输出与任意邻接临时文件均不得覆盖。
- 外部Agent通过MCP只能访问运营者授权的COSMIC_MCP_ROOT目录。MCP不接受审批密钥，因此只能产生安全候选结果，正式审批仅由审核人本地进行。
- 需要后续迭代时，业务人员可修改前一版唯一工作簿，再生成新版本。所有改动后旧签名自动失效，必须重新签名，不能把批准状态的文字当真实核验。

## 操作
```bash
python3 scripts/v2_cli.py --input customer.xlsx --sheet 功能需求 --output candidate.xlsx
python3 scripts/v2_review.py --input reviewed.xlsx --output signed.xlsx --key-file reviewer.key --source-root /verified/sources
python3 scripts/v2_cli.py --input signed.xlsx --output COSMIC工作量拆解.xlsx --approval-key-file reviewer.key --source-root /verified/sources
```
完整说明在 `SKILL.md` 与 `README_V2.md`。不使用历史特定客户生成器、固定列号、固定行数或额外侧车报表。
