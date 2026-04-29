# 单视频项目数据契约

> 权威规格：`ProjectManager/Specs/index-schema/current.md`、`note-template/current.md`、`failure-handling/current.md`

## 维护源

| 文件 | 是否人工维护 | 说明 |
|---|---:|---|
| `index/video_index.yaml` | 是 | 主索引，给人和 Agent 读写 |
| `index/video_index.json` | 否 | 从 YAML 自动导出，给脚本和工具消费 |
| `notes/video_note.md` | 是 | 人类阅读版笔记，可由 Agent 生成和修订 |
| `logs/process_log.md` | 是 | 记录处理过程、工具、参数和已知限制 |
| `logs/failure_log.json` | 是 | 记录失败类型、尝试修复和用户下一步动作 |
| `logs/index_change_log.md` | 是 | 记录索引修正、重写、删除和价值重分类 |

## 索引契约

`video_index.yaml` 必须能够回答三个问题：

1. 视频完整脉络是什么。
2. 高价值内容出现在哪些时间段。
3. 后续追问可以用哪些片段作为依据。

普通章节可以低成本记录，高价值内容必须细化到片段、观点、数据、案例、方法或操作步骤。

## JSON 导出契约

- JSON 只从 YAML 生成。
- JSON 不承担人工修订职责。
- 导出失败时，不得覆盖已有有效 JSON。
- 导出脚本应保留 `generated_from` 或等价来源信息。

## 笔记契约

`video_note.md` 面向快速阅读和复盘，不替代索引。笔记中的章节、片段和时间段应能追溯到 `video_index.yaml`。

## 日志契约

处理日志和失败日志必须让后续复盘者知道：

- 哪个阶段失败或降级。
- 已经尝试过什么修复。
- 保留了哪些中间结果。
- 用户下一步需要补什么。
- 哪些问题应进入后续优化。
