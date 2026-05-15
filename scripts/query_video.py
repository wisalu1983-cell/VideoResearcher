"""V2-lite video project query and retrieval."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from process_video import UserFacingError, parse_transcript_timestamp, format_index_time, render_yaml


@dataclass(frozen=True)
class SegmentMatch:
    chapter_id: str
    segment_id: str
    start: str
    end: str
    summary: str
    match_fields: tuple[str, ...]
    confidence: str
    chapter_title: str
    chapter_summary: str


def load_index(project_dir: Path) -> dict:
    json_path = project_dir / "index" / "video_index.json"
    if not json_path.exists():
        raise UserFacingError(
            "未找到 index/video_index.json。\n下一步建议：请先完成 V1 Phase 3 生成索引。"
        )
    try:
        return json.loads(json_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise UserFacingError(
            f"索引 JSON 不可解析：{exc}\n下一步建议：请重新生成索引。"
        ) from exc


def load_transcript(project_dir: Path) -> dict:
    json_path = project_dir / "transcript" / "transcript.json"
    if not json_path.exists():
        raise UserFacingError(
            "未找到 transcript/transcript.json。\n下一步建议：请先完成 V1 Phase 2 转录。"
        )
    try:
        return json.loads(json_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise UserFacingError(
            f"转录 JSON 不可解析：{exc}\n下一步建议：请重新生成转录。"
        ) from exc


def _text_contains_keyword(text: str, keyword: str) -> bool:
    return keyword.lower() in text.lower()


def _collect_searchable_text(segment: dict, chapter: dict) -> dict[str, str]:
    fields: dict[str, str] = {}
    if segment.get("summary"):
        fields["summary"] = str(segment["summary"])
    if segment.get("key_points"):
        fields["key_points"] = " ".join(str(point) for point in segment["key_points"])
    if segment.get("original_snippets"):
        fields["original_snippets"] = " ".join(str(s) for s in segment["original_snippets"])
    if chapter.get("title"):
        fields["chapter_title"] = str(chapter["title"])
    if chapter.get("summary"):
        fields["chapter_summary"] = str(chapter["summary"])
    return fields


def search_segments(index_data: dict, keywords: list[str]) -> list[SegmentMatch]:
    if not keywords:
        return []
    chapters = index_data.get("chapters") or []
    matches: list[tuple[int, SegmentMatch]] = []
    for chapter in chapters:
        chapter_id = chapter.get("id", "")
        for segment in chapter.get("segments") or []:
            searchable = _collect_searchable_text(segment, chapter)
            matched_fields: list[str] = []
            total_hits = 0
            for field_name, text in searchable.items():
                field_hits = sum(1 for kw in keywords if _text_contains_keyword(text, kw))
                if field_hits > 0:
                    matched_fields.append(field_name)
                    total_hits += field_hits
            if not matched_fields:
                continue
            score = len(matched_fields) * 10 + total_hits
            match = SegmentMatch(
                chapter_id=chapter_id,
                segment_id=segment.get("id", ""),
                start=segment.get("start", ""),
                end=segment.get("end", ""),
                summary=str(segment.get("summary", "")),
                match_fields=tuple(matched_fields),
                confidence=str(segment.get("confidence", "medium")),
                chapter_title=str(chapter.get("title", "")),
                chapter_summary=str(chapter.get("summary", "")),
            )
            matches.append((score, match))
    matches.sort(key=lambda item: item[0], reverse=True)
    return [match for _score, match in matches]


def _parse_time_to_seconds(time_str: str) -> float:
    return parse_transcript_timestamp(time_str)


def get_transcript_range(project_dir: Path, start: str, end: str) -> list[dict]:
    transcript = load_transcript(project_dir)
    segments = transcript.get("segments") or []
    start_seconds = _parse_time_to_seconds(start)
    end_seconds = _parse_time_to_seconds(end)
    result = []
    for segment in segments:
        seg_start = segment.get("start_seconds")
        seg_end = segment.get("end_seconds")
        if seg_start is None or seg_end is None:
            seg_start = _parse_time_to_seconds(segment.get("start", "0"))
            seg_end = _parse_time_to_seconds(segment.get("end", "0"))
        if seg_end < start_seconds or seg_start > end_seconds:
            continue
        result.append({
            "id": segment.get("id", ""),
            "start": segment.get("start", ""),
            "end": segment.get("end", ""),
            "text": segment.get("text", ""),
        })
    return result


def get_quality_warnings(index_data: dict) -> list[str]:
    quality = index_data.get("quality") or {}
    warnings: list[str] = []
    tq = quality.get("transcription_quality", "")
    if tq.startswith("B"):
        warnings.append("B_overview 转录，时间戳为近似值，定位可能不精确")
    elif tq.startswith("C"):
        warnings.append("C_unreliable 转录，不适合可靠追问")
    tsq = quality.get("timestamp_quality", "")
    if tsq == "approximate":
        warnings.append("时间戳质量为近似，回查原视频时需留意偏移")
    elif tsq == "unreliable":
        warnings.append("时间戳不可靠，无法精确定位视频片段")
    for limitation in quality.get("known_limitations") or []:
        warnings.append(str(limitation))
    return warnings


def format_answer_context(
    matches: list[SegmentMatch],
    transcript_segments: list[dict] | None = None,
    quality_warnings: list[str] | None = None,
) -> str:
    lines: list[str] = []
    if quality_warnings:
        lines.append("## 质量警告")
        for warning in quality_warnings:
            lines.append(f"- {warning}")
        lines.append("")
    if not matches:
        lines.append("## 检索结果")
        lines.append("未找到与查询相关的索引片段。索引中可能没有覆盖该主题，或关键词需要调整。")
        return "\n".join(lines)
    lines.append(f"## 检索结果（{len(matches)} 个匹配片段）")
    lines.append("")
    for i, match in enumerate(matches, 1):
        lines.append(f"### 片段 {i}: {match.chapter_title}")
        lines.append(f"- 时间段：{match.start} - {match.end}")
        lines.append(f"- 摘要：{match.summary}")
        lines.append(f"- 匹配字段：{', '.join(match.match_fields)}")
        lines.append(f"- 置信度：{match.confidence}")
        lines.append("")
    if transcript_segments:
        lines.append("## 转录原文摘录")
        lines.append("")
        for seg in transcript_segments:
            lines.append(f"[{seg['start']} - {seg['end']}] {seg['text']}")
        lines.append("")
    return "\n".join(lines)


def _load_yaml_index(project_dir: Path) -> str:
    yaml_path = project_dir / "index" / "video_index.yaml"
    if not yaml_path.exists():
        raise UserFacingError("未找到 index/video_index.yaml。")
    return yaml_path.read_text(encoding="utf-8")


def _write_index_change_log(
    project_dir: Path,
    *,
    changed_section: str,
    change_type: str,
    reason: str,
    source: str,
    related_question: str = "",
    before: str = "",
    after: str = "",
) -> None:
    log_path = project_dir / "logs" / "index_change_log.md"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    existing = log_path.read_text(encoding="utf-8") if log_path.exists() else ""
    entry = "\n".join([
        "",
        f"## {datetime.now().astimezone().isoformat(timespec='seconds')}",
        "",
        f"- changed_section: {changed_section}",
        f"- change_type: {change_type}",
        f"- reason: {reason}",
        f"- source: {source}",
        f"- related_question: {related_question}",
        f"- before: {before}",
        f"- after: {after}",
        "",
    ])
    log_path.write_text(existing.rstrip() + "\n" + entry, encoding="utf-8")


def _sync_json_from_yaml(project_dir: Path, index_data: dict) -> None:
    json_path = project_dir / "index" / "video_index.json"
    json_data = {"generated_from": "index/video_index.yaml", **index_data}
    json_path.write_text(
        json.dumps(json_data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def add_index_topic(
    project_dir: Path,
    topic: str,
    related_segments: list[str],
    *,
    reason: str = "",
    related_question: str = "",
) -> None:
    index_data = load_index(project_dir)
    follow_up = index_data.setdefault("follow_up_index", {})
    topics = follow_up.setdefault("important_topics", [])
    entry = {"topic": topic, "related_segments": related_segments}
    topics.append(entry)

    yaml_path = project_dir / "index" / "video_index.yaml"
    yaml_path.write_text("\n".join(render_yaml(index_data)) + "\n", encoding="utf-8")
    _sync_json_from_yaml(project_dir, index_data)

    _write_index_change_log(
        project_dir,
        changed_section="follow_up_index.important_topics",
        change_type="incremental_addition",
        reason=reason or f"追问中发现重要主题：{topic}",
        source="query_video.py add_index_topic",
        related_question=related_question,
        before="",
        after=json.dumps(entry, ensure_ascii=False),
    )


def update_segment_value(
    project_dir: Path,
    segment_id: str,
    new_value_level: str,
    *,
    reason: str,
    related_question: str = "",
) -> None:
    if new_value_level not in ("high", "medium", "low"):
        raise UserFacingError(f"无效 value_level：{new_value_level}，应为 high/medium/low。")

    index_data = load_index(project_dir)
    found = False
    old_value = ""
    for chapter in index_data.get("chapters") or []:
        for segment in chapter.get("segments") or []:
            if segment.get("id") == segment_id:
                old_value = chapter.get("value_level", "")
                chapter["value_level"] = new_value_level
                found = True
                break
        if found:
            break

    if not found:
        raise UserFacingError(f"未找到 segment_id={segment_id}。")

    yaml_path = project_dir / "index" / "video_index.yaml"
    yaml_path.write_text("\n".join(render_yaml(index_data)) + "\n", encoding="utf-8")
    _sync_json_from_yaml(project_dir, index_data)

    _write_index_change_log(
        project_dir,
        changed_section=f"chapters[].value_level (segment {segment_id})",
        change_type="value_reclassification",
        reason=reason,
        source="query_video.py update_segment_value",
        related_question=related_question,
        before=old_value,
        after=new_value_level,
    )


def _matches_to_dicts(matches: list[SegmentMatch]) -> list[dict]:
    return [
        {
            "chapter_id": m.chapter_id,
            "segment_id": m.segment_id,
            "start": m.start,
            "end": m.end,
            "summary": m.summary,
            "match_fields": list(m.match_fields),
            "confidence": m.confidence,
            "chapter_title": m.chapter_title,
        }
        for m in matches
    ]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="V2-lite：查询视频项目索引和转录。",
    )
    parser.add_argument(
        "--project-dir",
        type=Path,
        required=True,
        help="已有 video_project run 目录。",
    )
    parser.add_argument(
        "--search",
        type=str,
        help="搜索关键词（空格分隔多个关键词）。",
    )
    parser.add_argument(
        "--time-range",
        nargs=2,
        metavar=("START", "END"),
        help="提取指定时间范围的转录文本（格式 HH:MM:SS）。",
    )
    parser.add_argument(
        "--with-transcript",
        action="store_true",
        help="搜索时同时输出匹配片段的转录原文。",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    project_dir = args.project_dir.expanduser().resolve()
    if not project_dir.exists():
        print(f"项目目录不存在：{project_dir}", file=sys.stderr)
        return 1

    try:
        if args.time_range:
            segments = get_transcript_range(project_dir, args.time_range[0], args.time_range[1])
            output = {
                "time_range": {"start": args.time_range[0], "end": args.time_range[1]},
                "segments": segments,
                "total_segments": len(segments),
            }
            print(json.dumps(output, ensure_ascii=False, indent=2))
            return 0

        if args.search:
            keywords = args.search.split()
            index_data = load_index(project_dir)
            matches = search_segments(index_data, keywords)
            warnings = get_quality_warnings(index_data)
            transcript_excerpts = None
            if args.with_transcript and matches:
                all_segments: list[dict] = []
                for match in matches:
                    range_segments = get_transcript_range(project_dir, match.start, match.end)
                    all_segments.extend(range_segments)
                seen_ids: set[str] = set()
                transcript_excerpts = []
                for seg in all_segments:
                    if seg["id"] not in seen_ids:
                        seen_ids.add(seg["id"])
                        transcript_excerpts.append(seg)
            output = {
                "query": args.search,
                "matches": _matches_to_dicts(matches),
                "quality_warnings": warnings,
                "total_matches": len(matches),
            }
            if transcript_excerpts is not None:
                output["transcript_excerpts"] = transcript_excerpts
            print(json.dumps(output, ensure_ascii=False, indent=2))
            return 0

        parser.error("请提供 --search 或 --time-range 参数。")
    except UserFacingError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
