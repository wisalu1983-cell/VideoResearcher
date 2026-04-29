# V1 分类、依赖与边界

| 类别 | V1 能力 | 依赖规格 |
|---|---|---|
| 输入与材料 | 本地视频输入校验、输出项目初始化 | `Specs/source-ingestion/current.md` |
| 音频处理 | FFmpeg 音频抽取、基础转码兜底 | `Specs/transcription/current.md` |
| 转录 | faster-whisper / whisper.cpp 适配、带时间戳输出 | `Specs/transcription/current.md` |
| 索引 | YAML 主索引初版生成、JSON 派生导出 | `Specs/index-schema/current.md` |
| 笔记 | Markdown 混合版笔记生成 | `Specs/note-template/current.md` |
| 失败处理 | 处理日志、失败日志、中间结果保留 | `Specs/failure-handling/current.md` |
| QA | 产物结构校验、转录质量抽检、样本占位 | `QA/v2-lite-acceptance-checklist.md` |

## 边界

V1 只负责自动建索引链路，不负责基于索引的正式追问回答。追问能力进入 V2-lite。
