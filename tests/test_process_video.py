from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "process_video.py"


def load_process_video_module():
    spec = importlib.util.spec_from_file_location("process_video", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("无法加载 process_video.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class ProcessVideoCliTests(unittest.TestCase):
    def test_help_lists_phase1_options(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--help"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn("--output-root", result.stdout)
        self.assertIn("--copy-input", result.stdout)

    def test_rejects_missing_input_with_chinese_next_action(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), str(ROOT / "missing.mp4")],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 1)
        self.assertIn("输入文件不存在", result.stderr)
        self.assertIn("下一步建议", result.stderr)


class ProcessVideoInitializationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="vr-phase1-"))
        self.video = self.temp_dir / "示例 视频.mp4"
        self.video.write_bytes(b"fake video bytes")
        self.output_root = self.temp_dir / "outputs"
        self.module = load_process_video_module()

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir)

    def test_creates_run_directory_from_template_without_copying_input(self) -> None:
        result = self.module.initialize_project(
            self.video,
            output_root=self.output_root,
            copy_input=False,
            timestamp="20260429-200000",
        )

        run_dir = result.run_dir
        self.assertEqual(run_dir.name, "示例-视频-20260429-200000")
        self.assertTrue((run_dir / "transcript" / "transcript.srt").exists())
        self.assertTrue((run_dir / "index" / "video_index.yaml").exists())
        self.assertTrue((run_dir / "notes" / "video_note.md").exists())
        self.assertTrue((run_dir / "logs" / "process_log.md").exists())
        self.assertFalse((run_dir / "input" / self.video.name).exists())

        process_log = (run_dir / "logs" / "process_log.md").read_text(encoding="utf-8")
        self.assertIn(str(self.video), process_log)
        self.assertIn(str(run_dir), process_log)
        self.assertIn("下一步：进入 Phase 2 音频抽取与转录。", process_log)

    def test_repeated_runs_create_unique_timestamped_directories(self) -> None:
        first = self.module.initialize_project(
            self.video,
            output_root=self.output_root,
            copy_input=False,
            timestamp="20260429-200000",
        )
        second = self.module.initialize_project(
            self.video,
            output_root=self.output_root,
            copy_input=False,
            timestamp="20260429-200001",
        )

        self.assertNotEqual(first.run_dir, second.run_dir)
        self.assertTrue(first.run_dir.exists())
        self.assertTrue(second.run_dir.exists())

    def test_copy_input_option_archives_original_video(self) -> None:
        result = self.module.initialize_project(
            self.video,
            output_root=self.output_root,
            copy_input=True,
            timestamp="20260429-200000",
        )

        archived = result.run_dir / "input" / self.video.name
        self.assertTrue(archived.exists())
        self.assertEqual(archived.read_bytes(), b"fake video bytes")


