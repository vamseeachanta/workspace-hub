"""Synthetic event v1 tests; passing mappings establish no native compatibility."""
from copy import deepcopy
import importlib
import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts/governance"))
import workflow_decision


@pytest.fixture
def normalizer():
    return importlib.import_module("consumer_event")


def context(provider="claude"):
    return {"schema_version": "1", "provider": provider, "operation_kind": "edit",
            "scope": {"repository_id": "fixture/repo", "task_id": "issue:3615",
                      "operation_id": "fixture-edit", "bounded": True},
            "changed_paths": ["docs/example.md"], "effects": ["local-reversible"],
            "authorization_reference": "session:fixture-reference"}


def envelope(provider="claude", kind="file.write", payload=None):
    return {"schema_version": "1", "provider": provider, "event_kind": kind,
            "payload": {"path": "docs/example.md"} if payload is None else payload,
            "evidence_reference": "fixture:unverified-event"}


def call(api, event=None, supplied=None):
    return api.normalize_event(json.dumps(event or envelope()), context() if supplied is None else supplied)


def rejected(status, reason):
    return {"mapping_status": status, "request": None, "reason_codes": [reason]}


@pytest.mark.parametrize("provider", ["claude", "codex"])
@pytest.mark.parametrize("kind", ["file.write", "file.edit", "file.patch"])
def test_supported_synthetic_events_map_existing_request(normalizer, provider, kind):
    payload = {"changes": ["docs/example.md"]} if kind == "file.patch" else {"path": "docs/example.md"}
    supplied = context(provider)
    result = call(normalizer, envelope(provider, kind, payload), supplied)
    assert result == {"mapping_status": "mapped", "request": supplied, "reason_codes": ["MAPPED_EVENT"]}
    assert workflow_decision.assess(result["request"]) == workflow_decision.assess(supplied)


def test_normalized_paths_include_both_rename_endpoints(normalizer):
    event = envelope(kind="file.patch", payload={"changes": [{"old_path": "docs\\old.md", "new_path": "docs/new.md"}]})
    supplied = context()
    supplied["changed_paths"] = ["docs/new.md", "docs/old.md", "docs/new.md"]
    result = call(normalizer, event, supplied)
    assert result["request"]["changed_paths"] == ["docs/new.md", "docs/old.md"]
    supplied["changed_paths"] = ["docs/new.md"]
    assert call(normalizer, event, supplied) == rejected("needs-context", "PATH_BINDING_MISMATCH")


@pytest.mark.parametrize("path", ["/tmp/file", "C:/file", "C:file", "../file", "docs/../file",
                                  "//host/share", "\\\\host\\share", "docs/file. ", "docs//file", ""])  # identifier-gate: example
def test_invalid_paths_remain_unmapped(normalizer, path):
    assert call(normalizer, envelope(payload={"path": path})) == rejected("needs-context", "PATH_BINDING_MISMATCH")


def test_supplied_path_escape_and_case_mismatch_are_not_relativized(normalizer):
    for paths in [["C:/docs/example.md"], ["docs/Example.md"], ["docs/other.md"]]:
        supplied = context()
        supplied["changed_paths"] = paths
        assert call(normalizer, supplied=supplied) == rejected("needs-context", "PATH_BINDING_MISMATCH")


@pytest.mark.parametrize("payload", [{}, {"path": 2}, {"path": "docs/example.md", "approved": True},
                                     {"changes": ["docs/example.md"]}])
def test_write_payload_shape_is_exact(normalizer, payload):
    assert call(normalizer, envelope(payload=payload)) == rejected("unsupported", "MALFORMED_EVENT")


@pytest.mark.parametrize("changes", [[], None, "docs/example.md", [2], [{}],
                                     [{"old_path": "a", "new_path": "b", "approved": True}],
                                     [{"old_path": "a"}], [{"old_path": 1, "new_path": "b"}]])
def test_patch_payload_shape_is_exact(normalizer, changes):
    event = envelope(kind="file.patch", payload={"changes": changes})
    assert call(normalizer, event) == rejected("unsupported", "MALFORMED_EVENT")


@pytest.mark.parametrize("command", ["echo harmless", "echo ok > file", "python -c write", "git push",
                                     "powershell -EncodedCommand opaque", "echo ok && delete stuff"])
def test_shell_never_extracts_routine_effects(normalizer, command):
    event = envelope(kind="shell.exec", payload={"command": command})
    assert call(normalizer, event) == rejected("needs-context", "INCOMPLETE_EFFECTS")


@pytest.mark.parametrize("field,value", [("provider", "other"), ("event_kind", "native.patch"),
                                         ("schema_version", "2")])
def test_unknown_event_contract_is_unsupported(normalizer, field, value):
    event = envelope()
    event[field] = value
    assert call(normalizer, event) == rejected("unsupported", "UNSUPPORTED_EVENT")


@pytest.mark.parametrize("change", ["extra", "missing", "empty_reference", "null_reference",
                                    "provider_type", "version_type", "kind_type"])
def test_envelope_malformed_fields(normalizer, change):
    event = envelope()
    if change == "extra": event["approval"] = True
    if change == "missing": del event["payload"]
    if change == "empty_reference": event["evidence_reference"] = "  "
    if change == "null_reference": event["evidence_reference"] = None
    if change == "provider_type": event["provider"] = 1
    if change == "version_type": event["schema_version"] = 1
    if change == "kind_type": event["event_kind"] = []
    assert call(normalizer, event) == rejected("unsupported", "MALFORMED_EVENT")


@pytest.mark.parametrize("raw", ['{"schema_version":"1","schema_version":"1"}', '{"x":NaN}',
                                  '{"x":Infinity}', '{"x":1e999}', '{', '[]', b'\xff',
                                  '{"x":"\\ud800"}', {}, None, 2], ids=lambda x: type(x).__name__)
