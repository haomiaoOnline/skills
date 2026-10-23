# Personal Skills

这是我的个人 Skill 仓库。每个 Skill 使用独立子目录保存。

## 目录约定

- 每个 Skill 对应仓库根目录下的一个独立子文件夹。
- skills.json 是唯一的 Skill 列表与展示元数据源。
- 数字花园等外部项目只消费 skills.json，不维护第二份 Skill 清单。
- 新增或修改 Skill 元数据后，运行 scripts/validate_catalog.py 做一致性检查。

## 当前结构

仓库中的 Skill 目录以 skills.json 为准。README 不重复维护 Skill 列表，避免双份数据产生漂移。

## Agent Skill 安装与发布

仓库根目录的每一个Skill使用独立子文件夹，由 `skills.json` 提供唯一目录和入口；新增 Skill 时使用 `python3 scripts/validate_catalog.py` 验证索引。

- [COSMIC 工作量拆解助手](cosmic-materials-assistant/README.md)：[交给Agent的自动安装文档](cosmic-materials-assistant/docs/AGENT_INSTALL.md)。
- 其他 Skill 以 `skills.json` 为准，避免维护第二份目录清单。
- 原有 `cosmic/` 只保存旧参考资料，不是当前通用 Skill 的安装入口。不得自动提交其中未跟踪的本地数据。
- 请勿将业务原始材料、第三方未授权内容、个人密钥及私有仓库历史发布到公开 Skills 仓库。
