"""Pure receipt comparisons and resource-owned literal conformance vectors."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
MODULE = ROOT / "scripts/governance/workflow_receipt.py"
sys.path.insert(0, str(MODULE.parent))


@pytest.fixture
def api():
    spec = importlib.util.spec_from_file_location("workflow_receipt", MODULE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def schema():
    return json.loads((ROOT / "config/schemas/workflow-receipt-v1.schema.json").read_text(encoding="utf-8"))


@pytest.fixture
def resources():
    return json.loads((ROOT / "config/schemas/resource-descriptor-v1.schema.json").read_text(encoding="utf-8"))


def receipt(api):
    key = {"repository_id": "fixture-repo", "task_id": "issue:1", "operation_id": "check",
           "changed_paths": ["src/a.py"], "code_revision": "fixture-revision",
           "dirty_diff_sha256": "a" * 64, "resource_stable_sha256s": [],
           "environment_sha256": "b" * 64, "criteria_revision": "v1",
           "verification_procedure_version": "v1"}
    return {"schema_version": "1", "observed_at": "2026-09-12T12:00:00Z", "key": key,
            "key_sha256": api.sha256(key), "resources": [],
            "evidence": {"locator": "fixture:receipt", "evidence_artifact_sha256":
                         api.evidence_digest("synthetic verification")}}


def compare(api, schema, prior, current, **options):
    kwargs = {"workflow_schema": schema, "as_of": "2026-09-13T12:00:00Z",
              "source_ids": [], "evidence_artifacts": {"fixture:receipt": "synthetic verification"}}
    kwargs.update(options)
    return api.compare_receipts(prior, current, **kwargs)


def test_identical_code_only_receipt_is_only_unverified_candidate(api, schema):
    item = receipt(api)
    assert compare(api, schema, item, item) == {
        "reuse_assessment": "candidate-pending-live-validation",
        "reason_codes": ["MUTABLE_VALIDATION_REQUIRED"]}


@pytest.mark.parametrize("key,value", [
    ("repository_id", "other"), ("task_id", "issue:2"), ("operation_id", "other"),
    ("changed_paths", ["src/b.py"]), ("code_revision", "other"),
    ("dirty_diff_sha256", "c" * 64), ("environment_sha256", "c" * 64),
    ("criteria_revision", "other"), ("verification_procedure_version", "other"),
])
def test_each_governing_key_change_invalidates(api, schema, key, value):
    prior = receipt(api)
    current = deepcopy(prior)
    current["key"][key] = value
    current["key_sha256"] = api.sha256(current["key"])
    assert compare(api, schema, prior, current)["reason_codes"] == ["KEY_CHANGED"]


def test_timestamp_and_identical_artifact_locator_change_do_not_change_key(api, schema):
    prior = receipt(api)
    current = deepcopy(prior)
    current["observed_at"] = "2026-09-13T12:00:00Z"
    current["evidence"]["locator"] = "fixture:relocated"
    output = compare(api, schema, prior, current, evidence_artifacts={
        "fixture:receipt": "synthetic verification", "fixture:relocated": "synthetic verification"})
    assert output["reuse_assessment"] == "candidate-pending-live-validation"


@pytest.mark.parametrize("artifacts", [{}, {"fixture:receipt": "changed"},
                                      {"fixture:receipt": b"\xff"}])
def test_actual_evidence_bytes_required(api, schema, artifacts):
    item = receipt(api)
    result = compare(api, schema, item, item, evidence_artifacts=artifacts)
    assert result["reuse_assessment"] == "invalid"
    assert result["reason_codes"] == ["EVIDENCE_DIGEST_MISMATCH"]


@pytest.mark.parametrize("path", ["../src/a.py", "/src/a.py", "C:/src/a.py",
                                   "src\\a.py", "src/./a.py", "src//a.py", "a/../b",
                                   "docs/a.md.", "docs /a.md"])
def test_receipt_paths_must_already_be_normalized(api, schema, path):
    item = receipt(api)
    item["key"]["changed_paths"] = [path]
    item["key_sha256"] = api.sha256(item["key"])
    assert compare(api, schema, item, item)["reuse_assessment"] == "invalid"


@pytest.mark.parametrize("replacement", [{}, True, {"$id": "urn:wrong"},
    {"$id": "urn:workspace-hub:workflow-receipt:1"}])
def test_substituted_schema_cannot_relax_contract(api, schema, replacement):
    item = receipt(api)
    assert compare(api, replacement, item, item)["reuse_assessment"] != "candidate-pending-live-validation"


@pytest.mark.resource_schema
def test_malformed_legacy_warning_has_public_value_error(api, resources):
    item = deepcopy(next(v["input"] for v in resources["x-conformance"] if v["id"] == "legacy_64"))
    item["identity_evidence"]["normalization_warning"] = 1
    with pytest.raises(ValueError):
        api.resource_hashes(item, resources, as_of="2026-09-12T12:00:00Z",
                            source_ids=["fixture:source"], legacy_read=True)


@pytest.mark.parametrize("change", ["issuer", "version", "key_digest", "missing_resources",
                                    "duplicate_paths", "unsorted_paths", "extra_key", "future"])
def test_forged_or_malformed_receipts_fail_closed(api, schema, change):
    item = receipt(api)
    if change == "issuer": item["issuer"] = "trusted-owner"
    if change == "version": item["schema_version"] = "2"
    if change == "key_digest": item["key_sha256"] = "0" * 64
    if change == "missing_resources": del item["resources"]
    if change == "duplicate_paths": item["key"]["changed_paths"] *= 2
    if change == "unsorted_paths": item["key"]["changed_paths"] = ["b", "a"]
    if change == "extra_key": item["key"]["approval"] = True
    if change == "future": item["observed_at"] = "2027-01-01T00:00:00Z"
    assert compare(api, schema, item, item)["reuse_assessment"] == "invalid"


@pytest.mark.parametrize("raw", ['{"x":1,"x":2}', '{"x":{"y":1,"y":2}}',
                                  '{"x":NaN}', '{"x":Infinity}', '{"x":-Infinity}',
                                  '{"x":1e999}', '{', '[]', b'\xff',
                                  '{"x":"\\ud800"}'])
def test_strict_json_rejection(api, raw):
    with pytest.raises(ValueError): api.load_json(raw)


def test_bounded_json_and_canonical_values(api):
    with pytest.raises(ValueError): api.load_json('{"large":"12345"}', max_bytes=8)
    with pytest.raises(ValueError): api.load_json('{"x":' * 70 + '0' + '}' * 70)
    with pytest.raises(ValueError): api.canonical_bytes({1: "not a JSON key"})
    with pytest.raises(ValueError): api.canonical_bytes({"x": float("nan")})
    assert api.load_json(b'{"zero":0}') == {"zero": 0}
    assert api.canonical_bytes({"z": "\u03bc", "a": 0}) == '{"a":0,"z":"\u03bc"}'.encode()


@pytest.mark.resource_schema
def test_all_resource_owned_conformance_literals(api, resources):
    ids = resources["x-catalog-fixture"]["source_ids"]
    for vector in resources["x-conformance"]:
        kwargs = {"as_of": vector["as_of"], "source_ids": ids,
                  "legacy_read": vector["mode"] == "legacy-read"}
        if vector["expected"] == "reject":
            with pytest.raises(ValueError, match=".+"):
                api.resource_hashes(vector["input"], resources, **kwargs)
        else:
            actual = api.resource_hashes(vector["input"], resources, **kwargs)
            assert actual == (vector["resource_descriptor_sha256"],
                              vector["resource_stable_sha256"]), vector["id"]


def attach_resource(api, item, vector):
    item["resources"] = [{"resource_descriptor_schema": "urn:workspace-hub:resource-descriptor:1",
                          "resource_descriptor_sha256": vector["resource_descriptor_sha256"],
                          "resource_stable_sha256": vector["resource_stable_sha256"],
                          "descriptor": deepcopy(vector["input"])}]
    item["key"]["resource_stable_sha256s"] = [vector["resource_stable_sha256"]]
    item["key_sha256"] = api.sha256(item["key"])


@pytest.mark.resource_schema
def test_resource_observation_refresh_uses_prior_recorded_time(api, schema, resources):
    vectors = {v["id"]: v for v in resources["x-conformance"]}
    prior, current = receipt(api), receipt(api)
    attach_resource(api, prior, vectors["nominal"])
    attach_resource(api, current, vectors["refreshed_observation"])
    current["observed_at"] = vectors["refreshed_observation"]["as_of"]
    result = compare(api, schema, prior, current, resource_schema=resources,
                     source_ids=resources["x-catalog-fixture"]["source_ids"])
    assert result["reuse_assessment"] == "candidate-pending-live-validation"


@pytest.mark.resource_schema
def test_resource_schema_is_lazy_and_missing_fails_closed(api, schema, resources):
    item = receipt(api)
    attach_resource(api, item, resources["x-conformance"][0])
    assert compare(api, schema, item, item) == {
        "reuse_assessment": "needs-context", "reason_codes": ["SCHEMA_UNAVAILABLE"]}


@pytest.mark.resource_schema
@pytest.mark.parametrize("change", ["full_hash", "stable_hash", "key_binding", "missing",
                                    "operation", "destination", "expired", "catalog"])
def test_resource_bindings_and_mutable_claims(api, schema, resources, change):
    item = receipt(api)
    attach_resource(api, item, resources["x-conformance"][0])
    kwargs = {"resource_schema": resources,
              "source_ids": resources["x-catalog-fixture"]["source_ids"]}
    if change == "full_hash": item["resources"][0]["resource_descriptor_sha256"] = "0" * 64
    if change == "stable_hash": item["resources"][0]["resource_stable_sha256"] = "0" * 64
    if change == "key_binding": item["key"]["resource_stable_sha256s"] = []
    if change == "missing": item["resources"] = []
    if change == "operation": kwargs["resource_operation"] = "publish"
    if change == "destination": kwargs["destination"] = "public"
    if change == "expired": kwargs["as_of"] = "2026-11-01T00:00:00Z"
    if change == "catalog": kwargs["source_ids"] = []
    item["key_sha256"] = api.sha256(item["key"])
    assert compare(api, schema, item, item, **kwargs)["reuse_assessment"] == "invalid"


def test_no_network_or_locator_file_reads(api, schema, monkeypatch):
    import socket
    import subprocess
    def deny(*args, **kwargs): raise AssertionError("unexpected side effect")
    item = receipt(api)
    monkeypatch.setattr(Path, "read_text", deny)
    monkeypatch.setattr(Path, "read_bytes", deny)
    monkeypatch.setattr(socket, "create_connection", deny)
    monkeypatch.setattr(subprocess, "run", deny)
    assert compare(api, schema, item, item)["reuse_assessment"] == "candidate-pending-live-validation"
