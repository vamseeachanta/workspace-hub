"""Tests for scripts/hygiene/host_baseline.py (#4532).

Fixtures are synthetic trees whose byte totals are hand-counted beside each test.
The conservation test is the comparator the script did not make: a parent's size
must equal the sum of its children plus its own direct files.
"""

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "scripts/hygiene/host_baseline.py"


def load_module():
    spec = importlib.util.spec_from_file_location("host_baseline", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def hb():
    return load_module()


def write(path: Path, nbytes: int):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"x" * nbytes)


def git(*args, cwd):
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@example.invalid",
               GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@example.invalid")
    subprocess.run(["git", *args], cwd=cwd, env=env, check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def by_path(rows):
    return {Path(r["path"]).as_posix(): r for r in rows}


def test_sizes_conserve_parent_equals_children_plus_direct_files(tmp_path, hb):
    # a/one.bin 100 + a/b/two.bin 200 + a/b/c/three.bin 300 + a/top.txt 7
    # depth-1 "a" = 607; depth-2 "a/b" = 500
    root = tmp_path / "root"
    write(root / "a" / "one.bin", 100)
    write(root / "a" / "top.txt", 7)
    write(root / "a" / "b" / "two.bin", 200)
    write(root / "a" / "b" / "c" / "three.bin", 300)
    rows = by_path(hb.scan_root(str(root), depth=2, workers=2)["dirs"])
    a = rows[(root / "a").as_posix()]
    b = rows[(root / "a" / "b").as_posix()]
    assert a["bytes"] == 607 and a["files"] == 4
    assert b["bytes"] == 500 and b["files"] == 2
    assert a["bytes"] == b["bytes"] + a["direct_bytes"]
    assert a["direct_bytes"] == 107


def test_symlinked_directory_is_not_followed(tmp_path, hb):
    root = tmp_path / "root"
    write(root / "real" / "f.bin", 50)
    try:
        os.symlink(root / "real", root / "link", target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("symlink creation not permitted on this host")
    rows = by_path(hb.scan_root(str(root), depth=1, workers=1)["dirs"])
    assert (root / "link").as_posix() not in rows
    assert rows[(root / "real").as_posix()]["bytes"] == 50


def test_stray_classification_signatures(hb):
    cls = hb.classify_stray
    assert cls("tmp", windows_drive_root=True)[0] == "posix-path-leak"
    assert cls("mnt", windows_drive_root=True)[0] == "posix-path-leak"
    assert cls("c", windows_drive_root=True)[0] == "drive-letter-mirror"
    assert cls("invalid", windows_drive_root=True)[0] == "test-fixture-leak"
    assert cls("Windows", windows_drive_root=True) is None
    assert cls("Program Files (x86)", windows_drive_root=True) is None
    assert cls("ws", windows_drive_root=True, expected={"ws"}) is None
    assert cls("CM_Projects", windows_drive_root=True)[0] == "unclassified"
    # On a POSIX home only the unambiguous leak signatures are reported.
    assert cls("tmp", windows_drive_root=False) is None
    assert cls("invalid", windows_drive_root=False)[0] == "test-fixture-leak"


def test_checkout_detection_clone_worktree_dirty_and_unpushed(tmp_path, hb):
    if subprocess.run(["git", "--version"], capture_output=True).returncode:
        pytest.skip("git unavailable")
    origin = tmp_path / "origin.git"
    git("init", "--bare", "-q", str(origin), cwd=tmp_path)
    root = tmp_path / "ws"
    clone = root / "repo"
    root.mkdir()
    git("init", "-q", "-b", "main", str(clone), cwd=root)
    write(clone / "a.txt", 3)
    git("add", "a.txt", cwd=clone)
    git("commit", "-q", "-m", "one", cwd=clone)
    git("remote", "add", "origin", str(origin), cwd=clone)
    git("push", "-q", "origin", "main", cwd=clone)
    git("worktree", "add", "-q", "-b", "side", str(root / "wt-side"), cwd=clone)
    write(root / "wt-side" / "b.txt", 1)
    git("add", "b.txt", cwd=root / "wt-side")
    git("commit", "-q", "-m", "two", cwd=root / "wt-side")
    write(clone / "untracked.txt", 1)

    rows = by_path(hb.find_checkouts([str(root)], max_depth=2))
    c = rows[clone.as_posix()]
    w = rows[(root / "wt-side").as_posix()]
    assert c["kind"] == "clone" and c["dirty"] == 1 and c["head_on_remote"] is True
    assert w["kind"] == "worktree" and w["dirty"] == 0 and w["head_on_remote"] is False


def test_cli_emits_schema_and_label_from_argument_only(tmp_path):
    root = tmp_path / "root"
    write(root / "d" / "f.bin", 10)
    out = subprocess.run(
        [sys.executable, "-I", str(SCRIPT), "--label", "host-under-test",
         "--roots", str(root), "--depth", "1", "--no-git", "--no-caches"],
        capture_output=True, text=True, check=True,
    )
    doc = json.loads(out.stdout)
    assert doc["schema"] == 1
    assert doc["label"] == "host-under-test"
    assert "hostname" not in json.dumps(doc).lower()
    assert any(d["free_bytes"] >= 0 for d in doc["disks"])
    assert by_path(doc["roots"][0]["dirs"])[(root / "d").as_posix()]["bytes"] == 10


def test_stdin_execution_matches_remote_invocation(tmp_path):
    """Remote hosts run `python3 - ARGS < host_baseline.py`; prove that path works."""
    root = tmp_path / "root"
    write(root / "d" / "f.bin", 4)
    out = subprocess.run(
        [sys.executable, "-I", "-", "--label", "x", "--roots", str(root),
         "--depth", "1", "--no-git", "--no-caches"],
        input=SCRIPT.read_text(encoding="utf-8"), capture_output=True,
        text=True, check=True,
    )
    assert json.loads(out.stdout)["label"] == "x"