def test_malformed_raw_input(normalizer, raw):
    assert normalizer.normalize_event(raw, context()) == rejected("unsupported", "MALFORMED_EVENT")


@pytest.mark.parametrize("case", ["oversized", "deep", "many_nodes"])
def test_existing_parser_limits(normalizer, case):
    raw = {"oversized": '{"x":"' + 'a' * 1048576 + '"}',
           "deep": '{"x":' * 70 + '0' + '}' * 70,
           "many_nodes": '{"x":[' + ','.join('0' for _ in range(100001)) + ']}'}[case]
    assert normalizer.normalize_event(raw, context()) == rejected("unsupported", "MALFORMED_EVENT")


@pytest.mark.parametrize("field,value", [("approval", True), ("scope", []), ("changed_paths", "x"),
                                         ("changed_paths", [2]), ("changed_paths", [{"new_path": "a"}]),
                                         ("effects", []), ("effects", ["local-reversible", "local-reversible"]),
                                         ("effects", ["magic"]), ("provider", 1),
                                         ("authorization_reference", ""), ("operation_kind", 1)])
def test_malformed_context(normalizer, field, value):
    supplied = context()
    supplied[field] = value
    assert call(normalizer, supplied=supplied) == rejected("unsupported", "MALFORMED_EVENT")


def test_missing_or_unbounded_context(normalizer):
    assert call(normalizer, supplied={}) == rejected("needs-context", "MISSING_CONTEXT")
    supplied = context()
    supplied["scope"]["bounded"] = False
    assert call(normalizer, supplied=supplied) == rejected("needs-context", "MISSING_CONTEXT")


@pytest.mark.parametrize("field,value", [("provider", "codex"), ("schema_version", "2"),
                                         ("operation_kind", "inspect"), ("operation_kind", "execute"),
                                         ("effects", ["read-only"]), ("effects", ["substantial-change"])])
def test_conflicting_context_does_not_erase_event_effects(normalizer, field, value):
    supplied = context()
    supplied[field] = value
    assert call(normalizer, supplied=supplied) == rejected("needs-context", "INCOMPLETE_EFFECTS")


@pytest.mark.parametrize("effect", ["publication", "destruction", "access-change",
                                   "engineering-basis-change", "substantial-change"])
def test_additional_consequential_effects_are_preserved(normalizer, effect):
    supplied = context()
    supplied["effects"].append(effect)
    result = call(normalizer, supplied=supplied)
    assert result["mapping_status"] == "mapped"
    assert result["request"]["effects"] == supplied["effects"]
    assert workflow_decision.assess(result["request"])["action_boundary"] == "approval-required"


def test_no_authority_minted_and_assessment_contract_unchanged(normalizer):
    supplied = context()
    del supplied["authorization_reference"]
    result = call(normalizer, supplied=supplied)
    assessment = workflow_decision.assess(result["request"])
    assert assessment["authorization_assessment"] == "missing"
    assert assessment["action_boundary"] == "needs-context"
    assert "MAPPED_EVENT" not in assessment["reason_codes"]
    assert set(result) == {"mapping_status", "request", "reason_codes"}


def test_deep_copy_and_optional_assessment_fields_preserved(normalizer):
    supplied = context()
    supplied["metrics"] = {"raw": {"test": [1]}, "sample_count": 0}
    before = deepcopy(supplied)
    result = call(normalizer, supplied=supplied)
    assert supplied == before
    result["request"]["metrics"]["raw"]["test"].append(2)
    assert supplied == before
    assert call(normalizer, supplied=supplied)["request"] == before


def test_context_bounds_and_wrong_argument_type(normalizer):
    assert normalizer.normalize_event(json.dumps(envelope()), []) == rejected("unsupported", "MALFORMED_EVENT")
    supplied = context()
    supplied["metrics"] = {"x": "a" * 1048576}
    assert call(normalizer, supplied=supplied) == rejected("unsupported", "MALFORMED_EVENT")
    supplied["metrics"] = {"x": float("nan")}
    assert call(normalizer, supplied=supplied) == rejected("unsupported", "MALFORMED_EVENT")


def test_mapper_has_no_io_assessment_or_locator_resolution(normalizer, monkeypatch):
    import socket
    import subprocess
    def deny(*args, **kwargs): raise AssertionError("Unexpected side effect")
    monkeypatch.setattr(Path, "open", deny)
    monkeypatch.setattr(socket, "create_connection", deny)
    monkeypatch.setattr(subprocess, "run", deny)
    monkeypatch.setattr(workflow_decision, "assess", deny)
    event = envelope()
    event["evidence_reference"] = "https://fixture.invalid/must-not-fetch"
    assert call(normalizer, event)["mapping_status"] == "mapped"


def test_unexpected_runtime_error_propagates(normalizer, monkeypatch):
    def fail(*args, **kwargs): raise RuntimeError("implementation defect")
    monkeypatch.setattr(normalizer, "load_json", fail)
    with pytest.raises(RuntimeError): call(normalizer)


@pytest.mark.parametrize("case,reason", [("missing_context", "MISSING_CONTEXT"),
    ("unknown_identity", "UNSUPPORTED_EVENT"), ("path_and_provider", "PATH_BINDING_MISMATCH")])
def test_overlapping_defect_precedence(normalizer, case, reason):
    event, supplied = envelope(), context()
    if case == "missing_context":
        event["payload"], supplied = {}, {}
    elif case == "unknown_identity":
        event["provider"], event["payload"] = "unknown", None
    else:
        supplied["provider"], supplied["changed_paths"] = "codex", ["other.md"]
    assert call(normalizer, event, supplied)["reason_codes"] == [reason]
