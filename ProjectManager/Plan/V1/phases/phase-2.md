# Phase 2：音频抽取与转录适配

建立 FFmpeg 音频抽取和本地转录工具适配层。

## 目标

- 使用 FFmpeg 抽取统一格式音频。
- 优先验证 faster-whisper。
- 保留 whisper.cpp 备用路径。
- 输出 `transcript/transcript.srt` 和 `transcript/transcript.json`。
- 对低质量转录和时间戳风险进行分级记录。
