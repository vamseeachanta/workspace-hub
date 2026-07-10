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


ROOT = Path(__file__).parents[2]
BUILDER_PATH = ROOT / "scripts/research/build_landman_pilot_decision.py"
EVIDENCE_PATH = ROOT / "docs/reports/landman/2026-07-09-pilot-evidence.yaml"
DECISION_PATH = ROOT / "docs/reports/landman/2026-07-09-pilot-decision.yaml"
HTML_PATH = ROOT / "docs/reports/landman/2026-07-09-pilot-decision.html"
CRITERIA = (
    "broker_workflow_value",
    "public_source_readiness",
    "county_title_feasibility",
    "fixture_reproducibility",
    "delivery_exception_learning",
)
CLUSTERS = (
    ("Texas", ("Midland", "Reeves")),
    ("Oklahoma", ("Grady", "Canadian")),
    ("Colorado", ("Rio Blanco", "Garfield")),
)


def load_builder():
    spec = importlib.util.spec_from_file_location("landman_pilot", BUILDER_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


builder = load_builder()


def synthetic_evidence():
    candidates = []
    for index, (jurisdiction, counties) in enumerate(CLUSTERS):
        candidate_id = f"candidate-{index}"
        rows = [
            {
                "id": f"{candidate_id}-{criterion}",
                "criterion": criterion,
                "source_url": "https://example.gov/source",
                "observed_at": "2026-07-09T23:15:20Z",
                "access_state": "public",
                "confidence": "verified",
                "limitation": "Research evidence only; no title conclusion.",
            }
            for criterion in CRITERIA
        ]
        candidates.append(
            {
                "id": candidate_id,
                "jurisdiction": jurisdiction,
                "county_cluster": list(counties),
                "acreage_mode": "private_only",
                "federal_deferred": True,
                "project_class": "public-source pilot",
                "primary_persona": "broker_project_manager",
                "primary_county": counties[0],
                "county_evidence": [
                    {
                        "county": county,
                        "official_source": f"{county} Recorder",
                        "source_url": "https://example.gov/county",
                        "observed_at": "2026-07-09T23:15:20Z",
                        "access_state": "public",
                        "fee_account": "no_paid_or_account_required",
                        "index": "official index",
                        "images": "not required for public-safe fixture",
                        "confidence": "verified",
                        "limitation": "No title search or legal conclusion.",
                        "readiness": "ready" if county == counties[0] else "conditional",
                    }
                    for county in counties
                ],
                "evidence_rows": rows,
                "scores": {
                    criterion: {"score": 3, "evidence_ids": [f"{candidate_id}-{criterion}"]}
                    for criterion in CRITERIA
                },
                "hard_gates": {
                    "complete_evidence": True,
                    "public_safe_fixture": True,
                    "paid_or_account_required": False,
                    "separate_evidence_classes": True,
                    "research_assistance_only": True,
                    "primary_county_ready": True,
                },
            }
        )
    return {
        "schema_version": "1.0",
        "decision_timestamp": "2026-07-09T23:15:20Z",
        "renderer_version": "1.0",
        "weights": dict(zip(CRITERIA, (25, 25, 20, 15, 15))),
        "score_anchors": {str(score): f"anchor-{score}" for score in range(6)},
        "authorization": {"outreach": "not_authorized", "account_creation": "not_authorized"},
        "candidates": candidates,
    }


def score_candidates(evidence, values):
    for candidate, value in zip(evidence["candidates"], values, strict=True):
        for score in candidate["scores"].values():
            score["score"] = value


def test_decision_schema_and_version():
    decision = builder.build_decision(yaml.safe_load(EVIDENCE_PATH.read_text()))
    assert decision["schema_version"] == "1.0"
    assert decision["decision_timestamp"].endswith("Z")
    assert decision["decision_status"] in {"selected", "owner_decision_required"}


def test_exact_candidate_clusters_and_counties():
    evidence = yaml.safe_load(EVIDENCE_PATH.read_text())
    observed = [(item["jurisdiction"], tuple(item["county_cluster"])) for item in evidence["candidates"]]
    assert observed == list(CLUSTERS)


def test_score_anchors_weights_decimal_and_evidence():
    evidence = synthetic_evidence()
    decision = builder.build_decision(evidence)
    assert set(evidence["score_anchors"]) == {str(score) for score in range(6)}
    assert sum(evidence["weights"].values()) == 100
    assert decision["candidates"][0]["raw_score"] == "60"
    assert decision["candidates"][0]["display_score"] == "60.00"
    assert all(item["evidence_ids"] for item in evidence["candidates"][0]["scores"].values())


def test_paired_weight_sensitivity_preserves_total():
    decision = builder.build_decision(synthetic_evidence())
    variants = decision["sensitivity"]
    assert len(variants) == len(CRITERIA) * (len(CRITERIA) - 1)
    assert all(sum(item["weights"].values()) == 100 for item in variants)


def test_selection_matches_highest_eligible_score():
    evidence = synthetic_evidence()
    score_candidates(evidence, (3, 4, 3))
    decision = builder.build_decision(evidence)
    assert decision["decision_status"] == "selected"
    assert decision["selection"]["candidate_id"] == evidence["candidates"][1]["id"]


def test_no_eligible_candidate_requires_owner_decision():
    evidence = synthetic_evidence()
    for candidate in evidence["candidates"]:
        candidate["hard_gates"]["public_safe_fixture"] = False
    decision = builder.build_decision(evidence)
    assert decision["decision_status"] == "owner_decision_required"
    assert decision["selection"] is None
    assert decision["decision_reason"] == "no_eligible_candidates"
    assert "blm_mlrs_evidence" not in decision["success_criteria"]
    assert "federal_deferred" not in decision["success_criteria"]


def test_unknown_score_remains_unknown_and_makes_candidate_ineligible():
    evidence = synthetic_evidence()
    evidence["candidates"][0]["scores"][CRITERIA[0]]["score"] = "unknown"
    candidate = next(item for item in builder.build_decision(evidence)["candidates"] if item["id"] == evidence["candidates"][0]["id"])
    assert candidate["raw_score"] is None
    assert candidate["display_score"] == "unknown"
    assert "unknown_score" in candidate["failed_gates"]


def test_tied_leaders_require_owner_decision():
    decision = builder.build_decision(synthetic_evidence())
    assert decision["decision_status"] == "owner_decision_required"
    assert decision["decision_reason"] == "tied_leaders"
    assert decision["selection"] is None


def test_sensitive_winner_requires_owner_decision():
    evidence = synthetic_evidence()
    first, second = evidence["candidates"][:2]
    for score in first["scores"].values():
        score["score"] = 3
    for score in second["scores"].values():
        score["score"] = 3
    first["scores"][CRITERIA[0]]["score"] = 4
    second["scores"][CRITERIA[2]]["score"] = 4
    evidence["candidates"][2]["hard_gates"]["public_safe_fixture"] = False
    decision = builder.build_decision(evidence)
    assert decision["decision_status"] == "owner_decision_required"
    assert decision["decision_reason"] == "sensitivity_change"


def test_owner_decision_is_bound_and_cannot_waive_gates():
    evidence = synthetic_evidence()
    draft = builder.build_decision(evidence)
    evidence["owner_decision"] = {
        "chosen_candidate": evidence["candidates"][0]["id"],
        "actor": "pilot owner",
        "decided_at": "2026-07-10T00:00:00Z",
        "rationale": "Bound decision after a documented tie.",
        "score_input_hash": draft["score_input_hash"],
    }
    assert builder.build_decision(evidence)["decision_status"] == "selected"
    for candidate in evidence["candidates"]:
        candidate["hard_gates"]["public_safe_fixture"] = False
    assert builder.build_decision(evidence)["selection"] is None


def test_selected_pilot_is_complete():
    evidence = synthetic_evidence()
    score_candidates(evidence, (2, 4, 3))
    selection = builder.build_decision(evidence)["selection"]
    assert set(selection) >= {"jurisdiction", "county_cluster", "acreage_mode", "project_class", "primary_persona", "rationale"}
    assert selection["primary_persona"] == "broker_project_manager"


def test_ready_counties_require_specific_evidence():
    evidence = synthetic_evidence()
    evidence["candidates"][0]["county_evidence"][0].pop("official_source")
    with pytest.raises(ValueError, match="county evidence"):
        builder.build_decision(evidence)


def test_primary_county_readiness_cannot_be_inherited():
    evidence = synthetic_evidence()
    evidence["candidates"][0]["county_evidence"][0]["readiness"] = "conditional"
    candidate = next(item for item in builder.build_decision(evidence)["candidates"] if item["id"] == evidence["candidates"][0]["id"])
    assert "primary_county_ready" in candidate["failed_gates"]


def test_workflow_has_eight_ordered_stages_and_distinct_personas():
    decision = builder.build_decision(synthetic_evidence())
    assert [stage["id"] for stage in decision["workflow"]] == [
        "intake", "aoi_tract_decomposition", "work_plan", "assignment",
        "evidence_capture", "exception_handling", "qa_signoff", "packet_delivery",
    ]
    assert {item["id"] for item in decision["personas"]} == {
        "broker_project_manager", "landman", "trainee", "title_examiner", "underwriter",
    }


def test_federal_and_title_evidence_are_separate_and_success_is_mode_aware():
    evidence = synthetic_evidence()
    score_candidates(evidence, (4, 3, 2))
    private = builder.build_decision(evidence)
    assert private["evidence_boundaries"]["federal"] != private["evidence_boundaries"]["county_title"]
    assert "federal_deferred" in private["success_criteria"]
    evidence["candidates"][1]["acreage_mode"] = "mixed"
    evidence["candidates"][1]["federal_deferred"] = False
    evidence["candidates"][1]["hard_gates"]["blm_mlrs_ready"] = True
    score_candidates(evidence, (2, 4, 3))
    assert "blm_mlrs_evidence" in builder.build_decision(evidence)["success_criteria"]


def test_builder_check_detects_html_or_yaml_drift(tmp_path):
    evidence = tmp_path / "evidence.yaml"
    decision = tmp_path / "decision.yaml"
    report = tmp_path / "decision.html"
    evidence.write_text(yaml.safe_dump(synthetic_evidence(), sort_keys=True), encoding="utf-8")
    command = [sys.executable, str(BUILDER_PATH), "--evidence", str(evidence), "--decision", str(decision), "--html", str(report)]
    assert subprocess.run(command, check=False).returncode == 0
    report.write_text("drift\n", encoding="utf-8")
    assert subprocess.run([*command, "--check"], check=False).returncode != 0


def test_generation_is_byte_deterministic_and_html_matches_yaml():
    evidence = synthetic_evidence()
    first = builder.render_outputs(evidence)
    second = builder.render_outputs(copy.deepcopy(evidence))
    assert first == second
    decision = yaml.safe_load(first[0])
    embedded = json.loads(first[1].split('<script id="decision-data" type="application/json">')[1].split("</script>")[0])
    assert embedded["decision_status"] == decision["decision_status"]
    assert embedded["workflow"] == decision["workflow"]
    assert first[0].endswith("\n") and first[1].endswith("\n")


def test_outreach_public_safe_and_legal_boundaries():
    decision = builder.build_decision(synthetic_evidence())
    assert decision["authorization"] == {"outreach": "not_authorized", "account_creation": "not_authorized"}
    assert "no title opinion" in decision["legal_boundary"].lower()
    assert "public-safe" in decision["fixture_boundary"].lower()
