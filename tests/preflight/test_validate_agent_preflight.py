"""Portable consumer tests for the agent-preflight/1 producer contract.

All timestamps and age limits are synthetic inputs, not operational defaults.
Hand calculation: 12:05 minus 12:00 = five minutes = 300 seconds. With an
input lifetime of 600 seconds that is current; equality at 12:10 is expired.
The expiry convention follows docs/architecture/agent-data-handling-contract.md
(valid_until > as_of). No probe or installed assistant is invoked by these tests.
"""

import copy
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "scripts/windows/validate-agent-preflight.py"
spec = importlib.util.spec_from_file_location("validate_agent_preflight", SCRIPT)
validator = importlib.util.module_from_spec(spec)


@pytest.fixture(scope="module", autouse=True)
def load_validator():
    spec.loader.exec_module(validator)


def receipt():
    """Minimal evidence from scripts/windows/agent-preflight.ps1, schema /1."""
    return {
        "schema": "agent-preflight/1",
        "generated_at": "2026-10-22T12:00:00.0000000Z",
        "python": {
            "selected": "python.exe", "selected_exists": True, "version": "3.12.0",
            "preferred_encoding": "UTF-8", "venv_cfg_present": None,
        },
        "git": {"path": "git.exe", "version": "git version 2.47.0"},
        "gh": {"path": "gh.exe", "version": "gh version synthetic", "auth_ok": True,
               "auth_status_ok": False},
        "findings": [{"id": "GH_STALE_STORED_ACCOUNT", "severity": "info", "message": "synthetic"}],
    }


def evaluate(data, as_of="2026-10-22T12:05:00Z", lifetime=600, required=("python", "git", "gh")):
    return validator.evaluate(data, as_of=as_of, max_age_seconds=lifetime, required=required)


def test_current_receipt_uses_active_auth_result():
    result = evaluate(receipt())
    assert result["status"] == "ready"
    assert result["age_seconds"] == 300
    assert result["failures"] == []


@pytest.mark.parametrize("as_of,code", [
    ("2026-10-22T12:10:00Z", "RECEIPT_EXPIRED"),
    ("2026-10-22T11:59:59Z", "RECEIPT_FROM_FUTURE"),
])
def test_freshness_boundaries(as_of, code):
    assert code in evaluate(receipt(), as_of=as_of)["failures"]


def test_timezone_offsets_compare_instants():
    assert evaluate(receipt(), as_of="2026-10-22T14:05:00+02:00")["age_seconds"] == 300


@pytest.mark.parametrize("timestamp", [None, "", "2026-10-22", "2026-10-22T12:00:00",
                                      "2026-13-22T12:00:00Z", "2026-10-22 12:00:00Z",
                                      "2026-10-22T12:00:00+00:99", "2026-10-22T12:60:00Z"])
def test_ambiguous_or_invalid_probe_time_is_rejected(timestamp):
    data = receipt()
    data["generated_at"] = timestamp
    with pytest.raises(ValueError):
        evaluate(data)


@pytest.mark.parametrize("lifetime", [0, -1, True, None, 1.5])
def test_lifetime_must_be_explicit_positive_integer(lifetime):
    with pytest.raises(ValueError):
        evaluate(receipt(), lifetime=lifetime)


def test_roundtrip_fraction_does_not_hide_future_or_premature_expiry():
    """A tenth of a microsecond remains positive before rounding for display.

    Synthetic inputs: age is -0.0000001 seconds in the first comparison and
    599.9999999 seconds in the second; compare unrounded against 0 and 600.
    """
    data = receipt()
    data["generated_at"] = "2026-10-22T12:00:00.0000001Z"
    assert "RECEIPT_FROM_FUTURE" in evaluate(data, as_of="2026-10-22T12:00:00Z")["failures"]
    assert evaluate(data, as_of="2026-10-22T12:10:00Z")["status"] == "ready"


@pytest.mark.parametrize("required", [(), ("unknown",), "python"])
def test_requirements_must_name_capabilities(required):
    with pytest.raises(ValueError):
        evaluate(receipt(), required=required)


@pytest.mark.parametrize("section,field,value,code", [
    ("python", "selected_exists", False, "PYTHON_UNVERIFIED"),
    ("python", "selected_exists", "true", "PYTHON_UNVERIFIED"),
    ("python", "selected", "", "PYTHON_UNVERIFIED"),
    ("python", "version", None, "PYTHON_UNVERIFIED"),
    ("python", "venv_cfg_present", False, "PYTHON_UNVERIFIED"),
    ("python", "venv_cfg_present", 1, "PYTHON_UNVERIFIED"),
    ("python", "preferred_encoding", "cp1252", "PYTHON_ENCODING_UNVERIFIED"),
    ("git", "version", None, "GIT_UNVERIFIED"),
    ("git", "path", "", "GIT_UNVERIFIED"),
    ("gh", "auth_ok", None, "GH_AUTH_UNVERIFIED"),
    ("gh", "auth_ok", False, "GH_AUTH_UNVERIFIED"),
    ("gh", "auth_ok", 1, "GH_AUTH_UNVERIFIED"),
    ("gh", "version", None, "GH_UNVERIFIED"),
])
def test_required_capability_needs_positive_evidence(section, field, value, code):
    data = receipt()
    data[section][field] = value
    result = evaluate(data)
    assert result["status"] == "not-ready" and code in result["failures"]


def test_irrelevant_missing_capability_does_not_block():
    data = receipt()
    del data["gh"]
    assert evaluate(data, required=("python",))["status"] == "ready"
    assert evaluate(data)["status"] == "not-ready"


