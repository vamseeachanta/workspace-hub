"""Cost-ceiling enforcement in the task dispatcher (#3205).

Drives the real dispatcher CLI. Under the hermes_batch context the dispatcher
must never recommend claude; without a context the interactive path is unchanged
(claude remains selectable).
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DISPATCHER = REPO_ROOT / "scripts" / "ai" / "task-dispatcher.py"


def _run(*args: str) -> dict:
    r = subprocess.run(
        [sys.executable, str(DISPATCHER), *args],
        capture_output=True, text=True,
    )
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout)


def test_dispatcher_hermes_context_excludes_claude():
    out = _run("--task", "summarize this quarterly report", "--tier", "complex",
               "--context", "hermes_batch")
    assert out["recommended_agent"] != "claude"
    assert all(a["agent"] != "claude" for a in out["alternatives"])
    assert "claude" in out["forbidden"]
    assert out["context"] == "hermes_batch"


def test_dispatcher_no_context_can_pick_claude():
    # No regression: the interactive path may still pick claude. We pick a task
    # whose keywords strongly favour claude (architecture/design) at a high tier.
    out = _run("--task", "design new auth architecture and refactor", "--tier", "reasoning")
    assert out["recommended_agent"] == "claude"
    assert out.get("context") in (None, "")


def test_dispatcher_unknown_context_fails_closed():
    r = subprocess.run(
        [sys.executable, str(DISPATCHER), "--task", "x", "--tier", "simple",
         "--context", "hermes-batch"],
        capture_output=True, text=True,
    )
    assert r.returncode != 0
