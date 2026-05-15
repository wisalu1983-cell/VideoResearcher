# Phase 2：音频抽取与转录适配

> 状态：已完成
> QA 记录：`QA/runs/2026-05-15-v1-phase-2.md`

建立 FFmpeg 音频抽取和本地转录工具适配层。

## 目标

- 使用 FFmpeg 抽取统一格式音频。
- 优先验证 faster-whisper。
- 保留 whisper.cpp 备用路径。
- 输出 `transcript/transcript.srt` 和 `transcript/transcript.json`。
- 对低质量转录和时间戳风险进行分级记录。

## 完成结果

- 已安装并验证 FFmpeg / ffprobe。
- 已新增 `requirements.txt`，在本地 `.venv` 中验证 `faster-whisper` 可用。
- `scripts/process_video.py` 已支持 `--phase2`，可在初始化 run 后继续抽取音频并生成转录。
- 音频统一输出到 `audio/audio.wav`，格式为 mono 16kHz PCM WAV。
- 转录层通过 adapter 隔离，默认使用 faster-whisper，保留 whisper.cpp adapter 占位。
- 真实样本已产出 `transcript/transcript.srt` 和 `transcript/transcript.json`。

## 已知限制

- 当前真实样本使用 `tiny` 模型和 CPU int8 做本地冒烟，质量标记为 `B_overview`。
- 时间戳标记为 `approximate`，需要后续人工抽检或更高质量模型验证后再提升为精确追问材料。
- HuggingFace 未配置 token 时模型下载会使用未认证请求；Windows 未启用 symlink 时模型缓存会占用更多空间。
