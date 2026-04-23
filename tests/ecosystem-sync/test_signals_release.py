from pathlib import Path
from scripts.ecosystem_sync.signals import detect_release_tag
from scripts.ecosystem_sync.state import RepoState

FIXTURE = Path(__file__).parent / "fixtures" / "repos" / "repo-with-release"


def _empty_state() -> RepoState:
    return RepoState(
        last_sync_utc="2026-04-20T00:00:00Z",
        last_commit_sha="",
        last_seen_tags=[],
    )


def test_detects_new_semver_tags():
    sigs = detect_release_tag("digitalmodel", FIXTURE, _empty_state())
    tags = sorted(s.payload["tag"] for s in sigs)
    assert tags == ["v1.0.0", "v1.1.0"]


def test_filters_nightly_snapshot_pre():
    sigs = detect_release_tag("digitalmodel", FIXTURE, _empty_state())
    for s in sigs:
        assert not s.payload["tag"].startswith(("nightly-", "snapshot-", "pre-"))


def test_known_tag_not_re_reported():
    state = RepoState(
        last_sync_utc="2026-04-20T00:00:00Z",
        last_commit_sha="",
        last_seen_tags=["v1.0.0"],
    )
    sigs = detect_release_tag("digitalmodel", FIXTURE, state)
    tags = [s.payload["tag"] for s in sigs]
    assert tags == ["v1.1.0"]


def test_dedupe_key_format():
    sigs = detect_release_tag("digitalmodel", FIXTURE, _empty_state())
    for s in sigs:
        assert s.dedupe_key == f"release:digitalmodel:{s.payload['tag']}"
