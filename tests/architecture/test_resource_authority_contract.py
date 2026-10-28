"""Resource authority shape/policy checks; no live entitlement or digest attestation."""
from copy import deepcopy
import json
from pathlib import Path
import re

from jsonschema import Draft202012Validator, FormatChecker
import pytest

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "config/schemas/resource-descriptor-v1.schema.json"
CONTRACT = ROOT / "docs/architecture/agent-data-handling-contract.md"
FIELDS = {
    "source_id", "dataset_id", "doc_key", "owner_repo", "source_version",
    "content_digest", "digest_scope", "derived_from", "units", "intended_use",
    "criteria_revision", "rights_revision",
}
STAMP = "2026-09-12T12:00:00Z"
UNKNOWN = {"state": "unknown", "reason": "not inspected"}
NA = {"state": "not_applicable", "reason": "not a document"}
LICENSED_CLASSES = ["licensed_standard_original", "licensed_standard_derivative"]
PRIVATE_RESIDENCIES = ["private_git", "licensed_location", "external"]


def descriptor():
    projection = {
        "source_id": "fixture:source", "dataset_id": "fixture:dataset",
        "doc_key": NA, "owner_repo": "fixture-owner", "source_version": "v1",
        "content_digest": "sha256:" + "a" * 64, "digest_scope": "source-bytes",
        "derived_from": [], "units": {"ratio": "1"},
        "intended_use": "synthetic structure test", "criteria_revision": "v1",
        "rights_revision": "v1",
    }
    return {
        "schema_version": "1", "resource": deepcopy(projection),
        "stable_projection": deepcopy(projection), "source_class": "public_collection",
        "source_status": "indexed", "readiness_status": "ready",
        "observed_at": STAMP, "verified_at": STAMP,
        "identity_evidence": {"original_doc_key": "", "normalization_warning": ""},
        "manifest": {"locator": "data/fixture/manifest.json", "revision": "v1"},
        "storage": {"residency": "external"},
        "rights": {"status": "permitted", "evidence_ref": "fixture:rights",
                   "operations": ["read"], "destinations": ["private"],
                   "checked_at": STAMP, "valid_until": "2026-10-01T00:00:00Z"},
        "access_status": "available",
        "freshness": {"source_vintage": STAMP, "valid_until": "2026-10-01T00:00:00Z",
                      "basis": "fixture criterion"},
        "qualification": {"criterion": "fixture criterion", "evidence_ref": "fixture:check",
                          "catalog_resolution": "verified"},
        "limitations": ["Synthetic; no live data or rights established"],
    }


def validator():
    assert "date-time" in FormatChecker.checkers, "Install jsonschema[format-nongpl]"
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema, format_checker=FormatChecker())


def assign(obj, path, value):
    parts = path.split(".")
    for part in parts[:-1]:
        obj = obj[part]
    obj[parts[-1]] = value


def licensed_descriptor(source_class, residency="external"):
    item = descriptor()
    item["source_class"] = source_class
    item["storage"] = {"residency": residency}
    if source_class == "licensed_standard_original":
        item["storage"]["source_ref"] = "fixture:licensed-location"
    else:
        for key in ("resource", "stable_projection"):
            item[key]["derived_from"] = ["sha256:" + "c" * 64]
    return item


@pytest.mark.parametrize("source_class", LICENSED_CLASSES)
@pytest.mark.parametrize("readiness", ["unverified", "partial", "ready", "unavailable"])
@pytest.mark.parametrize("residency", PRIVATE_RESIDENCIES + ["public_git", "unavailable"])
def test_licensed_private_storage_needs_no_rights_record(source_class, readiness, residency):
    item = licensed_descriptor(source_class, residency)
    item["readiness_status"] = readiness
    del item["rights"]
    for key in ("resource", "stable_projection"):
        item[key]["rights_revision"] = deepcopy(UNKNOWN)
    assert validator().is_valid(item) == (residency in PRIVATE_RESIDENCIES)


@pytest.mark.parametrize("source_class", LICENSED_CLASSES)
@pytest.mark.parametrize("path,value", [
    ("rights", {}), ("rights.status", "unknown"), ("rights.status", "denied"),
    ("rights.evidence_ref", UNKNOWN), ("rights.valid_until", UNKNOWN),
    ("rights.valid_until", "2020-01-01T00:00:00Z"),
    ("rights.operations", []), ("rights.destinations", []),
])
def test_optional_licensed_rights_metadata_does_not_gate_ready(source_class, path, value):
    item = licensed_descriptor(source_class)
    assign(item, path, deepcopy(value))
    validator().validate(item)


