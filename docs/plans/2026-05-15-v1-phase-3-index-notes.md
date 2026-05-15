# V1 Phase 3 Index And Notes Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Generate the first YAML index, derived JSON index, and Markdown note from Phase 2 transcript outputs.

> 2026-05-15 修正说明：本计划已完成结构链路，但真实样本笔记质量未达到预研中的第一轮索引价值要求。Phase 3 后续已改为脚本生成 `notes/video_note.draft.md`，Agent synthesis 生成正式 `notes/video_note.md`。后续质量修正见 `docs/plans/2026-05-15-v1-phase-3-quality-correction.md`。

**Architecture:** Keep `scripts/process_video.py` as the CLI entry. Add Phase 3 helpers that read `transcript/transcript.json`, generate a conservative overview index, write `index/video_index.yaml`, derive `index/video_index.json`, write `notes/video_note.draft.md`, and update `logs/process_log.md`. For B-grade transcripts, outputs must clearly mark timestamp and term risks. Formal `notes/video_note.md` is maintained by Agent synthesis, not overwritten by the script.

**Tech Stack:** Python standard library, project template files, `unittest`.

---

## Scope

- Add `--phase3` to generate index and notes.
- Add `--project-dir` so Phase 3 can run on an existing Phase 2 run without re-transcribing.
- Generate deterministic overview chapters from transcript segments.
- Preserve traceability from note sections to transcript/index time ranges.
- Mark `B_overview` transcript outputs as overview-only.

## Out of Scope

- No LLM summarization, external APIs, OCR, frame extraction, or V2-lite Q&A.
- No claim of precise high-value detection for B-grade transcript.
- No automatic correction of transcription errors.

## Tasks

### Task 1: Tests

- Test that `run_phase3(project_dir)` writes `index/video_index.yaml`, `index/video_index.json`, and `notes/video_note.draft.md`.
- Test that Phase 3 does not overwrite existing `notes/video_note.md`.
- Test JSON includes `generated_from: index/video_index.yaml`.
- Test B-grade transcript limitations appear in YAML/JSON/note.
- Test empty transcript fails with a clear `UserFacingError` and failure log.
- Test CLI supports `--project-dir <run> --phase3`.

### Task 2: Index Generation

- Read transcript JSON from `transcript/transcript.json`.
- Group segments into time-window chapters.
- Use conservative summaries built from transcript snippets.
- Set value levels to `medium` by default for B-grade material.
- Store original snippets and confidence as `medium` or `low` according to transcript quality.

### Task 3: JSON Derivation

- Write YAML first.
- Export JSON with `generated_from: index/video_index.yaml`.
- Do not make JSON the manual source.

### Task 4: Note Generation

- Write `notes/video_note.draft.md` using the R0 note template shape as script draft.
- Include value summary, complete outline, representative segments, follow-up directions, and known limitations.
- Avoid long verbatim transcript output.

### Task 5: CLI And Logging

- Add `--project-dir` mode for existing runs.
- Add `--phase3` mode.
- Update process log for index, note, and JSON export statuses.
- Preserve failure logs on errors.

### Task 6: Verification

- Run `python -m unittest discover -s tests`.
- Run `.venv\\Scripts\\python -m unittest discover -s tests`.
- Run `python scripts/pm_sync_check.py`.
- Run `git diff --check`.
