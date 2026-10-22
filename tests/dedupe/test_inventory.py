"""Byte fixtures are independent: equal bytes must match; changed bytes must differ.

The boundary fixture has 65,536 'a' bytes, a one-byte middle, then 65,536
'z' bytes: head and tail are equal while only the middle differs.
These are constructed examples, not reference hash values.
"""

import json
import os
from pathlib import Path

import pytest
from dedupe.hash_inventory import inventory, run


def tree(tmp_path, contents):
    root = tmp_path / "input"
    root.mkdir()
    for name, data in contents.items():
        (root / name).write_bytes(data)
    return root


def test_unique_sizes_never_opened(tmp_path):
    root = tree(tmp_path, {"a": b"x", "b": b"yy"})

    def forbidden(*args, **kwargs):
        pytest.fail("size singletons must not be opened")

    rows, meta = inventory({"roots": [str(root)]}, "A", opener=forbidden)
    assert meta["complete"]
    assert [(r["size"], r["stage"], r["sha256"]) for r in rows] == [
        (1, "size", None),
        (2, "size", None),
    ]


def test_same_size_different_head(tmp_path):
    root = tree(tmp_path, {"a": b"abc", "b": b"xyz"})
    reads = []

    def opener(path, mode):
        reads.append(path)
        return open(path, mode)

    rows, _ = inventory({"roots": [str(root)]}, "A", opener=opener)
    assert [r["stage"] for r in rows] == ["sample", "sample"]
    assert all(r["sha256"] is None for r in rows)
    assert len(reads) == 2


def test_equal_samples_different_middle(tmp_path):
    boundary = 65536  # Issue #4224 sampling window, a performance choice.
    root = tree(
        tmp_path,
        {
            "a": b"a" * boundary + b"x" + b"z" * boundary,
            "b": b"a" * boundary + b"y" + b"z" * boundary,
        },
    )
    rows, _ = inventory({"roots": [str(root)]}, "A")
    assert len({r["sample_sha256"] for r in rows}) == 1
    assert len({r["sha256"] for r in rows}) == 2
    assert {r["stage"] for r in rows} == {"full"}


@pytest.mark.parametrize("payload", [b"", b"abc"])
def test_identical_files_and_zero_bytes(tmp_path, payload):
    root = tree(tmp_path, {"a": payload, "b": payload})
    rows, _ = inventory({"roots": [str(root)]}, "A")
    assert rows[0]["sha256"] == rows[1]["sha256"]
    assert rows[0]["sha256"] is not None
    assert all(r["size"] == len(payload) for r in rows)


def test_unreadable_recorded_without_crash(tmp_path):
    root = tree(tmp_path, {"a": b"abc", "b": b"abc"})

    def denied(path, mode):
        raise PermissionError("synthetic denial")

    rows, meta = inventory({"roots": [str(root)]}, "A", opener=denied)
    assert not meta["complete"]
    assert all(r["error"] == "PermissionError" for r in rows)
    assert all(r["sha256"] is None for r in rows)


def test_exclusions_symlinks_and_multiple_roots(tmp_path):
    root = tree(tmp_path, {"a": b"x", "skip.tmp": b"xx"})
    (root / "link").symlink_to(root / "a")
    other = tmp_path / "other"
    other.mkdir()
    (other / "a").write_bytes(b"x")
    rows, _ = inventory(
        {
            "roots": [str(root), str(other)],
            "exclude": ["*.tmp"],
            "follow_symlinks": False,
        },
        "A",
    )
    assert [(r["root"], r["path"]) for r in rows] == [(0, "a"), (1, "a")]
    assert len({r["sha256"] for r in rows}) == 1


def test_threshold_is_inclusive(tmp_path):
    root = tree(tmp_path, {"a": b"x", "b": b"yy"})
    rows, _ = inventory({"roots": [str(root)], "min_size_bytes": 2}, "A")
    assert [r["path"] for r in rows] == ["b"]


@pytest.mark.parametrize(
    "config",
    [
        {"roots": []},
        {"roots": ["missing"], "follow_symlinks": True},
        {"roots": ["missing"], "min_size_bytes": -1},
    ],
)
def test_invalid_configuration(config):
    with pytest.raises(ValueError):
        inventory(config, "A")


def test_outputs_inside_scan_rejected_before_write(tmp_path):
    root = tree(tmp_path, {"a": b"abc"})
    out = root / "a"
    with pytest.raises(ValueError):
        run({"roots": [str(root)]}, "A", out)
    assert out.read_bytes() == b"abc"


