# Troubleshooting / 常见错误

| 症状 | 原因与处理 |
| --- | --- |
| `python3: command not found` | 安装Python 3.9+；MCP 推荐Python 3.11。Agent不能静默执行系统提权安装 |
| `FileExistsError: destination already exists` | Installer永不覆盖旧Skill。请查看旧目录或另选 `--target`，不要删除未知文件 |
| `pip install` 无网络 | 离线可使用 `--skip-deps` 复制清单，但必须报告依赖/测试尚未验收 |
| `ModuleNotFoundError openpyxl/docx` | 激活Skill下隔离虚拟环境或 `.venv/bin/python`，再安装 `requirements.txt` |
| MCP `mcp` 模块不可用 | 在Python 3.11下安装 `requirements-mcp.txt` |
| `COSMIC_MCP_ROOT is mandatory` | 运营者在明确授权的目录下配置环境变量，不应该任意放宽路径访问 |
| CSV表头冲突、多个Sheet | 明确给 `--sheet`、`--profile`，不要自动选择可能是历史样例的工作表 |
| 返回 exit 2 | 正常生成候选，待核查Sheet有详情，不是安装失败；未完成正式业务CFP审核 |
| `UNVERIFIABLE_SOURCE` | 检查 `source_file` 在指定 `--source-root` 内且SHA256与当前源文件匹配 |
| `UNVERIFIED_APPROVAL_SIGNATURE` | 缺审核人独立签名，或行内容已变更。需要审核人再次亲自审核和签名 |
| `DEVELOPMENT_RATIO_MISMATCH` | 真实新增/复用/利旧分类不符合额外交付比例，不能为凑比例编造类型 |
| `GLOBAL_DUPLICATE_...` | 根据原始真实FUR重审对应字段，不允许改数字后缀伪造不同OOI |

如果Agent不能运行Python或访问本地文件，单独发送一份Markdown文档并不足以自动安装。必须具备目标机器的执行权限并可读取发行ZIP/仓库文件。
