from scripts.ecosystem_sync.signals import detect_new_case_study
from scripts.ecosystem_sync.state import RepoState


def _state_with_baseline(sha) -> RepoState:
    return RepoState(
        last_sync_utc="2026-04-20T00:00:00Z",
        last_commit_sha=sha,
    )


def test_detects_new_case_study(case_study_repo, case_study_baseline):
    sigs = detect_new_case_study(
        "digitalmodel", case_study_repo, _state_with_baseline(case_study_baseline)
    )
    paths = sorted(s.payload["path"] for s in sigs)
    assert "case-studies/mooring-failures.md" in paths


def test_filters_draft_and_template(case_study_repo, case_study_baseline):
    sigs = detect_new_case_study(
        "digitalmodel", case_study_repo, _state_with_baseline(case_study_baseline)
    )
    paths = [s.payload["path"] for s in sigs]
    assert "case-studies/_draft/wip-study.md" not in paths
    assert "case-studies/CASE_STUDY_TEMPLATE.md" not in paths


def test_dedupe_key(case_study_repo, case_study_baseline):
    sigs = detect_new_case_study(
        "digitalmodel", case_study_repo, _state_with_baseline(case_study_baseline)
    )
    assert all(s.dedupe_key.startswith("case-study:digitalmodel:") for s in sigs)
