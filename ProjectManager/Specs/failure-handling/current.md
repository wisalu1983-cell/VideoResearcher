# 失败处理 current spec

> 状态：R0 基线
> 来源：`video_agent_requirements_research.md` §16、§18

## 当前承诺

V2-lite 首版不追求所有失败自动修复。合理要求是识别失败类型、保留已完成的中间结果、告诉用户下一步需要补什么，并保存失败记录作为后续优化依据。

## 失败类型与处理

| 失败类型 | 处理方式 |
|---|---|
| 视频文件无法读取 | 输出错误原因，提示转码或换格式 |
| 音频抽取失败 | 尝试 FFmpeg 转码，再失败则停止 |
| 本地转录失败 | 尝试降级模型、CPU 模式或分段重试 |
| 转录质量明显差 | 标记低质量转录，建议 API 兜底或重新提供音频；API 前必须人工确认 |
| 时间戳错位严重 | 保留文本，但提示不适合精确片段定位 |
| 索引生成不完整 | 保留已有结果，标记缺失章节 |
| 追问无法回答 | 明确说明索引中依据不足，并指出需要回查材料 |
| 外部资料不足 | 明确说明无法可靠补充，不使用低质量来源硬答 |

## 质量分级

| 等级 | 处理策略 |
|---|---|
| A：可精确追问 | 进入完整笔记、索引和追问闭环 |
| B：可概览但不适合精确定位 | 允许生成概览产物，追问时提示定位风险 |
| C：不可可靠分析 | 停止确定性结论，只保留中间结果、失败记录和用户下一步建议 |

## 失败记录字段

```yaml
failure_record:
  time:
  video_id:
  stage:
  error_type:
  error_message:
  input_file:
  attempted_fixes:
  remaining_problem:
  user_action_needed:
  optimization_notes:
```

## 处理日志

`logs/process_log.md` 记录每次处理的阶段、输入、输出、中间结果、工具版本、关键参数和已知限制。

## QA 收口记录

Phase 4 通过 `process_video.py --phase4` 执行 V1 产物结构验收，写入 `logs/qa_report.md`，并更新 `logs/process_log.md` 的 `QA 检查` 状态。若关键产物缺失、JSON 不可解析，或 `notes/video_note.md` 仍是模板占位内容，则写入 `logs/failure_log.json`，保留已有中间结果并提示用户补齐后重跑。

## 索引变更记录

`logs/index_change_log.md` 记录非增量修改：

```yaml
change_record:
  time:
  changed_section:
  change_type: incremental_addition | correction | deletion | rewrite | value_reclassification
  reason:
  source:
  related_question:
  before:
  after:
```
