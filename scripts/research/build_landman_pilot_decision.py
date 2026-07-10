"""Build the deterministic, public-safe Landman pilot decision artifacts."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

import yaml


ROOT = Path(__file__).parents[2]
DEFAULT_EVIDENCE = ROOT / "docs/reports/landman/2026-07-09-pilot-evidence.yaml"
DEFAULT_DECISION = ROOT / "docs/reports/landman/2026-07-09-pilot-decision.yaml"
DEFAULT_HTML = ROOT / "docs/reports/landman/2026-07-09-pilot-decision.html"
CRITERIA = (
    "broker_workflow_value", "public_source_readiness", "county_title_feasibility",
    "fixture_reproducibility", "delivery_exception_learning",
)
EXPECTED_CLUSTERS = (
    ("Texas", ("Midland", "Reeves")), ("Oklahoma", ("Grady", "Canadian")),
    ("Colorado", ("Rio Blanco", "Garfield")),
)
UTC_TIMESTAMP = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def decimal_text(value: Decimal, places: int | None = None) -> str:
    if places is not None:
        value = value.quantize(Decimal("1." + "0" * places), rounding=ROUND_HALF_UP)
        return format(value, f".{places}f")
    return format(value, "f").rstrip("0").rstrip(".") or "0"


def canonical_hash(evidence: dict) -> str:
    source = {key: value for key, value in evidence.items() if key != "owner_decision"}
    encoded = json.dumps(source, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def validate_candidate(candidate: dict, weights: dict) -> None:
    required = {"id", "jurisdiction", "county_cluster", "acreage_mode", "primary_county", "county_evidence", "evidence_rows", "scores", "hard_gates"}
    require(required <= candidate.keys(), "candidate is missing required fields")
    counties = candidate["county_cluster"]
    require(len(counties) == 2 and len(set(counties)) == 2, "candidate must have exactly two counties")
    rows = candidate["county_evidence"]
    require({row.get("county") for row in rows} == set(counties), "county evidence must be specific to each county")
    county_fields = {"official_source", "source_url", "observed_at", "access_state", "fee_account", "index", "images", "confidence", "limitation", "readiness"}
    for row in rows:
        require(county_fields <= row.keys(), "county evidence is missing required fields")
        require(UTC_TIMESTAMP.match(str(row["observed_at"])) is not None, "county evidence timestamp must be UTC")
    evidence_ids = {row.get("id") for row in candidate["evidence_rows"]}
    require(len(evidence_ids) == len(candidate["evidence_rows"]), "evidence row IDs must be unique")
    for row in candidate["evidence_rows"]:
        require({"criterion", "source_url", "observed_at", "access_state", "confidence", "limitation"} <= row.keys(), "evidence row is incomplete")
        require(row["criterion"] in weights and row["source_url"].startswith("https://"), "evidence row is not sourced")
    require(set(candidate["scores"]) == set(weights), "candidate scores do not match declared criteria")
    for criterion, score in candidate["scores"].items():
        value = score.get("score")
        require(value == "unknown" or type(value) is int and 0 <= value <= 5, f"{criterion} score must be 0 to 5 or unknown")
        require(score.get("evidence_ids") and set(score["evidence_ids"]) <= evidence_ids, "score must cite evidence rows")


def validate_evidence(evidence: dict) -> None:
    require(evidence.get("schema_version") == "1.0", "unsupported evidence schema")
    require(UTC_TIMESTAMP.match(str(evidence.get("decision_timestamp", ""))) is not None, "decision timestamp must be UTC")
    require(evidence.get("renderer_version"), "renderer version is required")
    weights = evidence.get("weights", {})
    require(set(weights) == set(CRITERIA) and sum(weights.values()) == 100, "weights must use the fixed criteria and total 100")
    require(set(evidence.get("score_anchors", {})) == {str(value) for value in range(6)}, "shared score anchors are required")
    observed_clusters = [(item.get("jurisdiction"), tuple(item.get("county_cluster", ()))) for item in evidence.get("candidates", [])]
    require(tuple(observed_clusters) == EXPECTED_CLUSTERS, "candidate clusters must be the declared TX/OK/CO comparison")
    for candidate in evidence["candidates"]:
        validate_candidate(candidate, weights)


def candidate_score(candidate: dict, weights: dict) -> Decimal | None:
    if any(item["score"] == "unknown" for item in candidate["scores"].values()):
        return None
    return sum((Decimal(item["score"]) / Decimal(5) * Decimal(weights[key]) for key, item in candidate["scores"].items()), Decimal())


def failed_gates(candidate: dict) -> list[str]:
    gates = candidate["hard_gates"]
    required_true = ("complete_evidence", "public_safe_fixture", "separate_evidence_classes", "research_assistance_only")
    failures = [gate for gate in required_true if gates.get(gate) is not True]
    primary_ready = any(row["county"] == candidate["primary_county"] and row["readiness"] == "ready" for row in candidate["county_evidence"])
    if gates.get("primary_county_ready") is not True or not primary_ready:
        failures.append("primary_county_ready")
    if any(item["score"] == "unknown" for item in candidate["scores"].values()):
        failures.append("unknown_score")
    if gates.get("paid_or_account_required") is not False:
        failures.append("paid_or_account_required")
    if candidate["acreage_mode"] in {"federal", "mixed"} and gates.get("blm_mlrs_ready") is not True:
        failures.append("blm_mlrs_ready")
    if candidate["acreage_mode"] == "private_only" and candidate.get("federal_deferred") is not True:
        failures.append("federal_deferred")
    return failures


def ranked_candidates(candidates: list[dict], weights: dict) -> list[dict]:
    results = []
    for candidate in candidates:
        raw_score = candidate_score(candidate, weights)
        result = {key: candidate[key] for key in ("id", "jurisdiction", "county_cluster", "acreage_mode", "project_class", "primary_persona", "primary_county")}
        result.update({"raw_score": decimal_text(raw_score) if raw_score is not None else None, "display_score": decimal_text(raw_score, 2) if raw_score is not None else "unknown", "eligible": not failed_gates(candidate), "failed_gates": failed_gates(candidate)})
        results.append(result)
    return sorted(results, key=lambda item: (item["raw_score"] is not None, Decimal(item["raw_score"] or "0"), item["id"]), reverse=True)


def sensitivity(candidates: list[dict], weights: dict) -> list[dict]:
    variants = []
    for added in CRITERIA:
        for removed in CRITERIA:
            if added == removed:
                continue
            variant_weights = dict(weights)
            variant_weights[added] += 5
            variant_weights[removed] -= 5
            ranking = ranked_candidates(candidates, variant_weights)
            eligible = [item for item in ranking if item["eligible"]]
            leader = eligible[0]["id"] if eligible and (len(eligible) == 1 or eligible[0]["raw_score"] != eligible[1]["raw_score"]) else None
            variants.append({"added_criterion": added, "removed_criterion": removed, "weights": variant_weights, "winner": leader})
    return variants


def workflow() -> list[dict]:
    ids = ("intake", "aoi_tract_decomposition", "work_plan", "assignment", "evidence_capture", "exception_handling", "qa_signoff", "packet_delivery")
    return [{"id": stage, "owner": "broker_project_manager", "input": "reviewed public research", "output": "auditable work product", "evidence_requirement": "claim-level provenance", "stop_condition": "missing evidence or unauthorized action"} for stage in ids]


def selection_for(ranking: list[dict], variants: list[dict], evidence: dict, score_hash: str) -> tuple[str, str, dict | None]:
    eligible = [item for item in ranking if item["eligible"]]
    if not eligible:
        return "owner_decision_required", "no_eligible_candidates", None
    tied = len(eligible) > 1 and eligible[0]["raw_score"] == eligible[1]["raw_score"]
    variant_winners = {item["winner"] for item in variants}
    reason = "tied_leaders" if tied else "sensitivity_change" if variant_winners != {eligible[0]["id"]} else "selected"
    owner = evidence.get("owner_decision")
    if reason == "selected":
        return "selected", reason, selected_fields(eligible[0])
    if owner is None:
        return "owner_decision_required", reason, None
    required = {"chosen_candidate", "actor", "decided_at", "rationale", "score_input_hash"}
    require(required <= owner.keys() and UTC_TIMESTAMP.match(str(owner["decided_at"])), "owner decision is incomplete")
    require(owner["score_input_hash"] == score_hash, "owner decision hash does not match evidence")
    chosen = next((item for item in eligible if item["id"] == owner["chosen_candidate"]), None)
    require(chosen is not None, "owner decision must choose an eligible ranked candidate")
    return "selected", "owner_decision_recorded", selected_fields(chosen, owner["rationale"])


def selected_fields(candidate: dict, rationale: str | None = None) -> dict:
    fields = ("id", "jurisdiction", "county_cluster", "acreage_mode", "project_class", "primary_persona", "primary_county")
    selection = {"candidate_id" if key == "id" else key: candidate[key] for key in fields}
    selection["rationale"] = rationale or "Highest eligible raw score with no sensitivity change."
    return selection


def build_decision(evidence: dict) -> dict:
    validate_evidence(evidence)
    score_hash = canonical_hash(evidence)
    ranking = ranked_candidates(evidence["candidates"], evidence["weights"])
    variants = sensitivity(evidence["candidates"], evidence["weights"])
    status, reason, selection = selection_for(ranking, variants, evidence, score_hash)
    ledger = [{"candidate_id": candidate["id"], **row} for candidate in evidence["candidates"] for row in candidate["evidence_rows"]]
    return {
        "schema_version": evidence["schema_version"], "decision_timestamp": evidence["decision_timestamp"], "renderer_version": evidence["renderer_version"],
        "score_input_hash": score_hash, "decision_status": status, "decision_reason": reason, "selection": selection,
        "weights": evidence["weights"], "score_anchors": evidence["score_anchors"], "candidates": ranking, "sensitivity": variants,
        "authorization": evidence["authorization"], "source_ledger": ledger, "workflow": workflow(),
        "personas": [{"id": item, "responsibility": f"{item.replace('_', ' ')} responsibility"} for item in ("broker_project_manager", "landman", "trainee", "title_examiner", "underwriter")],
        "evidence_boundaries": {"federal": "BLM/MLRS lease and case evidence, not ownership.", "regulator": "State regulator evidence, separate from federal and title.", "county_title": "County access and manual research evidence, not a title opinion."},
        "fixture_boundary": "Only public-safe fixtures without paid portal use or account creation are eligible.", "legal_boundary": "Research assistance only; no legal advice and no title opinion.",
        "success_criteria": success_criteria(selection), "risks": ["Mapped federal feature counts are directional, not acreage or unique-lease totals.", "County/title gaps remain separate from federal and regulator evidence."],
    }


def success_criteria(selection: dict | None) -> list[str]:
    criteria = ["winning_jurisdiction_regulator_item", "winning_primary_county_title_manual_or_unavailable_exception", "provenance_or_unavailable_coverage_100_percent", "versioned_reviewer_signoff"]
    if selection is None:
        return criteria
    return criteria + (["blm_mlrs_evidence"] if selection and selection["acreage_mode"] in {"federal", "mixed"} else ["federal_deferred"])


def render_html(decision: dict) -> str:
    data = json.dumps(decision, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    links = "".join(f'<li><a href="{html.escape(row["source_url"], quote=True)}">{html.escape(row["id"])}</a></li>' for row in decision["source_ledger"])
    title = "Landman Pilot Decision"
    return f'<!doctype html>\n<html lang="en">\n<head><meta charset="utf-8"><title>{title}</title></head>\n<body><main><h1>{title}</h1><p>Status: {html.escape(decision["decision_status"])}</p><p>{html.escape(decision["legal_boundary"])}</p><ul>{links}</ul></main><script id="decision-data" type="application/json">{data}</script></body>\n</html>\n'


def render_outputs(evidence: dict) -> tuple[str, str]:
    decision = build_decision(evidence)
    document = yaml.safe_dump(decision, sort_keys=True, allow_unicode=False, default_flow_style=False, width=1000)
    return document, render_html(decision)


def write_outputs(evidence_path: Path, decision_path: Path, html_path: Path, check: bool) -> bool:
    evidence = yaml.safe_load(evidence_path.read_text(encoding="utf-8"))
    decision, report = render_outputs(evidence)
    if check:
        return decision_path.read_bytes() == decision.encode("utf-8") and html_path.read_bytes() == report.encode("utf-8")
    decision_path.parent.mkdir(parents=True, exist_ok=True)
    decision_path.write_text(decision, encoding="utf-8", newline="\n")
    html_path.write_text(report, encoding="utf-8", newline="\n")
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence", type=Path, default=DEFAULT_EVIDENCE)
    parser.add_argument("--decision", type=Path, default=DEFAULT_DECISION)
    parser.add_argument("--html", type=Path, default=DEFAULT_HTML)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    return 0 if write_outputs(args.evidence, args.decision, args.html, args.check) else 1


if __name__ == "__main__":
    raise SystemExit(main())
