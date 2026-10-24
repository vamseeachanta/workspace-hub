"""Offline composition regressions for issue #3849 (2026).

All numbers are synthetic inputs, not engineering acceptance limits. The domain
is a rectangle with corners (0,0), (2,0), (2,3), (0,3), in arbitrary units.
Independent criterion calculation: 2 + 3 = 5, which lies in [4,6]. Moving the
left boundary to -1 or the upper boundary to 4 changes the complete domain even
if a separate loaded-edge check still passes. Event numbers express order only.
"""

import copy
import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "scripts/solver/verification_composition.py"
spec = importlib.util.spec_from_file_location("verification_composition", SCRIPT)
api = importlib.util.module_from_spec(spec)
spec.loader.exec_module(api)


def encode(value):
    return json.dumps(value, allow_nan=False).encode()


def digest(value):
    return hashlib.sha256(value).hexdigest()


@pytest.fixture
def case():
    source = b"synthetic model input\n"
    domain = {"unit": "arbitrary", "nodes": [[0, 0], [2, 0], [2, 3], [0, 3]],
              "cells": [[0, 1, 2, 3]]}
    requirements = {
        "input_sha256": digest(source), "evidence_sha256": "",
        "evidence_kind": "synthetic", "domain": domain,
        "settings": {"shape_check": "default", "limit": "specified"},
        "criterion": {"source": "Independent hand calculation: 2 + 3 = 5 in [4,6]",
                      "result_id": "sum", "quantity": "sum", "unit": "arbitrary",
                      "minimum": 4, "maximum": 6},
    }
    evidence = {
        "input_sha256": digest(source), "evidence_kind": "synthetic",
        "domain": copy.deepcopy(domain),
        "settings_history": [{"event": 1, "source": "Synthetic current snapshot",
                              "values": copy.deepcopy(requirements["settings"])}],
        "result": {"event": 3, "settings_event": 1, "result_id": "sum",
                   "quantity": "sum", "unit": "arbitrary", "value": 5},
    }
    return requirements, source, evidence


def evaluate(case):
    requirements, source, evidence = case
    raw = encode(evidence)
    requirements["evidence_sha256"] = digest(raw)
    return api.compose(requirements, source, raw)


def test_complete_content_match_does_not_qualify_model(case):
    report = evaluate(case)
    assert report["content_status"] == "PASS"
    assert set(report["checks"].values()) == {"PASS"}
    assert report["whole_model_readiness"] == "NOT_EVALUATED"
    assert report["provenance"] == "independently_unverified"
    assert report["evidence_kind"] == "synthetic"


@pytest.mark.parametrize("corner,axis,value", [(0, 0, -1), (3, 1, 4)])
def test_full_domain_not_just_loaded_boundary(case, corner, axis, value):
    case[2]["domain"]["nodes"][corner][axis] = value
    assert evaluate(case)["checks"]["domain"] == "FAIL"


def test_topology_and_extra_domain_data_cannot_be_ignored(case):
    case[2]["domain"]["cells"] = [[0, 1, 3, 2]]
    assert evaluate(case)["checks"]["domain"] == "FAIL"
    case[2]["domain"] = copy.deepcopy(case[0]["domain"])
    case[2]["domain"]["extra_region"] = "unintended"
    assert evaluate(case)["checks"]["domain"] == "FAIL"


def test_later_modified_settings_override_earlier_default(case):
    case[2]["settings_history"].append(
        {"event": 2, "source": "Synthetic modified snapshot",
         "values": {"shape_check": "modified", "limit": "specified"}})
    report = evaluate(case)
    assert report["checks"]["settings"] == "FAIL"
    assert report["checks"]["criterion"] == "PASS"


def test_result_must_bind_latest_applicable_snapshot(case):
    snapshot = copy.deepcopy(case[2]["settings_history"][0])
    snapshot["event"] = 2
    case[2]["settings_history"].append(snapshot)
    assert evaluate(case)["checks"]["settings"] == "FAIL"
    case[2]["result"]["settings_event"] = 2
    assert evaluate(case)["checks"]["settings"] == "PASS"


def test_future_settings_do_not_govern_earlier_result(case):
    case[2]["settings_history"].append(
        {"event": 4, "source": "Later snapshot", "values": {"shape_check": "modified"}})
    assert evaluate(case)["checks"]["settings"] == "PASS"


@pytest.mark.parametrize("change", ["duplicate", "unordered", "same_event", "bool_event"])
def test_ambiguous_settings_order_rejected(case, change):
    snapshot = copy.deepcopy(case[2]["settings_history"][0])
    if change == "duplicate":
        case[2]["settings_history"].append(snapshot)
    elif change == "unordered":
        snapshot["event"] = 0
        case[2]["settings_history"].append(snapshot)
    elif change == "same_event":
        case[2]["result"]["event"] = 1
    else:
        case[2]["settings_history"][0]["event"] = True
    assert evaluate(case)["checks"]["settings"] == "FAIL"


