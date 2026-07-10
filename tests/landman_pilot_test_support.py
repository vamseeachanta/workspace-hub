"""Synthetic evidence builders for Landman pilot contract tests."""

from __future__ import annotations


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
AUTHORIZATION = {
    "outreach": "not_authorized",
    "account_creation": "not_authorized",
    "paid_portals": "not_authorized",
    "representation_of_a_and_ce": "not_authorized",
}
ANCHORS = (
    "Official evidence contradicts readiness or pilot fit",
    "Conceptual relevance only; no verified access or reproducible evidence",
    "Official source is accessible but material limitations remain untested or manual",
    "Access and pilot relevance are verified with disclosed limitations",
    "Verified and reproducible with a public-safe fixture path",
    "Verified, reproducible, and fully fits the declared broker workflow and pilot boundary",
)


def _source_rows(candidate_id: str) -> list[dict]:
    return [
        {
            "id": f"{candidate_id}-{criterion}",
            "criterion": criterion,
            "source_url": f"https://example.gov/{candidate_id}/{criterion}",
            "observed_at": "2026-07-09T23:15:20Z",
            "access_state": "public",
            "confidence": "verified",
            "reproducible": False,
            "limitation": "Research evidence only; no title conclusion.",
        }
        for criterion in CRITERIA
    ]


def _county_rows(counties: tuple[str, str]) -> list[dict]:
    return [
        {
            "county": county,
            "official_source": f"{county} Recorder",
            "source_url": f"https://example.gov/{county}",
            "observed_at": "2026-07-09T23:15:20Z",
            "access_state": "public",
            "fee_account": "no_paid_or_account_required",
            "index": "official index",
            "images": "not required",
            "confidence": "verified",
            "limitation": "No title search or legal conclusion.",
            "readiness": "ready" if county == counties[0] else "conditional",
        }
        for county in counties
    ]


def _evidence_classes(candidate_id: str) -> list[dict]:
    return [
        {
            "class": "federal",
            "source_url": f"https://example.gov/{candidate_id}/federal",
            "status": "deferred",
        },
        {
            "class": "state_regulator",
            "source_url": f"https://example.gov/{candidate_id}/regulator",
            "status": "available",
        },
        {
            "class": "county_title",
            "source_url": f"https://example.gov/{candidate_id}/county-title",
            "status": "manual",
        },
    ]


def _candidate(index: int, jurisdiction: str, counties: tuple[str, str]) -> dict:
    candidate_id = f"candidate-{index}"
    return {
        "id": candidate_id,
        "jurisdiction": jurisdiction,
        "county_cluster": list(counties),
        "acreage_mode": "private_only",
        "federal_deferred": True,
        "project_class": "public-source pilot",
        "primary_persona": "broker_project_manager",
        "primary_county": counties[0],
        "county_evidence": _county_rows(counties),
        "evidence_classes": _evidence_classes(candidate_id),
        "evidence_rows": _source_rows(candidate_id),
        "scores": {
            criterion: {
                "score": 3,
                "anchor": 3,
                "evidence_ids": [f"{candidate_id}-{criterion}"],
            }
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


def synthetic_evidence() -> dict:
    candidates = [
        _candidate(index, jurisdiction, counties)
        for index, (jurisdiction, counties) in enumerate(CLUSTERS)
    ]
    return {
        "schema_version": "1.0",
        "decision_timestamp": "2026-07-09T23:15:20Z",
        "renderer_version": "1.0",
        "weights": dict(zip(CRITERIA, (25, 25, 20, 15, 15))),
        "score_anchors": {str(score): ANCHORS[score] for score in range(6)},
        "authorization": dict(AUTHORIZATION),
        "candidates": candidates,
    }


def score_candidates(evidence: dict, values: tuple[int, int, int]) -> None:
    for candidate, value in zip(evidence["candidates"], values, strict=True):
        for criterion, score in candidate["scores"].items():
            score["score"] = score["anchor"] = value
            if value >= 4:
                row = next(
                    row
                    for row in candidate["evidence_rows"]
                    if row["id"] in score["evidence_ids"]
                )
                row.update({"confidence": "verified", "reproducible": True})
                if criterion == "fixture_reproducibility":
                    row.update(
                        {
                            "source_url": (
                                "https://raw.githubusercontent.com/example/repo/"
                                f"{'a' * 40}/fixture.json"
                            ),
                            "artifact_sha256": "b" * 64,
                        }
                    )


def ranked_candidate(decision: dict, evidence: dict, index: int = 0) -> dict:
    candidate_id = evidence["candidates"][index]["id"]
    return next(item for item in decision["candidates"] if item["id"] == candidate_id)
