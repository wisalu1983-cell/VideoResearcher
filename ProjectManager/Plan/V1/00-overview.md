# V1 概览

## 背景

v0.1 已完成后续开发依赖的规格、模板、数据契约和 QA 口径。V1 的任务是从文档基线进入自动建索引能力，让本地视频可以被处理成带时间戳转录、Markdown 笔记、YAML 主索引、JSON 派生索引和日志。

## 目标

1. 建立本地处理脚本入口。
2. 支持本地视频输入校验。
3. 支持 FFmpeg 音频抽取。
4. 建立 faster-whisper 优先、whisper.cpp 备用的转录适配层。
5. 生成 `transcript.srt` 和 `transcript.json`。
6. 生成 `video_index.yaml` 初版。
7. 从 YAML 导出 `video_index.json`。
8. 写入 `process_log.md` 和 `failure_log.json`。

## 非目标

- 不完成 V2-lite 追问闭环。
- 不接入在线视频下载或提取工具。
- 不做 OCR、抽帧或完整画面理解。
- 不做本地应用 UI。
- 不默认调用外部 API、公司模型或自费工具。

## 收口条件

- 至少一个本地样本能产出完整 `video_project` 文件包。
- 转录、索引、笔记和日志产物符合 R0 数据契约。
- 失败场景能保留中间结果并写入失败日志。
- V2-lite 的追问实现入口明确。
