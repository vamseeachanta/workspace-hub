"""Synthetic Linux examples for supplied-data validation, without live probes.

Basis: docs/modules/ai/readiness-evidence-bundle.schema.yaml defines version
1.0, required fields and status vocabulary. The timestamp and writer version
below are arbitrary synthetic literals, following the worked example in
docs/modules/ai/readiness-evidence-validation.html. That example also supplies
the healthy tally: access + workspace + command = three passes; optional tools
= one skip; total = four. Every changed tally is hand-counted below, without
using validator internals to derive an expected result.
"""

from __future__ import annotations

import copy
import importlib.util
from pathlib import Path

import pytest
import yaml
from jsonschema import Draft7Validator, FormatChecker

SCRIPT_PATH = (
    Path(__file__).resolve().parents[2]
    / "scripts"
    / "analysis"
    / "readiness_bundle_schema.py"
)
_spec = importlib.util.spec_from_file_location("linux_readiness_schema", SCRIPT_PATH)
readiness_schema = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(readiness_schema)


@pytest.fixture
def linux_bundle(tmp_path, monkeypatch):
    """Use withheld identities and locators relative to a temporary directory."""
    monkeypatch.chdir(tmp_path)
    evidence_dir = Path("evidence")
    evidence_dir.mkdir()
    return {
        "schema_version": "1.0",
        "machine": {
            "id": "withheld",
            "hostname": "withheld",
            "user": "withheld",
            "os": "linux",
        },
        "collected_at": "2026-10-22T00:00:00Z",
        "source_writer": {
            "name": "synthetic-example",
            "version": "1",
            "entrypoint": "example",
        },
        "access": {"mode": "local_no_ssh", "reachable": True},
        "checks": [
            {
                "id": "access-mode",
                "name": "Access",
                "status": "pass",
                "summary": "Synthetic access observation",
                "evidence": {"transport": "local_no_ssh"},
            },
            {
                "id": "workspace-root",
                "name": "Workspace",
                "status": "pass",
                "summary": "Synthetic workspace observation",
                "evidence": {"path": "evidence"},
            },
            {
                "id": "ai-cli",
                "name": "Command availability",
                "status": "pass",
                "summary": "Synthetic command observation",
                "evidence": {"claude": True, "codex": True},
            },
            {
                "id": "licensed-tools",
                "name": "Optional tools",
                "status": "skip",
                "summary": "Tools excluded from the synthetic task",
                "evidence": {"required": False},
            },
        ],
        "overall": {
            "verdict": "ready",
            "summary": "Internally consistent synthetic evidence",
            "counts": {
                "total": 4, "pass": 3, "warn": 0,
                "fail": 0, "error": 0, "skip": 1,
            },
        },
    }


def _assert_structurally_valid(bundle):
    validator = Draft7Validator(
        readiness_schema.load_schema(), format_checker=FormatChecker()
    )
    assert list(validator.iter_errors(bundle)) == []


def _assert_validation_round_trip(bundle, expected_errors):
    """Validate supplied data and its temporary YAML representation identically."""
    _assert_structurally_valid(bundle)
    path = Path("evidence") / "bundle.yaml"
    path.write_text(yaml.safe_dump(bundle), encoding="utf-8")
    assert readiness_schema.validate_bundle(bundle) == expected_errors
    assert readiness_schema.validate_bundle_file(path) == expected_errors


def test_linux_healthy_bundle_is_consistent(linux_bundle):
    """Hand count: three pass + one skip = four rows; zero errors expected."""
    _assert_validation_round_trip(linux_bundle, [])


@pytest.mark.parametrize(
    ("statuses", "counts"),
    [
        # Each isolated replacement leaves two pass + one adverse + one skip.
        (
            {"workspace-root": "warn"},
            {"total": 4, "pass": 2, "warn": 1, "fail": 0, "error": 0, "skip": 1},
        ),
        (
            {"workspace-root": "fail"},
            {"total": 4, "pass": 2, "warn": 0, "fail": 1, "error": 0, "skip": 1},
        ),
        (
            {"workspace-root": "error"},
            {"total": 4, "pass": 2, "warn": 0, "fail": 0, "error": 1, "skip": 1},
        ),
        # One warn + one fail + one error + one skip = four; no pass remains.
        (
            {"access-mode": "error", "workspace-root": "warn", "ai-cli": "fail"},
            {"total": 4, "pass": 0, "warn": 1, "fail": 1, "error": 1, "skip": 1},
        ),
    ],
    ids=["warning", "failure", "error", "mixed"],
)
def test_linux_degraded_bundle_cannot_claim_ready(linux_bundle, statuses, counts):
    """A consistent degraded example has zero errors; ready adds one error."""
    for check in linux_bundle["checks"]:
        if check["id"] in statuses:
            check["status"] = statuses[check["id"]]
            check["summary"] = "Synthetic adverse observation"
    linux_bundle["overall"] = {
        "verdict": "degraded",
        "summary": "Synthetic adverse evidence prevents a ready verdict",
        "counts": counts,
    }
    _assert_validation_round_trip(linux_bundle, [])

    linux_bundle["overall"]["verdict"] = "ready"
    _assert_validation_round_trip(
        linux_bundle, ["overall/verdict: ready contradicts evidence"]
    )


def test_linux_unreachable_access_cannot_claim_ready(linux_bundle):
    """Unreachable access alone adds one error; row counts remain unchanged."""
    linux_bundle["access"]["reachable"] = False
    _assert_validation_round_trip(
        linux_bundle, ["overall/verdict: ready contradicts evidence"]
    )
    linux_bundle["overall"]["verdict"] = "blocked"
    _assert_validation_round_trip(linux_bundle, [])


@pytest.mark.parametrize(
    ("field", "incorrect"),
    # Healthy counts are four total, three pass, one skip and zero others.
    # Each literal below exceeds its independently counted value by one.
    [("total", 5), ("pass", 4), ("warn", 1), ("fail", 1), ("error", 1), ("skip", 2)],
)
def test_linux_incorrect_summary_count_is_detected(linux_bundle, field, incorrect):
    """Changing only one supplied count produces exactly one mismatch."""
    linux_bundle["overall"]["counts"][field] = incorrect
    _assert_validation_round_trip(
        linux_bundle, [f"overall/counts/{field}: count mismatch"]
    )


def test_linux_duplicate_check_id_is_detected(linux_bundle):
    """An extra access row gives four pass + one skip = five; one ID repeats."""
    access_check = next(
        check for check in linux_bundle["checks"] if check["id"] == "access-mode"
    )
    linux_bundle["checks"].append(copy.deepcopy(access_check))
    linux_bundle["overall"]["counts"] = {
        "total": 5, "pass": 4, "warn": 0, "fail": 0, "error": 0, "skip": 1,
    }
    _assert_validation_round_trip(linux_bundle, ["checks: duplicate check id"])


def test_linux_access_transport_contradiction_is_detected(linux_bundle):
    """SSH evidence disagrees with local access; one equality check fails."""
    access_check = next(
        check for check in linux_bundle["checks"] if check["id"] == "access-mode"
    )
    access_check["evidence"]["transport"] = "ssh"
    _assert_validation_round_trip(
        linux_bundle, ["checks/0/evidence: transport mismatch"]
    )
