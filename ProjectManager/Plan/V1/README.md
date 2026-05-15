# V1 自动建索引

> 所属版本：V1
> 创建：2026-04-29
> 状态：Phase 4 已完成，V1 收口
> 设计规格：`ProjectManager/Specs/_index.md`

## 导航入口

| 想了解什么 | 打开哪个文件 |
|---|---|
| 版本背景、目标、阶段结构 | `00-overview.md` |
| 来源材料与 v0.1 交接 | `01-source-catalog.md` |
| 功能分类、依赖、边界 | `02-classification.md` |
| Phase 总图 | `03-phase-plan.md` |
| 执行纪律与验收规则 | `04-execution-discipline.md` |

## 当前状态

- v0.1 已完成规格、模板、数据契约和 QA 口径收口。
- V1 聚焦自动建索引，不扩展到追问闭环、OCR、抽帧、在线视频自动处理或本地应用 UI。
- Phase 1 已完成本地处理脚本基线，支持本地视频输入校验、输出项目目录初始化和初始处理日志。
- Phase 2 已完成 FFmpeg 音频抽取和本地转录适配层，真实样本可产出 SRT / JSON 转录。
- Phase 3 已完成 YAML 主索引、JSON 派生索引、脚本笔记草稿和 Agent 最终笔记链路。
- 已将 `notes/video_note.draft.md` 与 `notes/video_note.md` 分离，脚本只生成草稿，Agent synthesis 维护最终人类阅读版笔记。
- Phase 4 已完成 `process_video.py --phase4` 产物结构 QA、`logs/qa_report.md`、失败日志和处理日志收口。

## 下一步

进入 V2-lite 规划：基本追问、片段检索、答案依据和不足提示闭环。
