"""Consumer audit cases for the field results projection.

Expected values use an independent synthetic enumeration: fields a and b;
wells x and y both belong to a; b has no wells; the atlas has three rows in
two countries. Therefore detail fields=2, wells=2, zero-well fields=1,
atlas fields=3, countries=2. No physical constants or production data are used.
The projection shape follows the upstream exporter documented in the guide.
"""

from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest
from hf.audit_field_explorer import AuditError, audit_bundle

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts/hf/audit_field_explorer.py"


def dump(value):
    return (json.dumps(value, sort_keys=True, allow_nan=False) + "\n").encode()


@pytest.fixture
def case(tmp_path):
    fields = {
        "field_a": {"id": "field_a", "provenance": "synthetic", "wellsCount": 2},
        "field_b": {"id": "field_b", "provenance": None, "wellsCount": 0},
    }
    wells = {
        "fields": {"field_a": {"display_name": "Synthetic A"}},
        "wells": [{"api": "well_x", "field_id": "field_a"},
                  {"api": "well_y", "field_id": "field_a"}],
    }
    atlas = {
        "countries": [{"country": "AA"}, {"country": "BB"}],
        "fields": [
            {"catalog_id": "a", "country": "AA", "density_tier": "rich"},
            {"catalog_id": "b", "country": "AA", "density_tier": "sample"},
            {"catalog_id": "c", "country": "BB", "density_tier": "roadmap"},
        ],
    }
    explorer = {"fields": fields, "wells": wells}
    sources = []
    for role, path, payload in (
        ("field_detail", "detail.json", explorer),
        ("global_funnel", "atlas.json", atlas),
    ):
        raw = dump(payload)
        (tmp_path / path).write_bytes(raw)
        sources.append({"role": role, "path": path,
                        "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)})
    bundle = {
        "schema_version": "1.0.0", "projection": "field_explorer_results",
        "hf_dataset": "worldenergydata", "sources": sources,
        "record_counts": {"fields": 2, "wells": 2, "countries": 2, "atlas_fields": 3},
        "field_provenance": {key: value["provenance"] for key, value in fields.items()},
        "fields": fields, "wells": wells, "atlas": atlas,
    }
    return tmp_path, bundle


def audit(case):
    root, bundle = case
    raw = dump(bundle)
    path = root / "bundle.json"
    path.write_bytes(raw)
    return audit_bundle(path, root, hashlib.sha256(raw).hexdigest())


def resync_source(case, role):
    """Rewrite synthetic source independently of the validator for relational probes."""
    root, bundle = case
    source = next(item for item in bundle["sources"] if item["role"] == role)
    value = ({"fields": bundle["fields"], "wells": bundle["wells"]}
             if role == "field_detail" else bundle["atlas"])
    raw = dump(value)
    (root / source["path"]).write_bytes(raw)
    source.update(sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw))


def test_hand_enumerated_coverage_and_determinism(case):
    report = audit(case)
    assert report == audit(case)
    assert report["integrity_status"] == "PASS"
    assert report["counts"] == {"fields": 2, "wells": 2, "countries": 2, "atlas_fields": 3}
    assert report["wells_per_field"] == {"field_a": 2, "field_b": 0}
    assert report["zero_well_fields"] == ["field_b"]
    assert report["atlas_density"] == {"rich": 1, "sample": 1, "roadmap": 1}
    assert report["eligibility_status"] == "NOT_EVALUATED"
    assert set(report["not_evaluated"]) == {
        "canonical_registry_membership", "source_freshness", "redistribution_rights",
        "engineering_readiness", "economics_basis", "global_completeness",
    }


def test_external_digest_is_required_and_checked(case):
    audit(case)
    root, _ = case
    for digest in ("", "main", "f" * 64):
        with pytest.raises(AuditError, match="bundle_digest"):
            audit_bundle(root / "bundle.json", root, digest)


def test_tampered_source_is_rejected(case):
    root, _ = case
    (root / "detail.json").write_text("{}")
    with pytest.raises(AuditError, match="source_integrity"):
        audit(case)


@pytest.mark.parametrize("path", ["../escape.json", "/absolute.json", "a/../detail.json",
                                  "https://invalid.example/data", "a\\b.json", "./detail.json"])
def test_unsafe_source_paths_are_rejected(case, path):
    case[1]["sources"][0]["path"] = path
    with pytest.raises(AuditError, match="source_path"):
        audit(case)


def test_source_symlink_is_rejected(case):
    root, bundle = case
    (root / "link.json").symlink_to(root / "detail.json")
    bundle["sources"][0]["path"] = "link.json"
    with pytest.raises(AuditError, match="source_path"):
        audit(case)


@pytest.mark.parametrize("key,value", [("schema_version", "2.0.0"),
                                        ("projection", "other"), ("hf_dataset", "other")])
def test_unknown_contract_is_rejected(case, key, value):
    case[1][key] = value
    with pytest.raises(AuditError, match="bundle_contract"):
        audit(case)


@pytest.mark.parametrize("mutation,rule", [
    (lambda b: b["sources"].pop(), "source_roles"),
    (lambda b: b["sources"].append(copy.deepcopy(b["sources"][0])), "source_roles"),
    (lambda b: b["sources"][0].update(bytes=True), "source_integrity"),
    (lambda b: b["record_counts"].update(wells=3), "record_counts"),
    (lambda b: b["record_counts"].update(countries=True), "record_counts"),
    (lambda b: b["fields"]["field_a"].update(name="changed"), "source_projection"),
    (lambda b: b["field_provenance"].update(field_a="changed"), "field_provenance"),
])
def test_integrity_and_projection_fail_closed(case, mutation, rule):
    mutation(case[1])
    with pytest.raises(AuditError, match=rule):
        audit(case)


@pytest.mark.parametrize("mutation,rule", [
    (lambda b: b["fields"]["field_a"].update(id="field_b"), "field_identity"),
    (lambda b: b["wells"]["wells"][1].update(api="well_x"), "well_identity"),
    (lambda b: b["wells"]["wells"][0].update(field_id="absent"), "well_parent"),
    (lambda b: b["wells"]["wells"][0].update(api=""), "well_identity"),
    (lambda b: b["wells"]["fields"].update(absent={}), "well_rollup"),
    (lambda b: b["fields"]["field_a"].update(wellsCount=3), "well_count"),
])
def test_field_and_well_relations(case, mutation, rule):
    mutation(case[1])
    resync_source(case, "field_detail")
    with pytest.raises(AuditError, match=rule):
        audit(case)


@pytest.mark.parametrize("mutation,rule", [
    (lambda b: b["atlas"]["fields"][1].update(catalog_id="a"), "atlas_identity"),
    (lambda b: b["atlas"]["fields"][0].update(country="absent"), "atlas_country"),
    (lambda b: b["atlas"]["fields"][0].update(density_tier="complete"), "atlas_density"),
    (lambda b: b["atlas"]["countries"].append({"country": "AA"}), "country_identity"),
])
def test_atlas_relations(case, mutation, rule):
    mutation(case[1])
    case[1]["record_counts"]["countries"] = len(case[1]["atlas"]["countries"])
    resync_source(case, "global_funnel")
    with pytest.raises(AuditError, match=rule):
        audit(case)


@pytest.mark.parametrize("raw", [b'{"x":1,"x":2}', b'{"x":NaN}', b'{"x":Infinity}',
                                 b'{"x":1e999}', b'[]', b'null', b'not-json'])
def test_strict_json_rejects_ambiguous_bundle(case, raw):
    root, _ = case
    path = root / "bundle.json"
    path.write_bytes(raw)
    with pytest.raises(AuditError):
        audit_bundle(path, root, hashlib.sha256(raw).hexdigest())


def test_cli_emits_report_and_sanitizes_failures(case):
    expected = audit(case)
    root, _ = case
    path = root / "bundle.json"
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    command = [sys.executable, str(SCRIPT), "--bundle", str(path),
               "--source-root", str(root), "--expected-sha256", digest]
    success = subprocess.run(command, capture_output=True, text=True, check=False)
    assert success.returncode == 0
    assert json.loads(success.stdout) == expected
    path.write_text("sensitive input must never appear in diagnostics")
    failure = subprocess.run(command, capture_output=True, text=True, check=False)
    assert failure.returncode == 1
    assert json.loads(failure.stdout) == {"integrity_status": "FAIL", "rule": "bundle_digest"}
    assert failure.stderr == ""
    assert str(root) not in failure.stdout


def test_missing_input_is_a_controlled_error(tmp_path):
    with pytest.raises(AuditError, match="input_read"):
        audit_bundle(tmp_path / "absent.json", tmp_path, "0" * 64)


def test_projection_distinguishes_boolean_from_numeric(case):
    case[1]["fields"]["field_a"]["metric"] = 1
    resync_source(case, "field_detail")
    case[1]["fields"]["field_a"]["metric"] = True
    with pytest.raises(AuditError, match="source_projection"):
        audit(case)


@pytest.mark.parametrize("raw", [b'{"fields":{},"fields":{}}', b'{"x":NaN}'])
def test_source_json_is_strict_even_with_matching_hash(case, raw):
    root, bundle = case
    (root / "detail.json").write_bytes(raw)
    bundle["sources"][0].update(sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw))
    with pytest.raises(AuditError, match="strict_json"):
        audit(case)


def test_directory_input_is_rejected_without_reading(case):
    case[1]["sources"][0]["path"] = "directory"
    (case[0] / "directory").mkdir()
    with pytest.raises(AuditError, match="input_read"):
        audit(case)


def test_worked_example_matches_hand_enumeration(tmp_path):
    output = tmp_path / "example"
    command = [sys.executable, str(REPO / "examples/field_explorer_audit.py"),
               "--out", str(output)]
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    assert result.returncode == 0
    report = json.loads(result.stdout)
    assert report["counts"] == {"fields": 2, "wells": 2, "countries": 2, "atlas_fields": 3}
    assert report["wells_per_field"] == {"field_a": 2, "field_b": 0}
    assert report["zero_well_fields"] == ["field_b"]
    assert report["atlas_density"] == {"rich": 1, "sample": 1, "roadmap": 1}
    assert report["eligibility_status"] == "NOT_EVALUATED"
    before = {path.name: path.read_bytes() for path in output.iterdir()}
    repeat = subprocess.run(command, capture_output=True, text=True, check=False)
    assert repeat.returncode != 0
    assert before == {path.name: path.read_bytes() for path in output.iterdir()}
