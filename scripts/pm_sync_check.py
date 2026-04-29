"""Project management document consistency check."""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PM = ROOT / "ProjectManager"
PLAN = PM / "Plan"
SPECS = PM / "Specs"
ISSUE_LIST = PM / "ISSUE_LIST.md"
BACKLOG = PM / "Backlog.md"

@dataclass
class Finding:
    level: str
    check: str
    message: str
    path: Path | None = None

findings: list[Finding] = []

def read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""

def report(level: str, check: str, message: str, path: Path | None = None) -> None:
    findings.append(Finding(level, check, message, path))

def check_required_files() -> None:
    required = [
        PM / "Overview.md",
        PM / "Backlog.md",
        PM / "ISSUE_LIST.md",
        PLAN / "README.md",
        SPECS / "_index.md",
        ROOT / "QA" / "README.md",
    ]
    for path in required:
        if not path.exists():
            report("error", "required-files", "missing required project management file", path)

def check_issue_backlog_overlap() -> None:
    issue_ids = set(re.findall(r"ISSUE-\d+", read(ISSUE_LIST)))
    backlog_ids = set(re.findall(r"ISSUE-\d+", read(BACKLOG)))
    for issue in sorted(issue_ids & backlog_ids):
        report("warn", "issue-backlog-overlap", f"{issue} appears in both ISSUE_LIST and Backlog")

def main() -> int:
    check_required_files()
    check_issue_backlog_overlap()
    if not findings:
        print("pm_sync_check: PASS")
        return 0
    for finding in findings:
        location = f" [{finding.path}]" if finding.path else ""
        print(f"{finding.level.upper()}: [{finding.check}] {finding.message}{location}")
    return 1 if any(f.level == "error" for f in findings) else 0

if __name__ == "__main__":
    raise SystemExit(main())
