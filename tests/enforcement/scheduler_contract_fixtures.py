"""Explicit working-tree snapshots for scheduler contract unit tests.

The production CLI reads the index. Transport tests continue to exercise that
interface; unit tests use a matching set of intended source and digest inputs.
This follows the checkout_records interface proposed for scheduler readers.
"""
from __future__ import annotations

from pathlib import Path

_INDEX_SNAPSHOTS: dict[Path, dict[bytes, bytes]] = {}


def checkout_records(checker, root: Path):
    if root not in _INDEX_SNAPSHOTS:
        _INDEX_SNAPSHOTS[root] = checker.read_index_records(root)
    records = dict(_INDEX_SNAPSHOTS[root])
    paths = [
        root / "docs/reports/hash-pinned-attestation-audit.json",
        root / "tests/enforcement/pin_helpers.py",
        root / "tests/enforcement/attestation_inventory.py",
        root / "tests/enforcement/workflow_contracts.py",
        root / "tests/enforcement/fixtures/pinned-preview.sh",
        Path(__file__),
    ]
    paths.extend((root / "scripts/enforcement").glob("scheduler_mutation*.py"))
    paths.extend((root / "tests/enforcement").glob("test_scheduler_mutation*.py"))
    paths.extend(root / "tests/enforcement" / name for name in (
        "test_pin_helpers.py", "test_wrapper_pin_reasons.py",
        "test_workflow_contracts.py", "test_attestation_inventory.py",
    ))
    for path in paths:
        records[path.relative_to(root).as_posix().encode()] = path.read_bytes()
    return records
