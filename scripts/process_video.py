"""V1 Phase 1 local video project initializer."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable, Protocol


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_DIR = ROOT / "ProjectManager" / "Templates" / "video_project"
DEFAULT_OUTPUT_ROOT = ROOT / "outputs"
SUPPORTED_VIDEO_EXTENSIONS = {".mp4", ".mov", ".mkv"}


@dataclass(frozen=True)
class InitializationResult:
    run_dir: Path
    input_path: Path
    copied_input: bool


@dataclass(frozen=True)
class TranscriptSegment:
    id: str
    start: float
    end: float
    text: str
    confidence: float | None = None


@dataclass(frozen=True)
class TranscriptionResult:
    language: str
    duration: float | None
    tool: dict
    quality: dict
    segments: list[TranscriptSegment]


@dataclass(frozen=True)
class Phase2Result:
    audio_path: Path
    transcript_json_path: Path
    transcript_srt_path: Path


@dataclass(frozen=True)
class Phase3Result:
    yaml_path: Path
    json_path: Path
    draft_note_path: Path
    final_note_path: Path


@dataclass(frozen=True)
class Phase4Result:
    qa_report_path: Path


class TranscriptionAdapter(Protocol):
    name: str

    def transcribe(self, audio_path: Path) -> TranscriptionResult:
        ...


class UserFacingError(Exception):
    """Error that should be shown directly to the user."""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="V1 Phase 1：校验本地视频并初始化单视频项目目录。",
    )
    parser.add_argument(
        "video_path",
        nargs="?",
        type=Path,
        help="本地视频文件路径。首轮支持 mp4、mov、mkv。",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT,
        help="输出 run 的根目录。默认使用仓库内 outputs/。",
    )
    parser.add_argument(
        "--copy-input",
        action="store_true",
        help="将原始视频复制到 run 的 input/ 目录。默认只在日志中记录原路径。",
    )
    parser.add_argument(
        "--phase2",
        action="store_true",
        help="初始化项目后继续执行 Phase 2：音频抽取与本地转录。",
    )
    parser.add_argument(
        "--phase3",
        action="store_true",
        help="继续执行 Phase 3：从转录产物生成索引和笔记。",
    )
    parser.add_argument(
        "--phase4",
        action="store_true",
        help="继续执行 Phase 4：产物结构 QA、日志收口和失败记录。",
    )
    parser.add_argument(
        "--project-dir",
        type=Path,
        help="已有 video_project run 目录。用于在不重新处理视频的情况下执行 Phase 3。",
    )
    parser.add_argument(
        "--model-size",
        default="tiny",
        help="faster-whisper 模型尺寸。默认 tiny，用于首轮本地冒烟。",
    )
    return parser


def sanitize_name(name: str) -> str:
    sanitized = re.sub(r'[<>:"/\\|?*\s]+', "-", name).strip("-. ")
    return sanitized or "video"


def current_timestamp() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def validate_video_input(video_path: Path) -> Path:
    resolved = video_path.expanduser().resolve()
    if not resolved.exists():
        raise UserFacingError(
            "输入文件不存在。\n下一步建议：请检查路径是否正确，并提供本地 mp4、mov 或 mkv 视频文件。"
        )
    if not resolved.is_file():
        raise UserFacingError(
            "输入路径不是文件。\n下一步建议：请提供具体的视频文件路径，而不是目录。"
        )
    if resolved.suffix.lower() not in SUPPORTED_VIDEO_EXTENSIONS:
        supported = ", ".join(sorted(SUPPORTED_VIDEO_EXTENSIONS))
        raise UserFacingError(
            f"暂不支持该文件格式：{resolved.suffix or '无扩展名'}。\n"
            f"下一步建议：请提供 {supported} 范围内的本地视频文件。"
        )
    try:
        with resolved.open("rb"):
            pass
    except OSError as exc:
        raise UserFacingError(
            f"输入文件不可读取：{exc}\n下一步建议：请检查文件权限、占用状态或换一个可读取的视频文件。"
        ) from exc
    return resolved


def require_executable(name: str) -> str:
    executable = shutil.which(name)
    if executable is None:
        raise UserFacingError(
            f"未找到 {name}。\n下一步建议：请先安装 FFmpeg 并确认 ffmpeg / ffprobe 已加入 PATH。"
        )
    return name


def build_ffmpeg_audio_command(input_path: Path, audio_path: Path) -> list[str]:
    return [
        "ffmpeg",
        "-y",
        "-i",
        str(input_path),
        "-vn",
        "-ac",
        "1",
        "-ar",
        "16000",
        "-c:a",
        "pcm_s16le",
        str(audio_path),
    ]


def extract_audio_with_ffmpeg(input_path: Path, audio_path: Path) -> None:
    require_executable("ffmpeg")
    audio_path.parent.mkdir(parents=True, exist_ok=True)
    command = build_ffmpeg_audio_command(input_path, audio_path)
    result = subprocess.run(command, text=True, capture_output=True, check=False)
    if result.returncode != 0:
        raise UserFacingError(
            "音频抽取失败。\n"
            f"错误信息：{result.stderr.strip() or result.stdout.strip()}\n"
            "下一步建议：请确认视频可播放，或先用 FFmpeg 转码后重试。"
        )


def format_srt_timestamp(seconds: float) -> str:
    milliseconds = max(0, round(seconds * 1000))
    hours, remainder = divmod(milliseconds, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    secs, millis = divmod(remainder, 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"


def transcript_to_dict(video_id: str, transcript: TranscriptionResult) -> dict:
    return {
        "video_id": video_id,
        "language": transcript.language,
        "duration": transcript.duration,
        "tool": transcript.tool,
        "quality": transcript.quality,
        "segments": [
            {
                "id": segment.id,
                "start": format_srt_timestamp(segment.start).replace(",", "."),
                "end": format_srt_timestamp(segment.end).replace(",", "."),
                "start_seconds": segment.start,
                "end_seconds": segment.end,
                "text": segment.text,
                "confidence": segment.confidence,
            }
            for segment in transcript.segments
        ],
    }


def write_transcript_outputs(
    run_dir: Path,
    video_id: str,
    transcript: TranscriptionResult,
) -> tuple[Path, Path]:
    transcript_dir = run_dir / "transcript"
    transcript_dir.mkdir(parents=True, exist_ok=True)
    json_path = transcript_dir / "transcript.json"
    srt_path = transcript_dir / "transcript.srt"

    json_path.write_text(
        json.dumps(transcript_to_dict(video_id, transcript), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    srt_blocks = []
    for index, segment in enumerate(transcript.segments, start=1):
        srt_blocks.append(
            "\n".join(
                [
                    str(index),
                    f"{format_srt_timestamp(segment.start)} --> {format_srt_timestamp(segment.end)}",
                    segment.text.strip(),
                ]
            )
        )
    srt_path.write_text("\n\n".join(srt_blocks) + ("\n" if srt_blocks else ""), encoding="utf-8")
    return json_path, srt_path


class FasterWhisperAdapter:
    name = "faster-whisper"

    def __init__(
        self,
        model_size: str = "tiny",
        device: str = "cpu",
        compute_type: str = "int8",
    ) -> None:
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type

    def transcribe(self, audio_path: Path) -> TranscriptionResult:
        try:
            from faster_whisper import WhisperModel
        except ImportError as exc:
            raise UserFacingError(
                "未安装 faster-whisper。\n下一步建议：运行 `.venv\\Scripts\\python -m pip install -r requirements.txt` 后重试。"
            ) from exc

        model = WhisperModel(
            self.model_size,
            device=self.device,
            compute_type=self.compute_type,
        )
        segments_iter, info = model.transcribe(str(audio_path), vad_filter=True)
        segments = [
            TranscriptSegment(
                id=f"seg-{index:03d}",
                start=float(segment.start),
                end=float(segment.end),
                text=segment.text.strip(),
                confidence=None,
            )
            for index, segment in enumerate(segments_iter, start=1)
        ]
        duration = float(getattr(info, "duration", 0.0) or (segments[-1].end if segments else 0.0))
        language = str(getattr(info, "language", "") or "")
        timestamp_quality = "approximate" if segments else "unreliable"
        transcription_quality = "B_overview" if segments else "C_unreliable"
        known_limitations = (
            [f"{self.model_size} 模型用于本地冒烟，需人工抽检后才能判定是否可精确追问"]
            if segments
            else ["未识别出可用转录片段"]
        )
        return TranscriptionResult(
            language=language,
            duration=duration,
            tool={
                "name": self.name,
                "version": self.model_size,
                "model": self.model_size,
                "parameters": {
                    "device": self.device,
                    "compute_type": self.compute_type,
                    "vad_filter": True,
                },
            },
            quality={
                "transcription_quality": transcription_quality,
                "timestamp_quality": timestamp_quality,
                "known_limitations": known_limitations,
            },
            segments=segments,
        )


class WhisperCppAdapter:
    name = "whisper.cpp"

    def transcribe(self, audio_path: Path) -> TranscriptionResult:
        raise UserFacingError(
            "whisper.cpp adapter 已预留但尚未启用。\n下一步建议：优先使用 faster-whisper；需要跨平台备用时再接入 whisper.cpp。"
        )


def update_phase2_process_log(
    run_dir: Path,
    *,
    audio_done: bool,
    transcription_done: bool | None,
) -> None:
    log_path = run_dir / "logs" / "process_log.md"
    text = read_text(log_path)
    text = text.replace(
        "| 音频抽取 | pending |  |  | FFmpeg | Phase 2 执行 |",
        "| 音频抽取 | done | input video | audio/audio.wav | FFmpeg | Phase 2 音频抽取完成 |"
        if audio_done
        else "| 音频抽取 | failed | input video | audio/audio.wav | FFmpeg | Phase 2 音频抽取失败 |",
    )
    if transcription_done is not None:
        transcription_line = (
            "| 转录 | done | audio/audio.wav | transcript/transcript.srt, transcript/transcript.json | faster-whisper / adapter | Phase 2 转录完成 |"
            if transcription_done
            else "| 转录 | failed | audio/audio.wav |  | faster-whisper / adapter | Phase 2 转录失败，已保留中间结果 |"
        )
        text = text.replace(
            "| 转录 | pending |  |  | faster-whisper / whisper.cpp | Phase 2 执行 |",
            transcription_line,
        )
        text = text.replace(
            "| 转录 | failed | audio/audio.wav |  | faster-whisper / adapter | Phase 2 转录失败，已保留中间结果 |",
            transcription_line,
        )
    if transcription_done:
        text = text.replace(
            "- finished_at:",
            f"- finished_at: {datetime.now().astimezone().isoformat(timespec='seconds')}",
        )
        text = text.replace(
            "- Phase 1 只完成本地视频输入校验和项目目录初始化。",
            "- Phase 1 已完成本地视频输入校验和项目目录初始化。",
        )
        text = text.replace(
            "- 尚未执行 FFmpeg 音频抽取、转录、索引生成或笔记生成。",
            "- Phase 2 已执行 FFmpeg 音频抽取和本地转录；转录质量需人工抽检后确认。",
        )
        text = text.replace(
            "- 下一步：进入 Phase 2 音频抽取与转录。",
            "- 下一步：进入 Phase 3 索引与笔记生成。",
        )
    log_path.write_text(text, encoding="utf-8")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def write_failure_log(
    run_dir: Path,
    *,
    stage: str,
    error_type: str,
    error_message: str,
    input_file: Path,
    attempted_fixes: list[str],
    user_action_needed: str,
    optimization_notes: str = "Failure captured for future workflow hardening.",
) -> None:
    failure_path = run_dir / "logs" / "failure_log.json"
    record = {
        "time": datetime.now().astimezone().isoformat(timespec="seconds"),
        "video_id": run_dir.name,
        "stage": stage,
        "error_type": error_type,
        "error_message": error_message,
        "input_file": str(input_file),
        "attempted_fixes": attempted_fixes,
        "remaining_problem": error_message,
        "user_action_needed": user_action_needed,
        "optimization_notes": optimization_notes,
    }
    failures: list[dict] = []
    if failure_path.exists():
        try:
            existing = json.loads(failure_path.read_text(encoding="utf-8"))
            failures = [
                item
                for item in list(existing.get("failures") or [])
                if any(item.get(key) for key in ("stage", "error_type", "error_message"))
            ]
        except json.JSONDecodeError:
            failures = []
    failures.append(record)
    failure_path.write_text(
        json.dumps({"failures": failures}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def parse_transcript_timestamp(value: str | int | float) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    hours, minutes, rest = value.split(":")
    seconds = rest.replace(",", ".")
    return int(hours) * 3600 + int(minutes) * 60 + float(seconds)


def load_transcript(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise UserFacingError(
            "未找到 transcript/transcript.json。\n下一步建议：请先完成 Phase 2 转录，再执行 Phase 3。"
        ) from exc
    except json.JSONDecodeError as exc:
        raise UserFacingError(
            f"转录 JSON 不可解析：{exc}\n下一步建议：请重新生成 transcript/transcript.json。"
        ) from exc


def safe_scalar(value: object) -> str:
    if value is None:
        return ""
    text = str(value)
    return text.replace("\n", " ").replace("\r", " ").strip()


def yaml_quote(value: object) -> str:
    text = safe_scalar(value)
    escaped = text.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def render_yaml(value: object, indent: int = 0) -> list[str]:
    prefix = " " * indent
    if isinstance(value, dict):
        lines: list[str] = []
        for key, child in value.items():
            if isinstance(child, (dict, list)):
                lines.append(f"{prefix}{key}:")
                lines.extend(render_yaml(child, indent + 2))
            else:
                lines.append(f"{prefix}{key}: {yaml_quote(child)}")
        return lines
    if isinstance(value, list):
        if not value:
            return [f"{prefix}[]"]
        lines = []
        for item in value:
            if isinstance(item, dict):
                lines.append(f"{prefix}-")
                lines.extend(render_yaml(item, indent + 2))
            else:
                lines.append(f"{prefix}- {yaml_quote(item)}")
        return lines
    return [f"{prefix}{yaml_quote(value)}"]


def format_index_time(seconds: float | None) -> str:
    if seconds is None:
        return ""
    milliseconds = max(0, round(seconds * 1000))
    hours, remainder = divmod(milliseconds, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    secs, _millis = divmod(remainder, 1000)
    return f"{hours:02}:{minutes:02}:{secs:02}"


def title_from_run_dir(run_dir: Path) -> str:
    parts = run_dir.name.rsplit("-", 2)
    if len(parts) >= 3 and parts[-2].isdigit() and parts[-1].isdigit():
        return "-".join(parts[:-2]).replace("-", " ")
    return run_dir.name.replace("-", " ")


def segment_seconds(segment: dict, key: str, fallback_key: str) -> float:
    if key in segment and segment[key] is not None:
        return float(segment[key])
    return parse_transcript_timestamp(segment[fallback_key])


def build_overview_chapters(segments: list[dict], window_seconds: int = 600) -> list[dict]:
    chapters: list[dict] = []
    current: list[dict] = []
    window_start: float | None = None

    for segment in segments:
        start = segment_seconds(segment, "start_seconds", "start")
        if window_start is None:
            window_start = start
        if current and start - window_start >= window_seconds:
            chapters.append(build_chapter(len(chapters) + 1, current))
            current = []
            window_start = start
        current.append(segment)

    if current:
        chapters.append(build_chapter(len(chapters) + 1, current))
    return chapters


VALUE_KEYWORDS = [
    "AI",
    "agent",
    "模型",
    "工具",
    "案例",
    "成本",
    "USD",
    "美金",
    "效率",
    "流程",
    "框架",
    "做法",
    "方法",
    "限制",
    "风险",
    "風險",
    "测试",
    "測試",
    "验证",
    "驗證",
    "網站",
    "网页",
    "網頁",
    "字幕",
    "转录",
    "轉錄",
    "Whisper",
    "Visper",
    "Google",
    "Cursor",
]

FILLER_PHRASES = [
    "大家好",
    "看一下",
    "然后继续",
    "然後",
    "好",
    "OK",
]


def score_snippet(text: str, order: int) -> tuple[int, int]:
    keyword_score = sum(1 for keyword in VALUE_KEYWORDS if keyword.lower() in text.lower())
    filler_penalty = sum(1 for phrase in FILLER_PHRASES if phrase in text)
    length_score = min(len(text), 40)
    return (keyword_score * 100 + length_score - filler_penalty * 30, -order)


def select_representative_snippets(snippets: list[str], limit: int = 3) -> list[str]:
    ranked = sorted(
        enumerate(snippets),
        key=lambda item: score_snippet(item[1], item[0]),
        reverse=True,
    )
    selected = [text for _index, text in ranked[:limit]]
    return selected or snippets[:limit]


def build_chapter(index: int, segments: list[dict]) -> dict:
    start = segment_seconds(segments[0], "start_seconds", "start")
    end = segment_seconds(segments[-1], "end_seconds", "end")
    snippets = [safe_scalar(segment.get("text")) for segment in segments if safe_scalar(segment.get("text"))]
    representative = select_representative_snippets(snippets)
    summary = " / ".join(representative)[:180]
    segment_id = f"seg-{index:03d}-overview"
    return {
        "id": f"ch-{index:03d}",
        "title": f"{format_index_time(start)} 概览片段",
        "start": format_index_time(start),
        "end": format_index_time(end),
        "summary": summary,
        "value_level": "medium",
        "tags": ["auto-generated", "overview"],
        "segments": [
            {
                "id": segment_id,
                "start": format_index_time(start),
                "end": format_index_time(end),
                "type": "concept",
                "summary": summary,
                "key_points": representative[:2],
                "original_terms": [],
                "original_snippets": representative,
                "supports_questions": [
                    "这一时间段主要讲了什么？",
                    "这里有哪些值得后续追问的线索？",
                ],
                "confidence": "medium",
            }
        ],
    }


def build_index_data(run_dir: Path, transcript: dict) -> dict:
    segments = transcript.get("segments") or []
    if not segments:
        raise UserFacingError(
            "转录中没有可用片段，无法生成索引。\n下一步建议：请重新执行 Phase 2，或补充可用字幕/转录文本。"
        )
    quality = transcript.get("quality") or {}
    return {
        "video": {
            "id": run_dir.name,
            "title": title_from_run_dir(run_dir),
            "source_type": "local_video",
            "source_path": "",
            "language": transcript.get("language", ""),
            "duration": transcript.get("duration", ""),
            "processed_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        },
        "analysis_profile": {
            "user_focus": "overview",
            "video_type": "unknown",
            "value_directions": [
                {
                    "id": "vd-001",
                    "description": "基于 B 档转录的概览级自动索引，需人工复核高价值判断。",
                }
            ],
        },
        "chapters": build_overview_chapters(segments),
        "follow_up_index": {
            "suggested_questions": [
                "这个视频的主要脉络是什么？",
                "哪些时间段值得人工复核？",
                "有哪些术语或时间戳需要校正？",
            ],
            "important_topics": [],
        },
        "quality": {
            "transcription_quality": quality.get("transcription_quality", "B_overview"),
            "timestamp_quality": quality.get("timestamp_quality", "approximate"),
            "known_limitations": quality.get("known_limitations", [])
            + ["Phase 3 自动生成分析草稿，时间戳或术语存在风险"],
        },
    }


def write_index_outputs(run_dir: Path, index_data: dict) -> tuple[Path, Path]:
    index_dir = run_dir / "index"
    index_dir.mkdir(parents=True, exist_ok=True)
    yaml_path = index_dir / "video_index.yaml"
    json_path = index_dir / "video_index.json"
    yaml_path.write_text("\n".join(render_yaml(index_data)) + "\n", encoding="utf-8")
    json_data = {"generated_from": "index/video_index.yaml", **index_data}
    json_path.write_text(
        json.dumps(json_data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return yaml_path, json_path


def infer_module_title(text: str) -> str:
    lowered = text.lower()
    module_rules = [
        (("成本", "usd", "美金", "效率", "時間", "时间", "字幕", "外包"), "成本、效率与投入产出"),
        (("限制", "風險", "风险", "不會", "問題", "问题", "治理"), "限制、风险与待复核点"),
        (("案例", "成功", "測試", "测试", "網站", "网页", "網頁"), "案例过程与验证结果"),
        (("步驟", "步骤", "流程", "框架", "做法", "方法"), "方法框架与操作流程"),
        (("ai", "模型", "agent", "工具", "cursor", "visco", "google"), "AI 工具链与能力边界"),
    ]
    for keywords, title in module_rules:
        if any(keyword in lowered or keyword in text for keyword in keywords):
            return title
    return "内容脉络与可追问线索"


def build_note_modules(chapters: list[dict], limit: int = 4) -> list[dict]:
    modules: list[dict] = []
    seen_titles: set[str] = set()
    for chapter in chapters:
        segment = chapter["segments"][0]
        snippets = segment.get("original_snippets", [])
        evidence_text = "；".join(snippets) or safe_scalar(segment.get("summary"))
        title = infer_module_title(evidence_text)
        if title in seen_titles:
            continue
        seen_titles.add(title)
        modules.append(
            {
                "title": title,
                "time_range": f"{segment['start']}-{segment['end']}",
                "claim": safe_scalar(segment.get("summary")),
                "evidence": evidence_text,
            }
        )
        if len(modules) >= limit:
            break
    if len(modules) < min(limit, len(chapters)):
        used_ranges = {module["time_range"] for module in modules}
        for chapter in chapters:
            segment = chapter["segments"][0]
            time_range = f"{segment['start']}-{segment['end']}"
            if time_range in used_ranges:
                continue
            snippets = segment.get("original_snippets", [])
            evidence_text = "；".join(snippets) or safe_scalar(segment.get("summary"))
            modules.append(
                {
                    "title": f"{infer_module_title(evidence_text)}（{segment['start']}）",
                    "time_range": time_range,
                    "claim": safe_scalar(segment.get("summary")),
                    "evidence": evidence_text,
                }
            )
            if len(modules) >= limit:
                break
    return modules


def write_video_note_draft(run_dir: Path, index_data: dict) -> Path:
    note_path = run_dir / "notes" / "video_note.draft.md"
    note_path.parent.mkdir(parents=True, exist_ok=True)
    chapters = index_data["chapters"]
    outline_rows = [
        f"| {chapter['start']}-{chapter['end']} | {chapter['title']} | {chapter['summary']} | {chapter['value_level']} |"
        for chapter in chapters
    ]
    module_sections = []
    for module in build_note_modules(chapters):
        module_sections.append(
            "\n".join(
                [
                    f"### {module['title']}",
                    "",
                    f"- 分析判断：{module['claim']}",
                    f"- 证据时间段：{module['time_range']}",
                    f"- 转录线索：{module['evidence']}",
                    "- 后续复核：回看该时间段，确认术语、画面信息和是否可升级为高价值片段。",
                ]
            )
        )
    limitations = index_data["quality"]["known_limitations"]
    note = "\n".join(
        [
            f"# {index_data['video']['title']} 笔记",
            "",
            "> 生成方式：脚本基于 `transcript/transcript.json` 的音频转录和 `index/video_index.yaml` 生成结构草稿。",
            "> 当前质量：B_overview draft。正式 `video_note.md` 必须经过 Agent synthesis pass，不应直接使用本草稿作为最终笔记。",
            "",
            "## 1. 核心结论",
            "",
            f"- 视频主题：`{index_data['video']['title']}`，当前可识别为一场围绕主题展开的经验分享或流程说明。",
            "- 高价值判断：有可继续追问的观点、方法或案例线索，但当前转录为概览级，需复核后再沉淀为确定结论。",
            "- 阅读建议：先看下方主题模块，再用证据时间段回查转录或原视频，避免只依赖片段拼接。",
            "",
            "## 2. 主题模块",
            "",
            *module_sections,
            "",
            "## 3. 完整大纲",
            "",
            "| 时间段 | 章节 | 核心内容 | 价值标记 |",
            "|---|---|---|---|",
            *outline_rows,
            "",
            "## 4. 可追问方向",
            "",
            "- 这场分享中最值得复用的方法框架是什么？对应证据时间段在哪里？",
            "- 哪些案例体现了 AI 工作流的成本或效率收益？",
            "- 哪些结论依赖画面、代码或网页操作，需要在 V3 画面能力里补充核对？",
            "- 哪些术语被转录错了，会影响后续检索和追问？",
            "",
            "## 5. 不确定性与质量边界",
            "",
            *[f"- {limitation}" for limitation in limitations],
            "- 当前笔记只基于音频转录和文本索引，未综合画面、OCR、代码或网页操作细节。",
            "- 观点级结论必须能回溯到证据时间段；证据不足时只作为追问线索保留。",
            "",
        ]
    )
    note_path.write_text(note, encoding="utf-8")
    return note_path


def update_phase3_process_log(run_dir: Path, *, success: bool) -> None:
    log_path = run_dir / "logs" / "process_log.md"
    text = read_text(log_path)
    status = "done" if success else "failed"
    text = text.replace(
        "| 索引生成 | pending |  |  | Agent / script | Phase 3 执行 |",
        f"| 索引生成 | {status} | transcript/transcript.json | index/video_index.yaml | process_video.py | Phase 3 结构索引生成{'完成' if success else '失败'} |",
    )
    text = text.replace(
        "| 笔记草稿生成 | pending |  |  | process_video.py | Phase 3 执行 |",
        f"| 笔记草稿生成 | {status} | index/video_index.yaml | notes/video_note.draft.md | process_video.py | Phase 3 脚本草稿生成{'完成' if success else '失败'} |",
    )
    text = text.replace(
        "| 笔记生成 | pending |  |  | Agent | Phase 3 执行 |",
        f"| 笔记草稿生成 | {status} | index/video_index.yaml | notes/video_note.draft.md | process_video.py | Phase 3 脚本草稿生成{'完成' if success else '失败'} |",
    )
    text = text.replace(
        "| JSON 导出 | pending |  |  | script | Phase 3 执行 |",
        f"| JSON 导出 | {status} | index/video_index.yaml | index/video_index.json | process_video.py | Phase 3 JSON 派生{'完成' if success else '失败'} |",
    )
    if success:
        text = text.replace(
            "- 下一步：进入 Phase 3 索引与笔记生成。",
            "- 下一步：执行 Agent synthesis pass 生成 notes/video_note.md，通过后进入 Phase 4 日志、失败处理与 QA。",
        )
        text = text.replace(
            "- Phase 2 已执行 FFmpeg 音频抽取和本地转录；转录质量需人工抽检后确认。",
            "- Phase 2 已执行 FFmpeg 音频抽取和本地转录；Phase 3 已生成索引和 notes/video_note.draft.md，正式笔记需 Agent synthesis pass。",
        )
    log_path.write_text(text, encoding="utf-8")


def run_phase3(run_dir: Path) -> Phase3Result:
    transcript_path = run_dir / "transcript" / "transcript.json"
    try:
        transcript = load_transcript(transcript_path)
        index_data = build_index_data(run_dir, transcript)
        yaml_path, json_path = write_index_outputs(run_dir, index_data)
        draft_note_path = write_video_note_draft(run_dir, index_data)
        update_phase3_process_log(run_dir, success=True)
        return Phase3Result(
            yaml_path=yaml_path,
            json_path=json_path,
            draft_note_path=draft_note_path,
            final_note_path=run_dir / "notes" / "video_note.md",
        )
    except UserFacingError as exc:
        update_phase3_process_log(run_dir, success=False)
        write_failure_log(
            run_dir,
            stage="index_generation",
            error_type=type(exc).__name__,
            error_message=str(exc),
            input_file=transcript_path,
            attempted_fixes=["已保留 transcript/transcript.json"],
            user_action_needed="请先补充可用转录片段，再重新执行 Phase 3。",
        )
        raise


def check_json_file(path: Path) -> tuple[bool, str]:
    if not path.exists():
        return False, "missing"
    try:
        json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return False, f"invalid json: {exc}"
    return True, "valid json"


def check_text_file(path: Path) -> tuple[bool, str]:
    if not path.exists():
        return False, "missing"
    if not path.read_text(encoding="utf-8").strip():
        return False, "empty"
    return True, "present"


def check_final_note_file(path: Path) -> tuple[bool, str]:
    ok, detail = check_text_file(path)
    if not ok:
        return ok, detail
    text = path.read_text(encoding="utf-8")
    if any(token in text for token in ("<视频标题>", "<章节>", "<问题 1>", "<摘要>")):
        return False, "template placeholders remain"
    return True, "present"


def build_phase4_checks(run_dir: Path) -> list[dict]:
    checks = [
        ("transcript/transcript.srt", check_text_file),
        ("transcript/transcript.json", check_json_file),
        ("index/video_index.yaml", check_text_file),
        ("index/video_index.json", check_json_file),
        ("notes/video_note.draft.md", check_text_file),
        ("notes/video_note.md", check_final_note_file),
        ("logs/process_log.md", check_text_file),
        ("logs/failure_log.json", check_json_file),
        ("logs/index_change_log.md", check_text_file),
    ]
    results = []
    for relative_path, checker in checks:
        ok, detail = checker(run_dir / relative_path)
        results.append(
            {
                "path": relative_path,
                "status": "PASS" if ok else "FAIL",
                "detail": detail,
            }
        )
    return results


def write_phase4_qa_report(run_dir: Path, checks: list[dict]) -> Path:
    report_path = run_dir / "logs" / "qa_report.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    rows = [f"| {item['path']} | {item['status']} | {item['detail']} |" for item in checks]
    failed = [item for item in checks if item["status"] != "PASS"]
    report = "\n".join(
        [
            "# Phase 4 QA Report",
            "",
            "## V1 产物结构验收",
            "",
            "| 产物 | 结果 | 说明 |",
            "|---|---|---|",
            *rows,
            "",
            "## 结论",
            "",
            "PASS：V1 相关产物结构齐备，可进入收口复核。"
            if not failed
            else "FAIL：存在缺失或不可解析产物，需要修复后重新执行 Phase 4。",
            "",
        ]
    )
    report_path.write_text(report, encoding="utf-8")
    return report_path


def update_phase4_process_log(run_dir: Path, *, success: bool, qa_report_path: Path) -> None:
    log_path = run_dir / "logs" / "process_log.md"
    text = read_text(log_path)
    status = "done" if success else "failed"
    replacement = (
        f"| QA 检查 | {status} | V1 artifacts | logs/qa_report.md | process_video.py | "
        f"Phase 4 QA {'完成' if success else '失败'} |"
    )
    lines = []
    replaced = False
    for line in text.splitlines():
        if line.startswith("| QA 检查 |"):
            lines.append(replacement)
            replaced = True
        else:
            lines.append(line)
    if not replaced:
        lines.append(replacement)
    text = "\n".join(lines) + "\n"
    text = re.sub(
        r"- finished_at:.*",
        f"- finished_at: {datetime.now().astimezone().isoformat(timespec='seconds')}",
        text,
        count=1,
    )
    text = text.replace(
        "- 下一步：执行 Agent synthesis pass 生成 notes/video_note.md，通过后进入 Phase 4 日志、失败处理与 QA。",
        "- 下一步：Phase 4 QA 已完成，进入 V1 收口复核。",
    )
    text = text.replace(
        "- 下一步：人工抽检 Agent 改写后的 Phase 3 笔记质量，通过后再进入 Phase 4 日志、失败处理与 QA。",
        "- 下一步：Phase 4 QA 已完成，进入 V1 收口复核。",
    )
    log_path.write_text(text, encoding="utf-8")


def run_phase4(run_dir: Path) -> Phase4Result:
    checks = build_phase4_checks(run_dir)
    qa_report_path = write_phase4_qa_report(run_dir, checks)
    failed = [item for item in checks if item["status"] != "PASS"]
    update_phase4_process_log(run_dir, success=not failed, qa_report_path=qa_report_path)
    if failed:
        failed_paths = ", ".join(item["path"] for item in failed)
        error_message = f"QA 检查失败，缺失或无效产物：{failed_paths}"
        write_failure_log(
            run_dir,
            stage="qa_check",
            error_type="Phase4QaFailed",
            error_message=error_message,
            input_file=run_dir,
            attempted_fixes=["已写入 logs/qa_report.md，保留现有中间结果"],
            user_action_needed="请补齐失败产物后重新执行 Phase 4。",
            optimization_notes="Phase 4 artifact validation failed.",
        )
        raise UserFacingError(f"{error_message}\n下一步建议：请查看 logs/qa_report.md。")
    return Phase4Result(qa_report_path=qa_report_path)


def run_phase2(
    run_dir: Path,
    input_path: Path,
    *,
    adapter: TranscriptionAdapter | None = None,
    extract_audio: Callable[[Path, Path], None] = extract_audio_with_ffmpeg,
) -> Phase2Result:
    audio_path = run_dir / "audio" / "audio.wav"
    adapter = adapter or FasterWhisperAdapter()
    try:
        audio_path.parent.mkdir(parents=True, exist_ok=True)
        extract_audio(input_path, audio_path)
        update_phase2_process_log(run_dir, audio_done=True, transcription_done=None)
        transcript = adapter.transcribe(audio_path)
        json_path, srt_path = write_transcript_outputs(run_dir, run_dir.name, transcript)
        update_phase2_process_log(run_dir, audio_done=True, transcription_done=True)
        return Phase2Result(
            audio_path=audio_path,
            transcript_json_path=json_path,
            transcript_srt_path=srt_path,
        )
    except UserFacingError:
        update_phase2_process_log(run_dir, audio_done=audio_path.exists(), transcription_done=False)
        raise
    except Exception as exc:
        update_phase2_process_log(run_dir, audio_done=audio_path.exists(), transcription_done=False)
        write_failure_log(
            run_dir,
            stage="transcription",
            error_type=type(exc).__name__,
            error_message=str(exc),
            input_file=input_path,
            attempted_fixes=["已保留 audio/audio.wav 中间结果"],
            user_action_needed="请检查转录依赖、模型配置或改用备用 adapter。",
        )
        raise UserFacingError(
            f"本地转录失败：{exc}\n下一步建议：请检查转录依赖、模型配置或改用备用 adapter。"
        ) from exc


def unique_run_dir(output_root: Path, base_name: str) -> Path:
    candidate = output_root / base_name
    if not candidate.exists():
        return candidate
    counter = 2
    while True:
        next_candidate = output_root / f"{base_name}-{counter:02d}"
        if not next_candidate.exists():
            return next_candidate
        counter += 1


def write_initial_process_log(
    run_dir: Path,
    input_path: Path,
    copied_input: bool,
    started_at: str,
) -> None:
    log_path = run_dir / "logs" / "process_log.md"
    copy_mode = "已复制到 input/ 目录" if copied_input else "仅记录原始路径，未复制原视频"
    log_path.write_text(
        "\n".join(
            [
                "# 处理日志",
                "",
                "## 基本信息",
                "",
                f"- video_id: {run_dir.name}",
                f"- input_file: {input_path}",
                f"- output_dir: {run_dir}",
                f"- started_at: {started_at}",
                "- finished_at:",
                "- environment: local",
                "- operator: CLI",
                f"- input_archive: {copy_mode}",
                "",
                "## 阶段记录",
                "",
                "| 阶段 | 状态 | 输入 | 输出 | 工具 / 参数 | 备注 |",
                "|---|---|---|---|---|---|",
                f"| 输入校验 | done | {input_path} | {run_dir} | process_video.py | Phase 1 初始化完成 |",
                "| 音频抽取 | pending |  |  | FFmpeg | Phase 2 执行 |",
                "| 转录 | pending |  |  | faster-whisper / whisper.cpp | Phase 2 执行 |",
                "| 索引生成 | pending |  |  | Agent / script | Phase 3 执行 |",
                "| 笔记草稿生成 | pending |  |  | process_video.py | Phase 3 执行 |",
                "| Agent 笔记合成 | pending | notes/video_note.draft.md, index/video_index.yaml, transcript/transcript.json | notes/video_note.md | Agent synthesis | Phase 3 人类可读笔记 |",
                "| JSON 导出 | pending |  |  | script | Phase 3 执行 |",
                "| QA 检查 | pending |  |  |  | Phase 4 执行 |",
                "",
                "## 已知限制",
                "",
                "- Phase 1 只完成本地视频输入校验和项目目录初始化。",
                "- 尚未执行 FFmpeg 音频抽取、转录、索引生成或笔记生成。",
                "",
                "## 后续动作",
                "",
                "- 下一步：进入 Phase 2 音频抽取与转录。",
                "",
            ]
        ),
        encoding="utf-8",
    )


def initialize_project(
    video_path: Path,
    *,
    output_root: Path = DEFAULT_OUTPUT_ROOT,
    copy_input: bool = False,
    timestamp: str | None = None,
) -> InitializationResult:
    input_path = validate_video_input(video_path)
    if not TEMPLATE_DIR.exists():
        raise UserFacingError(
            f"项目模板不存在：{TEMPLATE_DIR}\n下一步建议：请先恢复 video_project 模板后再重试。"
        )

    output_root = output_root.expanduser().resolve()
    output_root.mkdir(parents=True, exist_ok=True)

    run_timestamp = timestamp or current_timestamp()
    base_name = f"{sanitize_name(input_path.stem)}-{run_timestamp}"
    run_dir = unique_run_dir(output_root, base_name)
    shutil.copytree(TEMPLATE_DIR, run_dir)

    if copy_input:
        shutil.copy2(input_path, run_dir / "input" / input_path.name)

    started_at = datetime.now().astimezone().isoformat(timespec="seconds")
    write_initial_process_log(run_dir, input_path, copy_input, started_at)

    return InitializationResult(
        run_dir=run_dir,
        input_path=input_path,
        copied_input=copy_input,
    )


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        phase2_result = None
        phase3_result = None
        phase4_result = None
        if args.project_dir is not None:
            if not args.phase3 and not args.phase4:
                parser.error("--project-dir 当前需配合 --phase3 或 --phase4 执行已有项目目录")
            run_dir = args.project_dir.expanduser().resolve()
            if not run_dir.exists():
                raise UserFacingError(
                    f"项目目录不存在：{run_dir}\n下一步建议：请提供已有 video_project run 目录。"
                )
            if args.phase3:
                phase3_result = run_phase3(run_dir)
                print("Phase 3 索引与笔记生成完成。")
                print(f"YAML：{phase3_result.yaml_path}")
                print(f"JSON：{phase3_result.json_path}")
                print(f"草稿笔记：{phase3_result.draft_note_path}")
                print(f"正式笔记：{phase3_result.final_note_path}（需 Agent synthesis pass，不由脚本覆盖）")
            if args.phase4:
                phase4_result = run_phase4(run_dir)
                print("Phase 4 QA 收口完成。")
                print(f"QA 报告：{phase4_result.qa_report_path}")
            return 0

        if args.video_path is None:
            parser.error("需要提供本地视频路径，或使用 --project-dir 指定已有项目目录")

        result = initialize_project(
            args.video_path,
            output_root=args.output_root,
            copy_input=args.copy_input,
        )
        if args.phase2:
            phase2_result = run_phase2(
                result.run_dir,
                result.input_path,
                adapter=FasterWhisperAdapter(model_size=args.model_size),
            )
        if args.phase3:
            phase3_result = run_phase3(result.run_dir)
        if args.phase4:
            phase4_result = run_phase4(result.run_dir)
    except UserFacingError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print("Phase 1 初始化完成。")
    print(f"输出项目目录：{result.run_dir}")
    if phase2_result is None:
        print("下一步：进入 Phase 2 音频抽取与转录。")
    else:
        print("Phase 2 音频抽取与转录完成。")
        print(f"音频文件：{phase2_result.audio_path}")
        print(f"SRT：{phase2_result.transcript_srt_path}")
        print(f"JSON：{phase2_result.transcript_json_path}")
    if phase3_result is not None:
        print("Phase 3 索引与笔记生成完成。")
        print(f"YAML：{phase3_result.yaml_path}")
        print(f"JSON：{phase3_result.json_path}")
        print(f"草稿笔记：{phase3_result.draft_note_path}")
        print(f"正式笔记：{phase3_result.final_note_path}（需 Agent synthesis pass，不由脚本覆盖）")
    if phase4_result is not None:
        print("Phase 4 QA 收口完成。")
        print(f"QA 报告：{phase4_result.qa_report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
