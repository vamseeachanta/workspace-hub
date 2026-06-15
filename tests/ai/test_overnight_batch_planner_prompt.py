"""#3143 Task 2 — the overnight launcher must NOT tell agents to blanket-commit.

`overnight-batch-planner.py` launches autonomous agents in a checkout that may
hold ANOTHER session's uncommitted work. Instructing "commit your changes" with
no scoping lets the agent `git add -A` and sweep that foreign WIP into a commit
(the #3143 incident shape). The prompt must scope staging to the task's own
file_scope and forbid blanket adds.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "scripts" / "ai" / "overnight-batch-planner.py"
spec = importlib.util.spec_from_file_location("overnight_batch_planner", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules["overnight_batch_planner"] = module
spec.loader.exec_module(module)

build_prompt = module.build_prompt

ISSUE = {
    "agent": "codex",
    "number": 999,
    "title": "Do the thing",
    "body": "implement the thing",
    "file_scope": ["scripts/foo.py", "tests/test_foo.py"],
}


def test_prompt_scopes_staging_to_file_scope():
    p = build_prompt(ISSUE)
    # scoped staging references the task's own files
    assert "scripts/foo.py" in p
    assert "git add" in p


def test_prompt_forbids_blanket_add():
    p = build_prompt(ISSUE).lower()
    # must explicitly warn against sweeping a shared checkout
    assert "git add -a" in p or "git add ." in p  # the forbidden form is named...
    assert "never" in p                            # ...as something to NEVER do


def test_prompt_keeps_conventional_commit_reference():
    p = build_prompt(ISSUE)
    assert "#999" in p
    assert "conventional commit" in p.lower()
