"""Independent examples for the advisory retention table, section 8.1.

Basis: docs/document-intelligence/durable-vs-transient-knowledge-boundary.md
sections 8.1 (90 days OR latest 12 runs) and 8.3 (promotion protection).
All dates and expected sets below are synthetic and hand calculated; no
production output format or promotion evidence is assumed.
"""

import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

import pytest


SCRIPT = (Path(__file__).resolve().parents[2] / "scripts" / "governance"
          / "recurring_retention_plan.py")
AS_OF = "2026-10-26T12:00:00Z"


@pytest.fixture
def planner():
    spec = importlib.util.spec_from_file_location("recurring_retention_plan", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.plan_retention


def run_record(run_id, timestamp, **overrides):
    return {"run_id": run_id, "timestamp": timestamp,
            "promotion_coverage": "complete", "pending_promotion": False,
            "promotion_evidence": [], **overrides}


@pytest.fixture
def manifest():
    # The latest twelve are w01..w12. Aug 3 is 84 days old; July 28 is
    # exactly 90 days old; July 27, July 20 and July 13 are 91, 98 and 105
    # days old at AS_OF. These are literal calendar calculations, not calls
    # to planner constants or helpers.
    dates = [
        ("w01", "2026-10-26"), ("w02", "2026-10-19"),
        ("w03", "2026-10-12"), ("w04", "2026-10-05"),
        ("w05", "2026-09-28"), ("w06", "2026-09-21"),
        ("w07", "2026-09-14"), ("w08", "2026-09-07"),
        ("w09", "2026-08-31"), ("w10", "2026-08-24"),
        ("w11", "2026-08-17"), ("w12", "2026-08-10"),
        ("age-only", "2026-08-03"), ("boundary", "2026-07-28"),
        ("older", "2026-07-27"), ("protected", "2026-07-20"),
        ("oldest", "2026-07-13"),
    ]
    records = [run_record(key, day + "T12:00:00Z") for key, day in dates]
    records[-2]["promotion_evidence"] = ["promotion-record"]
    return {"family": "weekly-review", "runs": records}


def decisions(result, state):
    return {row["run_id"] for row in result["decisions"]
            if row["decision"] == state}


def row_for(result, run_id):
    return next(row for row in result["decisions"] if row["run_id"] == run_id)


def test_age_or_latest_retention(planner, manifest):
    result = planner(manifest, as_of=AS_OF)
    assert result["status"] == "ok"
    assert decisions(result, "keep") == {
        "w01", "w02", "w03", "w04", "w05", "w06", "w07", "w08",
        "w09", "w10", "w11", "w12", "age-only", "boundary", "protected",
    }
    assert decisions(result, "archive_candidate") == {"older", "oldest"}
    assert row_for(result, "age-only")["reasons"] == ["within_age_window"]
    assert row_for(result, "protected")["reasons"] == ["promotion_evidence"]
    assert result["policy"] == {
        "source": "docs/document-intelligence/durable-vs-transient-knowledge-boundary.md#81-retention-schedule",
        "age_days": 90, "latest_runs": 12, "advisory": True,
    }


def test_latest_runs_extend_age_window(planner):
    # Fourteen weekly runs, all older than 90 days: retain Jan 19..Apr 6,
    # the latest twelve; only Jan 5 and Jan 12 can be archive candidates.
    dates = ["2026-01-05", "2026-01-12", "2026-01-19", "2026-01-26",
             "2026-02-02", "2026-02-09", "2026-02-16", "2026-02-23",
             "2026-03-02", "2026-03-09", "2026-03-16", "2026-03-23",
             "2026-03-30", "2026-04-06"]
    result = planner({"family": "weekly-review", "runs": [
        run_record(day, day + "T12:00:00Z") for day in dates]}, as_of=AS_OF)
    assert decisions(result, "keep") == {
        "2026-01-19", "2026-01-26", "2026-02-02", "2026-02-09",
        "2026-02-16", "2026-02-23", "2026-03-02", "2026-03-09",
        "2026-03-16", "2026-03-23", "2026-03-30", "2026-04-06",
    }
    assert decisions(result, "archive_candidate") == {"2026-01-05", "2026-01-12"}
    assert all(row["reasons"] == ["within_latest_runs"]
               for row in result["decisions"] if row["decision"] == "keep")


@pytest.mark.parametrize("timestamp,expected", [
    ("2026-07-28T11:59:59.999999Z", "archive_candidate"),
    ("2026-07-28T12:00:00Z", "keep"),
    ("2026-07-28T12:00:00.000001Z", "keep"),
    ("2026-07-28T14:00:00+02:00", "keep"),
])
def test_age_boundary(planner, manifest, timestamp, expected):
    manifest["runs"][-3]["timestamp"] = timestamp
    assert row_for(planner(manifest, as_of=AS_OF), "older")["decision"] == expected


def test_pending_promotion_blocks_archive(planner, manifest):
    manifest["runs"][-1]["pending_promotion"] = True
    result = planner(manifest, as_of=AS_OF)
    assert row_for(result, "oldest")["decision"] == "keep"
    assert row_for(result, "oldest")["reasons"] == ["pending_promotion"]
    assert decisions(result, "archive_candidate") == {"older"}


@pytest.mark.parametrize("coverage", [None, "unknown", "partial", False])
def test_unknown_coverage_cannot_archive(planner, manifest, coverage):
    manifest["runs"][-1]["promotion_coverage"] = coverage
    result = planner(manifest, as_of=AS_OF)
    assert result["status"] == "unresolved"
    assert row_for(result, "oldest")["decision"] == "unresolved"
    assert "promotion_coverage_unknown" in row_for(result, "oldest")["reasons"]
    assert "oldest" not in decisions(result, "archive_candidate")


@pytest.mark.parametrize("field", ["promotion_coverage", "pending_promotion",
                                    "promotion_evidence"])
def test_missing_promotion_fields_are_unresolved(planner, manifest, field):
    del manifest["runs"][-1][field]
    result = planner(manifest, as_of=AS_OF)
    assert row_for(result, "oldest")["decision"] == "unresolved"


@pytest.mark.parametrize("field,value", [
    ("pending_promotion", "false"), ("pending_promotion", 0),
    ("promotion_evidence", "record"), ("promotion_evidence", [None]),
    ("promotion_evidence", [""]),
])
def test_invalid_promotion_fields_are_errors(planner, manifest, field, value):
    manifest["runs"][-1][field] = value
    result = planner(manifest, as_of=AS_OF)
    assert result["status"] == "error"
    assert row_for(result, "oldest")["decision"] == "error"


@pytest.mark.parametrize("timestamp", [
    "not-a-date", None, "2026-02-30T12:00:00Z", "2026-07-13",
    "2026-07-13T12:00:00", "2026-10-26T12:00:00.000001Z",
    "2026-10-27T12:00:00Z", "2026-07-13T12:00:00-00:00",
])
def test_invalid_timestamp_blocks_archive_and_ranking(planner, manifest, timestamp):
    manifest["runs"][-1]["timestamp"] = timestamp
    result = planner(manifest, as_of=AS_OF)
    assert result["status"] == "error"
    assert row_for(result, "oldest")["decision"] == "error"
    assert not decisions(result, "archive_candidate")
    assert row_for(result, "older")["decision"] == "unresolved"
    assert "ranking_unresolved" in row_for(result, "older")["reasons"]


def test_duplicate_identifiers_are_errors(planner, manifest):
    manifest["runs"].append(run_record("older", "2026-01-01T12:00:00Z"))
    result = planner(manifest, as_of=AS_OF)
    assert result["status"] == "error"
    duplicate_rows = [row for row in result["decisions"] if row["run_id"] == "older"]
    assert len(duplicate_rows) == 2  # Both supplied duplicate records survive.
    assert all(row["decision"] == "error" and "duplicate_run_id" in row["reasons"]
               for row in duplicate_rows)
    assert not decisions(result, "archive_candidate")


def test_tied_latest_cutoff_is_conservative(planner, manifest):
    # Matching the twelfth timestamp cannot establish a strict older ordering.
    manifest["runs"][-1]["timestamp"] = "2026-08-10T12:00:00Z"
    result = planner(manifest, as_of="2027-10-26T12:00:00Z")
    assert "within_latest_runs" in row_for(result, "oldest")["reasons"]
    assert "within_latest_runs" in row_for(result, "w12")["reasons"]


@pytest.mark.parametrize("invalid", [None, [], {}, {"family": "nightly-batch", "runs": []},
                                    {"family": "weekly-review", "runs": {}},
                                    {"family": "weekly-review", "runs": [None]}])
def test_invalid_manifest_cannot_archive(planner, invalid):
    result = planner(invalid, as_of=AS_OF)
    assert result["status"] == "error"
    assert not decisions(result, "archive_candidate")


@pytest.mark.parametrize("run_id", [None, "", " ambiguous ", 7])
def test_invalid_identifier_blocks_ranking(planner, manifest, run_id):
    manifest["runs"][-1]["run_id"] = run_id
    result = planner(manifest, as_of=AS_OF)
    assert result["status"] == "error"
    assert not decisions(result, "archive_candidate")


@pytest.mark.parametrize("as_of", [None, "2026-10-26", "bad"])
def test_invalid_as_of_is_explicit(planner, manifest, as_of):
    result = planner(manifest, as_of=as_of)
    assert result["status"] == "error"
    assert "invalid_as_of" in result["errors"]
    assert not decisions(result, "archive_candidate")


def test_empty_manifest(planner):
    result = planner({"family": "weekly-review", "runs": []}, as_of=AS_OF)
    assert result["status"] == "ok"
    assert result["decisions"] == []


def snapshot(root):
    return {str(path.relative_to(root)): path.read_bytes() if path.is_file() else None
            for path in root.rglob("*")}


def test_planner_is_read_only(planner, manifest, tmp_path, monkeypatch):
    (tmp_path / "output.txt").write_text("retained bytes", encoding="utf-8")
    manifest["runs"][-1]["output_path"] = str(tmp_path / "output.txt")
    original = copy.deepcopy(manifest)
    before = snapshot(tmp_path)

    def forbidden(*args, **kwargs):
        pytest.fail("The pure planner attempted filesystem access")

    with monkeypatch.context() as patch:
        patch.setattr("builtins.open", forbidden)
        patch.setattr("os.scandir", forbidden)
        patch.setattr("io.open", forbidden)
        result = planner(manifest, as_of=AS_OF)
    assert result["status"] == "ok"
    assert manifest == original
    assert snapshot(tmp_path) == before


def cli(path, as_of=AS_OF):
    return subprocess.run([sys.executable, str(SCRIPT), "--manifest", str(path),
                           "--as-of", as_of], capture_output=True, check=False)


def test_cli_is_deterministic(manifest, tmp_path):
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(manifest), encoding="utf-8")
    (tmp_path / "output.txt").write_bytes(b"unchanged\n")
    before = snapshot(tmp_path)
    first = cli(path)
    second = cli(path)
    assert first.returncode == second.returncode == 0
    assert first.stderr == second.stderr == b""
    assert first.stdout == second.stdout
    assert decisions(json.loads(first.stdout), "archive_candidate") == {"older", "oldest"}
    assert snapshot(tmp_path) == before
    manifest["runs"].reverse()
    path.write_text(json.dumps(manifest, sort_keys=True), encoding="utf-8")
    assert cli(path).stdout == first.stdout


@pytest.mark.parametrize("raw", ["{", '{"family":"weekly-review","runs":[],"runs":[]}',
                                  '{"family":"weekly-review","runs":[],"x":NaN}'])
def test_cli_invalid_json_is_structured(tmp_path, raw):
    path = tmp_path / "invalid.json"
    path.write_text(raw, encoding="utf-8")
    result = cli(path)
    assert result.returncode != 0
    assert result.stderr == b""
    assert json.loads(result.stdout)["errors"] == ["invalid_json"]


def test_cli_missing_manifest_is_structured(tmp_path):
    result = cli(tmp_path / "absent.json")
    assert result.returncode != 0
    assert json.loads(result.stdout)["errors"] == ["manifest_unreadable"]


def test_cli_unresolved_has_nonzero_status(manifest, tmp_path):
    del manifest["runs"][-1]["promotion_coverage"]
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(manifest), encoding="utf-8")
    result = cli(path)
    assert result.returncode != 0
    assert json.loads(result.stdout)["status"] == "unresolved"
