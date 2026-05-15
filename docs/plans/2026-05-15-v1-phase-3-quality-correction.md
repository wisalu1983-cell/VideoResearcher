# V1 Phase 3 分析质量修正计划

## 背景

首次真实样本验证后，Phase 3 初版只能证明 `transcript -> index -> note` 文件链路打通。生成的 `notes/video_note.md` 仍以时间窗口概览和片段拼接为主，未达到预研要求中的“快速消化视频”“识别高价值信息”“形成完整脉络”“支持后续追问定位”。

## 修正目标

- 保留已完成的结构链路：`transcript.json` 到 `video_index.yaml`、`video_index.json`、`video_note.draft.md`、`video_note.md`。
- 将 `video_note.md` 从概览模板升级为分析型草稿，至少包含核心结论、主题模块、证据时间段、完整大纲、可追问方向和质量边界。
- 明确脚本产物和 Agent 产物的边界：脚本负责结构草稿和证据定位，Agent synthesis pass 负责把模块内部改写成实质观点、依据解释和追问入口。
- 修改脚本行为：`process_video.py --phase3` 只生成或覆盖 `notes/video_note.draft.md`，不得覆盖 `notes/video_note.md`。
- 对 `B_overview` 转录明确标注为分析草稿，避免把低置信度内容包装成确定结论。
- Phase 4 启动前，用真实样本重新跑 Phase 3，并补充 QA 记录。

## 偏差清单

| 偏差 | 所属范围 | 修正方式 |
|---|---|---|
| Phase 3 验收只看文件存在和数据契约 | V1 Phase 3 | 补充 NOTE 质量门：观点、主题模块、证据时间段、质量边界 |
| 笔记缺少成体系观点与结论 | V1 Phase 3 | 重写笔记生成结构，输出分析型草稿 |
| 模块有结构但内容仍空泛 | V1 Phase 3 | 增加 Agent synthesis pass，模块内部必须写明结论、依据、重要性、追问点和置信边界 |
| 重跑脚本可能覆盖最终笔记 | V1 Phase 3 | 将脚本输出改为 `video_note.draft.md`，正式 `video_note.md` 由 Agent synthesis 维护 |
| 高价值判断与追问线索过弱 | V1 Phase 3 / V2-lite 前置 | 在笔记中保留候选线索和追问方向，后续追问再增量修正索引 |
| Phase 4 过早启动 | V1 Phase 4 | Phase 4 暂缓，等待 Phase 3 质量修正通过 |
| 画面综合分析期望需要澄清边界 | 后续版本 | V1/V2-lite 只基于音频、字幕和文本索引；完整画面理解、OCR、抽帧进入 V3 |

## 实施任务

1. 更新 Phase 3 测试，使笔记必须包含分析型结构和证据时间段。
2. 更新 Phase 3 测试，锁定脚本只写 `video_note.draft.md` 且不覆盖 `video_note.md`。
3. 调整 `scripts/process_video.py` 的笔记生成逻辑，减少模板化片段罗列，并输出 draft。
4. 对真实样本执行 Agent synthesis pass，把模块内容改写成可读分析笔记。
5. 更新 Phase 3 文档、QA 记录、Note spec、模板和 V2-lite 验收清单。
6. 在当前真实样本上重新执行 Phase 3，并确认 `video_note.md` 未被脚本覆盖。
7. 运行单测、PM 同步和文档一致性检查。

## 验收标准

- 自动化测试覆盖新的分析型笔记结构。
- 当前真实样本的 `notes/video_note.md` 不再只是时间窗口片段拼接。
- 当前真实样本的模块内部不再只是转录摘句，而是包含结论、依据解释、重要性、追问点和质量边界。
- 重跑 Phase 3 时，脚本只更新 `notes/video_note.draft.md`，保留 Agent 整理后的 `notes/video_note.md`。
- 文档状态如实反映：Phase 3 结构链路已通过，分析质量修正中。
- 所有新增结论均绑定时间段或明确标注为待复核线索。
