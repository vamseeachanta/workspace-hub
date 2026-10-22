"""Evidence bookkeeping tests; all values are synthetic, not design criteria.

Independent hand calculation for the complete fixture: one capability has two
available inputs; four artifacts form geometry -> case -> results -> report;
one pursuit has a terminal outcome and evidence. There are no missing records:
capabilities=1, inputs=2, artifacts=4, pursuits=1, findings=0. Removing one input
record's evidence and its workflow reference creates exactly two findings.
Contract source: docs/gtm/delivery-readiness.md, Contract v1 (2026).
Digest and version literals describe that contract; counts are hand-calculated
synthetic examples. No engineering constants are used.
"""
from __future__ import annotations

import copy
import importlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "delivery_readiness.py"
EXAMPLE = SCRIPT.parents[1].parent / "docs/gtm/examples/delivery-readiness.json"


@pytest.fixture
def module():
    return importlib.import_module("gtm.delivery_readiness")


@pytest.fixture
def snapshot():
    return {
        "schema_version": 1,
        "capabilities": [{
            "id": "screening",
            "workflow_ref": "methods/screening",
            "criteria_ref": "criteria/synthetic",
            "inputs": [
                {"id": "geometry", "state": "available", "evidence_ref": "evidence/geometry",
                 "acquisition_ref": None},
                {"id": "conditions", "state": "available", "evidence_ref": "evidence/conditions",
                 "acquisition_ref": None},
            ],
        }],
        "artifacts": [
            {"stage": stage, "ref": f"evidence/{stage}", "revision": "example-v1",
             "sha256": digest * 64, "upstream_sha256": upstream * 64 if upstream else None}
            for stage, digest, upstream in [
                ("geometry", "a", None), ("case", "b", "a"),
                ("results", "c", "b"), ("report", "d", "c"),
            ]
        ],
        "pursuits": [{"id": "sample", "state": "won", "evidence_ref": "decisions/sample",
                      "next_action_ref": None}],
    }


def test_complete_records_do_not_claim_engineering_qualification(module, snapshot):
    before = copy.deepcopy(snapshot)
    result = module.evaluate(snapshot)
    assert result["status"] == "RECORDED"
    assert result["engineering_status"] == "NOT_EVALUATED"
    assert result["counts"] == {
        "capabilities": 1, "inputs": 2, "artifacts": 4, "pursuits": 1, "findings": 0,
    }
    assert snapshot == before


@pytest.mark.parametrize("state,status", [("missing", "GAPS"), ("unknown", "NOT_EVALUATED")])
def test_acquisition_gap_remains_visible(module, snapshot, state, status):
    item = snapshot["capabilities"][0]["inputs"][0]
    item.update(state=state, evidence_ref=None, acquisition_ref="requests/geometry")
    result = module.evaluate(snapshot)
    assert result["status"] == status
    assert result["findings"][0]["action_ref"] == "requests/geometry"
    assert result["counts"]["findings"] == 1


def test_available_claim_needs_evidence_and_workflow(module, snapshot):
    """Two omitted independent references yield two findings by enumeration."""
    snapshot["capabilities"][0]["workflow_ref"] = None
    snapshot["capabilities"][0]["inputs"][0]["evidence_ref"] = None
    result = module.evaluate(snapshot)
    assert result["status"] == "NOT_EVALUATED"
    assert result["counts"]["findings"] == 2


def test_missing_criteria_stays_unevaluated(module, snapshot):
    snapshot["capabilities"][0]["criteria_ref"] = None
    assert module.evaluate(snapshot)["capabilities"][0]["status"] == "NOT_EVALUATED"


@pytest.mark.parametrize("stage", ["geometry", "case", "results", "report"])
def test_missing_artifact_blocks_delivery(module, snapshot, stage):
    snapshot["artifacts"] = [a for a in snapshot["artifacts"] if a["stage"] != stage]
    assert module.evaluate(snapshot)["delivery"]["status"] == "GAPS"


