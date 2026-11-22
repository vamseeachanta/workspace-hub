"""Snapshot adapter contract; numeric examples are independently tallied below."""

from __future__ import annotations

import ast
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

import pytest

MODULE = Path(__file__).resolve().parents[2] / "scripts/readiness/ecosystem_doctor.py"
GROUPS = (
    "repositories", "providers", "machines", "schedules", "skills", "memory",
    "privacy", "business_outcomes",
)


def doctor():
    spec = importlib.util.spec_from_file_location("ecosystem_doctor", MODULE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def healthy():
    # Hand tally: two declared, configured, present, complete repositories;
    # none missing, non-Git, unexpected or incomplete. Version per producer v1.
    return {
        "schema_version": 1,
        "repositories": [{"name": "suppressed-marker"}],
        "summary": {
            "declared": 2, "configured": 2, "present": 2,
            "observed_declared": 2, "missing": 0, "non_git": 0,
            "contract_complete": 2, "unexpected_count": 0, "unknown": 0,
            "adapter_coverage": {"complete": 2, "incomplete": 0},
        },
    }


def incomplete():
    # Hand tally: four declared = two present + one missing + one non-Git;
    # one complete leaves three incomplete; one extra repository is undeclared.
    return {
        "schema_version": 1,
        "summary": {
            "declared": 4, "configured": 3, "present": 2,
            "observed_declared": 2, "missing": 1, "non_git": 1,
            "contract_complete": 1, "unexpected_count": 1, "unknown": 1,
            "adapter_coverage": {"complete": 1, "incomplete": 3},
        },
    }


def invoke(path, as_json):
    command = [sys.executable, str(MODULE), "--inventory", str(path)]
    if as_json:
        command.append("--json")
    return subprocess.run(command, capture_output=True, text=True, check=False)


def test_doctor_inventory_healthy():
    result = doctor().normalize_repository_inventory(healthy())
    assert result == {
        "group": "repositories", "status": "healthy",
        "reason_code": "inventory_complete",
        "counts": {
            "declared": 2, "configured": 2, "present": 2, "missing": 0,
            "non_git": 0, "contract_complete": 2, "contract_incomplete": 0,
            "unexpected_count": 0,
        },
    }


def test_doctor_inventory_incomplete():
    result = doctor().normalize_repository_inventory(incomplete())
    assert result == {
        "group": "repositories", "status": "degraded",
        "reason_code": "inventory_incomplete",
        "counts": {
            "declared": 4, "configured": 3, "present": 2, "missing": 1,
            "non_git": 1, "contract_complete": 1, "contract_incomplete": 3,
            "unexpected_count": 1,
        },
    }


@pytest.mark.parametrize("snapshot", [None, {}, [], "suppressed-marker", True])
def test_doctor_rejects_invalid_shapes(snapshot):
    result = doctor().normalize_repository_inventory(snapshot)
    assert result["status"] == "unavailable"
    assert result["counts"] == {}
    assert "suppressed-marker" not in json.dumps(result)


@pytest.mark.parametrize("field", list(healthy()["summary"]))
def test_doctor_requires_complete_summary(field):
    snapshot = healthy()
    del snapshot["summary"][field]
    assert doctor().normalize_repository_inventory(snapshot)["status"] == "unavailable"


@pytest.mark.parametrize("value", [-1, True, 2.0, "suppressed-marker", None, {}, []])
def test_doctor_rejects_non_counts(value):
    snapshot = healthy()
    snapshot["summary"]["configured"] = value
    result = doctor().normalize_repository_inventory(snapshot)
    assert result["status"] == "unavailable"
    assert result["counts"] == {}


@pytest.mark.parametrize("field,value", [
    ("declared", 3), ("present", 3), ("observed_declared", 3),
    ("contract_complete", 3), ("unknown", 1),
    ("adapter_coverage", {"complete": 1, "incomplete": 1}),
    ("adapter_coverage", {"complete": 2, "incomplete": True}),
])
def test_doctor_rejects_inconsistent_counts(field, value):
    # Every mutation contradicts the independent two-repository tally above.
    snapshot = healthy()
    snapshot["summary"][field] = value
    assert doctor().normalize_repository_inventory(snapshot)["status"] == "unavailable"


@pytest.mark.parametrize("version", [None, True, 1.0, 2])
def test_doctor_rejects_unsupported_version(version):
    snapshot = healthy()
    snapshot["schema_version"] = version
    result = doctor().normalize_repository_inventory(snapshot)
    assert result["status"] == "unavailable"
    assert result["reason_code"] == "snapshot_unsupported"


def test_doctor_empty_is_not_healthy():
    # Empty population: every count is zero; absence establishes no coverage.
    snapshot = healthy()
    snapshot["summary"] = dict.fromkeys(snapshot["summary"], 0)
    snapshot["summary"]["adapter_coverage"] = {"complete": 0, "incomplete": 0}
    result = doctor().normalize_repository_inventory(snapshot)
    assert result["status"] == "unavailable"
    assert result["reason_code"] == "inventory_empty"


@pytest.mark.parametrize("payload", [None, b'{"suppressed-marker":', b'\xff',
                                      b'{"schema_version":1,"schema_version":1}',
                                      b'{"extra":NaN}', b'[]'])
def test_doctor_unavailable_is_explicit(tmp_path, payload):
    path = tmp_path / "suppressed-marker.json"
    if payload is not None:
        path.write_bytes(payload)
    for as_json in (False, True):
        completed = invoke(path, as_json)
        assert completed.returncode != 0
        assert "unavailable" in completed.stdout
        assert "healthy" not in completed.stdout
        assert "suppressed-marker" not in completed.stdout + completed.stderr
        assert str(tmp_path) not in completed.stdout + completed.stderr
        assert completed.stderr == ""
        if as_json:
            result = json.loads(completed.stdout)
            assert result["probes"][0]["counts"] == {}
            assert result["probes"][0]["reason_code"] in {
                "snapshot_missing", "snapshot_malformed",
            }


@pytest.mark.parametrize("fixture", [healthy, incomplete])
def test_doctor_formats_agree(tmp_path, fixture):
    path = tmp_path / "inventory.json"
    path.write_text(json.dumps(fixture()), encoding="utf-8")
    human = invoke(path, False)
    structured = invoke(path, True)
    result = json.loads(structured.stdout)
    assert result["schema_version"] == 1  # See ecosystem_doctor.md, result v1.
    assert result["status"] == "unavailable"
    assert human.returncode == structured.returncode != 0
    assert "overall: " + result["status"] in human.stdout
    assert tuple(probe["group"] for probe in result["probes"]) == GROUPS
    for probe in result["probes"]:
        assert f"{probe['group']}: {probe['status']} ({probe['reason_code']})" in human.stdout
    assert all(probe["status"] == "unavailable" for probe in result["probes"][1:])
    assert "suppressed-marker" not in human.stdout + structured.stdout
    assert human.stdout == invoke(path, False).stdout
    assert structured.stdout == invoke(path, True).stdout


def test_doctor_does_not_mutate(tmp_path):
    module = doctor()
    snapshot = healthy()
    snapshot["summary"]["untrusted"] = "suppressed-marker"
    before = copy.deepcopy(snapshot)
    module.normalize_repository_inventory(snapshot)
    assert snapshot == before
    path = tmp_path / "inventory.json"
    path.write_text(json.dumps(snapshot), encoding="utf-8")
    source_before = {p.name: p.read_bytes() for p in tmp_path.iterdir()}
    for as_json in (False, True):
        assert invoke(path, as_json).returncode != 0
        assert {p.name: p.read_bytes() for p in tmp_path.iterdir()} == source_before


def test_doctor_has_no_collectors():
    # Review guard: production dependencies are restricted to parsing/rendering.
    tree = ast.parse(MODULE.read_text(encoding="utf-8"))
    allowed = {"__future__", "argparse", "json", "pathlib"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            assert all(alias.name in allowed for alias in node.names)
        if isinstance(node, ast.ImportFrom):
            assert node.module in allowed
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            assert node.func.id not in {"eval", "exec", "__import__", "compile"}


def test_doctor_missing_argument_is_unavailable(capsys):
    module = doctor()
    assert module.main(["--json"]) != 0
    result = json.loads(capsys.readouterr().out)
    assert result["probes"][0] == {
        "group": "repositories", "status": "unavailable",
        "reason_code": "snapshot_missing", "counts": {},
    }


def test_doctor_unreadable_is_sanitized(tmp_path):
    for as_json in (False, True):
        completed = invoke(tmp_path, as_json)
        assert completed.returncode != 0
        assert "snapshot_unreadable" in completed.stdout
        assert str(tmp_path) not in completed.stdout + completed.stderr
        assert completed.stderr == ""


def test_doctor_argument_errors_are_sanitized(capsys):
    with pytest.raises(SystemExit) as raised:
        doctor().main(["--suppressed-marker"])
    assert raised.value.code != 0
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == "Invalid arguments; use --help for usage.\n"


def test_doctor_human_includes_json_counts(tmp_path):
    path = tmp_path / "inventory.json"
    path.write_text(json.dumps(incomplete()), encoding="utf-8")
    result = json.loads(invoke(path, True).stdout)
    human = invoke(path, False).stdout
    for key, value in result["probes"][0]["counts"].items():
        assert f"{key}={value}" in human


def test_doctor_allows_configured_superset():
    snapshot = healthy()
    # Producer counts configured independently: the two declared plus one extra.
    snapshot["summary"]["configured"] = 3
    assert doctor().normalize_repository_inventory(snapshot)["status"] == "healthy"
