# Phase 3：本地处理脚本基线设计

为后续 V1 自动建索引准备处理脚本开发文档，明确 FFmpeg、转录工具、分段处理、输出路径和失败保留规则。

## R0 产出

- 转录规格：`ProjectManager/Specs/transcription/current.md`
- 索引规格：`ProjectManager/Specs/index-schema/current.md`
- 失败处理规格：`ProjectManager/Specs/failure-handling/current.md`
- 模板数据契约：`ProjectManager/Templates/video_project/DATA_CONTRACTS.md`
- 后续子计划入口：`ProjectManager/Plan/v0.1/subplans/2026-04-29-v1-local-processing-baseline.md`

## V1 入口

V1 应从本地视频处理脚本开始，优先完成：

1. 输入校验。
2. FFmpeg 音频抽取。
3. faster-whisper / whisper.cpp 转录适配层。
4. 带时间戳转录输出。
5. YAML 主索引生成。
6. JSON 派生索引导出。
7. 处理日志和失败日志。
