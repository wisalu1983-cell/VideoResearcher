# VideoResearcher Specs 规格矩阵

> 用途：新计划启动前的必查清单。按视频处理能力维度定位已有规格，避免漏检历史约束。

| 维度 | Spec | 状态 | 关键断言 |
|---|---|---|---|
| 输入与材料 | `source-ingestion/current.md` | 待建立 | 本地视频为首版刚性输入；在线视频只做可行性和合法边界处理 |
| 转录 | `transcription/current.md` | 待建立 | 首版优先 FFmpeg + 本地开源转录工具，转录层可替换 |
| 索引 | `index-schema/current.md` | 待建立 | YAML 主索引 + JSON 派生索引；高价值内容细粒度 |
| 笔记 | `note-template/current.md` | 待建立 | Markdown 简明笔记面向人类阅读 |
| 追问 | `follow-up-qa/current.md` | 待建立 | 基于索引定位片段，说明支撑理由 |
| 外部资料 | `external-evidence/current.md` | 待建立 | 外部资料只用于直接相关的补足或校验 |
| 失败处理 | `failure-handling/current.md` | 待建立 | 识别失败类型、保留中间结果、提示下一步 |
