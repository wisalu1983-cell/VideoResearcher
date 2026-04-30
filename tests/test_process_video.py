from __future__ import annotations

import importlib.util
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


if __name__ == "__main__":
    unittest.main()
