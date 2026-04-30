"""V1 Phase 1 local video project initializer."""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_DIR = ROOT / "ProjectManager" / "Templates" / "video_project"
DEFAULT_OUTPUT_ROOT = ROOT / "outputs"
SUPPORTED_VIDEO_EXTENSIONS = {".mp4", ".mov", ".mkv"}


@dataclass(frozen=True)
class InitializationResult:
    run_dir: Path
    input_path: Path
    copied_input: bool


class UserFacingError(Exception):
    """Error that should be shown directly to the user."""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="V1 Phase 1：校验本地视频并初始化单视频项目目录。",
    )
    parser.add_argument(
        "video_path",
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
                "| 笔记生成 | pending |  |  | Agent | Phase 3 执行 |",
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
        result = initialize_project(
            args.video_path,
            output_root=args.output_root,
            copy_input=args.copy_input,
        )
    except UserFacingError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print("Phase 1 初始化完成。")
    print(f"输出项目目录：{result.run_dir}")
    print("下一步：进入 Phase 2 音频抽取与转录。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
