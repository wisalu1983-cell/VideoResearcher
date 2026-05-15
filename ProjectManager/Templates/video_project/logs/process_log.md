# 处理日志

## 基本信息

- video_id:
- input_file:
- started_at:
- finished_at:
- environment:
- operator:

## 阶段记录

| 阶段 | 状态 | 输入 | 输出 | 工具 / 参数 | 备注 |
|---|---|---|---|---|---|
| 输入校验 | pending |  |  |  |  |
| 音频抽取 | pending |  |  | FFmpeg |  |
| 转录 | pending |  |  | faster-whisper / whisper.cpp |  |
| 索引生成 | pending |  |  | Agent / script |  |
| 笔记草稿生成 | pending |  |  | process_video.py |  |
| Agent 笔记合成 | pending | notes/video_note.draft.md, index/video_index.yaml, transcript/transcript.json | notes/video_note.md | Agent synthesis |  |
| JSON 导出 | pending |  |  | script |  |
| QA 检查 | pending | V1 artifacts | logs/qa_report.md | process_video.py --phase4 | Phase 4 执行 |

## 已知限制

- 

## 后续动作

- 
