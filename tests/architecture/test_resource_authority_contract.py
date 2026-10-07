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


@pytest.mark.parametrize("residency", ["private_git", "public_git", "external"])
def test_licensed_original_never_routes_into_git(residency):
    item = descriptor()
    item["source_class"] = "licensed_standard_original"
    item["storage"] = {"residency": residency, "source_ref": "fixture:licensed-location", "raw_copy_allowed": False}
    assert list(validator().iter_errors(item))
    item["storage"]["residency"] = "licensed_location"
    validator().validate(item)


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
    assert "raw_copy_allowed: false" in rule
    assert "source-specific rights" in rule
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


@pytest.mark.parametrize("extra", [
    {"raw_path": "data/fixture/raw/original.pdf"}, {"ignore_exception": True},
    {"raw_digest": "sha256:" + "c" * 64}, {"raw_copy_allowed": True},
])
def test_licensed_location_cannot_hide_git_copy_metadata(extra):
    item = descriptor()
    item["source_class"] = "licensed_standard_original"
    item["storage"] = {"residency": "licensed_location", "source_ref": "fixture:source",
                       "raw_copy_allowed": False, **extra}
    assert list(validator().iter_errors(item))


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
