# v2.0.1 通用语义字段、来源签名和单文件准入

COSMIC V5标准计量遵守真实FUR、功能用户、软件块边界、E/X/R/W每条有效移动1 CFP。额外的语义字段全表唯一、2:7:1比例、0.33折算、三级模块1:1与8条上限是本Skill用户指定的通用交付合同，不是COSMIC官方定律。

## 模型
`level1,level2,level3,functional_process,functional_process_id,fur_id,trigger,functional_user,subprocess,movement,data_group,attributes,cfp,development_type,development_basis,evidence_text,source_locator,status`。安全与审批扩展：`source_file,source_sha256,boundary_basis,movement_basis,review_status,reviewer,reviewed_at,approval_signature`。每一列可通过`--profile`的`column_mapping`以真实表头映射；无固定I/K/L字母。

## 不可绕过的门
1. 子过程/数据组/数据属性各列全表规范化不重复，跨过程无豁免。合法限定必须源文可核验，仅允许真实独立过程与真实上下文；同一三级模块不能自行添加额外过程突破1:1合同。
2. 开发类型实际比率2:7:1、组织折算系数1/0.33/0；标准CFP与经验工作量分开计算。要有实际开发依据，不按配额虚报。
3. 三级模块完整路径映射一个逻辑过程、每过程最多8条真实E/X/R/W移动，首条真实触发E；对不能证明独立触发的需求保持待审候选。
4. 不存在的源文件、来源SHA不匹配、审批行数据修改、签名缺失、审核日期无效均阻断正式CFP。不能因为电子表格写着approved就认为已批准。
5. 客户只得到一个XLSX，内含拆解及所有待核查问题、折算汇总。输入不覆盖、缺失行不丢、重复列报错、疑义Sheet人工指定，文本不变活动Excel公式。
6. 可选MCP默认必须配置COSMIC_MCP_ROOT，目录之外只读/写都拒绝。MCP不接受审批密钥。
7. 签名由独立审核方使用私有HMAC密钥完成，仅证明密钥持有与行内容完整性，不会验证法律身份、源文语义或官方计量认证。

## 操作路径
普通Agent：`python3 scripts/v2_cli.py --input customer.xlsx --output candidate.xlsx`。
独立审核人：`python3 scripts/v2_review.py --input reviewed.xlsx --output signed.xlsx --key-file reviewer.key --source-root sources`。
终审验证：`python3 scripts/v2_cli.py --input signed.xlsx --output COSMIC工作量拆解.xlsx --approval-key-file reviewer.key --source-root sources`。

输出0=工程及已签名证据门通过并等待用户最终业务验收，2=仅候选，1=工程错误。数据真实性必须由具备业务知识的独立人审核。
