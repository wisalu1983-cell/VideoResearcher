# V1 Phase 2 Transcription Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build the V1 Phase 2 local audio extraction and transcription adapter layer.

**Architecture:** Keep `scripts/process_video.py` as the CLI entry. Add Phase 2 helpers for FFmpeg probing/extraction, a replaceable transcription adapter interface, transcript JSON/SRT writers, and process log updates. The CLI should run Phase 1 initialization first, then optionally run Phase 2 when requested.

**Tech Stack:** Python standard library, FFmpeg/ffprobe, optional `faster-whisper` for real transcription, `unittest` for tests.

---

## Scope

- Add `--phase2` to run audio extraction and transcription after project initialization.
- Extract audio to `audio/audio.wav` with mono 16kHz PCM WAV.
- Write `transcript/transcript.srt` and `transcript/transcript.json`.
- Keep transcription adapter replaceable; default to faster-whisper when installed.
- Provide a deterministic fake adapter for automated tests.
- Update `logs/process_log.md` with Phase 2 status, tool choices, and known limitations.
- Preserve intermediate files if transcription fails.

## Out of Scope

- No OCR, frame extraction, online video download, UI, or V2-lite Q&A.
- No external API, company model, or paid tool.
- whisper.cpp is an adapter placeholder in this phase unless needed as fallback.

## Tasks

### Task 1: Tooling

- Add `.venv/` to `.gitignore`.
- Add `requirements.txt` with Phase 2 Python dependency names.
- Install FFmpeg using `winget` if it is still missing from PATH.
- Create/use a local `.venv` for Python dependencies where possible.

### Task 2: TDD Tests

- Add tests for FFmpeg command construction and missing-FFmpeg user errors.
- Add tests for writing transcript JSON/SRT from adapter segments.
- Add tests for `--phase2` using a fake transcript adapter and generated sample video/audio.
- Add tests for preserving audio and writing failure logs on transcription failure.

### Task 3: FFmpeg Extraction

- Add `audio/audio.wav` output under each run directory.
- Use `ffmpeg -y -i <input> -vn -ac 1 -ar 16000 -c:a pcm_s16le <audio>`.
- Use `ffprobe` where needed for duration metadata; degrade gracefully if duration is unavailable.

### Task 4: Transcription Adapter

- Define a stable segment shape: `id`, `start`, `end`, `text`, `confidence`.
- Implement fake adapter for tests.
- Implement faster-whisper adapter with lazy import and clear install guidance.
- Add whisper.cpp placeholder error explaining it is reserved as a later fallback.

### Task 5: Real Sample Smoke

- Run Phase 2 on `VedioSamples/AI工作流开发实战分享_Gavin Chen_20260427_CN SUB.mp4`.
- Prefer a tiny/small model and record any compatibility, model download, GPU, or runtime issue.
- If Python 3.13 is incompatible with faster-whisper, stop with evidence and recommend Python 3.11/3.12 venv.

### Task 6: Verification

- Run `python -m unittest discover -s tests`.
- Run `python scripts/pm_sync_check.py`.
- Run `git diff --check`.
- Read lints for changed files.
