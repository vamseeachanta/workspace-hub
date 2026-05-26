#!/usr/bin/env python3
"""Reconcile GitHub issues into the kanban board tree."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable


@dataclass
class ReconcileResult:
    changed: bool
    diff: str
    changed_files: list[Path]


def fetch_repo_issues(repo: str, *, limit: int = 100000, runner=None) -> list[dict]:
    return []


def reconcile_kanban(
    kanban_root: Path,
    *,
    issue_fetcher: Callable[[str], list[dict]],
    dry_run: bool = True,
) -> ReconcileResult:
    return ReconcileResult(changed=False, diff="", changed_files=[])
