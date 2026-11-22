"""Disposable regressions for the manifest substitution described in issue #3439.

Independent example: inventory I = {live.svg, spare.svg}; current C = {live.svg};
history H = recovery R = {}. By hand, the referenced partition is {live.svg}
and the unreferenced/prune partition is {spare.svg}. A FIFO contributes no
regular manifest evidence, so every partition must instead be empty.
"""

import errno
import json
import os
import stat
import subprocess
import sys
import textwrap
from pathlib import Path
from types import SimpleNamespace

import pytest

import asset_reachability as reader


# Issue #3439 requires an explicit child safety timeout. Ten seconds is a test
# containment budget, not a performance requirement for the reporting reader.
CHILD_TIMEOUT_SECONDS = 10


@pytest.fixture
def manifest_root(tmp_path):
    root = tmp_path / "root"
    root.mkdir()
    (root / "assets").mkdir()
    for name in ("live.svg", "spare.svg"):
        (root / "assets" / name).write_bytes(b"synthetic asset")
    documents = {
        "inventory.json": {
            "schema": "asset-inventory-v1",
            "assets": ["assets/live.svg", "assets/spare.svg"],
        },
        "current.json": {
            "schema": "asset-references-v1", "assets": ["assets/live.svg"],
        },
        "index.json": {
            "schema": "asset-reference-index-v1", "publication_status": "succeeded",
            "current": ["current.json"], "history": [], "recovery": [],
        },
    }
    for name, value in documents.items():
        (root / name).write_text(json.dumps(value), encoding="utf-8")
    return root


def test_manifest_fifo_substitution_never_blocks(manifest_root):
    if not hasattr(os, "mkfifo") or not hasattr(os, "O_NONBLOCK"):
        pytest.skip("FIFO and nonblocking open support required")
    child = textwrap.dedent('''
        import json
        import os
        import stat
        import sys
        from pathlib import Path

        _, root_arg, script_dir = sys.argv
        sys.path.insert(0, script_dir)
        import asset_reachability as reader

        root = Path(root_arg)
        original_bytes = (root / "current.json").read_bytes()
        original_check = reader._regular_file
        replaced = False

        def substitute_after_check(root, locator):
            global replaced
            candidate = original_check(root, locator)
            if locator == "current.json":
                candidate.rename(root / "retained-current.json")
                os.mkfifo(candidate)
                replaced = True
            return candidate

        reader._regular_file = substitute_after_check
        result = reader.plan_reachability(root, "inventory.json", "index.json")
        assert replaced
        assert stat.S_ISFIFO((root / "current.json").lstat().st_mode)
        assert (root / "retained-current.json").read_bytes() == original_bytes
        print(json.dumps(result))
    ''')
    # No writer is supplied. subprocess.run kills and waits for a timed-out child;
    # the timeout is a regression failure, never evidence of safe rejection.
    try:
        completed = subprocess.run(
            [sys.executable, "-c", child, str(manifest_root),
             str(Path(reader.__file__).resolve().parent)],
            capture_output=True, text=True, timeout=CHILD_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired:
        pytest.fail("manifest FIFO substitution exceeded the child safety timeout")
    assert completed.returncode == os.EX_OK, "FIFO child did not complete successfully"
    assert completed.stderr == ""
    assert json.loads(completed.stdout) == {
        "status": "UNRESOLVED", "dry_run": True,
        "reason": "manifest is not a regular file",
        "referenced": [], "unreferenced": [], "prune_candidates": [],
    }
    assert str(manifest_root) not in completed.stdout + completed.stderr


# Python stat file-type constants supply the injected non-regular descriptor modes.
@pytest.mark.parametrize("mode", [
    stat.S_IFIFO, stat.S_IFDIR, stat.S_IFCHR, stat.S_IFBLK, stat.S_IFSOCK, stat.S_IFLNK,
])
def test_nonregular_descriptor_is_closed_without_read(manifest_root, monkeypatch, mode):
    real_close, real_fstat = os.close, os.fstat
    descriptor = os.open(manifest_root / "current.json", os.O_RDONLY)
    events = []
    opened_flags = []

    def injected_open(candidate, flags):
        assert candidate == manifest_root / "current.json"
        opened_flags.append(flags)
        events.append("open")
        return descriptor

    def injected_fstat(opened):
        assert opened == descriptor
        events.append("fstat")
        return SimpleNamespace(st_mode=mode)

    def close(opened):
        assert opened == descriptor
        events.append("close")
        real_close(opened)

    def unexpected_read(*args, **kwargs):
        pytest.fail("non-regular descriptor reached stream creation or reading")

    # Isolate injected operations from pytest's own capture descriptors.
    monkeypatch.setattr(reader, "os", SimpleNamespace(**vars(os)))
    monkeypatch.setattr(reader.os, "open", injected_open)
    monkeypatch.setattr(reader.os, "fstat", injected_fstat)
    monkeypatch.setattr(reader.os, "close", close)
    monkeypatch.setattr(reader.os, "fdopen", unexpected_read)
    monkeypatch.setattr(reader.os, "read", unexpected_read)
    monkeypatch.setattr(reader, "load_manifest", unexpected_read)
    try:
        with pytest.raises(reader.ReachabilityError, match="^manifest is not a regular file$"):
            reader._read(manifest_root, "current.json")
        assert events == ["open", "fstat", "close"]
        for flags in opened_flags:
            if hasattr(os, "O_NONBLOCK"):
                assert flags & os.O_NONBLOCK
            if hasattr(os, "O_NOFOLLOW"):
                assert flags & os.O_NOFOLLOW
            if hasattr(os, "O_NOATIME"):
                assert flags & os.O_NOATIME
        with pytest.raises(OSError) as closed:
            real_fstat(descriptor)
        assert closed.value.errno == errno.EBADF
    finally:
        # Keep even a failing regression from leaking its disposable descriptor.
        try:
            real_fstat(descriptor)
        except OSError as exc:
            assert exc.errno == errno.EBADF
        else:
            real_close(descriptor)


def test_regular_manifest_partition_unchanged(manifest_root):
    # Literal result from the independent set calculation in the module docstring.
    assert reader.plan_reachability(manifest_root, "inventory.json", "index.json") == {
        "status": "RESOLVED", "dry_run": True,
        "referenced": ["assets/live.svg"],
        "unreferenced": ["assets/spare.svg"], "prune_candidates": ["assets/spare.svg"],
    }
