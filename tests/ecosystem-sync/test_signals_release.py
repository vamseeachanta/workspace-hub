from datetime import datetime, timezone
from pathlib import Path
import os
import subprocess

import pytest

from scripts.ecosystem_sync import signals
from scripts.ecosystem_sync.signals import detect_release_tag
from scripts.ecosystem_sync.state import RepoState

# Policy: issues/2416 retains the 90-day cutoff. Hand calculation:
# 2026-04-01 minus 31 days (March), 28 (February), 31 (January)
# is 2026-01-01; equality is fresh under the existing strict-less-than filter.
# Boundary probes differ by one second; versions and other dates are synthetic.
RECENT = "2026-03-31T00:00:00+00:00"
OLD = "2025-12-31T23:59:59+00:00"
CUTOFF = "2026-01-01T00:00:00+00:00"


@pytest.fixture(autouse=True)
def frozen_clock(monkeypatch):
    class FrozenDatetime(datetime):
        @classmethod
        def now(cls, tz=None):
            return cls(2026, 4, 1, tzinfo=timezone.utc).astimezone(tz)

    monkeypatch.setattr(signals, "datetime", FrozenDatetime)


@pytest.fixture
def git_tags(monkeypatch):
    """Stub only Git; tagger and commit dates deliberately remain independent."""
    def install(tags):
        calls = []

        def git(repo, *args):
            assert repo == Path("release-fixture")
            calls.append(args)
            if args == ("tag", "-l"):
                return "\n".join(tags)
            if args[0] == "for-each-ref":
                assert args[1] == "--format=%(taggerdate:iso-strict)"
                tag = args[2].removeprefix("refs/tags/")
                value = tags[tag][0]
            elif args[:3] == ("log", "-1", "--format=%cI"):
                value = tags[args[3]][1]
            else:
                assert args[0] == "log" and args[-1] == "--oneline"
                return "abc release change\n"
            if isinstance(value, Exception):
                raise value
            return value + "\n"

        monkeypatch.setattr(signals, "_git", git)
        return calls

    return install


def _detect(known=()):
    state = RepoState(last_sync_utc="2026-04-01T00:00:00Z",
                      last_commit_sha="", last_seen_tags=list(known))
    return detect_release_tag("demo", Path("release-fixture"), state)


def test_detects_new_semver_tags(git_tags):
    git_tags({"v1.0.0": ("", RECENT), "v1.1.0": ("", RECENT)})
    assert [s.payload["tag"] for s in _detect()] == ["v1.0.0", "v1.1.0"]


def test_filters_nightly_snapshot_pre(git_tags):
    calls = git_tags({tag: ("", RECENT) for tag in
                      ("nightly-release", "snapshot-release", "pre-release", "notes", "v1.2.3")})
    assert [s.payload["tag"] for s in _detect()] == ["v1.2.3"]
    assert all("notes" not in call for call in calls)


def test_known_tag_not_re_reported(git_tags):
    calls = git_tags({"v1.0.0": ("", RECENT), "v1.1.0": ("", RECENT)})
    assert [s.payload["tag"] for s in _detect(["v1.0.0"])] == ["v1.1.0"]
    assert ("log", "-1", "--format=%cI", "v1.0.0") not in calls


def test_dedupe_key_format(git_tags):
    git_tags({"v1.0.0": ("", RECENT)})
    signal, = _detect()
    assert signal.dedupe_key == "release:demo:v1.0.0"
    assert signal.payload == {"tag": "v1.0.0"}
    assert signal.kind == "release"
    assert signal.title == "[sync] demo released v1.0.0"
    assert "abc release change" in signal.body


def test_recent_annotated_tag_on_old_commit_is_fresh(git_tags):
    calls = git_tags({"v1.0.0": (RECENT, OLD)})
    assert [s.payload["tag"] for s in _detect()] == ["v1.0.0"]
    assert ("log", "-1", "--format=%cI", "v1.0.0") not in calls


