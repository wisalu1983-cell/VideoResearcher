# V1 执行纪律与验收规则

## 执行原则

- 先实现本地文件链路，再考虑在线视频前置工具。
- `video_index.yaml` 仍是主索引，`video_index.json` 只能从 YAML 派生。
- 转录层必须可替换，不让索引和笔记逻辑绑定单一工具。
- 外部 API、公司模型和自费工具只作为人工批准 gate。
- 失败时优先保留中间结果和用户下一步建议。

## 验收规则

- 产物目录符合 `ProjectManager/Templates/video_project/`。
- JSON 模板和导出文件可解析。
- 处理日志记录输入、输出、工具、参数和已知限制。
- 失败日志记录失败类型、尝试修复和用户动作。
- `python scripts/pm_sync_check.py` 通过。
- V1 收口时明确 V2-lite 追问入口。
