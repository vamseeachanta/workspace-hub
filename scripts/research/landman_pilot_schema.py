"""Schema and evidence validation for the Landman pilot decision."""

from __future__ import annotations

import hashlib
import json
import re


CRITERIA = (
    "broker_workflow_value",
    "public_source_readiness",
    "county_title_feasibility",
    "fixture_reproducibility",
    "delivery_exception_learning",
)
EXPECTED_CLUSTERS = (
    ("Texas", ("Midland", "Reeves")),
    ("Oklahoma", ("Grady", "Canadian")),
    ("Colorado", ("Rio Blanco", "Garfield")),
)
MODES = {"private_only", "mixed", "federal"}
CLASS_NAMES = {"federal", "state_regulator", "county_title"}
AUTHORIZATION = {
    "outreach": "not_authorized",
    "account_creation": "not_authorized",
    "paid_portals": "not_authorized",
    "representation_of_a_and_ce": "not_authorized",
}
SCORE_ANCHORS = {
    "0": "Official evidence contradicts readiness or pilot fit",
    "1": "Conceptual relevance only; no verified access or reproducible evidence",
    "2": "Official source is accessible but material limitations remain untested or manual",
    "3": "Access and pilot relevance are verified with disclosed limitations",
    "4": "Verified and reproducible with a public-safe fixture path",
    "5": "Verified, reproducible, and fully fits the declared broker workflow and pilot boundary",
}
UTC_TIMESTAMP = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
WORKFLOW = (
    {
        "id": "intake",
        "owner": "broker_project_manager",
        "input": "authorized intake brief and public AOI",
        "output": "approved research scope",
        "evidence_requirement": "scope provenance and authorization state",
        "stop_condition": "scope requires outreach or private data",
    },
    {
        "id": "aoi_tract_decomposition",
        "owner": "landman",
        "input": "approved AOI and public reference maps",
        "output": "tract and jurisdiction worklist",
        "evidence_requirement": "source-linked tract assumptions",
        "stop_condition": "tract identity cannot be stated as research evidence",
    },
    {
        "id": "work_plan",
        "owner": "broker_project_manager",
        "input": "tract worklist and source constraints",
        "output": "sequenced assignment plan",
        "evidence_requirement": "named source, exception, and review gates",
        "stop_condition": "required source needs a paid portal or account",
    },
    {
        "id": "assignment",
        "owner": "broker_project_manager",
        "input": "reviewable assignment plan",
        "output": "bounded landman or trainee task",
        "evidence_requirement": "role, due state, and stop condition",
        "stop_condition": "task crosses a title-review responsibility",
    },
    {
        "id": "evidence_capture",
        "owner": "landman",
        "input": "bounded public-source task",
        "output": "claim ledger with source links",
        "evidence_requirement": "observed timestamp, confidence, and limitation",
        "stop_condition": "claim lacks public provenance",
    },
    {
        "id": "exception_handling",
        "owner": "title_examiner",
        "input": "unavailable, conflicting, or manual-only evidence",
        "output": "classified exception record",
        "evidence_requirement": "unresolved boundary and escalation reason",
        "stop_condition": "exception would require a title opinion",
    },
    {
        "id": "qa_signoff",
        "owner": "underwriter",
        "input": "evidence ledger and exception record",
        "output": "versioned risk signoff",
        "evidence_requirement": "coverage and limitation review",
        "stop_condition": "material uncertainty is not disclosed",
    },
    {
        "id": "packet_delivery",
        "owner": "broker_project_manager",
        "input": "signed-off public research packet",
        "output": "delivery packet and next-step queue",
        "evidence_requirement": "review version and source manifest",
        "stop_condition": "packet implies legal advice or ownership",
    },
)
PERSONAS = (
    {
        "id": "broker_project_manager",
        "responsibility": "owns scope, assignment, delivery, and authorization boundaries",
    },
    {
        "id": "landman",
        "responsibility": "captures public research evidence and records field-level limitations",
    },
    {
        "id": "trainee",
        "responsibility": "prepares supervised source extracts without making research conclusions",
    },
    {
        "id": "title_examiner",
        "responsibility": "classifies title-research exceptions without issuing a title opinion",
    },
    {
        "id": "underwriter",
        "responsibility": "reviews disclosed risk and records versioned acceptance or rejection",
    },
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def canonical_hash(evidence: dict) -> str:
    source = {key: value for key, value in evidence.items() if key != "owner_decision"}
    encoded = json.dumps(
        source, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    )
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def classes_are_distinct(candidate: dict) -> bool:
    classes = candidate.get("evidence_classes", [])
    names = {item.get("class") for item in classes}
    urls = [item.get("source_url") for item in classes]
    federal = next((item for item in classes if item.get("class") == "federal"), {})
    expected = (
        "deferred" if candidate.get("acreage_mode") == "private_only" else "available"
    )
    valid_urls = all(
        isinstance(url, str) and url.startswith("https://") and item.get("status")
        for url, item in zip(urls, classes, strict=True)
    )
    return (
        len(classes) == 3
        and names == CLASS_NAMES
        and len(set(urls)) == 3
        and valid_urls
        and federal.get("status") == expected
    )


def _validate_county_rows(candidate: dict) -> None:
    counties = candidate["county_cluster"]
    rows = candidate["county_evidence"]
    fields = {
        "official_source",
        "source_url",
        "observed_at",
        "access_state",
        "fee_account",
        "index",
        "images",
        "confidence",
        "limitation",
        "readiness",
    }
    require(
        len(counties) == 2
        and len(set(counties)) == 2
        and candidate["primary_county"] in counties,
        "candidate must have exactly two counties",
    )
    require(
        {row.get("county") for row in rows} == set(counties),
        "county evidence must be specific to each county",
    )
    for row in rows:
        complete = fields <= row.keys() and UTC_TIMESTAMP.match(str(row["observed_at"]))
        require(
            complete and row["source_url"].startswith("https://"),
            "county evidence is incomplete",
        )


def _index_evidence_rows(candidate: dict, weights: dict) -> dict[str, dict]:
    rows = {row.get("id"): row for row in candidate["evidence_rows"]}
    require(
        len(rows) == len(candidate["evidence_rows"]), "evidence row IDs must be unique"
    )
    fields = {
        "criterion",
        "source_url",
        "observed_at",
        "access_state",
        "confidence",
        "reproducible",
        "limitation",
    }
    for row in rows.values():
        complete = fields <= row.keys() and row["criterion"] in weights
        sourced = row["source_url"].startswith("https://") and UTC_TIMESTAMP.match(
            str(row["observed_at"])
        )
        require(
            complete and sourced and type(row["reproducible"]) is bool,
            "evidence row is incomplete",
        )
    return rows


def _validate_score(criterion: str, score: dict, rows: dict[str, dict]) -> None:
    value = score.get("score")
    ids = score.get("evidence_ids", [])
    require(
        value == "unknown" or type(value) is int and 0 <= value <= 5,
        f"{criterion} score must be 0 to 5 or unknown",
    )
    matching = ids and set(ids) <= set(rows)
    matching = matching and all(
        rows[row_id]["criterion"] == criterion for row_id in ids
    )
    require(matching, "score evidence IDs must match their criterion")
    if value != "unknown":
        require(score.get("anchor") == value, "score anchor must match score")
    if isinstance(value, int) and value >= 4:
        reproducible = all(
            rows[row_id]["confidence"] == "verified" and rows[row_id]["reproducible"]
            for row_id in ids
        )
        require(reproducible, "high scores require verified reproducible evidence")


def validate_candidate(candidate: dict, weights: dict) -> None:
    required = {
        "id",
        "jurisdiction",
        "county_cluster",
        "acreage_mode",
        "project_class",
        "primary_persona",
        "primary_county",
        "county_evidence",
        "evidence_classes",
        "evidence_rows",
        "scores",
        "hard_gates",
    }
    require(required <= candidate.keys(), "candidate is missing required fields")
    require(candidate["acreage_mode"] in MODES, "candidate acreage_mode is invalid")
    _validate_county_rows(candidate)
    rows = _index_evidence_rows(candidate, weights)
    require(
        set(candidate["scores"]) == set(weights),
        "candidate scores do not match declared criteria",
    )
    for criterion, score in candidate["scores"].items():
        _validate_score(criterion, score, rows)
    distinct = classes_are_distinct(candidate)
    declared = candidate["hard_gates"].get("separate_evidence_classes") is True
    require(distinct and declared, "evidence classes are not structurally distinct")


def validate_evidence(evidence: dict) -> None:
    valid_metadata = (
        evidence.get("schema_version") == "1.0"
        and UTC_TIMESTAMP.match(str(evidence.get("decision_timestamp", "")))
        and evidence.get("renderer_version")
    )
    require(valid_metadata, "evidence metadata is invalid")
    weights = evidence.get("weights", {})
    require(
        set(weights) == set(CRITERIA) and sum(weights.values()) == 100,
        "score contract is invalid",
    )
    require(
        evidence.get("score_anchors") == SCORE_ANCHORS, "score anchor text is invalid"
    )
    require(
        evidence.get("authorization") == AUTHORIZATION,
        "authorization must remain not_authorized",
    )
    observed = [
        (item.get("jurisdiction"), tuple(item.get("county_cluster", ())))
        for item in evidence.get("candidates", [])
    ]
    require(
        tuple(observed) == EXPECTED_CLUSTERS,
        "candidate clusters must be the declared TX/OK/CO comparison",
    )
    for candidate in evidence["candidates"]:
        validate_candidate(candidate, weights)