class ProcessVideoPhase2Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="vr-phase2-"))
        self.video = self.temp_dir / "示例 视频.mp4"
        self.video.write_bytes(b"fake video bytes")
        self.output_root = self.temp_dir / "outputs"
        self.module = load_process_video_module()
        self.run = self.module.initialize_project(
            self.video,
            output_root=self.output_root,
            copy_input=False,
            timestamp="20260429-210000",
        )

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir)

    def test_builds_ffmpeg_command_for_standard_audio_output(self) -> None:
        audio_path = self.run.run_dir / "audio" / "audio.wav"

        command = self.module.build_ffmpeg_audio_command(self.video, audio_path)

        self.assertEqual(command[0], "ffmpeg")
        self.assertIn("-vn", command)
        self.assertIn("-ac", command)
        self.assertIn("1", command)
        self.assertIn("-ar", command)
        self.assertIn("16000", command)
        self.assertEqual(command[-1], str(audio_path))

    def test_writes_transcript_json_and_srt_from_segments(self) -> None:
        transcript = self.module.TranscriptionResult(
            language="zh",
            duration=3.5,
            tool={"name": "fake-transcriber", "version": "test", "parameters": {}},
            quality={
                "transcription_quality": "A_precise",
                "timestamp_quality": "precise",
                "known_limitations": [],
            },
            segments=[
                self.module.TranscriptSegment(
                    id="seg-001",
                    start=0.0,
                    end=1.5,
                    text="你好，世界。",
                    confidence=0.95,
                ),
                self.module.TranscriptSegment(
                    id="seg-002",
                    start=1.5,
                    end=3.5,
                    text="这是一个测试。",
                    confidence=None,
                ),
            ],
        )

        self.module.write_transcript_outputs(self.run.run_dir, self.run.run_dir.name, transcript)

        transcript_json = json.loads(
            (self.run.run_dir / "transcript" / "transcript.json").read_text(encoding="utf-8")
        )
        transcript_srt = (self.run.run_dir / "transcript" / "transcript.srt").read_text(
            encoding="utf-8"
        )

        self.assertEqual(transcript_json["video_id"], self.run.run_dir.name)
        self.assertEqual(transcript_json["language"], "zh")
        self.assertEqual(transcript_json["segments"][0]["text"], "你好，世界。")
        self.assertIn("00:00:00,000 --> 00:00:01,500", transcript_srt)
        self.assertIn("这是一个测试。", transcript_srt)

    def test_run_phase2_with_fake_adapter_preserves_audio_and_updates_log(self) -> None:
        class FakeAdapter:
            name = "fake-transcriber"

            def transcribe(self, audio_path: Path):
                self.audio_path = audio_path
                audio_path.write_bytes(b"fake wav")
                return self_module.TranscriptionResult(
                    language="zh",
                    duration=1.0,
                    tool={"name": self.name, "version": "test", "parameters": {}},
                    quality={
                        "transcription_quality": "A_precise",
                        "timestamp_quality": "precise",
                        "known_limitations": [],
                    },
                    segments=[
                        self_module.TranscriptSegment(
                            id="seg-001",
                            start=0.0,
                            end=1.0,
                            text="测试转录。",
                            confidence=1.0,
                        )
                    ],
                )

        self_module = self.module

        result = self.module.run_phase2(
            self.run.run_dir,
            self.video,
            adapter=FakeAdapter(),
            extract_audio=lambda _input, output: output.write_bytes(b"fake wav"),
        )

        self.assertTrue(result.audio_path.exists())
        self.assertTrue((self.run.run_dir / "transcript" / "transcript.json").exists())
        process_log = (self.run.run_dir / "logs" / "process_log.md").read_text(encoding="utf-8")
        self.assertIn("音频抽取 | done", process_log)
        self.assertIn("转录 | done", process_log)

    def test_run_phase2_records_failure_without_deleting_audio(self) -> None:
        class FailingAdapter:
            name = "failing-transcriber"

            def transcribe(self, audio_path: Path):
                raise RuntimeError("boom")

        with self.assertRaises(self.module.UserFacingError):
            self.module.run_phase2(
                self.run.run_dir,
                self.video,
                adapter=FailingAdapter(),
                extract_audio=lambda _input, output: output.write_bytes(b"fake wav"),
            )

        self.assertTrue((self.run.run_dir / "audio" / "audio.wav").exists())
        failure_log = json.loads(
            (self.run.run_dir / "logs" / "failure_log.json").read_text(encoding="utf-8")
        )
        self.assertEqual(failure_log["failures"][0]["stage"], "transcription")
        self.assertIn("boom", failure_log["failures"][0]["error_message"])


