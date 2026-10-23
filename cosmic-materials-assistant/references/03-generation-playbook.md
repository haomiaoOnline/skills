# 通用 COSMIC 数据移动拆解指南

本文件只描述发布包中存在的工具。COSMIC V5 的数据移动语义与用户规定的额外交付合同应区别对待。

## 建立真实材料
1. 明确被计量软件块边界、功能用户、独立触发事件、功能过程及其来源条款。
2. 一条真实E/X/R/W移动为一行，记下实际数据组、属性、FUR原文、来源文件路径与SHA256、边界及具体移动依据。仅凭动词不可推断R/W或X。
3. 按语义字段“子过程/数据组/数据属性”各自全表规范化严格不重复；只能用在真实FUR中确有证据的业务上下文区分，不能凭空增加过程、对象或移动。
4. 新增/复用/利旧比率2:7:1及折算系数1/0.33/0是额外交付合同，不影响每条真实合法移动1标准CFP。
5. 每个三级模块完整路径对应一个逻辑功能过程，每过程最多8条实际移动。若真实FUR支持多个独立过程，必须由业务方重新确认三级模块归属，不能在同一三级模块直接增设过程来规避去重。只有一个真实触发E，后续移动的性质需边界证据。
6. 不允许没有原始FUR、实际边界、真实设计及审核证据的候选条目计入已批准CFP。

## 单文件与审核工作流
`scripts/v2_cli.py --input 需求.xlsx --output 候选.xlsx` 提取/检查并创建一个候选工作簿，核查事项内嵌在“待核查与规则说明”Sheet。
审核方填写原始来源 `source_file`、`source_sha256`、`source_locator`、`evidence_text`、`boundary_basis`、`movement_basis`、`reviewer`、ISO日期 `reviewed_at`，在理解真实性与边界后设置 `review_status=approved`。然后审核人离线使用独立持有的密钥对当前工作簿签名：
```bash
python3 scripts/v2_review.py --input reviewed.xlsx --output signed.xlsx --key-file reviewer.key --source-root /verified/sources
python3 scripts/v2_cli.py --input signed.xlsx --output COSMIC工作量拆解.xlsx --approval-key-file reviewer.key --source-root /verified/sources
```
最后只交付一份 `COSMIC工作量拆解.xlsx`。秘钥不要放入Agent可访问目录。行或来源文件修改后签名失效，缺密钥只会输出候选。签名仅证明密钥持有，不证明审核人现实身份或FUR业务语义。

输入支持CSV/XLSX/DOCX/Markdown，后两者仅抽取候选证据，绝不据此自动发明数据移动；重复表头、多个候选Sheet需用户显式消歧。不修改原文件，不产生单独审核清单或CSV。可选 `--qualify-with-process` 仅在不同真实三级模块且过程名在FUR原文中出现时创建待审描述，并清除旧确认。
