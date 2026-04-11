from __future__ import annotations

import re
from pathlib import Path
from typing import Sequence

REPO_ROOT = Path(__file__).resolve().parents[2]
PatternEntry = tuple[str, re.Pattern[str]]

CORE_BANNED_STALE_REFERENCE_PATTERNS: list[PatternEntry] = [
    ("deleted new-spec helper", re.compile(r"scripts/work-queue/new-spec\.sh")),
    ("deleted parse-session-logs helper", re.compile(r"scripts/work-queue/parse-session-logs\.sh")),
    ("deleted agent wrapper tree", re.compile(r"scripts/agents/")),
    ("deleted specs/wrk plan path", re.compile(r"specs/wrk/WRK-(?:\d+|NNN)/plan\.md")),
    (
        "deleted work-queue gate scripts",
        re.compile(
            r"scripts/work-queue/(?:verify-gate-evidence|generate-html-review|start_stage|exit_stage|verify_checklist|stage_exit_checks)\.py"
        ),
    ),
    (
        "deleted work-queue lifecycle scripts",
        re.compile(r"scripts/work-queue/(?:close-item|whats-next|archive-item|claim-item)\.sh"),
    ),
    ("legacy local work-queue path", re.compile(r"\.claude/work-queue/")),
    (
        "deleted legacy work-queue workflow skill",
        re.compile(r"\.claude/skills/workspace-hub/work-queue-workflow/SKILL\.md"),
    ),
    (
        "deleted legacy coordination work-queue skill",
        re.compile(r"\.claude/skills/coordination/workspace/work-queue/SKILL\.md"),
    ),
    (
        "deleted legacy workflow gatepass skill",
        re.compile(r"\.claude/skills/workspace-hub/workflow-gatepass/SKILL\.md"),
    ),
]


def scan_stale_reference_hits(
    relative_path: str,
    patterns: Sequence[PatternEntry] = CORE_BANNED_STALE_REFERENCE_PATTERNS,
) -> list[str]:
    text = (REPO_ROOT / relative_path).read_text(encoding="utf-8")
    hits: list[str] = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        for label, pattern in patterns:
            match = pattern.search(line)
            if match:
                hits.append(f"{relative_path}:{line_no}: {label}: {match.group(0)}")
    return hits
