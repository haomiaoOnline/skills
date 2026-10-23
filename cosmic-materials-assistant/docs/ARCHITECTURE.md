# 架构和模块清单

## 结构
```text
Agent / CLI / stdio MCP
  ├─ scripts/install_agent.py     安装到Agent自有目录，不覆盖原件
  ├─ scripts/v2_cli.py           候选/核验统一入口与退出码
  ├─ scripts/v2_mcp.py           stdio MCP工具，目录沙箱
  ├─ scripts/v2_io.py            输入字段映射和唯一XLSX写出
  ├─ scripts/v2_core.py          通用规则与COSMIC候选验证
  ├─ scripts/v2_auth.py          来源文件SHA+审核行HMAC
  └─ scripts/v2_review.py        独立审核人员本机签名入口
```

`scripts/build_release.py` 持有唯一的第三方发布清单；`tests/test_v2_*.py` 仅依赖模拟数据，禁止依赖本地历史客户文档。`docs/`是面向第三方Agent的操作资料，`AGENTS.md` 为仓库级Agent指令，`SKILL.md` 为可加载技能入口。

## 数据流
`客户已授权材料 -> v2_io.read_source -> v2_core.validate -> v2_io.export_workbook -> 单一候选XLSX`。因无证据/签名进入 `BLOCKED_CANDIDATE_ONLY`；真实材料与独立签名均满足后核验 `READY_FOR_USER_ACCEPTANCE`，非代表客户最终签章。

## 规则来源说明
E/X/R/W与有效移动1 CFP属于COSMIC方法要点；语义字段全表唯一、2:7:1、0.33、三级模块与8条移动限制为当前客户要求的**通用交付合同**。真实FUR违反附加合同应保持阻断，不可伪造业务来通过。

## 兼容与遗留模块
本地版本历史保留用于旧客户的 `P0/P1/P2/P3` 及旧 `scripts/*` 工具；**发布ZIP不收录**。新Agent必须从 `scripts/v2_cli.py` 和 `SKILL.md` 开始，不调用旧山东特例代码。当前 v2.0.3 发行版未提供图形界面或SaaS后台。
