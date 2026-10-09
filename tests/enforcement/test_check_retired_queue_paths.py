from __future__ import annotations

import importlib.util
from pathlib import Path

SCRIPT = (
    Path(__file__).parents[2]
    / "scripts"
    / "enforcement"
    / "check-retired-queue-paths.py"
)


def _load():
    spec = importlib.util.spec_from_file_location("retired_queue_paths", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_blocks_new_work_queue_file():
    mod = _load()
    assert mod.violations([("A", ".claude/work-queue/pending/WRK-1.md")])


def test_blocks_new_planning_file():
    mod = _load()
    assert mod.violations([("A", ".planning/plan-approved/3999.md")])


def test_allows_archive_under_retired_paths():
    mod = _load()
    rows = [
        ("A", ".claude/work-queue/_archive/2026-10-legacy-queue/WRK-1.md"),
        ("A", ".planning/archive/2026-10-legacy-queue/old.md"),
    ]
    assert mod.violations(rows) == []


def test_blocks_renamed_file_into_retired_path():
    mod = _load()
    rows = [("R100", ".planning/plan-approved/3999.md")]
    assert mod.violations(rows) == [".planning/plan-approved/3999.md"]


def test_blocks_archive_name_outside_exact_archive_prefix():
    mod = _load()
    rows = [("A", ".planning/plan-approved/archive/3999.md")]
    assert mod.violations(rows) == [".planning/plan-approved/archive/3999.md"]


def test_ignores_existing_modified_historical_files():
    mod = _load()
    rows = [("M", ".claude/work-queue/INDEX.md")]
    assert mod.violations(rows) == []
