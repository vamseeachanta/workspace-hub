from pathlib import Path
from scripts.ecosystem_sync.state import (
    load_state, save_state, has_substantive_change, RepoState
)


def test_load_state_missing_file_returns_empty(tmp_path):
    state = load_state(tmp_path / "missing.yaml")
    assert state == {}


def test_roundtrip(tmp_path):
    path = tmp_path / "state.yaml"
    state = {
        "digitalmodel": RepoState(
            last_sync_utc="2026-04-20T11:00:00Z",
            last_commit_sha="abc123",
            last_seen_tags=["v1.0.0"],
            last_readme_hash={"Capabilities": "sha256:xyz"},
            last_case_studies=[],
            last_closed_showcase_issues=[],
        )
    }
    save_state(path, state)
    loaded = load_state(path)
    assert loaded["digitalmodel"].last_commit_sha == "abc123"


def test_substantive_change_ignores_timestamp_only():
    before = {"digitalmodel": RepoState(
        last_sync_utc="2026-04-19T11:00:00Z",
        last_commit_sha="abc", last_seen_tags=[], last_readme_hash={},
        last_case_studies=[], last_closed_showcase_issues=[],
    )}
    after = {"digitalmodel": RepoState(
        last_sync_utc="2026-04-20T11:00:00Z",  # only this changed
        last_commit_sha="abc", last_seen_tags=[], last_readme_hash={},
        last_case_studies=[], last_closed_showcase_issues=[],
    )}
    assert has_substantive_change(before, after) is False


def test_substantive_change_detects_new_tag():
    before = {"digitalmodel": RepoState(
        last_sync_utc="2026-04-19T11:00:00Z",
        last_commit_sha="abc", last_seen_tags=["v1.0.0"], last_readme_hash={},
        last_case_studies=[], last_closed_showcase_issues=[],
    )}
    after = {"digitalmodel": RepoState(
        last_sync_utc="2026-04-20T11:00:00Z",
        last_commit_sha="abc", last_seen_tags=["v1.0.0", "v1.1.0"],
        last_readme_hash={}, last_case_studies=[], last_closed_showcase_issues=[],
    )}
    assert has_substantive_change(before, after) is True