def test_overlapping_roots_rejected(tmp_path):
    root = tree(tmp_path, {"a": b"x"})
    with pytest.raises(ValueError):
        inventory({"roots": [str(root), str(root)]}, "A")


def test_file_change_during_hash_invalidates_evidence(tmp_path):
    root = tree(tmp_path, {"a": b"abc", "b": b"abc"})

    def changing(path, mode):
        stat = path.stat()
        os.utime(path, ns=(stat.st_atime_ns, stat.st_mtime_ns + 1))
        return open(path, mode)

    rows, meta = inventory({"roots": [str(root)]}, "A", opener=changing)
    assert not meta["complete"]
    assert all(r["sha256"] is None and "error" in r for r in rows)


def test_jsonl_has_metadata_and_relative_paths(tmp_path):
    root = tree(tmp_path, {"a": b"abc"})
    out = tmp_path / "manifest.jsonl"
    run({"roots": [str(root)]}, "A", out)
    lines = [json.loads(line) for line in out.read_text().splitlines()]
    assert lines[0]["type"] == "manifest"
    assert lines[0]["complete"]
    assert lines[1]["path"] == "a"
    assert "roots" not in lines[0]
    assert not Path(lines[1]["path"]).is_absolute()


def test_later_hash_changes_earlier_file_invalidates_it(tmp_path):
    """Reading b changes a's mtime by one ns; final validation must reject a."""
    root = tree(tmp_path, {"a": b"abc", "b": b"abc"})
    calls = []

    def changing_other(path, mode):
        calls.append(path.name)
        if path.name == "b" and calls.count("b") == 2:
            a = root / "a"
            info = a.stat()
            os.utime(a, ns=(info.st_atime_ns, info.st_mtime_ns + 1))
        return open(path, mode)

    rows, meta = inventory({"roots": [str(root)]}, "A", opener=changing_other)
    assert not meta["complete"]
    assert "error" in rows[0] and rows[0]["sha256"] is None


def test_stat_failure_is_a_file_error_record(tmp_path, monkeypatch):
    from contextlib import contextmanager

    from dedupe import hash_inventory

    root = tree(tmp_path, {"a": b"x"})

    class Entry:
        name = "a"
        path = str(root / "a")

        def is_symlink(self):
            return False

        def stat(self, **kwargs):
            raise PermissionError("synthetic metadata denial")

    @contextmanager
    def denied(directory):
        yield [Entry()]

    monkeypatch.setattr(hash_inventory.os, "scandir", denied)
    rows, meta = inventory({"roots": [str(root)]}, "A")
    assert not meta["complete"]
    assert rows[0]["path"] == "a" and rows[0]["error"] == "PermissionError"


def test_published_sha256_abc_example(tmp_path):
    """NIST SHA256.pdf, One Block Message Sample, final Message Digest (2015).

    Expected words are transcribed from the opened NIST example, not this tool.
    Source: csrc.nist.gov Cryptographic Standards examples/SHA256.pdf.
    """
    root = tree(tmp_path, {"a": b"abc", "b": b"abc"})
    rows, _ = inventory({"roots": [str(root)]}, "A")
    expected = "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
    assert {r["sha256"] for r in rows} == {expected}


def test_platform_without_optional_open_flags(tmp_path, monkeypatch):
    """Optional POSIX flags cannot make the stdlib CLI platform-dependent."""
    root = tree(tmp_path, {"a": b"abc", "b": b"abc"})
    monkeypatch.delattr(os, "O_NOFOLLOW", raising=False)
    monkeypatch.delattr(os, "O_NONBLOCK", raising=False)
    rows, meta = inventory({"roots": [str(root)]}, "A")
    assert meta["complete"] and rows[0]["sha256"] == rows[1]["sha256"]


def test_changed_file_record_can_be_consumed_by_merge(tmp_path):
    """A late full-hash invalidation must remain a valid error record."""
    from dedupe.merge_manifests import merge

    root = tree(tmp_path, {"a": b"abc", "b": b"abc"})
    opened = []

    def changing(path, mode):
        opened.append(path.name)
        if opened == ["a", "b", "a", "b"]:
            previous = root / "a"
            info = previous.stat()
            os.utime(previous, ns=(info.st_atime_ns, info.st_mtime_ns + 1))
        return open(path, mode)

    out = tmp_path / "manifest.jsonl"
    run({"roots": [str(root)]}, "A", out, opener=changing)
    result = merge([out])
    assert result["incomplete_labels"] == ["A"]
    assert [r["path"] for r in result["errors"]] == ["a"]
