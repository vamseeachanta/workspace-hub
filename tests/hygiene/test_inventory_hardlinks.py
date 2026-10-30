"""Hard-link totals count directory entries, not allocated or deduplicated bytes."""

import builtins
import importlib.util
import io
import os
import stat
from datetime import datetime
from pathlib import Path

import pytest

# Two parent levels locate the repository from tests/hygiene (fixture layout).
SCRIPT = Path(__file__).resolve().parents[2] / "scripts/hygiene/inventory.py"
# Arbitrary synthetic aware instant; no wall-clock dependency or measured limit.
FIXED = datetime.fromisoformat("2000-01-01T00:00:00+00:00")


@pytest.fixture
def inventory():
    spec = importlib.util.spec_from_file_location("inventory_hardlinks", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def linked_pair(tmp_path, payload, source_name):
    root = tmp_path / "tree"
    root.mkdir()
    source = root / source_name
    source.write_bytes(payload)
    other_name = "beta.txt" if source_name == "alpha.txt" else "alpha.txt"
    (root / other_name).hardlink_to(source)
    return root


def snapshot(root):
    """Retain payloads, device/inode identities and exact directory membership."""
    result = {}
    for path in root.iterdir():
        info = path.stat()
        assert stat.S_ISREG(info.st_mode)
        result[path.name] = (path.read_bytes(), (info.st_dev, info.st_ino))
    return result


def manifest_without_payload_reads(inventory, root, monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("payload opened during scanning or aggregation")

    with monkeypatch.context() as patch:
        for target, name in (
            (Path, "open"),
            (builtins, "open"),
            (io, "open"),
            (os, "open"),
        ):
            patch.setattr(target, name, forbidden)
        return inventory.build_manifest(
            # Hand count: alpha.txt and beta.txt are exactly two entries.
            {"root": str(root), "repos": [], "max_files": 2},
            clock=lambda: FIXED,
        )


def test_regular_hardlinks_count_each_path(tmp_path, inventory, monkeypatch):
    """Hand calculation: two paths, each b'abc' (3 bytes), give 3+3=6 bytes."""
    root = linked_pair(tmp_path, b"abc", "alpha.txt")
    before = snapshot(root)
    alpha_bytes, alpha_identity = before["alpha.txt"]
    beta_bytes, beta_identity = before["beta.txt"]
    assert alpha_bytes == beta_bytes == b"abc"
    assert alpha_identity == beta_identity
    assert set(before) == {"alpha.txt", "beta.txt"}

    result = manifest_without_payload_reads(inventory, root, monkeypatch)

    assert snapshot(root) == before
    assert result["root"] == str(root)
    assert result["generated_utc"] == "2000-01-01T00:00:00Z"
    assert result["repos"] == []
    assert [(row["path"], row["size"], row["category"]) for row in result["files"]] == [
        ("alpha.txt", 3, "document"),
        ("beta.txt", 3, "document"),
    ]
    totals = result["totals"]
    assert (totals["count"], totals["bytes"]) == (2, 6)
    documents = totals["categories"]["document"]
    assert (documents["count"], documents["bytes"]) == (2, 6)


def test_empty_hardlinks_count_paths_without_bytes(tmp_path, inventory, monkeypatch):
    """Hand calculation: two empty paths give 0+0=0 logical bytes."""
    # Create beta first so insertion order differs from the required lexical order.
    root = linked_pair(tmp_path, b"", "beta.txt")
    before = snapshot(root)
    alpha_bytes, alpha_identity = before["alpha.txt"]
    beta_bytes, beta_identity = before["beta.txt"]
    assert alpha_bytes == beta_bytes == b""
    assert alpha_identity == beta_identity
    assert set(before) == {"alpha.txt", "beta.txt"}

    result = manifest_without_payload_reads(inventory, root, monkeypatch)

    assert snapshot(root) == before
    assert result["repos"] == []
    expected = [("alpha.txt", 0), ("beta.txt", 0)]
    assert [(row["path"], row["size"]) for row in result["files"]] == expected
    totals = result["totals"]
    assert (totals["count"], totals["bytes"]) == (2, 0)
    documents = totals["categories"]["document"]
    assert (documents["count"], documents["bytes"]) == (2, 0)
    for group in (totals, documents):
        assert [(row["path"], row["size"]) for row in group["largest_files"]] == expected
