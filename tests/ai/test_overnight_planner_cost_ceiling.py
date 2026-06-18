"""Cost-ceiling enforcement in the overnight batch planner (#3205, r1-F9/r2-C4).

Overnight/overnight-batch issues run in the hermes_batch context, where claude
is forbidden. The planner must:
  - never DEFAULT an overnight issue to claude (downgrade to the context primary),
  - HARD-ERROR on an explicit `agent:claude` label for an overnight issue,
  - keep `--dry-run` usable (its synthetic set must not contain a now-erroring
    agent:claude+overnight issue).
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "scripts" / "ai" / "overnight-batch-planner.py"
spec = importlib.util.spec_from_file_location("overnight_batch_planner", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules["overnight_batch_planner"] = module
spec.loader.exec_module(module)

resolve_agent = module.resolve_agent


def _issue(labels, body="design a complex architecture"):
    return {"number": 1, "title": "t", "body": body,
            "labels": [{"name": n} for n in labels]}


def test_overnight_no_claude_default():
    # Heuristic would pick claude (architecture/design/complex); under the
    # overnight ceiling it must downgrade to the context primary (codex).
    agent = resolve_agent(_issue(["overnight", "refactor"]))
    assert agent != "claude"
    assert agent == "codex"


def test_overnight_explicit_agent_claude_errors():
    with pytest.raises(ValueError):
        resolve_agent(_issue(["overnight", "agent:claude"]))


def test_overnight_explicit_codex_ok():
    assert resolve_agent(_issue(["overnight", "agent:codex"])) == "codex"


def test_overnight_multilabel_prefers_allowed_over_error():
    # review r3-F4: claude + codex both explicit under the ceiling -> pick codex,
    # do NOT hard-error just because claude was listed first.
    assert resolve_agent(_issue(["overnight", "agent:claude", "agent:codex"])) == "codex"


def test_non_overnight_issue_not_ceilinged():
    # Outside the overnight context the ceiling does not apply.
    assert resolve_agent(_issue(["agent:claude"])) == "claude"


def test_dry_run_synthetic_set_has_no_claude_overnight_issue():
    # r2-C4: every bundled synthetic overnight issue must resolve without error
    # and never to claude, so `--dry-run` stays usable.
    for issue in module._synthetic_issues():
        agent = resolve_agent(issue)
        assert agent != "claude", f"issue {issue['number']} resolved to claude"
