---
name: video-note-synthesis
description: Synthesize final VideoResearcher notes from transcript, index, and draft notes. Use when converting notes/video_note.draft.md into final notes/video_note.md, reviewing Phase 3 note quality, or answering follow-up questions from a processed video.
---

# Video Note Synthesis

## When To Use

Use this skill after `scripts/process_video.py --phase3` generates:

- `transcript/transcript.json`
- `index/video_index.yaml`
- `index/video_index.json`
- `notes/video_note.draft.md`

## Workflow

1. Read `notes/video_note.draft.md`, `index/video_index.yaml`, and relevant transcript windows.
2. Identify the real topic structure; do not trust draft module names blindly.
3. Rewrite `notes/video_note.md` as the final human-readable note.
4. Preserve evidence time ranges for every substantive conclusion.
5. Mark low-confidence content as a clue, not a fact.
6. Update `logs/process_log.md` if synthesis changes the processing status.

## Final Note Requirements

The final note must include:

- Core conclusions in prose, not just bullets copied from transcript.
- Theme modules with conclusion, evidence time range, transcript/index basis, why it matters, follow-up questions, and quality boundaries.
- A complete outline with value markers.
- Known limitations, especially missing OCR/frame analysis or weak transcription.

## Non-Negotiables

- Never treat `video_note.draft.md` as the final note.
- Never overwrite a higher-quality `video_note.md` with script output.
- Never claim precise visual understanding unless screenshots, OCR, or frame analysis were actually used.