def test_old_annotated_tag_on_recent_commit_is_stale(git_tags):
    git_tags({"v1.0.0": (OLD, RECENT)})
    assert _detect() == []


@pytest.mark.parametrize("tagger,commit,fresh", [
    ("", RECENT, True), ("", OLD, False),
    ("", CUTOFF, True), (CUTOFF, OLD, True),
    ("", "2026-01-01T00:00:01+00:00", True),
    ("2026-01-01T00:00:01+00:00", OLD, True),
    ("2025-12-31T23:59:59+00:00", RECENT, False),
    ("2026-01-01T01:00:00+01:00", OLD, True),
])
def test_lightweight_and_cutoff_boundaries(git_tags, tagger, commit, fresh):
    git_tags({"v1.0.0": (tagger, commit)})
    assert bool(_detect()) is fresh


@pytest.mark.parametrize("tagger,commit", [
    ("invalid", RECENT), ("2026-02-30T00:00:00+00:00", RECENT),
    ("2026-03-31T00:00:00", RECENT), ("", "invalid"),
    ("", ""), ("", "2026-03-31T00:00:00"),
    (subprocess.CalledProcessError(1, "git"), RECENT),
    ("", subprocess.CalledProcessError(1, "git")),
])
def test_malformed_or_unavailable_dates_skip_tag(git_tags, tagger, commit):
    git_tags({"v1.0.0": (tagger, commit), "v1.1.0": ("", RECENT)})
    assert [s.payload["tag"] for s in _detect()] == ["v1.1.0"]


@pytest.mark.parametrize("commit_date,tagger_date,fresh", [
    (OLD, RECENT, True),
    (RECENT, OLD, False),
    (RECENT, None, True),
    (OLD, None, False),
])
def test_release_dates_with_real_git(tmp_path, monkeypatch, commit_date,
                                     tagger_date, fresh):
    """Exercise Git output parsing with independent commit and tagger dates."""
    # Confine every Git operation to the disposable repository, including when
    # callers export Git bindings or have signing, hooks or templates configured.
    for key in tuple(os.environ):
        if key.startswith("GIT_"):
            monkeypatch.delenv(key)
    monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", os.devnull)
    for role in ("AUTHOR", "COMMITTER"):
        monkeypatch.setenv(f"GIT_{role}_NAME", "Test fixture")
        monkeypatch.setenv(f"GIT_{role}_EMAIL", "fixture" + "@" + "example.invalid")
        monkeypatch.setenv(f"GIT_{role}_DATE", commit_date)

    repo = tmp_path / "release-repo"
    repo.mkdir()

    def git(*args):
        return subprocess.run(
            ["git", "-C", str(repo), *args],
            capture_output=True, text=True, check=True, timeout=30,
        ).stdout.strip()

    git("init", "--quiet", "--template=")
    assert Path(git("rev-parse", "--show-toplevel")) == repo.resolve()
    git("commit", "--quiet", "--allow-empty", "-m", "release fixture")
    if tagger_date is None:
        git("tag", "v1.0.0")
    else:
        monkeypatch.setenv("GIT_COMMITTER_DATE", tagger_date)
        git("tag", "--annotate", "v1.0.0", "-m", "release fixture")
    assert git("cat-file", "-t", "refs/tags/v1.0.0") == (
        "commit" if tagger_date is None else "tag"
    )
    assert git("log", "-1", "--format=%cI", "v1.0.0") == commit_date

    state = RepoState(last_sync_utc="2026-04-01T00:00:00Z",
                      last_commit_sha="", last_seen_tags=[])
    found = detect_release_tag("demo", repo, state)
    assert [signal.payload["tag"] for signal in found] == (
        ["v1.0.0"] if fresh else []
    )
    if fresh:
        assert found[0].dedupe_key == "release:demo:v1.0.0"
        assert "release fixture" in found[0].body
