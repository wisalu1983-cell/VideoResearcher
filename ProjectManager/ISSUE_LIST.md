# ISSUE_LIST（当前版本开放问题）

> 当前版本：V2-lite

## 当前开放数

| 当前开放数 | 是否阻塞当前主线 | 当前需关注项 |
|---|---|---|
| 1 | 否 | ISS-001 |

## 开放问题清单

### ISS-001 · GPU 推理缺少 cuBLAS 库

- 状态：开放
- 发现日期：2026-05-22
- 阻塞：否（CPU 模式可替代，但显著更慢）
- 现象：`faster-whisper` 使用 `device="cuda"` 时，ctranslate2 能检测到 GPU，但执行推理时报 `RuntimeError: Library cublas64_12.dll is not found or cannot be loaded`
- 原因：venv 中缺少 NVIDIA cuBLAS 运行时库，或 ctranslate2 版本与系统 CUDA 版本不匹配
- 影响：medium/large 模型只能用 CPU int8 跑，42 分钟视频转录时间从预估几分钟增加到 20-40 分钟
- 解决方向：安装对应版本 CUDA Toolkit，或 `pip install nvidia-cublas-cu12` 补齐缺失库
