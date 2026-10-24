"""Native fixture modes: expected values follow Git's index-format contract.

Source: Git 2.44.0 gitformat-index, Index entry mode field.
https://git-scm.com/docs/gitformat-index/2.44.0
Regular files use permission fields 644 or 755; only executability is tracked.
Each expected status is derived independently from the deliberate chmod/index
operations below, rather than calculated by the helper under test.
"""
import os
import stat

import pytest
from fixture_modes import assert_file_modes, prepare_file_mode
from test_sibling_sso_native_preflight import commit_all, git, native_repo

pytestmark = pytest.mark.skipif(
    os.name == "nt", reason="POSIX physical mode coverage requires a native filesystem"
)


@pytest.mark.parametrize("executable", [False, True])
def test_prepared_file_has_physical_index_and_clean_status(tmp_path, monkeypatch, executable):
    _, repo = native_repo(monkeypatch, tmp_path)
    path = repo / "control.sh"
    path.write_text("#!/bin/sh\nexit 0\n")
    prepare_file_mode(path, executable=executable)
    commit_all(repo)
    assert_file_modes(repo, "control.sh", executable=executable)
    # Independent literals from the cited index format, not the helper's table.
    assert stat.S_IMODE(path.stat().st_mode) == (0o755 if executable else 0o644)
    assert git(repo, "ls-files", "--stage", "--", "control.sh").split()[0] == (
        "100755" if executable else "100644"
    )
    assert git(repo, "status", "--porcelain", "--", "control.sh") == ""


@pytest.mark.parametrize("executable", [False, True])
def test_physical_mode_mismatch_is_rejected(tmp_path, monkeypatch, executable):
    """An unchanged blob with inverted executability is dirty with filemode=true."""
    _, repo = native_repo(monkeypatch, tmp_path)
    path = repo / "control.sh"
    path.write_text("#!/bin/sh\nexit 0\n")
    prepare_file_mode(path, executable=executable)
    commit_all(repo)
    prepare_file_mode(path, executable=not executable)
    with pytest.raises(AssertionError, match="physical mode"):
        assert_file_modes(repo, "control.sh", executable=executable)
    assert git(repo, "diff-files", "--name-only", "--", "control.sh").strip() == "control.sh"


def test_index_only_executable_fix_is_rejected(tmp_path, monkeypatch):
    """644 on disk + 100755 in index => physical mismatch and unstaged dirt."""
    _, repo = native_repo(monkeypatch, tmp_path)
    path = repo / "control.sh"
    path.write_text("#!/bin/sh\nexit 0\n")
    prepare_file_mode(path, executable=False)
    commit_all(repo)
    git(repo, "update-index", "--chmod=+x", "--", "control.sh")
    with pytest.raises(AssertionError, match="physical mode"):
        assert_file_modes(repo, "control.sh", executable=True)
    with pytest.raises(AssertionError, match="index mode"):
        assert_file_modes(repo, "control.sh", executable=False)
    assert git(repo, "diff-files", "--name-only", "--", "control.sh").strip() == "control.sh"


def test_mode_check_requires_clean_content(tmp_path, monkeypatch):
    _, repo = native_repo(monkeypatch, tmp_path)
    path = repo / "control.sh"
    path.write_text("#!/bin/sh\nexit 0\n")
    prepare_file_mode(path, executable=True)
    commit_all(repo)
    path.write_text("#!/bin/sh\nexit 1\n")
    with pytest.raises(AssertionError, match="owned path is dirty"):
        assert_file_modes(repo, "control.sh", executable=True)


def test_mode_check_refuses_disabled_native_detection(tmp_path, monkeypatch):
    _, repo = native_repo(monkeypatch, tmp_path)
    commit_all(repo)
    git(repo, "config", "core.filemode", "false")
    with pytest.raises(AssertionError, match="requires core.filemode=true"):
        assert_file_modes(repo, "AGENTS.md", executable=False)


def test_mode_check_ignores_foreign_git_bindings(tmp_path, monkeypatch):
    """A foreign index must remain byte-for-byte unchanged by fixture readback."""
    _, repo = native_repo(monkeypatch, tmp_path)
    commit_all(repo)
    foreign = tmp_path / "foreign"
    foreign.mkdir()
    git(foreign, "init", "-q")
    before = {p.relative_to(foreign): p.read_bytes() for p in foreign.rglob("*") if p.is_file()}
    monkeypatch.setenv("GIT_DIR", str(foreign / ".git"))
    monkeypatch.setenv("GIT_WORK_TREE", str(foreign))
    monkeypatch.setenv("GIT_COMMON_DIR", str(foreign / ".git"))
    monkeypatch.setenv("GIT_INDEX_FILE", str(foreign / ".git/index"))
    assert_file_modes(repo, "AGENTS.md", executable=False)
    assert {p.relative_to(foreign): p.read_bytes() for p in foreign.rglob("*") if p.is_file()} == before
