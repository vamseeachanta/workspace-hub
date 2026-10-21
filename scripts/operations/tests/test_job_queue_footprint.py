"""Independent byte counts for a disposable two-revision storage experiment."""

import hashlib
import importlib.util
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


def test_layouts_have_independently_counted_payloads(tmp_path, monkeypatch):
    """Full: 5+3+2=10 bytes; cone sparse: root 5 + selected 3=8 bytes.

    Git sparse-checkout cone mode includes root files; history is two commits
    except the depth-one clone. These are hand counts of fixture literals.
    """
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
    assert result["checkout_policy"] == {"core.autocrlf": "false", "core.eol": "lf"}
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


def test_broken_symlink_counts_its_stored_target_bytes(tmp_path):
    """A link stores the literal target 'absent': six bytes, with no target file."""
    link = tmp_path / "link"
    try:
        link.symlink_to("absent")
    except OSError:
        pytest.skip("symlink creation unavailable")
    assert load_module().file_bytes(link) == len(b"absent")
    assert load_module().file_bytes(tmp_path) == len(b"absent")


def test_checkout_overrides_conflicting_git_defaults(tmp_path, monkeypatch):
    source = source_repo(tmp_path)
    module = load_module()
    original_run = module.subprocess.run
    config = tmp_path / "gitconfig"
    write_text(config, "[core]\n\tautocrlf = true\n\teol = crlf\n")

    def with_conflicting_defaults(*args, **kwargs):
        kwargs["env"].update(GIT_CONFIG_GLOBAL=str(config), GIT_CONFIG_NOSYSTEM="1")
        return original_run(*args, **kwargs)

    monkeypatch.setattr(module.subprocess, "run", with_conflicting_defaults)
    result = module.measure(source, tmp_path / "experiment", "selected")
    assert [row["payload_bytes"] for row in result["measurements"]] == [10, 10, 10, 8]


def test_directory_symlink_counts_target_without_following(tmp_path):
    target = tmp_path / "target"
    target.mkdir()
    write_text(target / "payload", "not counted through the link\n")
    container = tmp_path / "container"
    container.mkdir()
    link = container / "link"
    try:
        link.symlink_to(target, target_is_directory=True)
    except OSError:
        pytest.skip("symlink creation unavailable")
    expected = len(os.fsencode(os.readlink(link)))
    assert load_module().file_bytes(link) == expected
    assert load_module().file_bytes(container) == expected


@pytest.mark.parametrize("selected", ["../escape", "/absolute", "", ".git", "missing"])
def test_sparse_selection_must_name_a_tracked_directory(tmp_path, selected):
    source = source_repo(tmp_path)
    destination = tmp_path / "experiment"
    with pytest.raises(ValueError):
        load_module().measure(source, destination, selected)
    assert not destination.exists()
