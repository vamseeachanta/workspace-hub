"""Corpus snapshot audit tests with independent counting oracles.

Basis: docs/architecture/agent-data-handling-contract.md, existing identities,
processing states and observation boundaries. These are synthetic counts, not
empirical coefficients or engineering acceptance limits.
"""

from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest
from knowledge.corpus_readiness import SnapshotError, audit_snapshot, load_snapshot

SCRIPT = Path(__file__).resolve().parents[2] / "scripts/knowledge/corpus_readiness.py"
EXAMPLE = Path(__file__).parent / "fixtures/corpus-readiness.json"


@pytest.fixture
def snapshot():
    return json.loads(EXAMPLE.read_text(encoding="utf-8"))


def test_worked_example(snapshot):
    """Hand count: markdown has two rows, csv one, pdf zero.

    One markdown row has all evidence; the other lacks fidelity and citation.
    The csv row has all evidence but restricted privacy on a public route.
    Thus three observed, one complete, two incomplete, one route conflict,
    and one declared format with no observations. Complete formats = one
    (markdown); csv is blocked and pdf is unobserved. No ratio is inferred.
    """
    report = audit_snapshot(snapshot)
    assert report["record_count"] == 3
    assert report["evidence_complete_count"] == 1
    assert report["incomplete_count"] == 2
    assert report["route_conflict_count"] == 1
    assert report["unobserved_format_count"] == 1
    assert report["formats_with_complete_evidence"] == 1
    assert report["formats"]["markdown"]["record_count"] == 2
    assert report["formats"]["csv"]["record_count"] == 1
    assert report["formats"]["pdf"]["record_count"] == 0
    assert report["qualification"] == "NOT_EVALUATED"


def test_pure_deterministic_audit(snapshot):
    before = copy.deepcopy(snapshot)
    report = audit_snapshot(snapshot)
    snapshot["sources"].reverse()
    assert audit_snapshot(snapshot) == report
    snapshot["sources"].reverse()
    assert snapshot == before


@pytest.mark.parametrize("field", ["method_ref", "fidelity_ref", "citation_ref", "rights_ref"])
@pytest.mark.parametrize("value", [None, "", "   "])
def test_missing_evidence_is_incomplete(snapshot, field, value):
    snapshot["sources"][0]["evidence"][field] = value
    assert audit_snapshot(snapshot)["evidence_complete_count"] == 0


@pytest.mark.parametrize("privacy", ["restricted", "unknown"])
def test_public_route_rejects_nonpublic_privacy(snapshot, privacy):
    snapshot["sources"][0]["privacy"] = privacy
    assert audit_snapshot(snapshot)["route_conflict_count"] == 2
    assert audit_snapshot(snapshot)["evidence_complete_count"] == 0


@pytest.mark.parametrize("route", ["metadata_only", "excluded_no_ingest"])
def test_non_ingest_routes_never_count_as_complete(snapshot, route):
    snapshot["sources"][0]["route"] = route
    assert audit_snapshot(snapshot)["evidence_complete_count"] == 0


@pytest.mark.parametrize("status", ["gap", "indexed", "summarized", "superseded", "unreachable"])
def test_processing_states_do_not_imply_extraction(snapshot, status):
    snapshot["sources"][0]["processing_status"] = status
    assert audit_snapshot(snapshot)["evidence_complete_count"] == 0


@pytest.mark.parametrize("status", ["extracted", "promoted"])
def test_extracted_states_still_require_all_evidence(snapshot, status):
    snapshot["sources"][0]["processing_status"] = status
    assert audit_snapshot(snapshot)["evidence_complete_count"] == 1


def test_private_route_can_have_documented_evidence(snapshot):
    snapshot["sources"][0].update(route="private_sidecar", privacy="restricted")
    report = audit_snapshot(snapshot)
    assert report["evidence_complete_count"] == 1
    assert report["qualification"] == "NOT_EVALUATED"


def test_empty_inventory_is_explicit(snapshot):
    snapshot["sources"] = []
    report = audit_snapshot(snapshot)
    assert report["record_count"] == 0
    assert report["unobserved_format_count"] == 3
    assert report["formats_with_complete_evidence"] == 0


def test_same_source_different_dataset_is_not_duplicate(snapshot):
    row = copy.deepcopy(snapshot["sources"][0])
    row["dataset_id"] = "another-dataset"
    snapshot["sources"].append(row)
    assert audit_snapshot(snapshot)["record_count"] == 4


def test_duplicate_identity_fails(snapshot):
    snapshot["sources"].append(copy.deepcopy(snapshot["sources"][0]))
    with pytest.raises(SnapshotError, match="duplicate identity"):
        audit_snapshot(snapshot)


@pytest.mark.parametrize("field", ["source_id", "dataset_id", "owner_repo"])
@pytest.mark.parametrize("value", [None, "", " padded ", 7, True])
def test_invalid_identity_fails(snapshot, field, value):
    snapshot["sources"][0][field] = value
    with pytest.raises(SnapshotError):
        audit_snapshot(snapshot)


@pytest.mark.parametrize("field,value", [
    ("format_family", "unlisted"), ("route", "unknown"),
    ("privacy", "private"), ("processing_status", "ready"),
    ("evidence", []), ("route", []), ("processing_status", {}),
])
def test_invalid_row_fails(snapshot, field, value):
    snapshot["sources"][0][field] = value
    with pytest.raises(SnapshotError):
        audit_snapshot(snapshot)


