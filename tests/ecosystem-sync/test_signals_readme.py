import hashlib

from scripts.ecosystem_sync.signals import (
    detect_readme_capability_diff, _extract_section, _hash_section
)
from scripts.ecosystem_sync.state import RepoState


def test_extract_section_basic():
    md = "# T\n\n## Capabilities\n- one\n- two\n\n## Other\nx\n"
    assert _extract_section(md, "Capabilities").strip() == "- one\n- two"


def test_extract_section_missing_returns_empty():
    md = "# T\n## Other\nx\n"
    assert _extract_section(md, "Capabilities") == ""


def test_hash_section_ignores_trailing_whitespace():
    a = _hash_section("- one\n- two")
    b = _hash_section("- one\n- two\n\n")
    assert a == b


def test_diff_fires_on_changed_hash(readme_repo):
    state = RepoState(
        last_sync_utc="2026-04-20T00:00:00Z",
        last_commit_sha="",
        last_readme_hash={"Capabilities": "sha256:wrong"},
    )
    sigs = detect_readme_capability_diff(
        "digitalmodel", readme_repo, state, sections=["Capabilities"]
    )
    assert len(sigs) == 1
    assert sigs[0].kind == "readme-diff"


def test_diff_no_fire_when_hash_matches(readme_repo):
    # Literal normalized fixture bytes keep the oracle independent of the detector.
    normalized = b"- thing one\n- thing two"
    expected_hash = "sha256:" + hashlib.sha256(normalized).hexdigest()
    state = RepoState(
        last_sync_utc="2026-04-20T00:00:00Z",
        last_commit_sha="",
        last_readme_hash={"Capabilities": expected_hash},
    )
    sigs = detect_readme_capability_diff(
        "digitalmodel", readme_repo, state, sections=["Capabilities"]
    )
    assert sigs == []


def test_missing_section_is_silent(readme_repo):
    state = RepoState(
        last_sync_utc="2026-04-20T00:00:00Z", last_commit_sha="",
    )
    sigs = detect_readme_capability_diff(
        "digitalmodel", readme_repo, state, sections=["Nonexistent Heading"]
    )
    assert sigs == []
