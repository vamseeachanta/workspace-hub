"""Synthetic readiness examples; no private records or live service access."""
import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest
from operations.personal_operations import REQUIREMENTS, evaluate, render_html

AS_OF = "2030-06-01T12:00:00Z"
ROOT = Path(__file__).resolve().parents[2]


def evidence(result="pass"):
    return {
        "result": result,
        "reference": "evidence-example",
        "checked_at": "2030-06-01T11:00:00Z",
        "valid_until": "2030-06-02T11:00:00Z",
    }


def portfolio():
    return {domain: {
        "state": "complete",
        "checks": {name: evidence() for name in (*checks, "terminal")},
    } for domain, checks in REQUIREMENTS.items()}


def test_complete_by_hand():
    """Issue 3609: each of three domains needs a surface and terminal state.

    Hand evaluation: every required check passes during its declared interval;
    every state is complete with terminal evidence, hence three COMPLETE rows.
    The fixture times and quantities are synthetic inputs, not acceptance limits.
    """
    rows = evaluate(portfolio(), AS_OF)
    assert [row["status"] for row in rows] == ["COMPLETE"] * 3
    assert all(not row["gaps"] for row in rows)


def test_missing_domains_are_not_evaluated():
    rows = evaluate({}, AS_OF)
    assert [row["domain"] for row in rows] == ["travel", "media", "workspace"]
    assert all(row["status"] == "NOT_EVALUATED" for row in rows)


@pytest.mark.parametrize("domain", REQUIREMENTS)
def test_every_required_check_is_needed(domain):
    for name in (*REQUIREMENTS[domain], "terminal"):
        data = portfolio()
        del data[domain]["checks"][name]
        row = next(row for row in evaluate(data, AS_OF) if row["domain"] == domain)
        assert row["status"] == "NOT_EVALUATED"
        assert name in row["gaps"]


def test_worked_example_by_hand():
    """Pass+complete => COMPLETE; fail => BLOCKED; absent => NOT_EVALUATED.

    No averaging: one blocked domain cannot be hidden by a completed domain.
    Example source: synthetic truth table in the accompanying user guide.
    """
    data = json.loads((ROOT / "examples/operations-evidence.json").read_text())
    assert [row["status"] for row in evaluate(data, AS_OF)] == [
        "COMPLETE", "BLOCKED", "NOT_EVALUATED",
    ]


@pytest.mark.parametrize("result,status", [("fail", "BLOCKED"), ("unknown", "NOT_EVALUATED")])
def test_failed_and_unknown_evidence(result, status):
    data = portfolio()
    data["media"]["checks"]["integrity"]["result"] = result
    assert evaluate(data, AS_OF)[1]["status"] == status


def test_active_does_not_claim_terminal_completion():
    data = portfolio()
    data["travel"]["state"] = "active"
    del data["travel"]["checks"]["terminal"]
    assert evaluate(data, AS_OF)[0]["status"] == "ACTIVE"


@pytest.mark.parametrize("field,value", [
    ("checked_at", "2030-06-01T12:00:01Z"),
    ("valid_until", AS_OF),
    ("valid_until", "2030-05-31T12:00:00Z"),
])
def test_stale_or_future_observations_are_unknown(field, value):
    data = portfolio()
    data["travel"]["checks"]["surface"][field] = value
    assert evaluate(data, AS_OF)[0]["status"] == "NOT_EVALUATED"


def test_timezone_offsets_compare_instants():
    data = portfolio()
    data["travel"]["checks"]["surface"]["checked_at"] = "2030-06-01T13:00:00+02:00"
    assert evaluate(data, AS_OF)[0]["status"] == "COMPLETE"


@pytest.mark.parametrize("mutation", [
    lambda d: d.update(unexpected={}),
    lambda d: d["travel"].update(notes="private text"),
    lambda d: d["travel"].update(state="closed"),
    lambda d: d["travel"]["checks"].update(unexpected=evidence()),
    lambda d: d["travel"]["checks"]["surface"].update(result=True),
    lambda d: d["travel"]["checks"]["surface"].update(reference="https://private.invalid"),
    lambda d: d["travel"]["checks"]["surface"].update(checked_at="2030-06-01"),
    lambda d: d["travel"]["checks"]["surface"].update(notes="private text"),
    lambda d: d.update(travel=[]),
])
def test_rejects_malformed_or_free_text_inputs(mutation):
    data = copy.deepcopy(portfolio())
    mutation(data)
    with pytest.raises(ValueError):
        evaluate(data, AS_OF)


