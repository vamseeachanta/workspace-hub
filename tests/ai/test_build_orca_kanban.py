from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "scripts" / "ai" / "build-orca-kanban.py"


def _module():
    spec = importlib.util.spec_from_file_location("build_orca_kanban", MODULE_PATH)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules["build_orca_kanban"] = mod
    spec.loader.exec_module(mod)
    return mod


def test_dispatch_active_wins_over_plan_approved_status() -> None:
    mod = _module()
    issue = {
        "state": "OPEN",
        "number": 1,
        "_status": "status:plan-approved",
        "_dispatch": "dispatch:active",
        "_labels": ["status:plan-approved", "dispatch:active"],
    }

    assert mod.assign_lane(issue) == "In Progress / Dispatch Active"
