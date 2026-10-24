"""The reviewed audit must enumerate new attestation tests, including callers."""
from __future__ import annotations

import json
from pathlib import Path

from attestation_inventory import discover_attestation_tests

ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "docs/reports/hash-pinned-attestation-audit.json"


def test_audit_covers_every_discovered_attestation_test():
    expected = discover_attestation_tests(ROOT / "tests/enforcement")
    rows = json.loads(AUDIT.read_text())["tests"]
    actual = {f'{row["module"]}::{row["test"]}' for row in rows}
    assert len(actual) == len(rows), "duplicate audit row"
    assert actual == expected, f"missing={expected - actual}; obsolete={actual - expected}"
    for row in rows:
        assert set(row) == {"module", "test", "before", "verdict"}
        assert row["verdict"] in {
            "refreshed-semantic", "provenance", "positive-control",
            "unpinned-structural", "helper-self-check", "baseline-gate",
        }


def test_discovery_finds_new_pinned_test_through_local_helper(tmp_path):
    """A new test needs an audit row even when only a helper names the API."""
    (tmp_path / "test_extra.py").write_text(
        "def local_helper(checker):\n"
        "    return checker.evaluate_attestation('setup-default-apply-v1', {}, b'fixture')\n"
        "def test_new_pin_case(checker):\n"
        "    assert not local_helper(checker)\n"
    )
    assert discover_attestation_tests(tmp_path) == {"tests/enforcement/test_extra.py::test_new_pin_case"}
