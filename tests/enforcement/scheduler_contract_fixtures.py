"""Explicit working-tree snapshots for scheduler contract unit tests.

The production CLI reads the index. Unit tests use the intended source snapshot
so unstaged registry changes are tested with matching source and digest inputs.
Transport tests still exercise the real Git index, including dirty-worktree
isolation and byte-preserving path handling.
"""
from __future__ import annotations

from pathlib import Path

_INDEX_SNAPSHOTS: dict[Path, dict[bytes, bytes]] = {}

def _index_snapshot(root: Path, reader):
    if root not in _INDEX_SNAPSHOTS:
        _INDEX_SNAPSHOTS[root] = reader(root)
    return _INDEX_SNAPSHOTS[root]


def checkout_records(checker, root: Path):
    # Cache only the expensive baseline transport. Return a fresh dictionary;
    # negative tests mutate their copies and cannot contaminate another test.
    records = dict(_index_snapshot(root, checker.read_index_records))
    paths = [
        root / "config/scheduled-tasks/mutation-surfaces.yaml",
        root / "scripts/enforcement/check-scheduler-mutation-surfaces.py",
        root / "docs/ops/scheduled-tasks.md",
        root / "scripts/operations/relocate-to-bulk.sh",
        root / "scripts/monitoring/bundle-sentinel-install/install.sh",
        Path(__file__),
    ]
    paths.extend((root / "scripts/enforcement").glob("scheduler_mutation*.py"))
    paths.extend((root / "tests/enforcement").glob("test_scheduler_mutation*.py"))
    for path in paths:
        records[path.relative_to(root).as_posix().encode()] = path.read_bytes()
    return records
