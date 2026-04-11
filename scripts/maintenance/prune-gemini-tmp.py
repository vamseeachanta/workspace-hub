#!/usr/bin/env python3
# ABOUTME: Prune stale Gemini temp workspace roots under ~/.gemini/tmp without touching repo-scoped histories.

from __future__ import annotations

import json
import shutil
import time
from pathlib import Path

HOME = Path.home()
BASE = HOME / ".gemini" / "tmp"
NOW = time.time()
TMP_PREFIXES = ("tmp", "tmp-")
MIN_AGE_DAYS = 7
FORCE_AGE_DAYS = 14


def age_days(path: Path) -> float:
    return (NOW - path.stat().st_mtime) / 86400


def safe_candidate(path: Path) -> tuple[bool, str]:
    name = path.name
    if not path.is_dir():
        return False, "not-dir"
    if not (name == "tmp" or name.startswith("tmp-")):
        return False, "not-temp-root"
    age = age_days(path)
    if age < MIN_AGE_DAYS:
        return False, "too-recent"
    project_root_file = path / ".project_root"
    if not project_root_file.exists():
        return False, "missing-project-root"
    project_root = project_root_file.read_text(encoding="utf-8", errors="replace").strip()
    if not project_root.startswith("/tmp"):
        return False, "project-root-not-under-tmp"
    target = Path(project_root)
    if not target.exists():
        return True, "orphan-temp-root"
    if age >= FORCE_AGE_DAYS:
        return True, "stale-temp-root"
    return False, "target-still-exists"


def main() -> None:
    results = {"removed": [], "skipped": [], "base_exists": BASE.exists()}
    if not BASE.exists():
        print(json.dumps(results, indent=2))
        return
    for path in sorted(BASE.iterdir()):
        ok, reason = safe_candidate(path)
        if ok:
            shutil.rmtree(path)
            results["removed"].append({"path": str(path), "reason": reason})
        else:
            results["skipped"].append({"path": str(path), "reason": reason})
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
