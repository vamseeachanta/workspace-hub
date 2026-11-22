"""Synthetic cases from docs/guides/portability-guidance-health.md.

Version strings, counts and exit codes follow that document's examples and
contract; expected compatibility is exact pair equality, computed by inspection.
"""

from __future__ import annotations

import copy
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest


# Repository layout: tests/memory is two parents below the repository root.
SCRIPT = (
    Path(__file__).resolve().parents[2]
    / "scripts/memory/portability_guidance_health.py"
)
LOCATOR = "docs/guides/portability.md"
MODEL = {"shape": "event-log", "schema_version": "schema-a"}


@pytest.fixture
def health():
    spec = importlib.util.spec_from_file_location("portability_health", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def evidence():
    return (
        {"audit_model": dict(MODEL), "counts": {"records": 10}},
        {"supported_audit_model": dict(MODEL)},
    )


def assert_result(result, status, reason):
    assert result["status"] == status
    assert result["reason_code"] == reason
    assert result["canonical_locator"] == LOCATOR
    assert result["diagnostic"]


def test_count_only_refresh_does_not_stale_guidance(health, evidence):
    audit, guidance = evidence
    initial = health.build_report(audit, guidance, LOCATOR)
    # Independent example: one new record changes ten to eleven, not the model.
    audit["counts"]["records"] = 11
    audit["generated_at"] = "later"
    refreshed = health.build_report(audit, guidance, LOCATOR)
    assert initial == refreshed
    assert_result(refreshed, "current", "GUIDANCE_CURRENT")


@pytest.mark.parametrize("field,value", [
    ("schema_version", "schema-b"),
    ("shape", "message-log"),
])
def test_model_change_requires_guidance_review(health, evidence, field, value):
    audit, guidance = evidence
    audit["audit_model"][field] = value
    result = health.build_report(audit, guidance, LOCATOR)
    assert_result(result, "incompatible_model", "GUIDANCE_REVIEW_REQUIRED")
    assert "Review" in result["diagnostic"]


def test_guidance_declares_new_supported_version(health, evidence):
    audit, guidance = evidence
    audit["audit_model"]["schema_version"] = "schema-b"
    guidance["supported_audit_model"]["schema_version"] = "schema-b"
    assert_result(
        health.build_report(audit, guidance, LOCATOR),
        "current", "GUIDANCE_CURRENT",
    )


@pytest.mark.parametrize("source", ["audit", "guidance"])
@pytest.mark.parametrize("invalid", [
    None, [], "opaque", {}, {"shape": "event-log"},
    {"shape": "event-log", "schema_version": None},
    {"shape": "event-log", "schema_version": True},
    {"shape": "event-log", "schema_version": 10},
    {"shape": "event-log", "schema_version": ""},
    {"shape": "event-log", "schema_version": " schema-a"},
    {"shape": "", "schema_version": "schema-a"},
    {"shape": [], "schema_version": "schema-a"},
    {**MODEL, "unrecognised_evidence": "opaque"},
])
def test_missing_or_malformed_model_is_unknown(health, evidence, source, invalid):
    audit, guidance = evidence
    if source == "audit":
        audit["audit_model"] = invalid
    else:
        guidance["supported_audit_model"] = invalid
    assert_result(
        health.build_report(audit, guidance, LOCATOR),
        "unknown_evidence", f"{source.upper()}_MODEL_INVALID",
    )


@pytest.mark.parametrize("source,key", [
    ("audit", "audit_model"), ("guidance", "supported_audit_model"),
])
def test_undeclared_model_is_unknown(health, evidence, source, key):
    audit, guidance = evidence
    target = audit if source == "audit" else guidance
    del target[key]
    assert_result(
        health.build_report(audit, guidance, LOCATOR),
        "unknown_evidence", f"{source.upper()}_MODEL_MISSING",
    )


@pytest.mark.parametrize("source", ["audit", "guidance"])
@pytest.mark.parametrize("document", [[], "opaque", False])
def test_non_object_documents_are_unknown(health, evidence, source, document):
    audit, guidance = evidence
    if source == "audit":
        audit = document
    else:
        guidance = document
    assert_result(
        health.build_report(audit, guidance, LOCATOR),
        "unknown_evidence", f"{source.upper()}_DOCUMENT_INVALID",
    )


def test_missing_documents_are_distinguished(health, evidence):
    audit, guidance = evidence
    assert_result(health.build_report(None, guidance, LOCATOR),
                  "unknown_evidence", "AUDIT_MISSING")
    assert_result(health.build_report(audit, None, LOCATOR),
                  "missing_guidance", "GUIDANCE_MISSING")
    assert_result(health.build_report(None, None, LOCATOR),
                  "missing_guidance", "GUIDANCE_MISSING")


def test_report_preserves_supplied_objects(health, evidence):
    original = copy.deepcopy(evidence)
    health.build_report(*evidence, LOCATOR)
    assert evidence == original


def test_diagnostics_do_not_echo_input_values(health, evidence):
    audit, guidance = evidence
    marker = "private-value-marker"
    audit["audit_model"]["schema_version"] = marker
    audit["counts"] = {marker: marker}
    result = health.build_report(audit, guidance, LOCATOR)
    assert_result(result, "incompatible_model", "GUIDANCE_REVIEW_REQUIRED")
    assert marker not in json.dumps(result)


@pytest.mark.parametrize("locator", [
    "", ".", "..", "../guidance.md", "docs/../guidance.md", "docs//guide.md",
    "docs/./guide.md", "docs/guide.md\n", "C:\\private\\guide.md",
    "docs/guide.md?query", "https://example.invalid/guide.md",
])
def test_invalid_locator_is_not_echoed(health, evidence, locator):
    result = health.build_report(*evidence, locator)
    assert result["status"] == "unknown_evidence"
    assert result["reason_code"] == "CANONICAL_LOCATOR_INVALID"
    assert result["canonical_locator"] is None


def test_absolute_temporary_locator_is_rejected(health, evidence, tmp_path):
    result = health.build_report(*evidence, str(tmp_path / "guide.md"))
    assert result["reason_code"] == "CANONICAL_LOCATOR_INVALID"
    assert str(tmp_path) not in json.dumps(result)


def write_inputs(tmp_path, evidence):
    audit_path = tmp_path / "audit.json"
    guidance_path = tmp_path / "guidance.json"
    for path, document in zip((audit_path, guidance_path), evidence):
        path.write_text(json.dumps(document), encoding="utf-8")
    return audit_path, guidance_path


def run_cli(*args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *map(str, args)],
        capture_output=True, text=True, check=False,
    )


