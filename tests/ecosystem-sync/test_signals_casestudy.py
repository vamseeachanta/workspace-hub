from pathlib import Path
from scripts.ecosystem_sync.signals import detect_new_case_study
from scripts.ecosystem_sync.state import RepoState

FIXTURE = Path(__file__).parent / "fixtures" / "repos" / "repo-with-casestudy"
BASELINE_FILE = FIXTURE.parent / "repo-with-casestudy.baseline-sha"


def _state_with_baseline() -> RepoState:
    sha = BASELINE_FILE.read_text().strip()
    return RepoState(
        last_sync_utc="2026-04-20T00:00:00Z",
        last_commit_sha=sha,
    )


def test_detects_new_case_study():
    sigs = detect_new_case_study("digitalmodel", FIXTURE, _state_with_baseline())
    paths = sorted(s.payload["path"] for s in sigs)
    assert "case-studies/mooring-failures.md" in paths


def test_filters_draft_and_template():
    sigs = detect_new_case_study("digitalmodel", FIXTURE, _state_with_baseline())
    paths = [s.payload["path"] for s in sigs]
    assert "case-studies/_draft/wip-study.md" not in paths
    assert "case-studies/CASE_STUDY_TEMPLATE.md" not in paths


def test_dedupe_key():
    sigs = detect_new_case_study("digitalmodel", FIXTURE, _state_with_baseline())
    assert all(s.dedupe_key.startswith("case-study:digitalmodel:") for s in sigs)
