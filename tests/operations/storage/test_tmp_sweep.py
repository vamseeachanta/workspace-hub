"""Exercise the temporary-folder sweep only in isolated temporary trees."""
import mmap
import os
from pathlib import Path
import socket
import subprocess
import time

import pytest

SCRIPT = Path(__file__).resolve().parents[3] / "scripts/operations/storage/tmp_sweep.sh"
OLD = time.time() - 5 * 86400


def old_tree(path):
    path.mkdir()
    (path / "payload").write_text("saved payload")
    for item in (path / "payload", path):
        os.utime(item, (OLD, OLD))
    return path


def run(root, *args):
    return subprocess.run(["bash", str(SCRIPT), "--root", str(root), *args],
                          text=True, capture_output=True, timeout=30)


def snapshot(root):
    return sorted((str(p.relative_to(root)), p.lstat().st_mode,
                   p.read_bytes() if p.is_file() and not p.is_symlink() else None)
                  for p in root.rglob("*"))


def test_report_does_not_change_tree(tmp_path):
    root = tmp_path / "tree"
    root.mkdir()
    old_tree(root / "idle")
    before = snapshot(root)
    result = run(root)
    assert result.returncode == 0, result.stderr
    assert "SWEEPABLE\t" in result.stdout
    assert "sweepable=1" in result.stdout
    assert snapshot(root) == before


def test_verified_local_move(tmp_path):
    root, archive = tmp_path / "tree", tmp_path / "archive"
    root.mkdir()
    folder = old_tree(root / "idle")
    before = snapshot(folder)
    result = run(root, "--move", str(archive))
    assert result.returncode == 0, result.stderr
    assert not folder.exists()
    assert snapshot(archive / "idle") == before
    manifest = (archive / "MANIFEST.tsv").read_text()
    assert "moved" in manifest and "idle" in manifest


@pytest.mark.parametrize("kind", ["new", "new-child", "hidden", "socket", "dirty-git", "git-without-remote", "readonly", "readonly-subtree", "symlink"])
def test_protected_folder_is_kept(tmp_path, kind):
    root, archive = tmp_path / "tree", tmp_path / "archive"
    root.mkdir()
    folder = old_tree(root / (".hidden" if kind == "hidden" else "kept"))
    listener = None
    if kind == "new":
        os.utime(folder, None)
    elif kind == "new-child":
        os.utime(folder / "payload", None)
    elif kind == "socket":
        listener = socket.socket(socket.AF_UNIX)
        listener.bind(str(folder / "socket"))
    elif kind in ("dirty-git", "git-without-remote"):
        subprocess.run(["git", "init", "-q", str(folder)], check=True)
        if kind == "dirty-git":
            (folder / "changed").write_text("uncommitted")
        else:
            (folder / ".git/info/exclude").write_text("payload\n")
        for p in folder.rglob("*"):
            if not p.is_symlink():
                os.utime(p, (OLD, OLD))
        os.utime(folder, (OLD, OLD))
    elif kind == "readonly":
        (folder / "payload").chmod(0o444)
    elif kind == "readonly-subtree":
        subtree = folder / "readonly"
        subtree.mkdir()
        (subtree / "payload").write_text("retained")
        os.utime(subtree / "payload", (OLD, OLD))
        os.utime(subtree, (OLD, OLD))
        os.utime(folder, (OLD, OLD))
        subtree.chmod(0o555)
    elif kind == "symlink":
        (folder / "link").symlink_to(tmp_path / "outside")
    if kind in ("socket", "symlink"):
        os.utime(folder, (OLD, OLD))
    before = snapshot(root)
    try:
        result = run(root, "--move", str(archive))
        assert result.returncode == 0, result.stderr
        assert "KEPT\t" in result.stdout
        if kind == "git-without-remote":
            assert "git-without-remote" in result.stdout
        assert folder.exists()
        assert snapshot(root) == before
        assert not (archive / folder.name).exists()
    finally:
        if listener:
            listener.close()


