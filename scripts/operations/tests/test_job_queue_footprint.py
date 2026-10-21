"""Independent byte counts for a disposable two-revision storage experiment."""

import importlib.util
import hashlib
import os
from pathlib import Path

import pytest

from test_job_queue_windows import git, write_text

MODULE = Path(__file__).parents[1] / "job_queue_footprint.py"


def load_module():
    spec = importlib.util.spec_from_file_location("footprint", MODULE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def source_repo(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    git(["init", "-b", "main"], source)
    git(["config", "user.name", "Test"], source)
    git(["config", "user.email", "test"], source)
    write_text(source / "README.md", "abc\n")
    write_text(source / "selected" / "item.txt", "xy\n")
    write_text(source / "excluded" / "item.txt", "z\n")
    git(["add", "."], source)
    git(["commit", "-m", "initial"], source)
    write_text(source / "README.md", "abcd\n")
    git(["add", "."], source)
    git(["commit", "-m", "update"], source)
    return source


@pytest.mark.parametrize("autocrlf", ["false", "true"])
def test_layouts_have_independently_counted_payloads(tmp_path, monkeypatch, autocrlf):
    """Full: 5+3+2=10 bytes; cone sparse: root 5 + selected 3=8 bytes.

    Git sparse-checkout cone mode includes root files; history is two commits
    except the depth-one clone. These are hand counts of fixture literals.
    """
    home = tmp_path / "home"
    home.mkdir()
    write_text(home / ".gitconfig", f"[core]\n\tautocrlf = {autocrlf}\n\teol = crlf\n")
    for key in ("HOME", "USERPROFILE", "XDG_CONFIG_HOME"):
        monkeypatch.setenv(key, str(home))
    source = source_repo(tmp_path)
    before = git(["status", "--porcelain"], source).stdout
    caller = tmp_path / "caller"
    caller.mkdir()
    git(["init"], caller)
    write_text(caller / "keep.txt", "caller evidence\n")
    def digests(root):
        return {path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
                for path in root.rglob("*") if path.is_file()}
    source_before, caller_before = digests(source), digests(caller)
    for key in ("GIT_DIR", "GIT_COMMON_DIR"):
        monkeypatch.setenv(key, str(caller / ".git"))
    monkeypatch.setenv("GIT_WORK_TREE", str(caller))
    result = load_module().measure(source, tmp_path / "experiment", "selected")
    assert digests(source) == source_before
    assert digests(caller) == caller_before
    rows = {row["layout"]: row for row in result["measurements"]}
    assert set(rows) == {"full", "linked", "shallow", "sparse"}
    for name in ("full", "linked", "shallow"):
        assert rows[name]["payload_bytes"] == 10
    assert rows["sparse"]["payload_bytes"] == 8
    assert rows["linked"]["incremental_object_bytes"] == 0
    assert rows["shallow"]["commits"] == 1
    assert rows["full"]["commits"] == 2
    assert result["git_version"] == git(["--version"], source).stdout.strip()
    assert result["core_autocrlf"] == "false"
    assert result["core_eol"] == "lf"
    assert result["source_commit"] == git(["rev-parse", "HEAD"], source).stdout.strip()
    assert git(["status", "--porcelain"], source).stdout == before
    assert len(git(["worktree", "list", "--porcelain"], source).stdout.split("worktree ")) == 2


def test_existing_experiment_is_never_overwritten(tmp_path):
    source = source_repo(tmp_path)
    destination = tmp_path / "experiment"
    destination.mkdir()
    write_text(destination / "keep", "retained\n")
    with pytest.raises(FileExistsError):
        load_module().measure(source, destination, "selected")
    assert (destination / "keep").read_text() == "retained\n"


@pytest.mark.parametrize("nested", [False, True])
def test_broken_symlink_counts_its_stored_target_bytes(tmp_path, monkeypatch, nested):
    """A link stores the literal target 'absent': six bytes, with no target file."""
    link = tmp_path / "link"
    try:
        link.symlink_to("absent")
    except OSError:
        pytest.skip("symlink creation unavailable")
    # Emulate the zero-size symlink metadata returned on Windows.
    original_lstat = Path.lstat
    def zero_size_lstat(path, *args, **kwargs):
        result = original_lstat(path, *args, **kwargs)
        if path == link:
            fields = list(result)
            fields[6] = 0
            return os.stat_result(fields)
        return result
    monkeypatch.setattr(Path, "lstat", zero_size_lstat)
    assert load_module().file_bytes(tmp_path if nested else link) == len(b"absent")


@pytest.mark.parametrize("selected", ["../escape", "/absolute", "", ".git", "missing"])
def test_sparse_selection_must_name_a_tracked_directory(tmp_path, selected):
    source = source_repo(tmp_path)
    destination = tmp_path / "experiment"
    with pytest.raises(ValueError):
        load_module().measure(source, destination, selected)
    assert not destination.exists()
