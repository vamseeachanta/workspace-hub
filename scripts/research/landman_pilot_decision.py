"""Scoring and deterministic selection for the Landman pilot."""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Callable

from scripts.research.landman_pilot_schema import (
    CRITERIA,
    PERSONAS,
    UTC_TIMESTAMP,
    WORKFLOW,
    canonical_hash,
    classes_are_distinct,
    require,
    validate_evidence,
)


def decimal_text(value: Decimal, places: int | None = None) -> str:
    if places is not None:
        quantized = value.quantize(Decimal("1." + "0" * places), rounding=ROUND_HALF_UP)
        return format(quantized, f".{places}f")
    text = format(value, "f")
    return text.rstrip("0").rstrip(".") if "." in text else text


def candidate_score(candidate: dict, weights: dict) -> Decimal | None:
    if any(score["score"] == "unknown" for score in candidate["scores"].values()):
        return None
    return sum(
        (
            Decimal(score["score"]) / Decimal(5) * Decimal(weights[criterion])
            for criterion, score in candidate["scores"].items()
        ),
        Decimal(),
    )


def failed_gates(candidate: dict) -> list[str]:
    gates = candidate["hard_gates"]
    required = ("complete_evidence", "public_safe_fixture", "research_assistance_only")
    failures = [name for name in required if gates.get(name) is not True]
    primary_ready = any(
        row["county"] == candidate["primary_county"] and row["readiness"] == "ready"
        for row in candidate["county_evidence"]
    )
    if not primary_ready:
        failures.append("primary_county_ready")
    if any(score["score"] == "unknown" for score in candidate["scores"].values()):
        failures.append("unknown_score")
    if gates.get("paid_or_account_required") is not False:
        failures.append("paid_or_account_required")
    if not classes_are_distinct(candidate):
        failures.append("separate_evidence_classes")
    if (
        candidate["acreage_mode"] in {"federal", "mixed"}
        and gates.get("blm_mlrs_ready") is not True
    ):
        failures.append("blm_mlrs_ready")
    if (
        candidate["acreage_mode"] == "private_only"
        and candidate.get("federal_deferred") is not True
    ):
        failures.append("federal_deferred")
    return failures


def _ranked_candidate(candidate: dict, weights: dict) -> dict:
    raw = candidate_score(candidate, weights)
    fields = (
        "id",
        "jurisdiction",
        "county_cluster",
        "acreage_mode",
        "project_class",
        "primary_persona",
        "primary_county",
        "evidence_classes",
    )
    result = {key: candidate[key] for key in fields}
    failures = failed_gates(candidate)
    result.update(
        {
            "_raw_score": raw,
            "raw_score": decimal_text(raw) if raw is not None else None,
            "display_score": decimal_text(raw, 2) if raw is not None else "unknown",
            "eligible": not failures,
            "failed_gates": failures,
        }
    )
    return result


def ranked_candidates(candidates: list[dict], weights: dict) -> list[dict]:
    results = [_ranked_candidate(candidate, weights) for candidate in candidates]
    return sorted(
        results,
        key=lambda item: (
            item["_raw_score"] is not None,
            item["_raw_score"] or Decimal(),
            item["id"],
        ),
        reverse=True,
    )


def public_candidates(ranking: list[dict]) -> list[dict]:
    return [
        {key: value for key, value in item.items() if key != "_raw_score"}
        for item in ranking
    ]


def sensitivity(candidates: list[dict], weights: dict) -> list[dict]:
    variants = []
    for added in CRITERIA:
        for removed in CRITERIA:
            if added == removed:
                continue
            variant = dict(weights)
            variant[added] += 5
            variant[removed] -= 5
            eligible = [
                item
                for item in ranked_candidates(candidates, variant)
                if item["eligible"]
            ]
            unique = bool(eligible) and (
                len(eligible) == 1
                or eligible[0]["_raw_score"] != eligible[1]["_raw_score"]
            )
            winner = eligible[0]["id"] if unique else None
            variants.append(
                {
                    "added_criterion": added,
                    "removed_criterion": removed,
                    "total_weight": sum(variant.values()),
                    "winner": winner,
                }
            )
    return variants


