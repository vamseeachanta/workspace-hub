from __future__ import annotations

import importlib.util
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "scripts" / "cron" / "gemini-nightly-batch.py"
spec = importlib.util.spec_from_file_location("gemini_nightly_batch", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules["gemini_nightly_batch"] = module
spec.loader.exec_module(module)


class Result:
    def __init__(self, stdout: str):
        self.returncode = 0
        self.stdout = stdout
        self.stderr = ""


def _issue(number: int, label: str) -> dict:
    return {
        "number": number,
        "title": f"Issue {number}",
        "labels": [{"name": label}],
        "body": "",
        "createdAt": "2026-10-08T00:00:00Z",
    }


def test_fetch_gemini_issues_reads_ai_agy_and_legacy_agent_aliases(monkeypatch):
    calls: list[list[str]] = []

    def fake_run_cmd(cmd: list[str], check: bool = True, capture: bool = True):
        calls.append(cmd)
        if 'ai:agy' in cmd:
            return Result(json.dumps([_issue(1, "ai:agy")]))
        if 'agent:gemini' in cmd:
            return Result(json.dumps([_issue(2, "agent:gemini")]))
        if 'agent:agy' in cmd:
            return Result(json.dumps([_issue(1, "agent:agy")]))
        raise AssertionError(cmd)

    monkeypatch.setattr(module, "run_cmd", fake_run_cmd)

    issues = module.fetch_gemini_issues()

    assert [issue["number"] for issue in issues] == [1, 2]
    assert any('ai:agy' in call for call in calls)
    assert any('agent:gemini' in call for call in calls)


@pytest.fixture(autouse=True)
def captured_subprocess(monkeypatch):
    """Keep every subprocess mocked, including unexpected calls."""
    calls = []
    result = Result("captured output")

    def fake_run(cmd, **kwargs):
        calls.append((cmd, kwargs))
        return result

    monkeypatch.setattr(module.subprocess, "run", fake_run)
    return calls, result


# Synthetic examples: issue 1 and midnight UTC on the first day of 2026.
# Return codes use the conventional zero-success/nonzero-failure contract.
# Expected bodies below transcribe the existing comment templates independently;
# prerequisite amounts and context sizes retain those templates' values.
@pytest.fixture
def fixed_clock(monkeypatch):
    class FixedDatetime:
        @classmethod
        def now(cls, tz):
            assert tz is timezone.utc
            return datetime(2026, 1, 1, tzinfo=tz)

    monkeypatch.setattr(module, "datetime", FixedDatetime)


@pytest.mark.parametrize(
    "check,capture,returncode",
    [(True, True, 0), (True, True, 1), (False, False, 1)],
)
def test_run_cmd_preserves_options_and_result(
    captured_subprocess, capsys, check, capture, returncode
):
    calls, completed = captured_subprocess
    completed.returncode = returncode
    completed.stderr = "synthetic failure"
    argv = ["gh", "issue", "comment", "1", "-b", ADVERSARIAL_TEXT]

    result = module.run_cmd(argv, check=check, capture=capture)

    assert result is completed
    assert calls == [(argv, {
        "shell": False,
        "capture_output": capture,
        "text": True,
        "cwd": module.WORKSPACE_HUB,
        # Existing wrapper timeout, retained unchanged by this repair.
        "timeout": 120,
    })]
    assert ("Command failed:" in capsys.readouterr().out) is (
        check and returncode != 0
    )


ADVERSARIAL_TEXT = "synthetic 'single' \"double\" `printf probe` $(printf probe)\nnext line"


def test_discovery_uses_argument_lists(captured_subprocess):
    calls, completed = captured_subprocess
    completed.stdout = "[]"

    assert module.fetch_gemini_issues() == []

    assert [cmd for cmd, _ in calls] == [
        ["gh", "issue", "list", "--label", label, "--state", "open",
         # Existing fetch_gemini_issues issue-list limit.
         "--json", "number,title,labels,body,createdAt", "--limit", "50"]
        for label in ["ai:agy", "agent:agy", "agent:gemini"]
    ]
    assert all(options["shell"] is False for _, options in calls)


@pytest.mark.parametrize("mode", ["local", "router"])
@pytest.mark.parametrize("returncode", [0, 1])
def test_comment_body_is_one_unchanged_argument(
    captured_subprocess, fixed_clock, mode, returncode
):
    calls, completed = captured_subprocess
    completed.returncode = returncode
    issue = {
        "number": 1,
        "title": ADVERSARIAL_TEXT,
        "body": ADVERSARIAL_TEXT,
        "category": ADVERSARIAL_TEXT,
    }
    if mode == "local":
        expected_body = (
            "**Gemini Nightly Batch — Triage Notes**\n\n"
            f"**Category:** {ADVERSARIAL_TEXT}\n"
            "**Execution Mode:** Local (filesystem/script)\n"
            "**Auto-processed:** 2026-01-01 00:00 UTC\n\n"
            "**Approach:**\n"
            "- General triage — review issue scope and assign to appropriate agent\n"
            "- If implementation-ready, re-label with ai:claude or ai:codex\n"
        )
        status = "triaged"
        process = module.process_local_issue
    else:
        expected_body = (
            "**Gemini Nightly Batch — Research Queue**\n\n"
            f"**Category:** {ADVERSARIAL_TEXT}\n"
            "**Execution Mode:** Router (Gemini 1M context / web research)\n"
            "**Queued:** 2026-01-01 00:00 UTC\n\n"
            "This issue requires Gemini's extended context or web research capabilities. "
            "It will be processed in the next available Gemini router session.\n\n"
            "**Prerequisites:**\n"
            "- OpenRouter credit balance > $5\n"
            "- Task prompt prepared in /tmp/gemini-task-1.txt\n"
        )
        status = "queued-for-router"
        process = module.process_router_issue

    result = process(issue)

    assert result == {
        "number": issue["number"],
        "status": status if returncode == 0 else "comment-failed",
        "mode": mode,
        "category": ADVERSARIAL_TEXT,
    }
    assert [cmd for cmd, _ in calls] == [
        ["gh", "issue", "comment", "1", "-b", expected_body]
    ]
    assert all(options["shell"] is False for _, options in calls)


@pytest.mark.parametrize("mode", ["local", "router"])
def test_dry_run_does_not_start_a_subprocess(captured_subprocess, mode):
    calls, _ = captured_subprocess
    process = getattr(module, f"process_{mode}_issue")
    issue = {"number": 1, "title": ADVERSARIAL_TEXT, "category": ADVERSARIAL_TEXT}

    assert process(issue, dry_run=True) == {
        "number": issue["number"], "status": "dry-run", "mode": mode,
    }
    assert calls == []