def test_process_working_directory_is_kept(tmp_path):
    root = tmp_path / "tree"
    root.mkdir()
    folder = old_tree(root / "busy")
    process = subprocess.Popen(["sleep", "3"], cwd=folder)
    try:
        result = run(root)
        assert result.returncode == 0, result.stderr
        assert "KEPT\t" in result.stdout and "in-use" in result.stdout
    finally:
        process.wait(timeout=10)


def test_open_file_is_kept(tmp_path):
    root = tmp_path / "tree"
    root.mkdir()
    folder = old_tree(root / "busy")
    with (folder / "payload").open():
        result = run(root)
    assert "in-use" in result.stdout
    assert "sweepable=0" in result.stdout


def test_archive_inside_root_is_rejected(tmp_path):
    result = run(tmp_path, "--move", str(tmp_path / "archive"))
    assert result.returncode == 2


@pytest.mark.parametrize("empty", [False, True])
def test_failed_copy_compare_preserves_source(tmp_path, empty):
    root, archive, bin_dir = (tmp_path / n for n in ("tree", "archive", "bin"))
    root.mkdir()
    bin_dir.mkdir()
    if empty:
        folder = root / "idle"
        (folder / "nested").mkdir(parents=True)
        os.utime(folder / "nested", (OLD, OLD))
        os.utime(folder, (OLD, OLD))
    else:
        folder = old_tree(root / "idle")
    fake = bin_dir / "cp"
    fake.write_text('#!/usr/bin/env bash\nmkdir -p -- "${@: -1}"\n')
    fake.chmod(0o755)
    env = dict(os.environ, PATH=str(bin_dir) + os.pathsep + os.environ["PATH"])
    before = snapshot(root)
    result = subprocess.run(["bash", str(SCRIPT), "--root", str(root), "--move", str(archive)],
                            env=env, text=True, capture_output=True, timeout=30)
    assert folder.exists() and snapshot(root) == before
    assert "verification-failed" in result.stdout
    assert "verification-failed" in (archive / "MANIFEST.tsv").read_text()


def test_removal_only_in_verified_branch():
    text = SCRIPT.read_text()
    assert "--delete" not in text
    removal_lines = [line.strip() for line in text.splitlines() if line.strip().startswith("rm ")]
    assert removal_lines == ['rm -r -- "$folder"']
    assert text.index("# BEGIN VERIFIED MOVE") < text.index('rm -r -- "$folder"') < text.index("# END VERIFIED MOVE")


def test_mapped_file_is_kept(tmp_path):
    root = tmp_path / "tree"
    root.mkdir()
    folder = old_tree(root / "busy")
    with (folder / "payload").open() as payload:
        with mmap.mmap(payload.fileno(), 0, access=mmap.ACCESS_READ):
            result = run(root)
    assert "in-use" in result.stdout
    assert "sweepable=0" in result.stdout


def test_nested_git_worktree_is_kept(tmp_path):
    root = tmp_path / "tree"
    root.mkdir()
    folder = old_tree(root / "nested")
    repo = folder / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    for item in folder.rglob("*"):
        os.utime(item, (OLD, OLD))
    os.utime(folder, (OLD, OLD))
    before = snapshot(root)
    result = run(root, "--move", str(tmp_path / "archive"))
    assert "git-without-remote" in result.stdout
    assert snapshot(root) == before


@pytest.mark.parametrize("move", [False, True])
def test_git_environment_cannot_redirect_safety_checks(tmp_path, move):
    root = tmp_path / "tree"
    root.mkdir()
    folder = old_tree(root / "dirty")
    subprocess.run(["git", "init", "-q", str(folder)], check=True)
    external = tmp_path / "external"
    subprocess.run(["git", "init", "-q", str(external)], check=True)
    (external / "untouched").write_text("external data")
    (external / ".git/info/exclude").write_text("untouched\n")
    with (external / ".git/config").open("a") as config:
        config.write('[remote "archive"]\n    url = example.invalid:archive\n')
    for item in folder.rglob("*"):
        os.utime(item, (OLD, OLD))
    os.utime(folder, (OLD, OLD))
    before, outside = snapshot(root), snapshot(external)
    args = ["bash", str(SCRIPT), "--root", str(root)]
    if move:
        args += ["--move", str(tmp_path / "archive")]
    env = dict(os.environ, GIT_DIR=str(external / ".git"),
               GIT_WORK_TREE=str(external), GIT_COMMON_DIR=str(external / ".git"))
    result = subprocess.run(args, env=env, text=True, capture_output=True, timeout=30)
    assert "uncommitted-git" in result.stdout
    assert snapshot(root) == before and snapshot(external) == outside


