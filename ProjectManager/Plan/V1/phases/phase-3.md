# Phase 3：索引与笔记生成

> 状态：已完成
> QA 记录：`QA/runs/2026-05-15-v1-phase-3.md`；质量修正记录：`QA/runs/2026-05-15-v1-phase-3-quality-correction.md`

从转录产物生成结构化索引和人类阅读笔记。

## 目标

- 生成 `index/video_index.yaml` 初版。
- 从 YAML 导出 `index/video_index.json`。
- 生成 `notes/video_note.draft.md` 脚本结构草稿。
- 通过 Agent synthesis pass 生成或更新 `notes/video_note.md` 人类阅读版最终笔记。
- 保持章节、片段、时间段和高价值标记可追溯。
- 笔记需要形成可读观点、主题模块、证据时间段和可追问方向，满足预研中“快速消化”和“后续追问定位”的第一轮索引价值。

## 完成结果

- `scripts/process_video.py` 已支持 `--project-dir <run> --phase3`，可在已有 Phase 2 run 上生成索引和脚本笔记草稿。
- 已生成 `index/video_index.yaml` 作为主索引。
- 已生成 `index/video_index.json`，包含 `generated_from: index/video_index.yaml`。
- 已将脚本产物固定为 `notes/video_note.draft.md`，避免重跑 Phase 3 覆盖 Agent / 人工整理后的 `notes/video_note.md`。
- 已新增项目规则和项目 skill，要求 Agent 将草稿合成为最终笔记。
- 当前真实样本基于 `B_overview` 转录，索引和笔记均明确标注时间戳或术语风险。

## 验证结果

- `python -m unittest discover -s tests`：13 tests OK。
- `& ".venv\\Scripts\\python" -m unittest discover -s tests`：13 tests OK。
- `python scripts/pm_sync_check.py`：PASS。
- `git diff --check`：无空白错误，仅有 CRLF 提示。
- 真实样本已重跑 Phase 3，生成 `notes/video_note.draft.md`，并保留 Agent synthesis 后的 `notes/video_note.md`。

## 已知限制

- Phase 3 脚本层使用 deterministic 概览生成，不调用外部模型，不自动断言高价值片段。
- 当前索引粒度按时间窗口生成，适合打通链路和后续人工复核。
- `scripts/process_video.py` 不具备真正语义综合能力，不能单独承担最终 `video_note.md` 质量验收。
- 预研要求中的高价值判断、成体系观点和可追问线索属于 V1 Phase 3 修正范围；完整画面理解、OCR、抽帧仍留到后续版本。

## 修正验收

- `notes/video_note.md` 至少包含核心结论、主题模块、证据时间段、完整大纲、可追问方向和质量边界。
- `scripts/process_video.py --phase3` 必须只写入或覆盖 `notes/video_note.draft.md`，不得覆盖 `notes/video_note.md`。
- 项目内必须有 Agent synthesis 规则 / skill 指导最终笔记生成。
- 主题模块内部必须包含实质结论、依据解释、为什么重要、可追问点和置信边界；不能只放转录摘句。
- 对 `B_overview` 转录，只输出分析草稿和追问线索，不把低置信度内容写成确定结论。
- 笔记中的观点或判断必须能追溯到索引或转录时间段。
- Phase 4 启动前，真实样本需要重新跑 Phase 3，保留 Agent 版最终笔记，并补充 QA 记录。