@pytest.mark.parametrize("field", ["domain", "settings_history", "result"])
def test_missing_evidence_not_evaluated(case, field):
    del case[2][field]
    assert evaluate(case)["content_status"] == "NOT_EVALUATED"


@pytest.mark.parametrize("field", ["domain", "settings", "criterion"])
def test_missing_requirement_not_evaluated(case, field):
    del case[0][field]
    assert evaluate(case)["content_status"] == "NOT_EVALUATED"


def test_stale_bytes_and_mismatched_source_binding(case):
    requirements, source, evidence = case
    raw = encode(evidence)
    requirements["evidence_sha256"] = digest(raw)
    assert api.compose(requirements, source + b"changed", raw)["checks"]["binding"] == "FAIL"
    assert api.compose(requirements, source, raw + b" ")["checks"]["binding"] == "FAIL"
    evidence["input_sha256"] = "0" * 64
    assert evaluate(case)["checks"]["binding"] == "FAIL"


@pytest.mark.parametrize("kind", ["native", "unknown", "Synthetic"])
def test_labels_cannot_be_promoted_or_mixed(case, kind):
    case[2]["evidence_kind"] = kind
    assert evaluate(case)["checks"]["binding"] == "FAIL"


def test_native_content_match_still_unverified(case):
    case[0]["evidence_kind"] = case[2]["evidence_kind"] = "native"
    report = evaluate(case)
    assert report["content_status"] == "PASS"
    assert report["whole_model_readiness"] == "NOT_EVALUATED"
    assert report["provenance"] == "independently_unverified"


@pytest.mark.parametrize("value,status", [(4, "PASS"), (6, "PASS"), (0, "FAIL"),
                                          (7, "FAIL"), (True, "FAIL"), ("5", "FAIL")])
def test_explicit_inclusive_criterion(case, value, status):
    case[2]["result"]["value"] = value
    assert evaluate(case)["checks"]["criterion"] == status


@pytest.mark.parametrize("field,value", [("unit", "other"), ("quantity", "other"),
                                         ("result_id", "other")])
def test_criterion_bound_to_specific_quantity(case, field, value):
    case[2]["result"][field] = value
    assert evaluate(case)["checks"]["criterion"] == "FAIL"


def test_zero_is_valid_and_absent_limit_never_defaults(case):
    case[0]["criterion"].update(minimum=0, maximum=0)
    case[2]["result"]["value"] = 0
    assert evaluate(case)["checks"]["criterion"] == "PASS"
    del case[0]["criterion"]["maximum"]
    assert evaluate(case)["checks"]["criterion"] == "NOT_EVALUATED"


@pytest.mark.parametrize("raw", [b'{"x":1,"x":2}', b'{"x":NaN}', b'{"x":1e999}', b'[]'])
def test_strict_json_rejects_ambiguous_or_nonfinite_records(raw):
    with pytest.raises((ValueError, TypeError)):
        api.read_record(raw)


def test_diagnostics_survive_binding_failure(case):
    case[0]["input_sha256"] = "0" * 64
    report = evaluate(case)
    assert report["content_status"] == "FAIL"
    assert report["checks"]["criterion"] == "PASS"


def test_worked_example_cli():
    root = SCRIPT.parents[2]
    folder = root / "docs/solver/examples/verification-composition"
    process = subprocess.run(
        [sys.executable, str(SCRIPT), str(folder / "requirements.json"),
         str(folder / "input.txt"), str(folder / "evidence.json")],
        capture_output=True, text=True, check=False)
    assert process.returncode == 0, process.stderr
    report = json.loads(process.stdout)
    assert report["content_status"] == "PASS"
    assert report["whole_model_readiness"] == "NOT_EVALUATED"


def test_cli_parse_failure_does_not_echo_input(tmp_path):
    invalid = tmp_path / "invalid.json"
    invalid.write_text('{"private_payload":', encoding="utf-8", newline="\n")
    process = subprocess.run([sys.executable, str(SCRIPT), str(invalid), str(invalid),
                              str(invalid)], capture_output=True, text=True, check=False)
    assert process.returncode == 2
    assert "private_payload" not in process.stderr
    assert "invalid.json" not in process.stderr


def test_unrecognized_evidence_label_is_not_echoed(case):
    case[2]["evidence_kind"] = "untrusted input label"
    report = evaluate(case)
    assert report["evidence_kind"] == "unknown"
    assert "untrusted input label" not in json.dumps(report)


@pytest.mark.parametrize("field", ["input_sha256", "evidence_sha256", "evidence_kind"])
def test_missing_binding_requirement_is_not_evaluated(case, field):
    raw = encode(case[2])
    case[0]["evidence_sha256"] = digest(raw)
    del case[0][field]
    assert api.compose(case[0], case[1], raw)["checks"]["binding"] == "NOT_EVALUATED"


@pytest.mark.parametrize("field,value", [("source", ""), ("minimum", True),
                                         ("minimum", 7), ("maximum", "6")])
def test_invalid_criterion_never_passes(case, field, value):
    case[0]["criterion"][field] = value
    assert evaluate(case)["checks"]["criterion"] == "FAIL"


