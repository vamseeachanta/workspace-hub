from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

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
    calls: list[str] = []

    def fake_run_cmd(cmd: str, check: bool = True, capture: bool = True):
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
