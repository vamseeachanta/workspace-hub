"""Qualify bounded full reads using synthetic files, without digest constants.

Source: scripts/dedupe/README.md, Staged hashing: equal sizes and samples
advance to full SHA-256; sample windows are 64 KiB and full reads are 1 MiB,
with 1024 bytes per KiB. These are fixture sizes, not production size limits.
Hand calculation: C = 1024 * 1024 = 1048576 bytes. Reading through EOF gives
[1048575, 0] for C-1, [1048576, 0] for C, and [1048576, 1, 0] for C+1.
The zero is the terminal EOF read; nonzero returns sum to each file's length.
"""

from contextlib import contextmanager
from types import SimpleNamespace

import pytest
from dedupe.hash_inventory import inventory

# README.md, Staged hashing: independently transcribed read-size conventions.
FULL_READ_BYTES = 1024 * 1024
SAMPLE_WINDOW_BYTES = 64 * 1024


class RecordingReader:
    """Observe reads while delegating descriptor and seek operations unchanged."""

    def __init__(self, stream, reads):
        self.stream = stream
        self.reads = reads

    def read(self, size):
        data = self.stream.read(size)
        self.reads.append((size, len(data)))
        return data

    def __getattr__(self, name):
        return getattr(self.stream, name)


def snapshot(root):
    """Retain path membership, entry kinds, and every input byte independently."""
    return {
        path.relative_to(root).as_posix(): (
            path.is_symlink(),
            path.is_file(),
            path.read_bytes() if path.is_file() else None,
        )
        for path in root.rglob("*")
    }


# Literal vectors come from the hand calculation in the module docstring.
@pytest.fixture(
    params=[
        (1048575, [1048575, 0]),
        (1048576, [1048576, 0]),
        (1048577, [1048576, 1, 0]),
    ],
    ids=["below-chunk", "exact-chunk", "above-chunk"],
)
def boundary_inventory(tmp_path, request):
    length, expected_returns = request.param
    # Each case has its own disposable root; the pair has equal size and bytes.
    root = tmp_path / "input"
    root.mkdir()
    payload = b"x" * length
    names = {"first.bin", "second.bin"}
    for name in names:
        (root / name).write_bytes(payload)
    before = snapshot(root)
    reads = {name: [] for name in names}

    @contextmanager
    def opener(path, mode):
        calls = []
        reads[path.name].append(calls)
        with open(path, mode) as stream:
            yield RecordingReader(stream, calls)

    rows, meta = inventory({"roots": [str(root)]}, "boundary", opener=opener)
    return SimpleNamespace(
        length=length,
        expected_returns=expected_returns,
        rows=rows,
        meta=meta,
        reads=reads,
        before=before,
        after=snapshot(root),
    )


def test_full_hash_chunk_boundary_reads_match_hand_counts(boundary_inventory):
    case = boundary_inventory
    assert set(case.reads) == {"first.bin", "second.bin"}
    for openings in case.reads.values():
        # README.md, Staged hashing: head and tail sample, then a full stream.
        sample_reads, full_reads = openings
        assert sample_reads == [
            (SAMPLE_WINDOW_BYTES, SAMPLE_WINDOW_BYTES),
            (SAMPLE_WINDOW_BYTES, SAMPLE_WINDOW_BYTES),
        ]
        assert all(size == FULL_READ_BYTES for size, _ in full_reads)
        returned = [count for _, count in full_reads]
        assert returned == case.expected_returns
        assert sum(count for count in returned if count) == case.length


def test_identical_boundary_files_retain_complete_full_evidence(boundary_inventory):
    case = boundary_inventory
    assert case.meta["type"] == "manifest"
    assert case.meta["complete"] is True
    assert case.meta["errors"] == []
    assert [row["path"] for row in case.rows] == ["first.bin", "second.bin"]
    for row in case.rows:
        assert row["stage"] == "full"
        assert row["size"] == case.length
        assert row["sample_sha256"] is not None
        assert row["sha256"] is not None
        assert "error" not in row
    first, second = case.rows
    assert first["sample_sha256"] == second["sample_sha256"]
    assert first["sha256"] == second["sha256"]
    assert set(case.before) == {"first.bin", "second.bin"}
    assert all(not symlink and regular for symlink, regular, _ in case.before.values())
    assert all(len(data) == case.length for _, _, data in case.before.values())
    assert case.before["first.bin"] == case.before["second.bin"]
    assert case.after == case.before