def test_no_snapshot_before_result_is_not_evaluated(case):
    case[2]["settings_history"][0]["event"] = 4
    assert evaluate(case)["checks"]["settings"] == "NOT_EVALUATED"


def test_settings_are_complete_not_default_filled(case):
    del case[2]["settings_history"][0]["values"]["limit"]
    assert evaluate(case)["checks"]["settings"] == "FAIL"


def test_json_type_difference_cannot_compare_equal(case):
    case[0]["settings"]["enabled"] = True
    case[2]["settings_history"][0]["values"]["enabled"] = 1
    assert evaluate(case)["checks"]["settings"] == "FAIL"
    case[2]["domain"]["nodes"][0][0] = False
    assert evaluate(case)["checks"]["domain"] == "FAIL"


@pytest.mark.parametrize("field", ["domain", "settings_history", "result"])
@pytest.mark.parametrize("value", [None, [], "unknown", True])
def test_malformed_sections_fail_closed(case, field, value):
    case[2][field] = value
    assert evaluate(case)["content_status"] != "PASS"


def test_object_key_order_does_not_change_content_comparison(case):
    case[2]["domain"] = dict(reversed(list(case[2]["domain"].items())))
    assert evaluate(case)["checks"]["domain"] == "PASS"


def test_nested_duplicate_json_keys_rejected():
    with pytest.raises(ValueError):
        api.read_record(b'{"domain":{"node":1,"node":2}}')


def test_cli_nonpassing_content_exit(case, tmp_path):
    requirements, source, evidence = case
    evidence["domain"]["nodes"][0][0] = -1
    raw = encode(evidence)
    requirements["evidence_sha256"] = digest(raw)
    paths = [tmp_path / name for name in ("requirements.json", "input.txt", "evidence.json")]
    for path, payload in zip(paths, (encode(requirements), source, raw)):
        path.write_bytes(payload)
    process = subprocess.run([sys.executable, str(SCRIPT), *map(str, paths)],
                             capture_output=True, text=True, check=False)
    assert process.returncode == 1
    assert json.loads(process.stdout)["checks"]["domain"] == "FAIL"


@pytest.mark.parametrize("section,old,new,check", [
    ("result", b'"value": 5', b'"value": 6.0000000000000001', "criterion"),
    ("result", b'"value": 5', b'"value": 3.9999999999999999', "criterion"),
    ("domain", b'[2.0, 0]', b'[2.0000000000000001, 0]', "domain"),
    ("settings", b'"precision": 2.0', b'"precision": 2.0000000000000001', "settings"),
])
def test_decimal_evidence_is_not_rounded(case, section, old, new, check):
    # Hand comparisons: 6 + 10^-16 > 6; 4 - 10^-16 < 4;
    # 2 + 10^-16 != 2. These differences must survive JSON decoding.
    requirements, source, evidence = case
    if section == "domain":
        requirements["domain"]["nodes"][1][0] = 2.0
        evidence["domain"]["nodes"][1][0] = 2.0
    elif section == "settings":
        requirements["settings"]["precision"] = 2.0
        evidence["settings_history"][0]["values"]["precision"] = 2.0
    raw = encode(evidence)
    assert old in raw
    raw = raw.replace(old, new)
    requirements["evidence_sha256"] = digest(raw)
    report = api.compose(api.read_record(encode(requirements)), source, raw)
    assert report["checks"]["binding"] == "PASS"
    assert report["checks"][check] == "FAIL"
    assert report["content_status"] == "FAIL"


def test_decimal_requirements_are_not_rounded(case):
    requirements, source, evidence = case
    evidence["result"]["value"] = 6
    raw = encode(evidence)
    requirements["evidence_sha256"] = digest(raw)
    required = encode(requirements).replace(b'"maximum": 6',
                                            b'"maximum": 5.9999999999999999')
    report = api.compose(api.read_record(required), source, raw)
    assert report["checks"]["criterion"] == "FAIL"


def test_exact_decimal_positive_case(case):
    requirements, source, evidence = case
    raw = encode(evidence).replace(b'"value": 5', b'"value": 5.0000000000000001')
    requirements["evidence_sha256"] = digest(raw)
    report = api.compose(api.read_record(encode(requirements)), source, raw)
    assert report["content_status"] == "PASS"


def test_decimal_and_integer_domain_types_remain_distinct(case):
    case[2]["domain"]["nodes"][1][0] = 2.0
    assert evaluate(case)["checks"]["domain"] == "FAIL"


def test_equal_decimal_tokens_and_direct_api_floats(case):
    requirements, source, evidence = case
    requirements["domain"]["nodes"][1][0] = 2.0
    evidence["domain"]["nodes"][1][0] = 2.0
    requirements["criterion"].update(minimum=0.1, maximum=0.1)
    evidence["result"]["value"] = 0.1
    raw = encode(evidence).replace(b'[2.0, 0]', b'[2.000, 0]')
    requirements["evidence_sha256"] = digest(raw)
    assert api.compose(requirements, source, raw)["content_status"] == "PASS"
