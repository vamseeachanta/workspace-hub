"""Contract tests for the public-safe Landman pilot decision builder."""

from __future__ import annotations

import copy
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from tests.landman_pilot_test_support import (
    AUTHORIZATION,
    CLUSTERS,
    CRITERIA,
    ranked_candidate,
    score_candidates,
    synthetic_evidence,
)


ROOT = Path(__file__).parents[2]
BUILDER_PATH = ROOT / "scripts/research/build_landman_pilot_decision.py"
EVIDENCE_PATH = ROOT / "docs/reports/landman/2026-07-09-pilot-evidence.yaml"


def load_builder():
    spec = importlib.util.spec_from_file_location("landman_pilot", BUILDER_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


builder = load_builder()


def test_schema_clusters_and_public_blocker_contract():
    evidence = yaml.safe_load(EVIDENCE_PATH.read_text())
    decision = builder.build_decision(evidence)
    assert decision["schema_version"] == "1.0"
    assert [
        (item["jurisdiction"], tuple(item["county_cluster"]))
        for item in evidence["candidates"]
    ] == list(CLUSTERS)
    assert decision["decision_status"] == "owner_decision_required"
    assert decision["selection"] is None and decision["closeout_ready"] is False


def test_decimal_scores_preserve_integral_hundreds_and_rank_without_strings():
    evidence = synthetic_evidence()
    score_candidates(evidence, (5, 4, 3))
    decision = builder.build_decision(evidence)
    assert ranked_candidate(decision, evidence)["raw_score"] == "100"
    assert [item["id"] for item in decision["candidates"]][:2] == [
        evidence["candidates"][0]["id"],
        evidence["candidates"][1]["id"],
    ]


def test_scores_require_matching_citations_anchors_and_reproducibility():
    evidence = synthetic_evidence()
    evidence["candidates"][0]["scores"][CRITERIA[0]]["evidence_ids"] = [
        "candidate-0-public_source_readiness"
    ]
    with pytest.raises(ValueError, match="criterion"):
        builder.build_decision(evidence)
    evidence = synthetic_evidence()
    evidence["candidates"][0]["scores"][CRITERIA[0]]["anchor"] = 2
    with pytest.raises(ValueError, match="anchor"):
        builder.build_decision(evidence)
    evidence = synthetic_evidence()
    evidence["candidates"][0]["scores"][CRITERIA[0]].update({"score": 4, "anchor": 4})
    with pytest.raises(ValueError, match="reproducible"):
        builder.build_decision(evidence)


def test_mode_class_and_authorization_validation_fail_closed():
    invalid_cases = []
    mode = synthetic_evidence()
    mode["candidates"][0]["acreage_mode"] = "federall"
    invalid_cases.append((mode, "acreage"))
    classes = synthetic_evidence()
    classes["candidates"][0]["evidence_classes"][1]["source_url"] = classes[
        "candidates"
    ][0]["evidence_classes"][0]["source_url"]
    invalid_cases.append((classes, "classes"))
    auth = synthetic_evidence()
    auth["authorization"]["outreach"] = "authorized"
    invalid_cases.append((auth, "authorization"))
    for evidence, message in invalid_cases:
        with pytest.raises(ValueError, match=message):
            builder.build_decision(evidence)


def test_metadata_sources_and_frozen_anchor_text_are_validated():
    invalid_cases = []
    project = synthetic_evidence()
    project["candidates"][0].pop("project_class")
    invalid_cases.append((project, "candidate"))
    persona = synthetic_evidence()
    persona["candidates"][0].pop("primary_persona")
    invalid_cases.append((persona, "candidate"))
    county = synthetic_evidence()
    county["candidates"][0]["county_evidence"][0]["source_url"] = "http://example.gov"
    invalid_cases.append((county, "county evidence"))
    source = synthetic_evidence()
    source["candidates"][0]["evidence_rows"][0]["source_url"] = "http://example.gov"
    invalid_cases.append((source, "evidence row"))
    observed = synthetic_evidence()
    observed["candidates"][0]["evidence_rows"][0]["observed_at"] = "2026-07-09"
    invalid_cases.append((observed, "evidence row"))
    anchors = synthetic_evidence()
    anchors["score_anchors"]["4"] = "made up"
    invalid_cases.append((anchors, "anchor text"))
    for evidence, message in invalid_cases:
        with pytest.raises(ValueError, match=message):
            builder.build_decision(evidence)


def test_selection_owner_resolution_and_closeout_readiness():
    evidence = synthetic_evidence()
    score_candidates(evidence, (3, 4, 3))
    selected = builder.build_decision(evidence)
    assert selected["selection"]["candidate_id"] == evidence["candidates"][1]["id"]
    assert selected["closeout_ready"] is True
    tied = synthetic_evidence()
    draft = builder.build_decision(tied)
    tied["owner_decision"] = {
        "chosen_candidate": tied["candidates"][0]["id"],
        "actor": "pilot owner",
        "decided_at": "2026-07-10T00:00:00Z",
        "rationale": "Auditable tie resolution.",
        "score_input_hash": draft["score_input_hash"],
    }
    assert builder.build_decision(tied)["decision_status"] == "selected"
    for item in tied["candidates"]:
        item["hard_gates"]["public_safe_fixture"] = False
    assert builder.build_decision(tied)["selection"] is None


def test_no_eligible_unknown_tie_and_sensitivity_require_owner_decision():
    evidence = synthetic_evidence()
    for item in evidence["candidates"]:
        item["hard_gates"]["public_safe_fixture"] = False
    blocked = builder.build_decision(evidence)
    assert (
        blocked["decision_reason"] == "no_eligible_candidates"
        and blocked["closeout_ready"] is False
    )
    unknown = synthetic_evidence()
    unknown["candidates"][0]["scores"][CRITERIA[0]]["score"] = "unknown"
    assert (
        ranked_candidate(builder.build_decision(unknown), unknown)["display_score"]
        == "unknown"
    )
    sensitive = synthetic_evidence()
    score_candidates(sensitive, (3, 3, 3))
    sensitive["candidates"][0]["scores"][CRITERIA[0]].update({"score": 4, "anchor": 4})
    next(
        row
        for row in sensitive["candidates"][0]["evidence_rows"]
        if row["criterion"] == CRITERIA[0]
    )["reproducible"] = True
    sensitive["candidates"][1]["scores"][CRITERIA[2]].update({"score": 4, "anchor": 4})
    next(
        row
        for row in sensitive["candidates"][1]["evidence_rows"]
        if row["criterion"] == CRITERIA[2]
    )["reproducible"] = True
    sensitive["candidates"][2]["hard_gates"]["public_safe_fixture"] = False
    assert builder.build_decision(sensitive)["decision_reason"] == "sensitivity_change"


def test_county_readiness_and_mode_specific_success_criteria():
    evidence = synthetic_evidence()
    evidence["candidates"][0]["county_evidence"][0]["readiness"] = "conditional"
    assert (
        "primary_county_ready"
        in ranked_candidate(builder.build_decision(evidence), evidence)["failed_gates"]
    )
    private = synthetic_evidence()
    score_candidates(private, (4, 3, 2))
    assert "federal_deferred" in builder.build_decision(private)["success_criteria"]
    mixed = synthetic_evidence()
    mixed["candidates"][1].update({"acreage_mode": "mixed", "federal_deferred": False})
    mixed["candidates"][1]["evidence_classes"][0]["status"] = "available"
    mixed["candidates"][1]["hard_gates"]["blm_mlrs_ready"] = True
    score_candidates(mixed, (2, 4, 3))
    assert "blm_mlrs_evidence" in builder.build_decision(mixed)["success_criteria"]


def test_workflow_and_personas_are_specific_and_non_overlapping():
    decision = builder.build_decision(synthetic_evidence())
    stages, personas = decision["workflow"], decision["personas"]
    assert [stage["id"] for stage in stages] == [
        "intake",
        "aoi_tract_decomposition",
        "work_plan",
        "assignment",
        "evidence_capture",
        "exception_handling",
        "qa_signoff",
        "packet_delivery",
    ]
    assert len({stage["owner"] for stage in stages}) >= 4
    assert all(
        len(stage["input"]) > 12 and len(stage["stop_condition"]) > 12
        for stage in stages
    )
    assert len({item["responsibility"] for item in personas}) == 5


def test_html_is_visible_deterministic_and_matches_yaml_decision():
    evidence = synthetic_evidence()
    first, second = (
        builder.render_outputs(evidence),
        builder.render_outputs(copy.deepcopy(evidence)),
    )
    assert first == second and all(item.endswith("\n") for item in first)
    decision = yaml.safe_load(first[0])
    report = first[1]
    for heading in (
        "Decision",
        "Ranked Scorecard",
        "Ranked Alternatives",
        "Sensitivity",
        "Workflow",
        "Personas",
        "Evidence Boundaries",
        "Risks",
        "Success Criteria",
        "Sources",
    ):
        assert f"<h2>{heading}</h2>" in report
    assert "owner_decision_required" in report and "https://example.gov/" in report
    embedded = json.loads(
        report.split('<script id="decision-data" type="application/json">')[1].split(
            "</script>"
        )[0]
    )
    assert embedded["decision_status"] == decision["decision_status"]


def test_embedded_json_escapes_script_markers_and_sensitivity_runs_once(monkeypatch):
    evidence = synthetic_evidence()
    evidence["candidates"][0]["evidence_rows"][0]["limitation"] = "</script><p>unsafe"
    report = builder.render_outputs(evidence)[1]
    assert "</script><p>unsafe" not in report and "\\u003c/script\\u003e" in report
    calls, original = [], builder.sensitivity
    monkeypatch.setattr(
        builder, "sensitivity", lambda *args: calls.append(1) or original(*args)
    )
    builder.build_decision(synthetic_evidence())
    assert calls == [1]


def test_builder_check_detects_drift_and_public_legal_boundaries(tmp_path):
    evidence, decision, report = (
        tmp_path / "evidence.yaml",
        tmp_path / "decision.yaml",
        tmp_path / "decision.html",
    )
    evidence.write_text(
        yaml.safe_dump(synthetic_evidence(), sort_keys=True), encoding="utf-8"
    )
    command = [
        sys.executable,
        str(BUILDER_PATH),
        "--evidence",
        str(evidence),
        "--decision",
        str(decision),
        "--html",
        str(report),
    ]
    assert subprocess.run(command, check=False).returncode == 0
    report.write_text("drift\n", encoding="utf-8")
    assert subprocess.run([*command, "--check"], check=False).returncode != 0
    actual = builder.build_decision(yaml.safe_load(EVIDENCE_PATH.read_text()))
    assert actual["authorization"] == AUTHORIZATION
    assert (
        "no title opinion" in actual["legal_boundary"].lower()
        and "public-safe" in actual["fixture_boundary"].lower()
    )
