# Personal Skills

这是我的个人 Skill 仓库。每个 Skill 使用独立子目录保存。

## 目录约定

- 每个 Skill 对应仓库根目录下的一个独立子文件夹。
- skills.json 是唯一的 Skill 列表与展示元数据源。
- 数字花园等外部项目只消费 skills.json，不维护第二份 Skill 清单。
- 新增或修改 Skill 元数据后，运行 scripts/validate_catalog.py 做一致性检查。

## 当前结构

仓库中的 Skill 目录以 skills.json 为准。README 不重复维护 Skill 列表，避免双份数据产生漂移。
