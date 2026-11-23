"""Collection controls for legacy work-queue tests."""
from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
WORK_QUEUE_DIR = REPO_ROOT / "scripts" / "work-queue"

collect_ignore = []
if not WORK_QUEUE_DIR.exists():
    collect_ignore.extend(str(path.name) for path in Path(__file__).parent.glob("test_*.py"))
