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


@pytest.fixture(
    params=["space name.sh", "tab\tname.sh", "line\nname.sh", "-leading.sh", "nested/control.sh"],
    ids=["space", "tab", "newline", "leading-dash", "nested"],
)
def unusual_name(request):
    return request.param


@pytest.fixture(
    # Independent permission and index literals from the module's Git citation.
    params=[(False, 0o644, "100644"), (True, 0o755, "100755")],
    ids=["nonexecutable", "executable"],
)
def native_mode(request):
    return request.param


def commit_unusual_file(repo, relative, executable):
    path = repo / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("#!/bin/sh\nexit 0\n")
    prepare_file_mode(path, executable=executable)
    commit_all(repo)
    return path


def assert_unusual_index_record(repo, relative, indexed):
    blob = git(repo, "hash-object", "--", relative).strip()
    # Handwritten stage-zero record: mode, blob, stage, TAB, verbatim name, NUL.
    # Mode and stage follow the module's Git index-format citation.
    assert git(repo, "ls-files", "--stage", "-z", "--", relative) == (
        f"{indexed} {blob} 0\t{relative}\0"
    )


def test_unusual_names_have_clean_physical_and_index_modes(
    tmp_path, monkeypatch, unusual_name, native_mode
):
    executable, physical, indexed = native_mode
    _, repo = native_repo(monkeypatch, tmp_path)
    path = commit_unusual_file(repo, unusual_name, executable)

    assert stat.S_IMODE(path.stat().st_mode) == physical
    assert git(repo, "config", "--get", "core.filemode").strip() == "true"
    assert_unusual_index_record(repo, unusual_name, indexed)
    assert git(
        repo, "status", "--porcelain=v1", "-z", "--untracked-files=all", "--", unusual_name
    ) == ""
    assert_file_modes(repo, unusual_name, executable=executable)


@pytest.mark.parametrize("mismatch", ["physical", "index", "content"])
def test_unusual_name_mismatch_is_rejected(
    tmp_path, monkeypatch, unusual_name, native_mode, mismatch
):
    executable, physical, indexed = native_mode
    _, repo = native_repo(monkeypatch, tmp_path)
    path = commit_unusual_file(repo, unusual_name, executable)
    assert_file_modes(repo, unusual_name, executable=executable)
    blob = git(repo, "hash-object", "--", unusual_name).strip()
    expected_index = indexed

    if mismatch == "physical":
        # Invert only executability, using the cited permission literals.
        path.chmod(0o644 if executable else 0o755)
        expected_error = "physical mode mismatch"
    elif mismatch == "index":
        git(repo, "update-index", "--chmod=-x" if executable else "--chmod=+x", "--", unusual_name)
        expected_index = "100644" if executable else "100755"
        expected_error = "index mode mismatch"
    else:
        path.write_text("#!/bin/sh\nexit 1\n")
        expected_error = "owned path is dirty"

    assert git(repo, "config", "--get", "core.filemode").strip() == "true"
    assert git(repo, "ls-files", "--stage", "-z", "--", unusual_name) == (
        f"{expected_index} {blob} 0\t{unusual_name}\0"
    )
    if mismatch != "physical":
        assert stat.S_IMODE(path.stat().st_mode) == physical
    # Porcelain v1: index-only chmod is staged AND differs from physical mode;
    # physical-only chmod and changed content have only an unstaged modification.
    status = "MM" if mismatch == "index" else " M"
    assert git(
        repo, "status", "--porcelain=v1", "-z", "--untracked-files=all", "--", unusual_name
    ) == f"{status} {unusual_name}\0"
    with pytest.raises(AssertionError, match=expected_error):
        assert_file_modes(repo, unusual_name, executable=executable)


@pytest.mark.parametrize("kind", ["symlink", "missing"])
def test_nonregular_fixture_refused(tmp_path, monkeypatch, unusual_name, native_mode, kind):
    executable, physical, _indexed = native_mode
    _, repo = native_repo(monkeypatch, tmp_path)
    path = repo / unusual_name
    path.parent.mkdir(parents=True, exist_ok=True)
    target = repo / "regular-target.sh"
    target.write_text("#!/bin/sh\nexit 0\n")
    target.chmod(physical)
    if kind == "symlink":
        path.symlink_to(os.path.relpath(target, path.parent))
    commit_all(repo)
    before = target.read_bytes(), stat.S_IMODE(target.stat().st_mode)

    with pytest.raises(AssertionError, match="expected regular fixture file"):
        prepare_file_mode(path, executable=not executable)
    with pytest.raises(AssertionError, match="expected regular fixture file"):
        assert_file_modes(repo, unusual_name, executable=executable)

    assert (target.read_bytes(), stat.S_IMODE(target.stat().st_mode)) == before
    assert path.is_symlink() == (kind == "symlink")
    assert path.exists() == (kind == "symlink")
    assert git(repo, "config", "--get", "core.filemode").strip() == "true"
    assert git(
        repo, "status", "--porcelain=v1", "-z", "--untracked-files=all", "--", unusual_name
    ) == ""