def selected_fields(candidate: dict, rationale: str | None = None) -> dict:
    fields = (
        "id",
        "jurisdiction",
        "county_cluster",
        "acreage_mode",
        "project_class",
        "primary_persona",
        "primary_county",
    )
    result = {"candidate_id" if key == "id" else key: candidate[key] for key in fields}
    result["rationale"] = (
        rationale or "Highest eligible raw score with no sensitivity change."
    )
    return result


def _owner_selection(eligible: list[dict], evidence: dict, score_hash: str) -> dict:
    owner = evidence["owner_decision"]
    required = {
        "chosen_candidate",
        "actor",
        "decided_at",
        "rationale",
        "score_input_hash",
    }
    complete = required <= owner.keys() and UTC_TIMESTAMP.match(
        str(owner["decided_at"])
    )
    require(complete, "owner decision is incomplete")
    require(
        owner["score_input_hash"] == score_hash,
        "owner decision hash does not match evidence",
    )
    chosen = next(
        (item for item in eligible if item["id"] == owner["chosen_candidate"]), None
    )
    require(
        chosen is not None, "owner decision must choose an eligible ranked candidate"
    )
    return selected_fields(chosen, owner["rationale"])


def selection_for(
    ranking: list[dict], variants: list[dict], evidence: dict, score_hash: str
) -> tuple[str, str, dict | None]:
    eligible = [item for item in ranking if item["eligible"]]
    if not eligible:
        return "owner_decision_required", "no_eligible_candidates", None
    tied = len(eligible) > 1 and eligible[0]["_raw_score"] == eligible[1]["_raw_score"]
    sensitive = {item["winner"] for item in variants} != {eligible[0]["id"]}
    reason = (
        "tied_leaders" if tied else "sensitivity_change" if sensitive else "selected"
    )
    if reason == "selected":
        return "selected", reason, selected_fields(eligible[0])
    if evidence.get("owner_decision") is None:
        return "owner_decision_required", reason, None
    return (
        "selected",
        "owner_decision_recorded",
        _owner_selection(eligible, evidence, score_hash),
    )


def success_criteria(selection: dict | None) -> list[str]:
    criteria = [
        "winning_jurisdiction_regulator_item",
        "winning_primary_county_title_manual_or_unavailable_exception",
        "provenance_or_unavailable_coverage_100_percent",
        "versioned_reviewer_signoff",
    ]
    if selection is None:
        return criteria
    mode_item = (
        "blm_mlrs_evidence"
        if selection["acreage_mode"] in {"federal", "mixed"}
        else "federal_deferred"
    )
    return [*criteria, mode_item]


def source_ledger(candidates: list[dict]) -> list[dict]:
    return [
        {"candidate_id": candidate["id"], **row}
        for candidate in candidates
        for row in candidate["evidence_rows"]
    ]


def build_decision(
    evidence: dict,
    sensitivity_fn: Callable[[list[dict], dict], list[dict]] = sensitivity,
) -> dict:
    validate_evidence(evidence)
    score_hash = canonical_hash(evidence)
    ranking = ranked_candidates(evidence["candidates"], evidence["weights"])
    variants = sensitivity_fn(evidence["candidates"], evidence["weights"])
    status, reason, selection = selection_for(ranking, variants, evidence, score_hash)
    return {
        "schema_version": evidence["schema_version"],
        "decision_timestamp": evidence["decision_timestamp"],
        "renderer_version": evidence["renderer_version"],
        "score_input_hash": score_hash,
        "decision_status": status,
        "decision_reason": reason,
        "selection": selection,
        "closeout_ready": selection is not None,
        "weights": evidence["weights"],
        "score_anchors": evidence["score_anchors"],
        "candidates": public_candidates(ranking),
        "sensitivity": variants,
        "authorization": evidence["authorization"],
        "source_ledger": source_ledger(evidence["candidates"]),
        "workflow": list(WORKFLOW),
        "personas": list(PERSONAS),
        "evidence_boundaries": {
            "federal": "BLM/MLRS lease and case evidence, not ownership.",
            "regulator": "State regulator evidence, separate from federal and title.",
            "county_title": "County access and manual research evidence, not a title opinion.",
        },
        "fixture_boundary": "Only public-safe fixtures without paid portal use or account creation are eligible.",
        "legal_boundary": "Research assistance only; no legal advice and no title opinion.",
        "success_criteria": success_criteria(selection),
        "risks": [
            "Mapped federal feature counts are directional, not acreage or unique-lease totals.",
            "County/title gaps remain separate from federal and regulator evidence.",
        ],
    }
