"""Synthetic freshness examples; seconds are direct timestamp subtraction.

At 00:01:00, age of 00:00:00 = 60 seconds; an input limit of 60 passes.
At 00:01:01 age = 61 seconds, which exceeds 60. No operational limit is assumed.
"""
import importlib.util
import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

import pytest
import yaml
from readiness import repo_hygiene as sync
from test_repo_sync import payload

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("matrix_hygiene", ROOT / "scripts/readiness/build-equality-matrix.py")
matrix = importlib.util.module_from_spec(spec)
spec.loader.exec_module(matrix)


@pytest.mark.parametrize("seconds, expected", [(60, "HYGIENE-OK"), (61, "HYGIENE-STALE"), (-1, "HYGIENE-STALE")])
def test_age_boundaries(seconds, expected):
    from datetime import timedelta
    now = datetime(2026, 1, 1, tzinfo=UTC) + timedelta(seconds=seconds)
    assert sync.verdict(payload(), now) == expected


@pytest.mark.parametrize("status, expected", [("dirty", "HYGIENE-DIRTY"), ("wedged", "HYGIENE-WEDGED"),
    ("busy", "HYGIENE-BLOCKED"), ("fetch_failed", "HYGIENE-BLOCKED")])
def test_current_failure_overrides_prior_success(status, expected):
    data = payload()
    data["repos"][0].update(status=status, dirty=status == "dirty", wedged=status == "wedged")
    assert sync.verdict(data, datetime(2026, 1, 1, tzinfo=UTC)) == expected


def test_matrix_routes_and_renders_hygiene(tmp_path, monkeypatch):
    data = payload()
    data["observed_at"] = data["repos"][0]["last_success_at"] = datetime.now(UTC).isoformat()
    report = {"provenance": {"dirty": False, "behind_main": 0, "ahead_main": 0, "origin_ref_age_h": 0},
              "dimensions": {"repo_hygiene": data}}
    roster = {"node": {"status": "active"}}
    assert matrix.verdict_for("repo_hygiene", "node", {"node": report}, {}, roster, []) == "HYGIENE-OK"
    assert "repo_hygiene" in matrix.DISPLAY_DIMS
    assert matrix.rollup_verdict(["HYGIENE-OK"]) == ("OK", "ok")
    assert matrix.remediate("repo_hygiene", "HYGIENE-WEDGED") is not None
    assert matrix.remediate("repo_hygiene", "HYGIENE-OK") is None
    detail = matrix.hygiene_details({"dimensions": {"repo_hygiene": payload()}},
                                    datetime(2026, 1, 1, 0, 1, tzinfo=UTC))
    assert "repo-a" in detail and "synced" in detail and "60.0s" in detail
    data["repos"][0]["id"] = "<script>"
    assert "<script>" not in matrix.hygiene_details(report)


def test_attach_includes_allowlisted_status_in_publishable_evidence(tmp_path):
    state = tmp_path / "status.json"
    data = payload()
    data["private"] = str(tmp_path)
    state.write_text(json.dumps(data))
    output = tmp_path / "equality.yaml"
    result = subprocess.run([sys.executable, str(ROOT / "scripts/readiness/repo_hygiene.py"),
        "--attach-equality", "--state", str(state), "--output", str(output)],
        input="schema_version: 4\ndimensions: {}\n", text=True, check=False, capture_output=True)
    assert result.returncode == 0, result.stderr
    assert yaml.safe_load(output.read_text())["dimensions"]["repo_hygiene"] == payload()
    assert str(tmp_path) not in output.read_text()


def test_attach_missing_status_never_claims_health(tmp_path):
    output = tmp_path / "equality.yaml"
    result = subprocess.run([sys.executable, str(ROOT / "scripts/readiness/repo_hygiene.py"),
        "--attach-equality", "--state", str(tmp_path / "absent"), "--output", str(output)],
        input="schema_version: 4\ndimensions: {}\n", text=True, check=False, capture_output=True)
    assert result.returncode == 0
    assert yaml.safe_load(output.read_text())["dimensions"]["repo_hygiene"] is None


def test_standalone_builder_without_optional_hygiene_module_fails_closed(tmp_path):
    directory = tmp_path / "scripts" / "readiness"
    directory.mkdir(parents=True)
    script = directory / "build-equality-matrix.py"
    script.write_text((ROOT / "scripts/readiness/build-equality-matrix.py").read_text())
    (directory / "harness-config.yaml").write_text("workstations: {node: {status: active}}\n")
    result = subprocess.run([sys.executable, str(script), "--json"],
                            check=False, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["node"]["repo_hygiene"] == "MISSING-EVIDENCE"


@pytest.mark.parametrize("report", [None, [], {"dimensions": None}, {"dimensions": []}])
def test_malformed_report_detail_is_empty(report):
    assert matrix.hygiene_details(report) == ""
