"""Tests for the #2893 statusline provider-coverage readiness helper."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "scripts" / "readiness" / "statusline_provider_coverage.py"


def load_helper():
    assert MODULE_PATH.exists(), "missing statusline_provider_coverage.py helper"
    spec = importlib.util.spec_from_file_location("statusline_provider_coverage", MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["statusline_provider_coverage"] = module
    spec.loader.exec_module(module)
    return module


def test_parse_complete_output_requires_claude_codex_gemini_and_hermes_alias():
    helper = load_helper()

    parsed = helper.parse_statusline_output(
        "C:95%?|O:35%·2.5d·5h99%|G:100%·6.6d|H=O"
    )

    assert parsed["claude"]["state"] == "estimate"
    assert parsed["codex"]["weekly_remaining_pct"] == 35
    assert parsed["codex"]["five_hour_remaining_pct"] == 99
    assert parsed["gemini"]["state"] == "fresh"
    assert parsed["hermes"]["state"] == "alias"
    assert helper.contract_verdict(parsed) == "COMPLETE"


def test_contract_verdict_is_partial_without_hermes_alias_binding():
    helper = load_helper()

    parsed = helper.parse_statusline_output(
        "C:95%?|O:35%·2.5d·5h99%|G:100%·6.6d"
    )

    assert parsed["hermes"]["state"] == "missing"
    assert helper.contract_verdict(parsed) == "PARTIAL"


def test_parse_codex_without_5h_marks_5h_state_missing():
    helper = load_helper()

    parsed = helper.parse_statusline_output("C:95%?|O:35%·2.5d|G:100%·6.6d|H=O")

    assert parsed["codex"]["five_hour_remaining_pct"] is None
    assert parsed["codex"]["five_hour_state"] == "missing"
    assert helper.contract_verdict(parsed) == "PARTIAL"


def test_inspect_measured_paths_fails_closed_on_dirty_or_missing_required_paths(tmp_path):
    helper = load_helper()
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init"], cwd=repo, check=True, stdout=subprocess.DEVNULL)

    required = [
        ".claude/statusline-command.sh",
        ".claude/statusline-combined.sh",
        "tests/statusline/",
    ]
    for rel in required:
        path = repo / rel
        if rel.endswith("/"):
            path.mkdir(parents=True, exist_ok=True)
            (path / ".keep").write_text("tracked\n")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("tracked\n")
    subprocess.run(["git", "add", "--all"], cwd=repo, check=True)

    (repo / ".claude/statusline-command.sh").write_text("modified\n")
    (repo / ".claude/statusline-combined.sh").unlink()

    status = helper.inspect_measured_paths(repo, required)

    assert status["dirty"] is True
    assert ".claude/statusline-command.sh" in status["dirty_paths"]
    assert any(
        item["path"] == ".claude/statusline-command.sh" for item in status["dirty_entries"]
    )
    assert ".claude/statusline-combined.sh" in status["missing_paths"]


def test_issue_2894_open_or_unknown_blocks_complete(monkeypatch):
    helper = load_helper()
    parsed = helper.parse_statusline_output(
        "C:95%?|O:35%·2.5d·5h99%|G:100%·6.6d|H=O"
    )

    monkeypatch.setenv("STATUSLINE_R6_BLOCKER_STATE", "open")
    blocker = helper.issue_2894_state()

    assert blocker["state"] == "open"
    assert helper.final_verdict(parsed, blocker, dirty=False, missing_paths=[]) == "PARTIAL"