@pytest.mark.parametrize("field", ["sources", "format_families", "schema_version"])
def test_required_root_fields(snapshot, field):
    del snapshot[field]
    with pytest.raises(SnapshotError):
        audit_snapshot(snapshot)


@pytest.mark.parametrize("value", [True, 1.0, "1", 2])
def test_exact_schema_version(snapshot, value):
    snapshot["schema_version"] = value
    with pytest.raises(SnapshotError):
        audit_snapshot(snapshot)


@pytest.mark.parametrize("value", [[], ["markdown", "markdown"], ["unknown"], None])
def test_invalid_format_denominator(snapshot, value):
    snapshot["format_families"] = value
    with pytest.raises(SnapshotError):
        audit_snapshot(snapshot)


def test_unknown_fields_fail_to_catch_misspellings(snapshot):
    snapshot["sources"][0]["evidence"]["citaiton_ref"] = "opaque"
    with pytest.raises(SnapshotError):
        audit_snapshot(snapshot)


@pytest.mark.parametrize("raw", [
    '{"schema_version":1,"schema_version":1}',
    '{"x": NaN}', '{"x": Infinity}', '{"x": -Infinity}', '[]', '{',
])
def test_strict_json(tmp_path, raw):
    path = tmp_path / "snapshot.json"
    path.write_text(raw, encoding="utf-8")
    with pytest.raises(SnapshotError):
        load_snapshot(path)


def test_cli_aggregate_only_and_read_only(tmp_path, snapshot):
    """Sensitive labels are input canaries; output may contain fixed enums only."""
    row = snapshot["sources"][0]
    row["source_id"] = "sensitive-source-canary"
    row["evidence"]["citation_ref"] = str(tmp_path / "not-opened-canary")
    path = tmp_path / "snapshot.json"
    path.write_text(json.dumps(snapshot), encoding="utf-8")
    before = path.read_bytes()
    result = subprocess.run([sys.executable, str(SCRIPT), str(path)],
                            capture_output=True, text=True, check=False)
    assert result.returncode == 0
    assert result.stderr == ""
    assert "canary" not in result.stdout
    assert str(tmp_path) not in result.stdout
    assert path.read_bytes() == before
    assert json.loads(result.stdout) == audit_snapshot(snapshot)
    assert sorted(p.name for p in tmp_path.iterdir()) == ["snapshot.json"]


@pytest.mark.parametrize("kind", ["missing", "invalid", "encoding", "directory"])
def test_cli_errors_are_redacted(tmp_path, kind):
    path = tmp_path / "sensitive-path-canary"
    if kind == "invalid":
        path.write_text('{"sensitive-value-canary":', encoding="utf-8")
    elif kind == "encoding":
        path.write_bytes(b"\xff")
    elif kind == "directory":
        path.mkdir()
    result = subprocess.run([sys.executable, str(SCRIPT), str(path)],
                            capture_output=True, text=True, check=False)
    assert result.returncode == 2
    assert result.stdout == ""
    assert "canary" not in result.stderr
    assert str(tmp_path) not in result.stderr
    assert "Traceback" not in result.stderr


def test_counts_conserve_rows_across_formats(snapshot):
    """Each row enters exactly one format, state, route and completeness bin."""
    report = audit_snapshot(snapshot)
    assert sum(c["record_count"] for c in report["formats"].values()) == 3
    for counts in report["formats"].values():
        assert sum(counts["processing_counts"].values()) == counts["record_count"]
        assert sum(counts["route_counts"].values()) == counts["record_count"]
        assert counts["evidence_complete_count"] + counts["incomplete_count"] == counts["record_count"]
    assert report["formats"]["markdown"]["missing_evidence_counts"] == {
        "method_ref": 0, "fidelity_ref": 1, "citation_ref": 1, "rights_ref": 0,
    }


def test_all_format_labels_are_observations_only(snapshot):
    from knowledge.corpus_readiness import FORMAT_FAMILIES

    snapshot["format_families"] = sorted(FORMAT_FAMILIES)
    snapshot["sources"] = []
    report = audit_snapshot(snapshot)
    assert set(report["formats"]) == FORMAT_FAMILIES
    assert report["unobserved_format_count"] == len(FORMAT_FAMILIES)
    assert report["formats_with_complete_evidence"] == 0


@pytest.mark.parametrize("value", [[], {}, True, 7])
def test_evidence_reference_type_is_strict(snapshot, value):
    snapshot["sources"][0]["evidence"]["method_ref"] = value
    with pytest.raises(SnapshotError):
        audit_snapshot(snapshot)


@pytest.mark.parametrize("field", ["owner_repo", "source_id", "dataset_id", "evidence"])
def test_missing_row_fields_fail(snapshot, field):
    del snapshot["sources"][0][field]
    with pytest.raises(SnapshotError):
        audit_snapshot(snapshot)


def test_nested_duplicate_json_key_is_rejected(tmp_path, snapshot):
    path = tmp_path / "snapshot.json"
    raw = json.dumps(snapshot).replace('"method_ref":', '"method_ref": null, "method_ref":', 1)
    path.write_text(raw, encoding="utf-8")
    with pytest.raises(SnapshotError, match="duplicate key"):
        load_snapshot(path)