@pytest.mark.parametrize("index", [1, 2, 3])
def test_changed_upstream_digest_blocks_delivery(module, snapshot, index):
    snapshot["artifacts"][index]["upstream_sha256"] = "f" * 64
    result = module.evaluate(snapshot)
    assert result["delivery"]["status"] == "GAPS"
    assert any(f["reason"] == "upstream_digest_mismatch" for f in result["findings"])


def test_unknown_dependency_digest_is_not_evaluated(module, snapshot):
    snapshot["artifacts"][2]["upstream_sha256"] = None
    assert module.evaluate(snapshot)["delivery"]["status"] == "NOT_EVALUATED"


@pytest.mark.parametrize("state", ["won", "lost", "declined", "withdrawn"])
def test_terminal_outcomes_require_evidence(module, snapshot, state):
    snapshot["pursuits"][0].update(state=state, evidence_ref=None)
    assert module.evaluate(snapshot)["pursuits"][0]["status"] == "NOT_EVALUATED"
    snapshot["pursuits"][0]["evidence_ref"] = "decisions/sample"
    assert module.evaluate(snapshot)["pursuits"][0]["status"] == "RECORDED"


def test_active_pursuit_is_open_even_with_evidence(module, snapshot):
    snapshot["pursuits"][0].update(state="active", next_action_ref="actions/follow-up")
    result = module.evaluate(snapshot)
    assert result["status"] == "GAPS"
    assert result["findings"][0]["action_ref"] == "actions/follow-up"


def test_known_gap_takes_precedence_over_unknown(module, snapshot):
    snapshot["capabilities"][0]["criteria_ref"] = None
    snapshot["artifacts"] = []
    assert module.evaluate(snapshot)["status"] == "GAPS"


@pytest.mark.parametrize("mutate", [
    lambda d: d.update(schema_version=True),
    lambda d: d.update(schema_version=2),
    lambda d: d.update(capabilities=[]),
    lambda d: d.update(pursuits=[]),
    lambda d: d.update(extra="ignored typo"),
    lambda d: d["capabilities"][0].update(inputs=[]),
    lambda d: d["capabilities"][0]["inputs"][0].update(state="ready"),
    lambda d: d["capabilities"][0]["inputs"][0].pop("acquisition_ref"),
    lambda d: d["capabilities"].append(copy.deepcopy(d["capabilities"][0])),
    lambda d: d["capabilities"][0]["inputs"].append(copy.deepcopy(d["capabilities"][0]["inputs"][0])),
    lambda d: d["artifacts"].append(copy.deepcopy(d["artifacts"][0])),
    lambda d: d["artifacts"][0].update(sha256="invalid"),
    lambda d: d["artifacts"][0].update(upstream_sha256="a" * 64),
    lambda d: d["pursuits"][0].update(state="closed"),
    lambda d: d["pursuits"].append(copy.deepcopy(d["pursuits"][0])),
])
def test_malformed_snapshot_is_rejected(module, snapshot, mutate):
    mutate(snapshot)
    with pytest.raises(module.SnapshotError):
        module.evaluate(snapshot)


@pytest.mark.parametrize("reference", ["../outside", "a/../b", "a//b", "C:\\private", "/absolute",
                                        "https://example.invalid", "evidence/line\nbreak"])
def test_references_are_relative_logical_locators(module, snapshot, reference):
    snapshot["capabilities"][0]["workflow_ref"] = reference
    with pytest.raises(module.SnapshotError):
        module.evaluate(snapshot)


def run_cli(tmp_path, text, *args):
    source = tmp_path / "snapshot.json"
    source.write_text(text, encoding="utf-8")
    return subprocess.run([sys.executable, str(SCRIPT), str(source), *args],
                          capture_output=True, text=True, check=False)


def test_cli_json_and_html(module, snapshot, tmp_path):
    text = json.dumps(snapshot)
    result = run_cli(tmp_path, text)
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == module.evaluate(snapshot)
    result = run_cli(tmp_path, text, "--format", "html")
    assert result.returncode == 0
    assert "<!doctype html>" in result.stdout
    assert "NOT_EVALUATED" in result.stdout
    assert "Revision history" in result.stdout