def test_unshared_commit_is_kept(tmp_path):
    root = tmp_path / "tree"
    root.mkdir()
    folder = root / "unshared"
    subprocess.run(["git", "init", "-q", str(folder)], check=True)
    tree = subprocess.run(["git", "-C", str(folder), "hash-object", "-t", "tree", "-w", "--stdin"],
                          input="", text=True, capture_output=True, check=True).stdout.strip()
    body = (f"tree {tree}\nauthor Synthetic <synthetic> 1 +0000\n"
            "committer Synthetic <synthetic> 1 +0000\n\nfixture\n")
    commit = subprocess.run(["git", "-C", str(folder), "hash-object", "-t", "commit", "-w", "--stdin"],
                            input=body, text=True, capture_output=True, check=True).stdout.strip()
    subprocess.run(["git", "-C", str(folder), "update-ref", "HEAD", commit], check=True)
    # Object immutability is independent of the unshared-history guard.
    for item in (folder / ".git/objects").rglob("*"):
        item.chmod(item.stat().st_mode | 0o200)
    with (folder / ".git/config").open("a") as config:
        config.write('[remote "archive"]\n    url = example.invalid:archive\n')
    for item in folder.rglob("*"):
        os.utime(item, (OLD, OLD))
    os.utime(folder, (OLD, OLD))
    before = snapshot(root)
    result = run(root, "--move", str(tmp_path / "archive"))
    assert "unshared-git" in result.stdout
    assert snapshot(root) == before


def test_process_view_failure_preserves_source(tmp_path):
    root, archive, tools = (tmp_path / name for name in ("tree", "archive", "bin"))
    root.mkdir()
    tools.mkdir()
    old_tree(root / "idle")
    readlink = tools / "readlink"
    readlink.write_text("#!/bin/sh\nexit 1\n")
    readlink.chmod(0o755)
    before = snapshot(root)
    env = dict(os.environ, PATH=str(tools) + os.pathsep + os.environ["PATH"])
    result = subprocess.run(["bash", str(SCRIPT), "--root", str(root), "--move", str(archive)],
                            env=env, text=True, capture_output=True, timeout=30)
    assert result.returncode == 0
    assert "process-view-unreadable" in result.stdout
    assert snapshot(root) == before
    assert not (archive / "idle").exists()


@pytest.mark.parametrize('name', ['busy', 'busy space'])
def test_mapping_without_open_descriptor_is_kept(tmp_path, name):
    import ctypes
    root = tmp_path / 'tree'
    root.mkdir()
    folder = old_tree(root / name)
    payload = folder / 'payload'
    library = ctypes.CDLL(None, use_errno=True)
    library.mmap.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.c_int,
                            ctypes.c_int, ctypes.c_int, ctypes.c_long]
    library.mmap.restype = ctypes.c_void_p
    library.munmap.argtypes = [ctypes.c_void_p, ctypes.c_size_t]
    descriptor = os.open(payload, os.O_RDONLY)
    size = payload.stat().st_size
    address = library.mmap(None, size, 1, 2, descriptor, 0)
    os.close(descriptor)
    assert address != ctypes.c_void_p(-1).value
    before = snapshot(root)
    try:
        result = run(root, '--move', str(tmp_path / 'archive'))
        assert 'in-use' in result.stdout
        assert snapshot(root) == before
    finally:
        assert library.munmap(address, size) == 0


def test_bare_repository_is_kept(tmp_path):
    root = tmp_path / 'tree'
    root.mkdir()
    folder = root / 'bare'
    subprocess.run(['git', 'init', '--bare', '-q', str(folder)], check=True)
    for item in folder.rglob('*'):
        os.utime(item, (OLD, OLD))
    os.utime(folder, (OLD, OLD))
    before = snapshot(root)
    result = run(root, '--move', str(tmp_path / 'archive'))
    assert 'bare-git' in result.stdout
    assert snapshot(root) == before
