"""Tests for the weekly skills-audit classification and ranking policy (#2282)."""
from __future__ import annotations

from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
POLICY_PATH = REPO_ROOT / "config" / "skills" / "weekly-audit-policy.yaml"
DOC_PATH = REPO_ROOT / "docs" / "standards" / "weekly-skills-audit-policy.md"

REQUIRED_BUCKETS = [
    "exact-duplicate",
    "canonical-wrapper-pair",
    "near-duplicate-same-intent",
    "stale-superseded",
    "adjacent-specialization",
    "generic-leaf-collision",
    "needs-human-review",
]
REQUIRED_SUMMARY_SECTIONS = [
    "new_findings",
    "changed_findings",
    "unresolved_high_confidence_findings",
    "suppressed_carry_forward_findings",
    "operational_errors_or_skipped_inputs",
]
REQUIRED_FINDING_FIELDS = [
    "finding_key",
    "classification",
    "severity",
    "confidence",
    "canonical_names",
    "paths",
    "summary",
    "recommended_action",
    "escalation_state",
    "is_new",
    "is_changed",
]
VALID_ESCALATION_STATES = {"no-escalation", "candidate"}
REQUIRED_SIGNALS = {
    "same_canonical_name",
    "same_primary_intent",
    "wrapper_redirect",
    "explicit_canonical_target",
    "substantial_overlap",
    "distinct_deliverable_surface",
    "generic_leaf_only",
    "maintained_replacement_exists",
    "conflicting_evidence",
    "insufficient_evidence",
}


def _load_policy() -> dict:
    assert POLICY_PATH.exists(), f"Missing policy file: {POLICY_PATH}"
    policy = yaml.safe_load(POLICY_PATH.read_text(encoding="utf-8"))
    assert isinstance(policy, dict), "Policy must parse to a mapping"
    return policy


def _validate_policy(policy: dict) -> None:
    required_keys = {
        "signal_vocabulary",
        "classification_buckets",
        "precedence_order",
        "finding_schema",
        "severity_levels",
        "confidence_levels",
        "weekly_summary_sections",
        "ranking_policy",
        "escalation_model",
        "carry_forward",
        "fixtures",
    }
    missing = required_keys - set(policy)
    assert not missing, f"Missing top-level keys: {sorted(missing)}"


def _bucket_map(policy: dict) -> dict[str, dict]:
    return {bucket["id"]: bucket for bucket in policy["classification_buckets"]}


def _signal_ids(policy: dict) -> set[str]:
    return {signal["id"] for signal in policy["signal_vocabulary"]}


def _matches_rule(signals: set[str], rule: dict) -> bool:
    match_all = set(rule.get("match_all", []))
    match_any = set(rule.get("match_any", []))
    exclude_if_any = set(rule.get("exclude_if_any", []))
    if exclude_if_any & signals:
        return False
    if not match_all.issubset(signals):
        return False
    if match_any and not (match_any & signals):
        return False
    return True


def _classify_fixture(policy: dict, fixture: dict) -> str:
    signals = set(fixture["signals"])
    buckets = _bucket_map(policy)
    for bucket_id in policy["precedence_order"]:
        if _matches_rule(signals, buckets[bucket_id]["rule"]):
            return bucket_id
    raise AssertionError(f"No bucket matched fixture {fixture['id']}")


def _expected_escalation_from_rules(policy: dict, classification: str) -> str:
    for rule in policy["escalation_model"]["rules"]:
        if classification in set(rule["when"]["classification_in"]):
            return rule["result"]
    raise AssertionError(f"No escalation rule for classification {classification}")


def _sort_findings(policy: dict, findings: list[dict]) -> list[dict]:
    ranking = policy["ranking_policy"]["finding_sort_order"]

    def key_for(item: dict):
        key = []
        for entry in ranking:
            value = item[entry["field"]]
            if "rank_order" in entry:
                rank = entry["rank_order"].index(value)
                key.append(rank)
            elif isinstance(value, bool):
                key.append((0 if value else 1) if entry["direction"] == "desc" else (1 if value else 0))
            else:
                key.append(value)
        return tuple(key)

    return sorted(findings, key=key_for)


def test_policy_file_exists_and_parses():
    _validate_policy(_load_policy())


def test_policy_rejects_invalid_policy_schema():
    invalid_policy = {"classification_buckets": []}
    try:
        _validate_policy(invalid_policy)
    except AssertionError as exc:
        assert "Missing top-level keys" in str(exc)
    else:
        raise AssertionError("Invalid policy must fail validation")


def test_policy_defines_signal_vocabulary_and_bounded_buckets():
    policy = _load_policy()
    assert _signal_ids(policy) == REQUIRED_SIGNALS
    assert [bucket["id"] for bucket in policy["classification_buckets"]] == REQUIRED_BUCKETS


def test_policy_rules_reference_only_known_signals():
    policy = _load_policy()
    known_signals = _signal_ids(policy)
    for bucket in policy["classification_buckets"]:
        rule = bucket["rule"]
        referenced = set(rule.get("match_all", [])) | set(rule.get("match_any", [])) | set(rule.get("exclude_if_any", []))
        assert referenced <= known_signals, f"Unknown signal in rule for {bucket['id']}"