@pytest.mark.parametrize("text", ['{"schema_version":1,"schema_version":1}', '{"value":NaN}', '[', '[]'])
def test_cli_rejects_bad_json_without_echoing_payload(tmp_path, text):
    result = run_cli(tmp_path, text)
    assert result.returncode == 2
    assert not result.stdout
    assert text not in result.stderr
    assert "Traceback" not in result.stderr


def test_cli_reports_gaps_with_nonzero_exit(snapshot, tmp_path):
    snapshot["artifacts"] = []
    result = run_cli(tmp_path, json.dumps(snapshot))
    assert result.returncode == 1
    assert json.loads(result.stdout)["status"] == "GAPS"


def test_cli_reports_unverified_snapshot_with_nonzero_exit(snapshot, tmp_path):
    snapshot["capabilities"][0]["criteria_ref"] = None
    result = run_cli(tmp_path, json.dumps(snapshot))
    assert result.returncode == 1
    assert json.loads(result.stdout)["status"] == "NOT_EVALUATED"


def test_cli_missing_file_has_sanitized_error(tmp_path):
    source = tmp_path / "absent.json"
    result = subprocess.run([sys.executable, str(SCRIPT), str(source)],
                            capture_output=True, text=True, check=False)
    assert result.returncode == 2
    assert str(source) not in result.stderr
    assert "Traceback" not in result.stderr


def test_worked_example(module):
    """One missing input and one active pursuit give exactly two findings."""
    result = module.evaluate(module.load_snapshot(EXAMPLE))
    assert result["status"] == "GAPS"
    assert result["counts"]["findings"] == 2
    assert result["delivery"]["status"] == "RECORDED"


@pytest.mark.parametrize("field", ["ref", "revision", "sha256"])
def test_missing_artifact_metadata_is_not_evaluated(module, snapshot, field):
    snapshot["artifacts"][0][field] = None
    assert module.evaluate(snapshot)["delivery"]["status"] == "NOT_EVALUATED"


def test_stage_order_is_independent_of_input_order(module, snapshot):
    expected = module.evaluate(snapshot)
    snapshot["artifacts"].reverse()
    assert module.evaluate(snapshot) == expected


def test_html_escapes_submitted_text(module):
    """An untrusted rendering caller cannot introduce active HTML content."""
    rendered = module.render_html({"status": "<script>alert('sample')</script>"})
    assert "<script>" not in rendered
    assert "&lt;script&gt;" in rendered


@pytest.mark.parametrize("mutate", [
    lambda d: d.update(capabilities=None),
    lambda d: d.update(artifacts={}),
    lambda d: d.update(pursuits="sample"),
    lambda d: d["capabilities"].__setitem__(0, []),
    lambda d: d["capabilities"][0].update(id=True),
    lambda d: d["capabilities"][0].update(workflow_ref=[]),
    lambda d: d["capabilities"][0].update(inputs="sample"),
    lambda d: d["capabilities"][0]["inputs"][0].update(state={}),
    lambda d: d["artifacts"][0].update(stage=[]),
    lambda d: d["artifacts"][0].update(sha256=False),
    lambda d: d["artifacts"][0].update(revision=1),
    lambda d: d["pursuits"][0].update(state={}),
])
def test_malformed_field_types_return_sanitized_cli_errors(snapshot, tmp_path, mutate):
    mutate(snapshot)
    result = run_cli(tmp_path, json.dumps(snapshot))
    assert result.returncode == 2
    assert "Traceback" not in result.stderr
    assert not result.stdout


def test_duplicate_nested_json_key_is_rejected(snapshot, tmp_path):
    text = json.dumps(snapshot).replace('"state": "won"', '"state": "won", "state": "lost"')
    result = run_cli(tmp_path, text)
    assert result.returncode == 2
    assert not result.stdout
