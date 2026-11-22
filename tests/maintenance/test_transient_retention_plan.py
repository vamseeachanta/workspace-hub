"""Synthetic metadata only; no live artifacts are inspected.

Policy basis: repository issue #2237 and
docs/document-intelligence/durable-vs-transient-knowledge-boundary.md,
sections 4.4, 4.8, 7.2, 8.1 and 8.4. The example windows below are supplied
policy, not new defaults: handoff after closure 30 days, quick planning after
closure 14 days, research 30 days, committed signals 7 days. Calendar arithmetic
is independent: April 1 + 30 days = May 1; April 17 + 14 days = May 1;
April 24 + 7 days = May 1. Summary counts are hand-counted fixture rows.
"""

import copy
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest


SCRIPT = Path(__file__).resolve().parents[2] / "scripts/maintenance/transient_retention_plan.py"
POLICY_SOURCE = "docs/document-intelligence/durable-vs-transient-knowledge-boundary.md#8.1"
NOW = "2026-05-01T00:00:00+00:00"


@pytest.fixture
def planner():
    spec = importlib.util.spec_from_file_location("transient_retention_plan", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def policy():
    return {
        "handoff": {"days": 30, "basis": "issue_closed_at", "source": POLICY_SOURCE},
        "planning_quick": {"days": 14, "basis": "issue_closed_at", "source": POLICY_SOURCE},
        "planning_research": {"days": 30, "basis": "created_at", "source": POLICY_SOURCE},
        "signal": {"days": 7, "basis": "created_at", "source": POLICY_SOURCE},
    }


def record(kind="handoff", **changes):
    row = {
        "id": "synthetic-record", "kind": kind, "classification": "transient",
        "evidence_verified": True, "promoted": False,
        "retention_evidence": {"verified": True, "policy_ref": POLICY_SOURCE},
        "issue_state": "closed", "issue_closed_at": "2026-04-01T00:00:00Z",
        "created_at": "2026-04-01T00:00:00Z",
    }
    row.update(changes)
    return row


def decision(planner, policy, row, now=NOW):
    return planner.build_plan([row], policy, now=now)["records"][0]


def test_durable_and_unverified_records_are_kept(planner, policy):
    rows = [record(classification="durable"), record(promoted=True),
            record(classification="governance"), record(evidence_verified=False)]
    plan = planner.build_plan(rows, policy, now=NOW)
    assert [row["status"] for row in plan["records"]] == ["keep", "keep", "keep", "unknown"]
    assert [row["reason"] for row in plan["records"]] == [
        "durable_content", "promoted_content", "governance_evidence", "unverified_evidence"]
    assert plan["summary"] == {"total": 4, "keep": 3, "eligible": 0, "unknown": 1}


@pytest.mark.parametrize("now,status", [
    ("2026-04-30T23:59:59.999999Z", "keep"),
    (NOW, "eligible"),
    ("2026-05-01T00:00:00.000001Z", "eligible"),
    ("2026-05-01T02:00:00+02:00", "eligible"),
])
def test_expiry_boundary_matches_supplied_policy(planner, policy, now, status):
    result = decision(planner, policy, record(), now)
    assert result["status"] == status
    assert result["expires_at"] == NOW
    assert result["reason"] == ("retention_elapsed" if status == "eligible" else "retention_pending")


def test_fixture_classes_and_hand_counted_summary(planner, policy):
    rows = [record(), record("planning_quick", issue_closed_at="2026-04-17T00:00:00Z"),
            record("planning_research"), record("signal", created_at="2026-04-24T00:00:00Z"),
            record(classification="durable"), record(promoted=True), {}]
    before = copy.deepcopy((rows, policy))
    plan = planner.build_plan(rows, policy, now=NOW)
    # Four expired transients, two protected records, one unknown record.
    assert plan["summary"] == {"total": 7, "keep": 2, "eligible": 4, "unknown": 1}
    assert all(row["expires_at"] == NOW for row in plan["records"][:4])
    assert plan["dry_run"] is True
    assert (rows, policy) == before


@pytest.mark.parametrize("field", ["classification", "evidence_verified", "promoted",
                                   "kind", "retention_evidence", "issue_state", "issue_closed_at"])
def test_missing_metadata_is_unknown(planner, policy, field):
    row = record()
    del row[field]
    assert decision(planner, policy, row)["status"] == "unknown"


@pytest.mark.parametrize("changes", [
    {"classification": "execution-bound"}, {"evidence_verified": "true"},
    {"promoted": "false"}, {"retention_evidence": {}},
    {"retention_evidence": {"verified": True, "policy_ref": "different-policy"}},
    {"retention_evidence": {"verified": False, "policy_ref": POLICY_SOURCE}},
    {"issue_closed_at": "invalid"}, {"issue_closed_at": "2026-04-01"},
    {"issue_closed_at": "2026-04-01T00:00:00"},
    {"issue_closed_at": "2026-06-01T00:00:00Z"},
    {"kind": "unsupported"}, {"kind": []}, {"classification": []},
])
def test_invalid_or_unverified_evidence_is_unknown(planner, policy, changes):
    assert decision(planner, policy, record(**changes))["status"] == "unknown"


def test_open_issue_kept_without_age_fallback(planner, policy):
    row = record(issue_state="open", created_at="2000-01-01T00:00:00Z")
    row.pop("issue_closed_at")
    assert decision(planner, policy, row)["reason"] == "issue_open"


@pytest.mark.parametrize("rule", [None, {}, {"days": 30},
    {"days": True, "basis": "created_at", "source": POLICY_SOURCE},
    {"days": 0, "basis": "created_at", "source": POLICY_SOURCE},
    {"days": -1, "basis": "created_at", "source": POLICY_SOURCE},
    {"days": 1.5, "basis": "created_at", "source": POLICY_SOURCE},
    {"days": 30, "basis": "mtime", "source": POLICY_SOURCE},
    {"days": 30, "basis": "created_at", "source": " "},
    {"days": 10**20, "basis": "created_at", "source": POLICY_SOURCE},
])
def test_invalid_policy_never_qualifies(planner, rule):
    # Zero/negative/fractional/bool windows and overflow are invalid synthetic
    # inputs, not retention constants. No supplied rule means unknown.
    assert decision(planner, {"handoff": rule}, record())["status"] == "unknown"


def test_no_policy_default_or_path_inference(planner, policy):
    assert decision(planner, {}, record())["status"] == "unknown"
    row = {"path": "docs/handoffs/ancient.md", "created_at": "2000-01-01T00:00:00Z"}
    assert decision(planner, policy, row)["status"] == "unknown"


def test_supplied_fallback_policy_is_used(planner, policy):
    # Section 8.4: explicitly supplied fallback, April 1 + 90 days = June 30.
    policy["handoff"] = {"days": 90, "basis": "created_at", "source": POLICY_SOURCE}
    row = record()
    row.pop("issue_closed_at")
    row.pop("issue_state")
    result = decision(planner, policy, row, "2026-06-30T00:00:00Z")
    assert result["status"] == "eligible"
    assert result["expires_at"] == "2026-06-30T00:00:00+00:00"


@pytest.mark.parametrize("now", [None, "bad", "2026-05-01", "2026-05-01T00:00:00"])
def test_current_time_must_be_explicit_and_aware(planner, policy, now):
    with pytest.raises(ValueError):
        planner.build_plan([record()], policy, now=now)


def test_malformed_record_and_empty_plan(planner, policy):
    assert decision(planner, policy, None)["status"] == "unknown"
    assert planner.build_plan([], policy, now=NOW)["summary"] == {
        "total": 0, "keep": 0, "eligible": 0, "unknown": 0}


def snapshot(root):
    """Capture names, bytes, modes and mtimes, excluding access times."""
    result = {}
    for path in [root, *root.rglob("*")]:
        stat = path.lstat()
        payload = (os.readlink(path) if path.is_symlink() else
                   path.read_bytes() if path.is_file() else None)
        result[str(path.relative_to(root))] = (stat.st_mode, stat.st_mtime_ns, payload)
    return result


def test_dry_run_leaves_tree_byte_identical(policy, tmp_path):
    target = tmp_path / "tree"
    target.mkdir()
    artifact = target / "artifact.txt"
    artifact.write_bytes(b"preserve this evidence\x00\xff")
    (target / "link").symlink_to(artifact)
    # Metadata locators are opaque: even a path outside the target is not opened.
    metadata = tmp_path / "metadata.json"
    metadata.write_text(json.dumps({"records": [record(path=str(artifact)),
        record(path=str(tmp_path / "absent"))], "policy": policy}), encoding="utf-8")
    before = snapshot(tmp_path)
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    for arguments in ([], ["--dry-run"]):
        result = subprocess.run([sys.executable, str(SCRIPT), str(metadata),
            "--now", NOW, *arguments], capture_output=True, text=True, env=env, check=False)
        assert result.returncode == 0, result.stderr
        plan = json.loads(result.stdout)
        assert plan["dry_run"] is True
        assert plan["summary"] == {"total": 2, "keep": 0, "eligible": 2, "unknown": 0}
    assert snapshot(tmp_path) == before


@pytest.mark.parametrize("payload", ["{", "[]", '{}',
    '{"records": [], "records": [], "policy": {}}',
    '{"records": [], "policy": {"signal": NaN}}',
    '{"records": {}, "policy": {}}', '{"records": [], "policy": []}'])
def test_cli_rejects_malformed_input(tmp_path, payload):
    metadata = tmp_path / "bad.json"
    metadata.write_text(payload, encoding="utf-8")
    result = subprocess.run([sys.executable, str(SCRIPT), str(metadata), "--now", NOW],
                            capture_output=True, text=True, check=False)
    assert result.returncode != 0
    assert not result.stdout
    assert "invalid metadata or policy" in result.stderr