def test_render_does_not_expose_evidence_references():
    data = portfolio()
    data["travel"]["checks"]["surface"]["reference"] = "evidence-sensitive"
    page = render_html(evaluate(data, AS_OF), AS_OF)
    assert "evidence-sensitive" not in page
    assert "COMPLETE" in page
    assert "self-reported" in page


def test_cli_writes_surface_and_returns_incomplete(tmp_path):
    output = tmp_path / "surface.html"
    run = subprocess.run([
        sys.executable, str(ROOT / "scripts/operations/personal_operations.py"),
        str(ROOT / "examples/operations-evidence.json"), "--as-of", AS_OF,
        "--output", str(output),
    ], capture_output=True, text=True, check=False)
    assert run.returncode == 1
    assert "BLOCKED" in output.read_text()
    assert not run.stderr


@pytest.mark.parametrize("raw", [
    '{"travel": {}, "travel": {}}',
    '{"travel": NaN}',
    '{"travel": "sensitive content"}',
])
def test_cli_errors_do_not_echo_input(tmp_path, raw):
    source = tmp_path / "input.json"
    source.write_text(raw)
    run = subprocess.run([
        sys.executable, str(ROOT / "scripts/operations/personal_operations.py"),
        str(source), "--as-of", AS_OF,
    ], capture_output=True, text=True, check=False)
    assert run.returncode == 2
    assert run.stderr == "Invalid input or inaccessible file.\n"
    assert not run.stdout


def test_criteria_match_documented_contract():
    assert REQUIREMENTS == {
        "travel": ("surface", "parameters", "cost_basis", "decision"),
        "media": ("surface", "extraction", "integrity", "offsite", "sync_decision"),
        "workspace": ("surface", "boundary", "membership", "isolation"),
    }


def test_html_records_assessment_time():
    page = render_html(evaluate({}, AS_OF), AS_OF)
    assert AS_OF.replace("Z", "+00:00") in page
    assert "Revision history" in page


@pytest.mark.parametrize("target", ["input", "existing"])
def test_cli_never_overwrites_records(tmp_path, target):
    source = tmp_path / "input.json"
    source.write_text(json.dumps(portfolio()))
    output = source if target == "input" else tmp_path / "existing.html"
    if target == "existing":
        output.write_text("retained report")
    before = output.read_bytes()
    run = subprocess.run([
        sys.executable, str(ROOT / "scripts/operations/personal_operations.py"),
        str(source), "--as-of", AS_OF, "--output", str(output),
    ], capture_output=True, text=True, check=False)
    assert run.returncode == 2
    assert output.read_bytes() == before


def test_cli_complete_json_and_input_preservation(tmp_path):
    source = tmp_path / "input.json"
    source.write_text(json.dumps(portfolio()))
    before = source.read_bytes()
    run = subprocess.run([
        sys.executable, str(ROOT / "scripts/operations/personal_operations.py"),
        str(source), "--as-of", AS_OF,
    ], capture_output=True, text=True, check=False)
    assert run.returncode == 0
    payload = json.loads(run.stdout)
    assert payload["basis"] == "self-reported"
    assert payload["as_of"] == "2030-06-01T12:00:00+00:00"
    assert payload["criteria"] == "personal-operations-evidence-v1"
    assert all(row["status"] == "COMPLETE" for row in payload["domains"])
    assert source.read_bytes() == before


@pytest.mark.parametrize("as_of", ["invalid", "2030-06-01", "2030-06-01T12:00:00"])
def test_assessment_requires_an_instant(as_of):
    with pytest.raises(ValueError):
        evaluate({}, as_of)


def test_failed_optional_terminal_identifies_blocker():
    data = portfolio()
    data["travel"]["state"] = "active"
    data["travel"]["checks"]["terminal"]["result"] = "fail"
    row = evaluate(data, AS_OF)[0]
    assert row["status"] == "BLOCKED"
    assert "terminal" in row["gaps"]
