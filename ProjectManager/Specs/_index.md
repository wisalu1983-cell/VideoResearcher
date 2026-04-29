# VideoResearcher Specs 规格矩阵

> 用途：新计划启动前的必查清单。按视频处理能力维度定位已有规格，避免漏检历史约束。

| 维度 | Spec | 状态 | 关键断言 |
|---|---|---|---|
| 输入与材料 | `source-ingestion/current.md` | R0 基线 | 本地视频为首版刚性输入；在线视频作为提取到本地项目的前置工具 |
| 转录 | `transcription/current.md` | R0 基线 | 首版优先 FFmpeg + 本地开源转录工具，转录层可替换 |
| 索引 | `index-schema/current.md` | R0 基线 | YAML 主索引 + JSON 派生索引；高价值内容细粒度 |
| 笔记 | `note-template/current.md` | R0 基线 | Markdown 混合版笔记面向快速消化与后续追问 |
| 追问 | `follow-up-qa/current.md` | R0 基线 | 基于索引定位片段，说明支撑理由，必要时回查转录 |
| 外部资料 | `external-evidence/current.md` | R0 基线 | 外部资料只用于直接相关的补足或校验，并区分来源 |
| 失败处理 | `failure-handling/current.md` | R0 基线 | 识别失败类型、保留中间结果、提示下一步 |