@pytest.mark.parametrize("source_class", LICENSED_CLASSES)
@pytest.mark.parametrize("path,value", [
    ("verified_at", UNKNOWN), ("access_status", "partial"),
    ("manifest.revision", UNKNOWN), ("freshness.source_vintage", UNKNOWN),
    ("freshness.valid_until", UNKNOWN), ("freshness.basis", UNKNOWN),
    ("qualification.criterion", UNKNOWN), ("qualification.evidence_ref", UNKNOWN),
    ("qualification.catalog_resolution", "unknown"), ("source_status", "unreachable"),
    ("resource.content_digest", UNKNOWN), ("stable_projection.content_digest", UNKNOWN),
    ("resource.units.ratio", UNKNOWN), ("stable_projection.units.ratio", UNKNOWN),
    ("resource.intended_use", UNKNOWN), ("stable_projection.intended_use", UNKNOWN),
    ("resource.criteria_revision", UNKNOWN), ("stable_projection.criteria_revision", UNKNOWN),
    ("resource.derived_from", UNKNOWN), ("stable_projection.derived_from", UNKNOWN),
])
def test_licensed_exception_preserves_engineering_qualification(source_class, path, value):
    item = licensed_descriptor(source_class)
    del item["rights"]
    # Establish an otherwise valid descriptor before testing each independent guard.
    validator().validate(item)
    assign(item, path, deepcopy(value))
    assert list(validator().iter_errors(item)), path


@pytest.mark.parametrize("source_class", [
    "public_collection", "curated_knowledge", "computational_derivative",
    "client_original", "measured_original",
])
@pytest.mark.parametrize("missing", ["rights", "status", "evidence_ref", "valid_until"])
def test_other_source_classes_still_require_rights(source_class, missing):
    item = descriptor()
    item["source_class"] = source_class
    if source_class in {"client_original", "measured_original"}:
        item["storage"] = {
            "residency": "private_git", "raw_path": "data/fixture/raw/input.zip",
            "raw_digest": "sha256:" + "b" * 64, "retention_status": "retained",
            "ignore_exception": True,
        }
    validator().validate(item)
    if missing == "rights":
        del item["rights"]
    else:
        del item["rights"][missing]
    assert list(validator().iter_errors(item)), missing


@pytest.mark.parametrize("source_class", ["client_original", "measured_original"])
@pytest.mark.parametrize("residency", PRIVATE_RESIDENCIES)
def test_retained_client_and_measured_originals_require_private_raw_evidence(source_class, residency):
    item = descriptor()
    item.update(source_class=source_class, readiness_status="unverified")
    item["storage"] = {
        "residency": residency, "source_ref": "fixture:source", "retention_status": "retained",
    }
    assert list(validator().iter_errors(item))


@pytest.mark.parametrize("residency", PRIVATE_RESIDENCIES)
def test_retained_licensed_original_needs_source_reference_without_private_raw_evidence(residency):
    item = licensed_descriptor("licensed_standard_original", residency)
    item["storage"]["retention_status"] = "retained"
    validator().validate(item)
    del item["storage"]["source_ref"]
    assert list(validator().iter_errors(item))


def test_valid_synthetic_descriptor():
    validator().validate(descriptor())


@pytest.mark.parametrize("path,value", [
    ("schema_version", "2"),
    ("source_status", "gap"), ("source_status", "unreachable"),
    ("stable_projection.doc_key", "md5:" + "a" * 32),
    ("stable_projection.content_digest", "sha256:" + "A" * 64),
    ("identity_evidence.original_doc_key", "a" * 64), ("observed_at", "yesterday"),
    ("observed_at", "2026-02-30T12:00:00Z"),
    ("manifest.locator", "../outside.json"), ("manifest.locator", "C:/private/a"),
    ("resource.source_id", ""), ("stable_projection.content_digest", "sha256:1234"),
    ("stable_projection.doc_key", "a" * 32), ("stable_projection.doc_key", "a" * 64),
    ("stable_projection.units.ratio", 0),
    ("stable_projection.derived_from", ["fixture:a", "fixture:a"]),
    ("stable_projection.derived_from", ["../private/file"]),
    ("readiness_status", "promoted"), ("source_status", "ready"),
    ("rights.status", "unknown"), ("rights.evidence_ref", UNKNOWN),
    ("rights.valid_until", UNKNOWN), ("rights.operations", []),
    ("access_status", "partial"), ("freshness.source_vintage", UNKNOWN),
    ("qualification.catalog_resolution", "unknown"),
    ("stable_projection.source_id", UNKNOWN), ("stable_projection.content_digest", UNKNOWN),
    ("stable_projection.rights_revision", UNKNOWN), ("stable_projection.units.ratio", UNKNOWN),
    ("stable_projection.digest_scope", "unknown"),
    ("stable_projection.digest_scope", "not-applicable"),
    ("stable_projection.content_digest", NA), ("stable_projection.rights_revision", NA),
])
def test_invalid_or_unverified_evidence_cannot_claim_ready(path, value):
    item = descriptor()
    assign(item, path, deepcopy(value))
    assert list(validator().iter_errors(item)), path


