"""Validation for #2112 online-researched GoM field-development data gate."""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
DATASET = REPO_ROOT / "data/field-development/gom-field-development-unblock-2112.json"
REPORT = REPO_ROOT / "docs/reports/field-development-unblock-2112.md"
REQUIRED_NUMERIC = ["num_trees", "num_manifolds", "tieback_distance_km"]
CONTEXT_FIELDS = ["host", "architecture", "cost_usd_bn", "water_depth_m", "source_urls", "confidence"]


def load_dataset() -> dict:
    return json.loads(DATASET.read_text(encoding="utf-8"))


def test_2112_candidate_dataset_has_ten_structural_gom_records() -> None:
    payload = load_dataset()
    assert payload["issue"] == 2112
    assert payload["required_gate"]["status"] == "blocked_adversarial_review_failed"
    assert payload["required_gate"]["records_with_all_required_structural"] == 10
    assert payload["required_gate"]["records_with_all_required_public_sourced_and_semantically_consistent"] == 0
    records = payload["gom_fields"]
    complete = [
        record
        for record in records
        if all(record.get(field) is not None for field in REQUIRED_NUMERIC)
    ]
    assert len(complete) >= 10
    assert {record["region"] for record in complete} == {"US Gulf of Mexico"}


def test_2112_candidates_have_sources_confidence_and_basis_notes() -> None:
    for record in load_dataset()["gom_fields"]:
        for field in REQUIRED_NUMERIC + CONTEXT_FIELDS:
            assert field in record, (record.get("name"), field)
        assert isinstance(record["source_urls"], list) and record["source_urls"], record["name"]
        assert all(str(url).startswith("http") for url in record["source_urls"])
        assert record["confidence"] in {"high", "medium", "low"}
        for field in REQUIRED_NUMERIC:
            assert record.get(f"{field}_basis"), (record["name"], field)


def test_2112_report_preserves_blocked_status_and_next_gate() -> None:
    text = REPORT.read_text(encoding="utf-8")
    assert "#2112" in text
    assert "records_with_all_required_structural: 10" in text
    assert "records_with_all_required_public_sourced_and_semantically_consistent: 0" in text
    assert "status:needs-data should remain" in text
    assert "No invented values are accepted as final" in text
    assert "normalized definition for `tieback_distance_km`" in text
