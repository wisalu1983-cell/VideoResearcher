# Phase 4：日志、失败处理与 QA

补齐处理日志、失败记录和产物结构验收。

> 状态：已完成

## 目标

- 写入完整 `logs/process_log.md`。
- 失败时写入 `logs/failure_log.json`。
- 保留已完成中间结果。
- 用 `QA/v2-lite-acceptance-checklist.md` 中与 V1 相关的项目验收产物结构。
- 形成 V1 收口时的 QA 记录。

## 实现结果

- 新增 `process_video.py --phase4`，用于已有项目目录的 V1 产物结构 QA。
- 生成 `logs/qa_report.md`，检查转录、索引、草稿笔记、最终笔记、过程日志、失败日志和索引变更日志。
- 若关键产物缺失、JSON 不可解析，或 `notes/video_note.md` 仍是模板占位内容，则写入 `logs/failure_log.json` 并停止放行。
- 当前真实样本已执行 Phase 4，`logs/qa_report.md` 全部 PASS。