def test_unknown_observation_remains_representable():
    item = descriptor()
    item["readiness_status"] = "unverified"
    item["rights"]["status"] = "unknown"
    item["resource"]["content_digest"] = UNKNOWN
    item["stable_projection"]["content_digest"] = UNKNOWN
    validator().validate(item)


@pytest.mark.parametrize("source_class", ["measured_original", "client_original"])
def test_original_retention_requires_private_raw_and_manifest(source_class):
    item = descriptor()
    item["source_class"] = source_class
    assert list(validator().iter_errors(item))
    item["storage"] = {
        "residency": "private_git", "raw_path": "data/fixture/raw/input.zip",
        "raw_digest": "sha256:" + "b" * 64, "retention_status": "retained",
        "ignore_exception": True,
    }
    validator().validate(item)
    for key, value in [("raw_path", "data/fixture/extracted/input.csv"),
                       ("raw_digest", ""), ("ignore_exception", False),
                       ("residency", "public_git")]:
        broken = deepcopy(item)
        broken["storage"][key] = value
        assert list(validator().iter_errors(broken)), key


@pytest.mark.parametrize("residency", ["private_git", "licensed_location", "external"])
def test_licensed_original_may_live_in_private_storage(residency):
    item = descriptor()
    item["source_class"] = "licensed_standard_original"
    item["storage"] = {"residency": residency, "source_ref": "fixture:licensed-location"}
    validator().validate(item)


def test_licensed_original_never_routes_into_public_git():
    item = descriptor()
    item["source_class"] = "licensed_standard_original"
    item["storage"] = {"residency": "public_git", "source_ref": "fixture:licensed-location"}
    assert list(validator().iter_errors(item))


def test_schema_closes_projection_and_unknown_properties():
    item = descriptor()
    assert set(item["stable_projection"]) == FIELDS
    item["stable_projection"]["verified_by_agent"] = True
    assert list(validator().iter_errors(item))


def test_conformance_vectors_are_shared_literals_not_a_second_canonicalizer():
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    vectors = schema["x-conformance"]
    required = {"nominal", "key_order", "refreshed_observation", "unicode", "dimensionless",
                "sorted_derivation", "duplicate_derivation", "unknown_identity",
                "missing_digest", "unknown_units", "inapplicable_identity", "forbidden_content_na",
                "forbidden_rights_na", "legacy_64", "ambiguous_32", "expired_rights",
                "projection_mismatch", "unsorted_derivation"}
    assert required <= {v["id"] for v in vectors}
    for vector in vectors:
        assert isinstance(vector["input"], dict)
        assert vector["schema_valid"] == validator().is_valid(vector["input"]), vector["id"]
        assert vector["expected"] in {"candidate", "reject"}
        if vector["expected"] == "candidate":
            assert set(vector["projection"]) == FIELDS
            for key in ["resource_descriptor_sha256", "resource_stable_sha256"]:
                assert re.fullmatch(r"[a-f0-9]{64}", vector[key])
        else:
            assert vector["reason"]
            assert "resource_stable_sha256" not in vector
            assert "resource_descriptor_sha256" not in vector
    by_id = {v["id"]: v for v in vectors}
    assert by_id["nominal"]["resource_descriptor_sha256"] == by_id["key_order"]["resource_descriptor_sha256"]
    assert by_id["nominal"]["resource_stable_sha256"] == by_id["key_order"]["resource_stable_sha256"]
    assert by_id["nominal"]["resource_stable_sha256"] == by_id["refreshed_observation"]["resource_stable_sha256"]
    assert by_id["nominal"]["resource_descriptor_sha256"] != by_id["refreshed_observation"]["resource_descriptor_sha256"]