def test_cli_is_read_only_and_ignores_mtimes(tmp_path, evidence):
    paths = write_inputs(tmp_path, evidence)
    # Both epochs are the same synthetic instant; compatibility ignores age.
    for path in paths:
        os.utime(path, (0, 0))
    before = [(p.read_bytes(), p.stat().st_mtime_ns) for p in paths]
    result = run_cli("--audit", paths[0], "--guidance", paths[1],
                     "--canonical-locator", LOCATOR)
    assert result.returncode == 0
    assert result.stderr == ""
    assert_result(json.loads(result.stdout), "current", "GUIDANCE_CURRENT")
    assert before == [(p.read_bytes(), p.stat().st_mtime_ns) for p in paths]
    assert sorted(tmp_path.iterdir()) == sorted(paths)


@pytest.mark.parametrize("source", ["audit", "guidance"])
@pytest.mark.parametrize("payload", [
    b"{", b"\xff", b"null", b"[]",
    b'{"audit_model":null,"audit_model":{}}',
    b'{"counts":NaN}', b'{"counts":Infinity}',
])
def test_cli_malformed_evidence_is_value_free(tmp_path, evidence, source, payload):
    paths = write_inputs(tmp_path, evidence)
    path = paths[0] if source == "audit" else paths[1]
    path.write_bytes(payload)
    before = [p.read_bytes() for p in paths]
    result = run_cli("--audit", paths[0], "--guidance", paths[1],
                     "--canonical-locator", LOCATOR)
    assert result.returncode == 1
    assert result.stderr == ""
    assert_result(json.loads(result.stdout), "unknown_evidence",
                  f"{source.upper()}_DOCUMENT_INVALID")
    assert str(tmp_path) not in result.stdout
    assert before == [p.read_bytes() for p in paths]


@pytest.mark.parametrize("source", ["audit", "guidance"])
@pytest.mark.parametrize("absent_parent", [False, True])
def test_cli_missing_file(tmp_path, evidence, source, absent_parent):
    paths = list(write_inputs(tmp_path, evidence))
    missing = tmp_path / "absent.json"
    if absent_parent:
        missing = tmp_path / "absent" / "evidence.json"
    paths[0 if source == "audit" else 1] = missing
    result = run_cli("--audit", paths[0], "--guidance", paths[1],
                     "--canonical-locator", LOCATOR)
    assert result.returncode == 1
    assert_result(json.loads(result.stdout),
                  "missing_guidance" if source == "guidance" else "unknown_evidence",
                  f"{source.upper()}_MISSING")


@pytest.mark.parametrize("source", ["audit", "guidance"])
def test_unreadable_evidence_is_distinct(health, tmp_path, evidence, monkeypatch, source):
    paths = write_inputs(tmp_path, evidence)
    unreadable = paths[0] if source == "audit" else paths[1]
    original_read = Path.read_text

    def denied(path, *args, **kwargs):
        if path == unreadable:
            raise PermissionError("private-value-marker")
        return original_read(path, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", denied)
    result = health.report_files(*paths, LOCATOR)
    assert_result(result, "unknown_evidence", f"{source.upper()}_UNREADABLE")
    assert "private-value-marker" not in json.dumps(result)


def test_invalid_locator_prevents_file_reads(health, tmp_path, monkeypatch):
    def unexpected_read(*args, **kwargs):
        pytest.fail("Invalid locator must be rejected before evidence is read")

    monkeypatch.setattr(Path, "read_text", unexpected_read)
    result = health.report_files(tmp_path / "audit", tmp_path / "guidance", "..")
    assert result["reason_code"] == "CANONICAL_LOCATOR_INVALID"


def test_guidance_declaration_error_precedes_missing_audit(health, tmp_path):
    guidance = tmp_path / "guidance.json"
    guidance.write_text("{}", encoding="utf-8")
    result = health.report_files(tmp_path / "absent.json", guidance, LOCATOR)
    assert_result(result, "unknown_evidence", "GUIDANCE_MODEL_MISSING")


def test_cli_incompatible_model(tmp_path, evidence):
    evidence[0]["audit_model"]["schema_version"] = "schema-b"
    paths = write_inputs(tmp_path, evidence)
    result = run_cli("--audit", paths[0], "--guidance", paths[1],
                     "--canonical-locator", LOCATOR)
    assert result.returncode == 1
    assert_result(json.loads(result.stdout), "incompatible_model",
                  "GUIDANCE_REVIEW_REQUIRED")


def test_cli_usage_errors_do_not_echo_arguments(tmp_path):
    result = run_cli("--unknown-option", tmp_path / "private-value-marker")
    assert result.returncode == 2
    assert "private-value-marker" not in result.stdout + result.stderr
    assert str(tmp_path) not in result.stdout + result.stderr
    assert "ARGUMENTS_INVALID" in result.stderr
