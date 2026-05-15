# 单视频项目模板

> 用途：复制为每个真实视频处理项目的初始目录。

## 目录结构

```text
video_project/
  input/
  transcript/
    transcript.srt
    transcript.json
  index/
    video_index.yaml
    video_index.json
  notes/
    video_note.draft.md
    video_note.md
  logs/
    process_log.md
    failure_log.json
    index_change_log.md
    qa_report.md
```

## 使用规则

- `input/` 存放用户有权处理的本地视频、音频、字幕或转录源文件。
- `transcript/` 存放转录结果，要求保留时间戳。
- `index/video_index.yaml` 是唯一人工 / Agent 维护源。
- `index/video_index.json` 从 YAML 自动导出，不人工维护。
- `notes/video_note.draft.md` 是脚本生成的结构草稿。
- `notes/video_note.md` 是 Agent synthesis 后的人类阅读版最终笔记，不应被脚本覆盖。
- `logs/` 记录处理过程、失败、索引变更和 Phase 4 QA 收口结果。

## 边界

此目录是模板，不代表实际样本。真实视频项目应复制该目录后再填入输入材料和产物。