def test_policy_consumers_resolve_authority_and_remove_blanket_permissions():
    contract = CONTRACT.read_text(encoding="utf-8")
    for phrase in ["data-source-catalog.yml", "domain-database-index.yml", "dataset-allocation-ledger.json",
                   "L2", "L3", "source_vintage", "workflow_receipt.py", "not installed",
                   "data/<dataset>/raw/", "SHA-256", "unknown", "not_applicable"]:
        assert phrase in contract
    paths = [ROOT / "docs/DATA_RESIDENCE_POLICY.md", ROOT / "docs/architecture/data-layer-contract.md",
             ROOT / ".claude/rules/codes-standards-data-routing.md"]
    for path in paths + [CONTRACT]:
        text = path.read_text(encoding="utf-8")
        if path != CONTRACT:
            assert "agent-data-handling-contract.md" in text
        for target in re.findall(r"\]\(([^)#]+)(?:#[^)]+)?\)", text):
            if not re.match(r"\w+://", target):
                assert (path.parent / target).exists(), (path, target)
    residence = paths[0].read_text(encoding="utf-8")
    assert "ingest acceptance remains blocked" in residence
    assert "required-original exception" in residence
    rule = paths[2].read_text(encoding="utf-8")
    assert "No rights checks" in rule
    assert "raw_copy_allowed: false" not in rule
    assert "unrestricted within copyright fair use" not in rule
    assert "when in doubt, route private" not in rule


def test_owner_issued_slug_ids_are_preserved_without_invented_namespace():
    item = descriptor()
    for key in ("resource", "stable_projection"):
        item[key]["source_id"] = "fixture-source"
        item[key]["dataset_id"] = "fixture-dataset"
    validator().validate(item)


@pytest.mark.parametrize("lineage", ["sha256:xyz", "md5:1"])
def test_reserved_lineage_namespaces_require_complete_digest(lineage):
    item = descriptor()
    item["stable_projection"]["derived_from"] = [lineage]
    assert list(validator().iter_errors(item))


def test_conformance_candidates_do_not_claim_future_observations():
    from datetime import datetime
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    for case in schema["x-conformance"]:
        if case["expected"] == "candidate":
            assert datetime.fromisoformat(case["input"]["observed_at"]) <= datetime.fromisoformat(case["as_of"])
    assert {"future_observation", "unknown_catalog_member", "malformed_lineage", "owner_slug"} <= {
        case["id"] for case in schema["x-conformance"]
    }


def test_licensed_derivative_requires_lineage_before_ready():
    item = descriptor()
    item["source_class"] = "licensed_standard_derivative"
    assert list(validator().iter_errors(item))
    for key in ("resource", "stable_projection"):
        item[key]["derived_from"] = ["sha256:" + "c" * 64]
    validator().validate(item)


def test_pending_original_is_explicit_and_not_public_or_ready():
    item = descriptor()
    item.update(source_class="client_original", readiness_status="unverified")
    item["storage"] = {"residency": "external"}
    assert list(validator().iter_errors(item))
    item["storage"]["retention_status"] = "required_pending"
    validator().validate(item)
    item["rights"]["destinations"] = ["public"]
    assert list(validator().iter_errors(item))


def test_distinct_candidate_vectors_except_intentional_key_order():
    vectors = json.loads(SCHEMA.read_text(encoding="utf-8"))["x-conformance"]
    hashes = [v["resource_descriptor_sha256"] for v in vectors
              if v["expected"] == "candidate" and v["id"] != "key_order"]
    assert len(set(hashes)) == len(hashes)


def test_explicit_md5_can_be_read_without_claiming_ready():
    item = descriptor()
    item["readiness_status"] = "unverified"
    for key in ("resource", "stable_projection"):
        item[key]["doc_key"] = "md5:" + "a" * 32
    validator().validate(item)


@pytest.mark.parametrize("required", [
    "Lift all the blockers.",
    "No rights checks and no \"metadata-only\" limit.",
    "originals may be kept in private Git",
    "Kept out of public repos and pages: the original PDFs",
    "Every job checks which CFR applies and cites the section.",
])
def test_standards_rule_records_maintainer_ruling(required):
    rule = (ROOT / ".claude/rules/codes-standards-data-routing.md").read_text(encoding="utf-8")
    section = rule.split("## Maintainer ruling (28 Oct 2026)", 1)[1].split("## Placement", 1)[0]
    assert required in section
    assert "metadata-only extraction remains metadata-only" not in rule
