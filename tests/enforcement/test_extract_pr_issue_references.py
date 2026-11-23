from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/enforcement/extract-pr-issue-references.py"


def _event(title: str, body: str) -> str:
    return json.dumps({"pull_request": {"title": title, "body": body}})


def _run_event(tmp_path: Path, title: str, body: str, repo: str = "example/project"):
    event = tmp_path / "event.json"
    event.write_text(_event(title, body))
    env = {**os.environ, "GITHUB_REPOSITORY": repo}
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(event)],
        env=env,
        capture_output=True,
        text=True,
    )


def test_extracts_bare_qualified_and_url_issue_references(tmp_path: Path):
    result = _run_event(
        tmp_path,
        "Fix #12 and upstream/repo#34",
        "Closes https://github.com/other/project/issues/56?plain=1#notes",
    )
    assert result.returncode == 0
    assert result.stdout.strip().split() == [
        "example/project#12",
        "upstream/repo#34",
        "other/project#56",
    ]


def test_pull_request_url_is_not_an_issue_reference(tmp_path: Path):
    result = _run_event(
        tmp_path,
        "Review pointer",
        "See https://github.com/other/project/pull/56 and issue #57.",
    )
    assert result.returncode == 0
    assert result.stdout.strip().split() == ["example/project#57"]


def test_deduplicates_per_repository_and_number(tmp_path: Path):
    result = _run_event(
        tmp_path,
        "Fix #12",
        "Duplicates example/project#12 and https://github.com/example/project/issues/12.",
    )
    assert result.returncode == 0
    assert result.stdout.strip().split() == ["example/project#12"]


def test_bare_reference_requires_repository_context(tmp_path: Path):
    event = tmp_path / "event.json"
    event.write_text(_event("Fix #12", ""))
    env = {**os.environ}
    env.pop("GITHUB_REPOSITORY", None)
    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(event)],
        env=env,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    assert "default repository is required" in result.stderr


def test_workflow_marker_label_parity_step_is_yaml_and_fail_capable():
    yaml = pytest.importorskip("yaml", reason="PyYAML is not installed")
    workflow = ROOT / ".github/workflows/enforcement-gate.yml"
    data = yaml.safe_load(workflow.read_text())
    job = data["jobs"]["marker-label-parity"]
    run_block = job["steps"][1]["run"]

    assert "python3 - <<'PY'" not in run_block
    assert "set -o pipefail" in run_block
    assert "tee /tmp/marker-parity.log" in run_block
    assert "extract-pr-issue-references.py" in run_block