@pytest.mark.parametrize("version", [
    "fatal: synthetic probe failure", "error: synthetic probe failure",
    "git version synthetic", "git version 2", "git version 2.47.0\nfatal: synthetic",
    "git version 2.47.0 failed", "prefix git version 2.47.0", "", None, 247,
])
def test_failed_git_version_cannot_report_ready(tmp_path, version):
    data = receipt()
    data["git"]["version"] = version
    result = evaluate(data, required=("git",))
    assert result["status"] == "not-ready"
    assert result["failures"] == ["GIT_UNVERIFIED"]
    path = tmp_path / "receipt.json"
    path.write_text(json.dumps(data), encoding="utf-8", newline="\n")
    response = run_cli(path, "--as-of", "2026-10-22T12:05:00Z",
                       "--max-age-seconds", "600", "--require", "git")
    assert response.returncode == 3
    assert json.loads(response.stdout)["failures"] == ["GIT_UNVERIFIED"]
    assert "synthetic" not in response.stdout


@pytest.mark.parametrize("version", [
    "git version 2.47.0", "git version 2.47.0.windows.1",
    "git version 2.39.3 (Apple Git-146)", "git version 2.48.0-rc0",
    "git version 2.47.GIT", "git version 2.47.0.123.gabcdef",
])
def test_successful_git_version_forms_report_ready(version):
    data = receipt()
    data["git"]["version"] = version
    assert evaluate(data, required=("git",))["status"] == "ready"


def test_error_findings_block_without_echoing_probe_text():
    data = receipt()
    data["findings"].append({"id": "SYNTHETIC", "severity": "error", "message": "private diagnostic"})
    result = evaluate(data)
    assert result["status"] == "not-ready" and "ERROR_FINDING" in result["failures"]
    assert "private diagnostic" not in json.dumps(result)


@pytest.mark.parametrize("data", [None, [], {}, {"schema": "agent-preflight/other"}])
def test_unknown_or_missing_schema_is_invalid(data):
    with pytest.raises(ValueError):
        evaluate(data)


@pytest.mark.parametrize("findings", [None, {}, ["error"], [{"severity": "unknown"}],
                                     [{"severity": "error"}], [{"id": "X", "severity": "info", "message": ""}]])
def test_incomplete_findings_cannot_report_ready(findings):
    data = receipt()
    data["findings"] = findings
    with pytest.raises(ValueError):
        evaluate(data)


def test_evaluation_does_not_mutate_receipt():
    data = receipt()
    before = copy.deepcopy(data)
    evaluate(data)
    assert data == before


def run_cli(path, *args):
    return subprocess.run([sys.executable, str(SCRIPT), str(path), *args],
                          capture_output=True, text=True, encoding="utf-8", check=False)


def test_cli_uses_explicit_requirements_and_emits_only_summary(tmp_path):
    path = tmp_path / "receipt.json"
    path.write_text(json.dumps(receipt()), encoding="utf-8", newline="\n")
    r = run_cli(path, "--as-of", "2026-10-22T12:05:00Z", "--max-age-seconds", "600",
                "--require", "python", "--require", "gh")
    assert r.returncode == 0, r.stderr
    assert json.loads(r.stdout)["status"] == "ready"
    r = run_cli(path, "--as-of", "2026-10-22T12:10:00Z", "--max-age-seconds", "600", "--require", "gh")
    assert r.returncode == 3 and json.loads(r.stdout)["status"] == "not-ready"
    assert "synthetic" not in r.stdout


@pytest.mark.parametrize("raw", [b"\xff", b"[]", b'{"schema":"other","schema":"agent-preflight/1"}', b"NaN"])
def test_cli_invalid_input_is_redacted_and_has_no_traceback(tmp_path, raw):
    path = tmp_path / "receipt.json"
    path.write_bytes(raw)
    r = run_cli(path, "--as-of", "2026-10-22T12:05:00Z", "--max-age-seconds", "600", "--require", "python")
    assert r.returncode == 1
    assert not r.stdout and "Traceback" not in r.stderr


def test_cli_accepts_collector_utf8_bom(tmp_path):
    path = tmp_path / "receipt.json"
    path.write_text("\ufeff" + json.dumps(receipt()), encoding="utf-8", newline="\n")
    result = run_cli(path, "--as-of", "2026-10-22T12:05:00Z",
                     "--max-age-seconds", "600", "--require", "git")
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["status"] == "ready"


def test_cli_needs_a_lifetime_and_capability(tmp_path):
    r = run_cli(tmp_path / "receipt.json")
    assert r.returncode == 2


def test_documented_receipt_example(tmp_path):
    """Execute the guide's JSON input and clock arithmetic, independent of evaluate.

    Five minutes is 300 seconds; ten minutes is 600 seconds. The guide supplies
    600 seconds as a synthetic lifetime. Equality expires, per the data contract.
    """
    guide = SCRIPT.parents[2] / "docs/standards/review-evidence-workflow.md"
    raw = guide.read_text(encoding="utf-8").split("```json\n", 1)[1].split("\n```", 1)[0]
    path = tmp_path / "receipt.json"
    path.write_text(raw, encoding="utf-8", newline="\n")
    for time, exit_code, status in [("12:05:00", 0, "ready"), ("12:10:00", 3, "not-ready")]:
        r = run_cli(path, "--as-of", f"2026-10-22T{time}Z", "--max-age-seconds", "600",
                    "--require", "python", "--require", "gh")
        assert r.returncode == exit_code, r.stderr
        result = json.loads(r.stdout)
        assert result["status"] == status
        assert result["age_seconds"] == (300 if status == "ready" else 600)
