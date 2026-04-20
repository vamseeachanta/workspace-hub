from unittest.mock import patch
from scripts.ecosystem_sync.signals import detect_showcase_labeled_closed_issues
from scripts.ecosystem_sync.state import RepoState


def _mock_gh_output(issues_by_label: dict[str, list[dict]]):
    """Return a function that mocks subprocess.run for gh issue list."""
    import json
    def fake_run(cmd, **kwargs):
        from subprocess import CompletedProcess
        for label, issues in issues_by_label.items():
            if f"--label" in cmd and label in cmd:
                return CompletedProcess(
                    cmd, 0, stdout=json.dumps(issues), stderr=""
                )
        return CompletedProcess(cmd, 0, stdout="[]", stderr="")
    return fake_run


def test_detects_new_closed_issue():
    issues = {"showcase": [
        {"number": 42, "title": "Deep-learning mooring model", "body": "body",
         "labels": [{"name": "showcase"}], "closedAt": "2026-04-20T10:00:00Z"}
    ]}
    state = RepoState(
        last_sync_utc="2026-04-20T00:00:00Z", last_commit_sha="",
        last_closed_showcase_issues=[],
    )
    with patch("subprocess.run", side_effect=_mock_gh_output(issues)):
        sigs = detect_showcase_labeled_closed_issues(
            "digitalmodel", state, since="2026-04-19"
        )
    assert len(sigs) == 1
    assert sigs[0].payload["issue_number"] == 42


def test_skips_known_issue():
    issues = {"showcase": [
        {"number": 42, "title": "T", "body": "b",
         "labels": [{"name": "showcase"}], "closedAt": "2026-04-20T10:00:00Z"}
    ]}
    state = RepoState(
        last_sync_utc="2026-04-20T00:00:00Z", last_commit_sha="",
        last_closed_showcase_issues=[42],
    )
    with patch("subprocess.run", side_effect=_mock_gh_output(issues)):
        sigs = detect_showcase_labeled_closed_issues(
            "digitalmodel", state, since="2026-04-19"
        )
    assert sigs == []


def test_skips_not_planned():
    issues = {"showcase": [
        {"number": 42, "title": "T", "body": "b",
         "labels": [{"name": "showcase"}, {"name": "not-planned"}],
         "closedAt": "2026-04-20T10:00:00Z"}
    ]}
    state = RepoState(
        last_sync_utc="2026-04-20T00:00:00Z", last_commit_sha="",
        last_closed_showcase_issues=[],
    )
    with patch("subprocess.run", side_effect=_mock_gh_output(issues)):
        sigs = detect_showcase_labeled_closed_issues(
            "digitalmodel", state, since="2026-04-19"
        )
    assert sigs == []
