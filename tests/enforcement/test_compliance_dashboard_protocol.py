"""Dashboard transport regressions for issue #3596 (2026)."""

import json
import subprocess

import pytest
from test_compliance_dashboard import SCRIPT, init_repo, run, run_dashboard


@pytest.fixture(autouse=True)
def isolated_git_environment(monkeypatch):
    """Fixture repositories must not inherit bindings to the caller's checkout."""
    for variable in ("GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR"):
        monkeypatch.delenv(variable, raising=False)


def test_json_mode_is_one_document_and_matches_saved_report(tmp_path):
    """One unreviewed commit: 0 / 1 * 100 = 0 (independent arithmetic)."""
    init_repo(tmp_path)
    run(["git", "commit", "--allow-empty", "-m", 'fix(core): quote "and" slash \\'], tmp_path)
    result = run_dashboard(tmp_path, {"COMPLIANCE_FORMAT": "json"})
    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["reviewable"] == 1
    assert payload["compliance_rate"] == 0
    assert payload["unreviewed_commits"] == [
        {
            "hash": subprocess.check_output(
                ["git", "rev-parse", "HEAD"], cwd=tmp_path, text=True
            ).strip(),
            "subject": 'fix(core): quote "and" slash \\',
        }
    ]


def test_json_flag_and_external_output_directory(tmp_path):
    """An empty window has no review obligations, so the dashboard passes."""
    import os
    import subprocess

    repo = tmp_path / "repo"
    repo.mkdir()
    init_repo(repo)
    reports = tmp_path / "reports"
    result = subprocess.run(
        ["bash", str(SCRIPT), "--json"], cwd=repo, text=True, capture_output=True,
        env={**os.environ, "COMPLIANCE_REPORTS_DIR": str(reports)}, check=False,
    )
    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["reviewable"] == 0
    assert payload["unreviewed_commits"] == []
    assert payload["verdict"] == "PASS"
    assert json.loads(next(reports.glob("compliance-*.json")).read_text()) == payload
    assert not (repo / "logs" / "compliance").exists()