def test_policy_precedence_is_single_winner_contract():
    policy = _load_policy()
    assert policy["precedence_order"] == REQUIRED_BUCKETS


def test_policy_defines_finding_schema_and_summary_sections():
    policy = _load_policy()
    schema_fields = [field["name"] for field in policy["finding_schema"]]
    assert schema_fields == REQUIRED_FINDING_FIELDS
    sections = [section["id"] for section in policy["weekly_summary_sections"]]
    assert sections == REQUIRED_SUMMARY_SECTIONS


def test_policy_defines_severity_and_confidence_levels():
    policy = _load_policy()
    assert [item["id"] for item in policy["severity_levels"]] == ["high", "medium", "low"]
    assert [item["id"] for item in policy["confidence_levels"]] == ["high", "medium", "low"]


def test_each_bucket_has_default_severity_and_confidence():
    policy = _load_policy()
    severities = {item["id"] for item in policy["severity_levels"]}
    confidences = {item["id"] for item in policy["confidence_levels"]}
    for bucket in policy["classification_buckets"]:
        assert bucket["default_severity"] in severities
        assert bucket["default_confidence"] in confidences


def test_fixture_classification_matches_bucket_rules():
    policy = _load_policy()
    for fixture in policy["fixtures"]:
        assert _classify_fixture(policy, fixture) == fixture["expected_bucket"]


def test_every_bucket_has_a_fixture_example():
    policy = _load_policy()
    fixture_buckets = {fixture["expected_bucket"] for fixture in policy["fixtures"]}
    assert fixture_buckets == set(REQUIRED_BUCKETS)


def test_fixture_fields_are_complete_and_reference_valid_values():
    policy = _load_policy()
    bucket_ids = set(REQUIRED_BUCKETS)
    severity_ids = {item["id"] for item in policy["severity_levels"]}
    confidence_ids = {item["id"] for item in policy["confidence_levels"]}
    for fixture in policy["fixtures"]:
        assert {"id", "scenario", "signals", "expected_bucket", "expected_severity", "expected_confidence", "expected_escalation"} <= set(fixture)
        assert set(fixture["signals"]) <= _signal_ids(policy)
        assert fixture["expected_bucket"] in bucket_ids
        assert fixture["expected_severity"] in severity_ids
        assert fixture["expected_confidence"] in confidence_ids
        assert fixture["expected_escalation"] in VALID_ESCALATION_STATES


def test_needs_human_review_fixture_wins_when_conflicting_evidence_is_present():
    policy = _load_policy()
    fixture = next(item for item in policy["fixtures"] if item["expected_bucket"] == "needs-human-review")
    assert _classify_fixture(policy, fixture) == "needs-human-review"


def test_policy_defines_deterministic_escalation_and_matches_fixtures():
    policy = _load_policy()
    states = {state["id"] for state in policy["escalation_model"]["states"]}
    assert states == VALID_ESCALATION_STATES
    for fixture in policy["fixtures"]:
        classification = fixture["expected_bucket"]
        assert _expected_escalation_from_rules(policy, classification) == fixture["expected_escalation"]


def test_policy_defines_carry_forward_behavior():
    policy = _load_policy()
    carry_forward = policy["carry_forward"]
    assert "unchanged_behavior" in carry_forward
    assert "suppression_rule" in carry_forward
    assert carry_forward["changed_but_unresolved_rule"]["surfaces_in"] == "changed_findings"


def test_policy_defines_ranking_contract():
    policy = _load_policy()
    ranking_policy = policy["ranking_policy"]
    assert ranking_policy["section_order"] == REQUIRED_SUMMARY_SECTIONS
    assert [item["field"] for item in ranking_policy["finding_sort_order"]] == [
        "escalation_state",
        "severity",
        "confidence",
        "is_new",
        "finding_key",
    ]


def test_ranking_contract_sorts_findings_deterministically():
    policy = _load_policy()
    findings = [
        {"finding_key": "z-last", "escalation_state": "no-escalation", "severity": "low", "confidence": "low", "is_new": False},
        {"finding_key": "a-candidate-medium", "escalation_state": "candidate", "severity": "medium", "confidence": "medium", "is_new": True},
        {"finding_key": "b-candidate-high", "escalation_state": "candidate", "severity": "high", "confidence": "high", "is_new": True},
        {"finding_key": "c-candidate-high-old", "escalation_state": "candidate", "severity": "high", "confidence": "high", "is_new": False},
    ]
    ordered = _sort_findings(policy, findings)
    assert [item["finding_key"] for item in ordered] == [
        "b-candidate-high",
        "c-candidate-high-old",
        "a-candidate-medium",
        "z-last",
    ]


def test_companion_doc_stays_consistent_with_yaml():
    policy = _load_policy()
    doc_text = DOC_PATH.read_text(encoding="utf-8")
    for signal in sorted(_signal_ids(policy)):
        assert f"`{signal}`" in doc_text
    for bucket in REQUIRED_BUCKETS:
        assert f"`{bucket}`" in doc_text
    for state in sorted(VALID_ESCALATION_STATES):
        assert f"`{state}`" in doc_text
