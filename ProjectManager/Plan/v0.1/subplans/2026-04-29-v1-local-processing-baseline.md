# V1 本地处理脚本基线子计划

> 所属版本：v0.1 → V1 入口
> Spec impact：`transcription/current.md`、`index-schema/current.md`、`failure-handling/current.md`
> 状态：已迁移至 `ProjectManager/Plan/V1/`

## 目标

为 V1 自动建索引建立本地处理脚本入口，使本地视频可以产出带时间戳转录、YAML 主索引、JSON 派生索引、Markdown 笔记和日志。

## 建议范围

1. `process_video.py path/to/video.mp4` CLI 契约。
2. 本地视频输入校验。
3. FFmpeg 音频抽取。
4. faster-whisper 优先、whisper.cpp 备用的转录适配层。
5. 1 到 3 小时视频分段处理策略。
6. `transcript.srt` 和 `transcript.json` 输出。
7. `video_index.yaml` 初版生成。
8. `video_index.json` 自动导出。
9. `process_log.md` 和 `failure_log.json` 写入。

## 非目标

- 不处理 OCR、抽帧和完整画面理解。
- 不接入在线视频下载或提取工具。
- 不做本地应用 UI。
- 不默认调用外部 API、公司模型或自费工具。

## 启动前检查

- 确认 FFmpeg 安装方式。
- 确认 4070 Ti 和 5060 Windows 台式机的 Python / CUDA / 驱动环境。
- 准备 `QA/v2-lite-sample-plan.md` 中的首批样本。
- 确认是否需要把脚本放入 `scripts/` 或单独应用目录。