class ProcessVideoPhase3Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="vr-phase3-"))
        self.video = self.temp_dir / "示例 视频.mp4"
        self.video.write_bytes(b"fake video bytes")
        self.output_root = self.temp_dir / "outputs"
        self.module = load_process_video_module()
        self.run = self.module.initialize_project(
            self.video,
            output_root=self.output_root,
            copy_input=False,
            timestamp="20260429-220000",
        )
        transcript = self.module.TranscriptionResult(
            language="zh",
            duration=720.0,
            tool={
                "name": "fake-transcriber",
                "version": "tiny",
                "model": "tiny",
                "parameters": {"device": "cpu"},
            },
            quality={
                "transcription_quality": "B_overview",
                "timestamp_quality": "approximate",
                "known_limitations": ["tiny 模型用于本地冒烟"],
            },
            segments=[
                self.module.TranscriptSegment(
                    id="seg-001",
                    start=0.0,
                    end=60.0,
                    text="第一段介绍项目背景和目标。",
                    confidence=None,
                ),
                self.module.TranscriptSegment(
                    id="seg-002",
                    start=300.0,
                    end=360.0,
                    text="第二段讨论实现步骤和工具链。",
                    confidence=None,
                ),
                self.module.TranscriptSegment(
                    id="seg-003",
                    start=660.0,
                    end=720.0,
                    text="第三段总结后续计划。",
                    confidence=None,
                ),
            ],
        )
        self.module.write_transcript_outputs(self.run.run_dir, self.run.run_dir.name, transcript)

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir)

    def test_run_phase3_writes_index_json_and_note(self) -> None:
        final_note = self.run.run_dir / "notes" / "video_note.md"
        final_note.write_text("人工整理后的最终笔记，不应被 Phase 3 脚本覆盖。\n", encoding="utf-8")

        result = self.module.run_phase3(self.run.run_dir)

        self.assertTrue(result.yaml_path.exists())
        self.assertTrue(result.json_path.exists())
        self.assertTrue(result.draft_note_path.exists())
        self.assertTrue(result.final_note_path.exists())

        index_json = json.loads(result.json_path.read_text(encoding="utf-8"))
        draft_note = result.draft_note_path.read_text(encoding="utf-8")
        final_note_text = result.final_note_path.read_text(encoding="utf-8")

        self.assertEqual(index_json["generated_from"], "index/video_index.yaml")
        self.assertEqual(index_json["video"]["id"], self.run.run_dir.name)
        self.assertEqual(index_json["quality"]["transcription_quality"], "B_overview")
        self.assertIn("tiny 模型用于本地冒烟", index_json["quality"]["known_limitations"])
        self.assertEqual(final_note_text, "人工整理后的最终笔记，不应被 Phase 3 脚本覆盖。\n")
        self.assertIn("## 1. 核心结论", draft_note)
        self.assertIn("## 2. 主题模块", draft_note)
        self.assertIn("证据时间段", draft_note)
        self.assertIn("## 5. 不确定性与质量边界", draft_note)
        self.assertIn("时间戳或术语存在风险", draft_note)
        self.assertIn("第一段介绍项目背景和目标", draft_note)

    def test_chapter_summary_prefers_value_keywords_over_opening_filler(self) -> None:
        segments = [
            {"start_seconds": 0.0, "end_seconds": 5.0, "text": "大家好，今天开始。"},
            {"start_seconds": 5.0, "end_seconds": 10.0, "text": "这个地方我们先看一下。"},
            {"start_seconds": 10.0, "end_seconds": 15.0, "text": "然后继续往下。"},
            {"start_seconds": 15.0, "end_seconds": 20.0, "text": "这个案例使用 AI 工具把字幕外包成本降下来。"},
        ]

        chapters = self.module.build_overview_chapters(segments, window_seconds=600)

        self.assertIn("AI 工具把字幕外包成本降下来", chapters[0]["summary"])

    def test_run_phase3_fails_for_empty_transcript_and_records_failure(self) -> None:
        empty = self.module.TranscriptionResult(
            language="zh",
            duration=0.0,
            tool={"name": "fake-transcriber", "version": "test", "parameters": {}},
            quality={
                "transcription_quality": "C_unreliable",
                "timestamp_quality": "unreliable",
                "known_limitations": ["没有可用片段"],
            },
            segments=[],
        )
        self.module.write_transcript_outputs(self.run.run_dir, self.run.run_dir.name, empty)

        with self.assertRaises(self.module.UserFacingError):
            self.module.run_phase3(self.run.run_dir)

        failure_log = json.loads(
            (self.run.run_dir / "logs" / "failure_log.json").read_text(encoding="utf-8")
        )
        self.assertEqual(failure_log["failures"][0]["stage"], "index_generation")

    def test_cli_runs_phase3_for_existing_project_dir(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--project-dir",
                str(self.run.run_dir),
                "--phase3",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn("Phase 3 索引与笔记生成完成", result.stdout)
        self.assertIn("草稿笔记", result.stdout)
        self.assertTrue((self.run.run_dir / "index" / "video_index.yaml").exists())
        self.assertTrue((self.run.run_dir / "notes" / "video_note.draft.md").exists())


class ProcessVideoPhase4Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="vr-phase4-"))
        self.video = self.temp_dir / "示例 视频.mp4"
        self.video.write_bytes(b"fake video bytes")
        self.output_root = self.temp_dir / "outputs"
        self.module = load_process_video_module()
        self.run = self.module.initialize_project(
            self.video,
            output_root=self.output_root,
            copy_input=False,
            timestamp="20260429-230000",
        )
        transcript = self.module.TranscriptionResult(
            language="zh",
            duration=60.0,
            tool={"name": "fake-transcriber", "version": "test", "parameters": {}},
            quality={
                "transcription_quality": "B_overview",
                "timestamp_quality": "approximate",
                "known_limitations": ["测试转录"],
            },
            segments=[
                self.module.TranscriptSegment(
                    id="seg-001",
                    start=0.0,
                    end=60.0,
                    text="这个案例使用 AI 工具把字幕外包成本降下来。",
                    confidence=None,
                )
            ],
        )
        self.module.write_transcript_outputs(self.run.run_dir, self.run.run_dir.name, transcript)
        self.module.run_phase3(self.run.run_dir)
        (self.run.run_dir / "notes" / "video_note.md").write_text(
            "# 最终笔记\n\n包含核心结论和证据时间段。\n",
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir)

    def test_run_phase4_writes_qa_report_and_marks_process_log_done(self) -> None:
        result = self.module.run_phase4(self.run.run_dir)

        self.assertTrue(result.qa_report_path.exists())
        report = result.qa_report_path.read_text(encoding="utf-8")
        process_log = (self.run.run_dir / "logs" / "process_log.md").read_text(encoding="utf-8")

        self.assertIn("## V1 产物结构验收", report)
        self.assertIn("| transcript/transcript.json | PASS |", report)
        self.assertIn("| notes/video_note.md | PASS |", report)
        self.assertIn("QA 检查 | done", process_log)
        self.assertIn("logs/qa_report.md", process_log)

    def test_run_phase4_fails_and_records_failure_when_final_note_missing(self) -> None:
        (self.run.run_dir / "notes" / "video_note.md").unlink()

        with self.assertRaises(self.module.UserFacingError):
            self.module.run_phase4(self.run.run_dir)

        self.assertTrue((self.run.run_dir / "logs" / "qa_report.md").exists())
        process_log = (self.run.run_dir / "logs" / "process_log.md").read_text(encoding="utf-8")
        failure_log = json.loads(
            (self.run.run_dir / "logs" / "failure_log.json").read_text(encoding="utf-8")
        )

        self.assertIn("QA 检查 | failed", process_log)
        self.assertEqual(failure_log["failures"][-1]["stage"], "qa_check")
        self.assertIn("notes/video_note.md", failure_log["failures"][-1]["error_message"])

    def test_run_phase4_fails_when_final_note_is_still_template(self) -> None:
        (self.run.run_dir / "notes" / "video_note.md").write_text(
            "# <视频标题> 笔记\n\n- <问题 1>\n",
            encoding="utf-8",
        )

        with self.assertRaises(self.module.UserFacingError):
            self.module.run_phase4(self.run.run_dir)

        report = (self.run.run_dir / "logs" / "qa_report.md").read_text(encoding="utf-8")
        self.assertIn("| notes/video_note.md | FAIL | template placeholders remain |", report)


if __name__ == "__main__":
    unittest.main()
