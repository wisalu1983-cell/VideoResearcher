# v0.1 分类、依赖与边界

| 类别 | 首批能力 | 长期规格位置 |
|---|---|---|
| 输入与材料 | 本地视频、字幕、转录文本、在线视频可行性 | `Specs/source-ingestion/` |
| 转录 | FFmpeg 音频抽取、faster-whisper / whisper.cpp 测试 | `Specs/transcription/` |
| 索引 | YAML 主索引、JSON 派生索引、混合粒度 | `Specs/index-schema/` |
| 笔记 | Markdown 简明笔记模板 | `Specs/note-template/` |
| 追问 | 基于索引定位片段、回答支撑理由 | `Specs/follow-up-qa/` |
| 外部资料 | 可靠来源、必要性、来源区分 | `Specs/external-evidence/` |
| 失败处理 | 失败类型、日志、保留中间结果 | `Specs/failure-handling/` |
