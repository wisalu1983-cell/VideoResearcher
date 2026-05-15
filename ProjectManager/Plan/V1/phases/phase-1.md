# Phase 1：脚本骨架与输入校验

> 状态：已完成
> QA 记录：`QA/runs/2026-05-15-v1-phase-1.md`

建立 V1 的本地处理脚本入口、输入校验和输出目录初始化。

## 目标

- 定义 `process_video.py path/to/video.mp4` 或等价 CLI。
- 校验本地视频路径、格式和可读性。
- 从 `ProjectManager/Templates/video_project/` 初始化真实处理项目目录。
- 写入初始 `logs/process_log.md`。

## 完成结果

- 已新增 `scripts/process_video.py` 作为 V1 本地视频处理入口。
- 已新增 `tests/test_process_video.py` 覆盖 CLI、输入校验、项目初始化、重复 run 和复制输入选项。
- 默认输出到 `outputs/`，并保留 `--output-root` 与 `--copy-input` 参数。
- Phase 1 不执行 FFmpeg、转录、索引生成或笔记生成，后续进入 Phase 2。
