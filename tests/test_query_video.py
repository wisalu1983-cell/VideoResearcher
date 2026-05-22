"""Tests for V2-lite query_video.py."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from query_video import (
    SegmentMatch,
    add_index_topic,
    format_answer_context,
    get_quality_warnings,
    get_transcript_range,
    load_index,
    search_segments,
    search_transcript,
    update_segment_value,
)


def _make_project(tmp: Path, index_data: dict | None = None, transcript_data: dict | None = None) -> Path:
    project = tmp / "test_project"
    (project / "index").mkdir(parents=True)
    (project / "transcript").mkdir(parents=True)
    if index_data is not None:
        (project / "index" / "video_index.json").write_text(
            json.dumps(index_data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    if transcript_data is not None:
        (project / "transcript" / "transcript.json").write_text(
            json.dumps(transcript_data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    return project


SAMPLE_INDEX = {
    "chapters": [
        {
            "id": "ch-001",
            "title": "AI 工具链介绍",
            "start": "00:00:00",
            "end": "00:09:59",
            "summary": "介绍 Cursor 和 AI agent 的基本概念",
            "value_level": "high",
            "segments": [
                {
                    "id": "seg-001",
                    "start": "00:00:00",
                    "end": "00:04:59",
                    "type": "concept",
                    "summary": "Cursor IDE 与 AI 编程工具链",
                    "key_points": ["Cursor 是 AI 编程 IDE", "支持多模型切换"],
                    "original_snippets": ["今天介绍 Cursor 这个工具"],
                    "confidence": "medium",
                },
                {
                    "id": "seg-002",
                    "start": "00:05:00",
                    "end": "00:09:59",
                    "type": "method",
                    "summary": "AI agent 工作流设计方法",
                    "key_points": ["agent 需要明确目标", "工具链选择"],
                    "original_snippets": ["agent 的核心是任务分解"],
                    "confidence": "high",
                },
            ],
        },
        {
            "id": "ch-002",
            "title": "成本与效率分析",
            "start": "00:10:00",
            "end": "00:19:59",
            "summary": "AI 工作流的成本效率权衡",
            "value_level": "medium",
            "segments": [
                {
                    "id": "seg-003",
                    "start": "00:10:00",
                    "end": "00:19:59",
                    "type": "data",
                    "summary": "使用 AI 工具的实际成本数据",
                    "key_points": ["每月 USD 20-50", "效率提升 3-5 倍"],
                    "original_snippets": ["成本大概是每个月 20 到 50 美金"],
                    "confidence": "medium",
                },
            ],
        },
    ],
    "quality": {
        "transcription_quality": "B_overview",
        "timestamp_quality": "approximate",
        "known_limitations": ["tiny 模型用于冒烟测试"],
    },
}

SAMPLE_TRANSCRIPT = {
    "segments": [
        {"id": "seg-t001", "start": "00:00:00.000", "end": "00:00:05.000", "start_seconds": 0.0, "end_seconds": 5.0, "text": "大家好今天来介绍 Cursor"},
        {"id": "seg-t002", "start": "00:00:05.000", "end": "00:00:12.000", "start_seconds": 5.0, "end_seconds": 12.0, "text": "Cursor 是一个 AI 编程 IDE"},
        {"id": "seg-t003", "start": "00:05:00.000", "end": "00:05:08.000", "start_seconds": 300.0, "end_seconds": 308.0, "text": "agent 工作流的设计需要明确目标"},
        {"id": "seg-t004", "start": "00:10:00.000", "end": "00:10:15.000", "start_seconds": 600.0, "end_seconds": 615.0, "text": "成本大概每月 20 到 50 美金"},
        {"id": "seg-t005", "start": "00:15:00.000", "end": "00:15:10.000", "start_seconds": 900.0, "end_seconds": 910.0, "text": "效率提升大概 3 到 5 倍"},
    ],
}


class SearchSegmentTests(unittest.TestCase):
    def test_search_finds_matching_segment_by_keyword(self) -> None:
        matches = search_segments(SAMPLE_INDEX, ["Cursor"])
        self.assertTrue(len(matches) >= 1)
        ids = [m.segment_id for m in matches]
        self.assertIn("seg-001", ids)

    def test_search_returns_empty_for_no_match(self) -> None:
        matches = search_segments(SAMPLE_INDEX, ["量子力学"])
        self.assertEqual(matches, [])

    def test_search_ranks_multi_field_match_higher(self) -> None:
        matches = search_segments(SAMPLE_INDEX, ["AI", "工具"])
        self.assertTrue(len(matches) >= 2)
        top = matches[0]
        self.assertTrue(len(top.match_fields) >= 2, f"Top match should hit multiple fields, got {top.match_fields}")

    def test_search_is_case_insensitive(self) -> None:
        matches_lower = search_segments(SAMPLE_INDEX, ["cursor"])
        matches_upper = search_segments(SAMPLE_INDEX, ["CURSOR"])
        self.assertEqual(len(matches_lower), len(matches_upper))

    def test_search_with_empty_keywords_returns_empty(self) -> None:
        matches = search_segments(SAMPLE_INDEX, [])
        self.assertEqual(matches, [])

    def test_search_multiple_keywords_increases_score(self) -> None:
        single = search_segments(SAMPLE_INDEX, ["成本"])
        double = search_segments(SAMPLE_INDEX, ["成本", "USD"])
        self.assertTrue(len(single) >= 1)
        self.assertTrue(len(double) >= 1)
        double_seg003 = next((m for m in double if m.segment_id == "seg-003"), None)
        self.assertIsNotNone(double_seg003)


class TranscriptRangeTests(unittest.TestCase):
    def test_transcript_range_filters_by_time(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = _make_project(Path(tmp), transcript_data=SAMPLE_TRANSCRIPT)
            segments = get_transcript_range(project, "00:00:00", "00:00:12")
            ids = [s["id"] for s in segments]
            self.assertIn("seg-t001", ids)
            self.assertIn("seg-t002", ids)
            self.assertNotIn("seg-t003", ids)

    def test_transcript_range_handles_boundary_segments(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = _make_project(Path(tmp), transcript_data=SAMPLE_TRANSCRIPT)
            segments = get_transcript_range(project, "00:04:59", "00:05:09")
            ids = [s["id"] for s in segments]
            self.assertIn("seg-t003", ids)
            self.assertNotIn("seg-t001", ids)

    def test_transcript_range_returns_empty_for_gap(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = _make_project(Path(tmp), transcript_data=SAMPLE_TRANSCRIPT)
            segments = get_transcript_range(project, "00:20:00", "00:25:00")
            self.assertEqual(segments, [])


class LoadIndexTests(unittest.TestCase):
    def test_load_index_returns_parsed_data(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = _make_project(Path(tmp), index_data=SAMPLE_INDEX)
            data = load_index(project)
            self.assertIn("chapters", data)
            self.assertEqual(len(data["chapters"]), 2)

    def test_load_index_raises_for_missing_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = _make_project(Path(tmp))
            from query_video import UserFacingError
            with self.assertRaises(UserFacingError):
                load_index(project)


class QualityWarningsTests(unittest.TestCase):
    def test_b_overview_generates_warnings(self) -> None:
        warnings = get_quality_warnings(SAMPLE_INDEX)
        self.assertTrue(any("B_overview" in w for w in warnings))
        self.assertTrue(any("近似" in w for w in warnings))

    def test_no_warnings_for_a_precise(self) -> None:
        index = {"quality": {"transcription_quality": "A_precise", "timestamp_quality": "precise", "known_limitations": []}}
        warnings = get_quality_warnings(index)
        self.assertEqual(warnings, [])


class FormatAnswerContextTests(unittest.TestCase):
    def test_format_with_no_matches_shows_not_found(self) -> None:
        result = format_answer_context([], quality_warnings=["测试警告"])
        self.assertIn("未找到", result)
        self.assertIn("测试警告", result)

    def test_format_with_matches_shows_segments(self) -> None:
        match = SegmentMatch(
            chapter_id="ch-001",
            segment_id="seg-001",
            start="00:00:00",
            end="00:04:59",
            summary="Cursor IDE",
            match_fields=("summary",),
            confidence="medium",
            chapter_title="AI 工具链",
            chapter_summary="介绍工具链",
        )
        result = format_answer_context([match])
        self.assertIn("00:00:00", result)
        self.assertIn("Cursor IDE", result)
        self.assertIn("1 个匹配片段", result)


class CliTests(unittest.TestCase):
    def test_cli_search_outputs_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = _make_project(Path(tmp), index_data=SAMPLE_INDEX, transcript_data=SAMPLE_TRANSCRIPT)
            result = subprocess.run(
                [sys.executable, str(SCRIPTS_DIR / "query_video.py"), "--project-dir", str(project), "--search", "Cursor"],
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            output = json.loads(result.stdout)
            self.assertIn("index_matches", output)
            self.assertIn("transcript_hits", output)
            self.assertIn("quality_warnings", output)
            self.assertTrue(output["total_index_matches"] >= 1)

    def test_cli_time_range_outputs_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = _make_project(Path(tmp), index_data=SAMPLE_INDEX, transcript_data=SAMPLE_TRANSCRIPT)
            result = subprocess.run(
                [sys.executable, str(SCRIPTS_DIR / "query_video.py"), "--project-dir", str(project), "--time-range", "00:00:00", "00:00:12"],
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            output = json.loads(result.stdout)
            self.assertIn("segments", output)
            self.assertTrue(output["total_segments"] >= 1)


class TranscriptSearchTests(unittest.TestCase):
    def test_search_transcript_finds_keyword_in_text(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = _make_project(Path(tmp), transcript_data=SAMPLE_TRANSCRIPT)
            hits = search_transcript(project, ["Cursor"])
            self.assertTrue(len(hits) >= 1)
            self.assertTrue(any("Cursor" in h.text for h in hits))

    def test_search_transcript_returns_context(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = _make_project(Path(tmp), transcript_data=SAMPLE_TRANSCRIPT)
            hits = search_transcript(project, ["agent"], context_window=1)
            hit_with_context = next((h for h in hits if h.context_before or h.context_after), None)
            self.assertIsNotNone(hit_with_context)

    def test_search_transcript_respects_max_hits(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            many_segments = {"segments": [
                {"id": f"s{i}", "start": "00:00:00", "end": "00:00:01", "text": f"keyword {i}"}
                for i in range(50)
            ]}
            project = _make_project(Path(tmp), transcript_data=many_segments)
            hits = search_transcript(project, ["keyword"], max_hits=5)
            self.assertEqual(len(hits), 5)

    def test_search_transcript_returns_empty_for_no_match(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = _make_project(Path(tmp), transcript_data=SAMPLE_TRANSCRIPT)
            hits = search_transcript(project, ["量子力学"])
            self.assertEqual(hits, [])


class FilteredTranscriptRangeTests(unittest.TestCase):
    def test_filter_reduces_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = _make_project(Path(tmp), transcript_data=SAMPLE_TRANSCRIPT)
            all_segs = get_transcript_range(project, "00:00:00", "00:15:10")
            filtered = get_transcript_range(project, "00:00:00", "00:15:10", filter_keywords=["Cursor"])
            self.assertGreater(len(all_segs), len(filtered))
            self.assertGreater(len(filtered), 0)

    def test_filter_includes_context_window(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = _make_project(Path(tmp), transcript_data=SAMPLE_TRANSCRIPT)
            filtered = get_transcript_range(project, "00:00:00", "00:15:10", filter_keywords=["Cursor"], context_window=1)
            texts = [s["text"] for s in filtered]
            has_non_cursor = any("Cursor" not in t for t in texts)
            self.assertTrue(has_non_cursor, "Context window should include non-matching segments")

    def test_filter_no_match_returns_empty(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = _make_project(Path(tmp), transcript_data=SAMPLE_TRANSCRIPT)
            filtered = get_transcript_range(project, "00:00:00", "00:00:12", filter_keywords=["量子力学"])
            self.assertEqual(filtered, [])


class DualSourceSearchCliTests(unittest.TestCase):
    def test_cli_returns_both_index_and_transcript_hits(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = _make_project(Path(tmp), index_data=SAMPLE_INDEX, transcript_data=SAMPLE_TRANSCRIPT)
            result = subprocess.run(
                [sys.executable, str(SCRIPTS_DIR / "query_video.py"), "--project-dir", str(project), "--search", "Cursor"],
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            output = json.loads(result.stdout)
            self.assertIn("index_matches", output)
            self.assertIn("transcript_hits", output)
            self.assertTrue(output["total_transcript_hits"] >= 1)

    def test_cli_transcript_only_hit(self) -> None:
        """Index has no match but transcript does — the key Q1 scenario."""
        with tempfile.TemporaryDirectory() as tmp:
            project = _make_project(Path(tmp), index_data=SAMPLE_INDEX, transcript_data=SAMPLE_TRANSCRIPT)
            result = subprocess.run(
                [sys.executable, str(SCRIPTS_DIR / "query_video.py"), "--project-dir", str(project), "--search", "大家好"],
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            output = json.loads(result.stdout)
            self.assertEqual(output["total_index_matches"], 0)
            self.assertTrue(output["total_transcript_hits"] >= 1)


class IndexWritebackTests(unittest.TestCase):
    def test_add_topic_appends_and_logs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = _make_project(Path(tmp), index_data=SAMPLE_INDEX, transcript_data=SAMPLE_TRANSCRIPT)
            (project / "logs").mkdir(parents=True, exist_ok=True)
            (project / "logs" / "index_change_log.md").write_text("# 索引变更日志\n", encoding="utf-8")
            add_index_topic(
                project,
                "Cursor 编程实践",
                ["seg-001"],
                reason="用户多次追问 Cursor 用法",
                related_question="Cursor 怎么配置？",
            )
            updated = load_index(project)
            topics = updated.get("follow_up_index", {}).get("important_topics", [])
            self.assertTrue(any(t.get("topic") == "Cursor 编程实践" for t in topics))
            log = (project / "logs" / "index_change_log.md").read_text(encoding="utf-8")
            self.assertIn("incremental_addition", log)
            self.assertIn("Cursor 编程实践", log)

    def test_update_value_changes_level_and_logs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = _make_project(Path(tmp), index_data=SAMPLE_INDEX, transcript_data=SAMPLE_TRANSCRIPT)
            (project / "logs").mkdir(parents=True, exist_ok=True)
            (project / "logs" / "index_change_log.md").write_text("# 索引变更日志\n", encoding="utf-8")
            update_segment_value(
                project,
                "seg-003",
                "high",
                reason="成本数据经核实后确认为高价值",
            )
            updated = load_index(project)
            ch002 = next(c for c in updated["chapters"] if c["id"] == "ch-002")
            self.assertEqual(ch002["value_level"], "high")
            log = (project / "logs" / "index_change_log.md").read_text(encoding="utf-8")
            self.assertIn("value_reclassification", log)
            self.assertIn("medium", log)
            self.assertIn("high", log)

    def test_update_value_rejects_invalid_level(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = _make_project(Path(tmp), index_data=SAMPLE_INDEX)
            from query_video import UserFacingError
            with self.assertRaises(UserFacingError):
                update_segment_value(project, "seg-001", "critical", reason="test")

    def test_update_value_rejects_unknown_segment(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = _make_project(Path(tmp), index_data=SAMPLE_INDEX)
            from query_video import UserFacingError
            with self.assertRaises(UserFacingError):
                update_segment_value(project, "seg-999", "high", reason="test")

    def test_add_topic_syncs_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = _make_project(Path(tmp), index_data=SAMPLE_INDEX, transcript_data=SAMPLE_TRANSCRIPT)
            (project / "logs").mkdir(parents=True, exist_ok=True)
            (project / "logs" / "index_change_log.md").write_text("", encoding="utf-8")
            add_index_topic(project, "测试主题", ["seg-001"])
            json_data = json.loads((project / "index" / "video_index.json").read_text(encoding="utf-8"))
            self.assertEqual(json_data["generated_from"], "index/video_index.yaml")
            topics = json_data.get("follow_up_index", {}).get("important_topics", [])
            self.assertTrue(any(t.get("topic") == "测试主题" for t in topics))


if __name__ == "__main__":
    unittest.main()
