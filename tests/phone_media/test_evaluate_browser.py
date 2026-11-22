"""Offline acceptance truth tables; no vendor installation or family media.

Expected decisions are independent Boolean derivations: any FAIL blocks a
candidate; otherwise any missing observation/version is NOT_EVALUATED;
otherwise all required observations PASS and the candidate is READY_FOR_REVIEW.
This conjunction is the local trial procedure in the evaluation runbook,
derived from issue #3588's private browsing requirement, not a vendor score.
"""

from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest

# scripts/ is on sys.path only through tests/conftest.py; a --noconftest run
# (or any run without that bootstrap) skips this module cleanly instead of
# failing collection.
_evaluate_browser = pytest.importorskip(
    "phone_media.evaluate_browser", reason="scripts/phone_media is not importable here"
)
REQUIREMENTS = _evaluate_browser.REQUIREMENTS
evaluate = _evaluate_browser.evaluate
load_assessment = _evaluate_browser.load_assessment

SCRIPT = Path(__file__).resolve().parents[2] / "scripts/phone_media/evaluate_browser.py"


def ready_candidate():
    return {
        "version": "synthetic-release",
        "checks": {
            name: {"status": "PASS", "kind": "observed", "reference": "trial-record"}
            for name in REQUIREMENTS
        },
    }


def assessment(candidate=None):
    return {"candidates": {"immich": candidate or ready_candidate()}}


def test_all_observed_pass_is_ready_without_mutating_input():
    data = assessment()
    before = copy.deepcopy(data)
    report = evaluate(data)
    assert report["eligible_candidates"] == ["immich"]
    assert report["candidates"]["immich"]["decision"] == "READY_FOR_REVIEW"
    assert data == before


@pytest.mark.parametrize("requirement", REQUIREMENTS)
def test_each_missing_check_prevents_readiness(requirement):
    data = assessment()
    del data["candidates"]["immich"]["checks"][requirement]
    report = evaluate(data)
    assert report["eligible_candidates"] == []
    assert report["candidates"]["immich"]["decision"] == "NOT_EVALUATED"


@pytest.mark.parametrize("requirement", REQUIREMENTS)
def test_each_failed_check_blocks_even_with_other_unknowns(requirement):
    data = assessment()
    checks = data["candidates"]["immich"]["checks"]
    checks[requirement]["status"] = "FAIL"
    for name in REQUIREMENTS:
        if name != requirement:
            del checks[name]
            break
    report = evaluate(data)
    assert report["candidates"]["immich"]["decision"] == "BLOCKED"


def test_documented_support_does_not_become_observed_pass():
    candidate = ready_candidate()
    candidate["checks"]["heic_preview"]["kind"] = "documentation"
    report = evaluate(assessment(candidate))
    assert report["candidates"]["immich"]["checks"]["heic_preview"] == "NOT_EVALUATED"
    assert report["eligible_candidates"] == []


def test_documented_failure_is_conservatively_blocking():
    candidate = ready_candidate()
    candidate["checks"]["heic_preview"].update(status="FAIL", kind="documentation")
    assert evaluate(assessment(candidate))["candidates"]["immich"]["decision"] == "BLOCKED"


@pytest.mark.parametrize("version", [None, "", "   "])
def test_missing_version_prevents_readiness(version):
    candidate = ready_candidate()
    candidate["version"] = version
    assert evaluate(assessment(candidate))["eligible_candidates"] == []


def test_two_ready_candidates_have_no_invented_ranking():
    data = {"candidates": {"photoprism": ready_candidate(), "immich": ready_candidate()}}
    assert evaluate(data)["eligible_candidates"] == ["immich", "photoprism"]


def test_blocked_candidate_does_not_hide_ready_alternative():
    data = assessment()
    other = ready_candidate()
    other["checks"]["tailnet_only"]["status"] = "FAIL"
    data["candidates"]["photoprism"] = other
    assert evaluate(data)["eligible_candidates"] == ["immich"]


@pytest.mark.parametrize("data", [
    {}, [], {"candidates": {}}, {"candidates": []},
    {"candidates": {"other": ready_candidate()}},
    {"candidates": {"immich": None}},
    {"candidates": {"immich": {"checks": {}}}},
    {"candidates": {"immich": {"version": True, "checks": {}}}},
    {"candidates": {"immich": {"version": None, "checks": [], }}},
    {"candidates": {"immich": {"version": None, "checks": {"typo": {}}}}},
    {"candidates": {"immich": {"version": None, "checks": {}, "typo": True}}},
    {"candidates": {"immich": ready_candidate()}, "typo": True},
])
def test_invalid_structure_rejected(data):
    with pytest.raises(ValueError):
        evaluate(data)


@pytest.mark.parametrize("change", [
    {"status": True}, {"status": "pass"}, {"status": "UNKNOWN"},
    {"kind": "vendor"}, {"reference": ""}, {"reference": "   "},
    {"reference": None}, {"unexpected": True},
])
def test_invalid_observation_rejected(change):
    candidate = ready_candidate()
    candidate["checks"]["tailnet_only"].update(change)
    with pytest.raises(ValueError):
        evaluate(assessment(candidate))


def test_unknown_observation_is_explicit():
    candidate = ready_candidate()
    candidate["checks"]["restore_verified"]["status"] = "NOT_EVALUATED"
    assert evaluate(assessment(candidate))["eligible_candidates"] == []


@pytest.mark.parametrize("text", [
    '{"candidates":{},"candidates":{}}', '{"candidates":NaN}',
    '{"candidates":Infinity}', '{"candidates":',
])
def test_ambiguous_or_invalid_json_rejected(text):
    with pytest.raises(ValueError):
        load_assessment(text)


@pytest.mark.parametrize("eligible", [True, False])
def test_cli_reads_only_input_and_emits_decision(tmp_path, eligible):
    """Exit 0 iff an eligible candidate exists; exit 1 otherwise (CLI contract)."""
    candidate = ready_candidate()
    if not eligible:
        candidate["checks"] = {}
    payload = json.dumps(assessment(candidate))
    source = tmp_path / "assessment.json"
    source.write_text(payload)
    result = subprocess.run([sys.executable, str(SCRIPT), str(source)],
                            capture_output=True, text=True, check=False)
    assert result.returncode == (0 if eligible else 1)
    assert json.loads(result.stdout)["eligible_candidates"] == (["immich"] if eligible else [])
    assert source.read_text() == payload
    assert list(tmp_path.iterdir()) == [source]


@pytest.mark.parametrize("payload", [b'\xff', b'{"private-marker":invalid}'])
def test_cli_invalid_input_does_not_echo_data_or_path(tmp_path, payload):
    source = tmp_path / "private-marker.json"
    source.write_bytes(payload)
    result = subprocess.run([sys.executable, str(SCRIPT), str(source)],
                            capture_output=True, text=True, check=False)
    assert result.returncode == 2  # CLI usage/validation error, not a trial decision.
    assert result.stdout == ""
    assert result.stderr == "Invalid assessment; check the documented input schema.\n"


def test_worked_example_matches_committed_answer():
    root = SCRIPT.parents[2]
    folder = root / "examples/phone-media"
    data = load_assessment((folder / "browser-assessment.json").read_text())
    expected = json.loads((folder / "browser-answer.json").read_text())
    # Hand derivation: Immich lacks an observed restore and version; PhotoPrism
    # has an observed network FAIL. Thus neither is eligible, regardless of
    # documented feature support. The runbook writes out this same truth table.
    assert evaluate(data) == expected
