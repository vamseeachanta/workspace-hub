"""Tests for weekly skills audit classification and ranking policy (#2282).

Policy source: config/skills/weekly-audit-policy.yaml (authoritative)
Companion doc:  docs/standards/weekly-skills-audit-policy.md (explanatory only)
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
POLICY_PATH = REPO_ROOT / "config" / "skills" / "weekly-audit-policy.yaml"


# ---------------------------------------------------------------------------
# Minimal policy engine — loads YAML rules, applies them in test assertions
# ---------------------------------------------------------------------------

class PolicyValidationError(ValueError):
    """Raised when a policy YAML fails structural validation."""


def load_policy(path: Path = POLICY_PATH) -> dict[str, Any]:
    """Load and validate the policy YAML."""
    if not path.exists():
        raise FileNotFoundError(f"Policy file not found: {path}")
    policy = yaml.safe_load(path.read_text())
    validate_policy(policy)
    return policy


def validate_policy(policy: dict[str, Any]) -> None:
    """Raise PolicyValidationError if the policy is structurally invalid."""
    required_top_level = [
        "version",
        "finding_schema",
        "classification_buckets",
        "severity_rubric",
        "confidence_rubric",
        "carry_forward_rules",
        "escalation",
        "weekly_summary",
        "fixtures",
        "fallback_bucket",
    ]
    missing = [k for k in required_top_level if k not in policy]
    if missing:
        raise PolicyValidationError(f"Policy missing required top-level keys: {missing}")

    buckets = policy.get("classification_buckets", [])
    if not buckets:
        raise PolicyValidationError("classification_buckets must be non-empty")

    bucket_names = {b["bucket"] for b in buckets}
    required_buckets = {
        "exact-duplicate",
        "canonical-wrapper-pair",
        "adjacent-specialization",
        "generic-leaf-collision",
        "needs-human-review",
    }
    missing_buckets = required_buckets - bucket_names
    if missing_buckets:
        raise PolicyValidationError(f"Policy missing required buckets: {missing_buckets}")


class PolicyEngine:
    """Minimal engine that reads the YAML policy and applies its rules."""

    def __init__(self, policy: dict[str, Any]) -> None:
        self._policy = policy
        # Non-fallback buckets sorted by precedence (ascending = highest priority first)
        self._buckets = sorted(
            [b for b in policy["classification_buckets"] if not b.get("is_fallback")],
            key=lambda b: b["precedence"],
        )
        self._fallback = policy.get("fallback_bucket", "needs-human-review")

    def classify(self, signals: dict[str, bool]) -> str:
        """Return the classification bucket for a given signal set.

        Global rules are checked before bucket matching.  If no bucket matches,
        ``fallback_bucket`` is returned.
        """
        # 1. Global override rules (e.g. conflicting_signals always wins)
        for rule in self._policy.get("global_rules", []):
            if signals.get(rule["trigger_signal"]):
                return rule["forced_bucket"]

        # 2. Bucket matching in precedence order (lowest precedence number = highest priority)
        for bucket_def in self._buckets:
            required = bucket_def["criteria"]["required_signals"]
            excluded = bucket_def["criteria"]["excluded_signals"]
            if all(signals.get(s) for s in required) and not any(
                signals.get(s) for s in excluded
            ):
                return bucket_def["bucket"]

        # 3. Fallback
        return self._fallback

    def compute_escalation(self, severity: str, confidence: str) -> str:
        """Return escalation_state computed from current severity and confidence."""
        criteria = self._policy["escalation"]["candidate_criteria"]
        if severity == criteria["severity"] and confidence == criteria["confidence"]:
            return "candidate"
        return "no-escalation"

    def compute_carry_forward(self, prior: dict[str, Any], current: dict[str, Any]) -> str:
        """Return the carry-forward rule name ('unchanged', 'changed', 'suppressed')."""
        if current.get("suppressed"):
            return "suppressed"

        change_triggers = self._policy["carry_forward_rules"]["changed"]["change_triggers"]
        trigger_map = {
            "severity_changed": ("severity", prior, current),
            "confidence_changed": ("confidence", prior, current),
            "escalation_state_changed": ("escalation_state", prior, current),
            "canonical_names_changed": ("canonical_names", prior, current),
            "paths_changed": ("paths", prior, current),
        }
        for trigger in change_triggers:
            if trigger in trigger_map:
                field, p, c = trigger_map[trigger]
                if p.get(field) != c.get(field):
                    return "changed"

        return "unchanged"


# ---------------------------------------------------------------------------
# Pytest fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def policy() -> dict[str, Any]:
    return load_policy()


@pytest.fixture(scope="module")
def engine(policy: dict[str, Any]) -> PolicyEngine:
    return PolicyEngine(policy)


def _fixture(policy: dict[str, Any], bucket_key: str, index: int = 0) -> dict[str, Any]:
    return policy["fixtures"][bucket_key][index]


# ---------------------------------------------------------------------------
# 1. Classification tests — one per bucket
# ---------------------------------------------------------------------------

def test_policy_classifies_exact_duplicate(policy: dict, engine: PolicyEngine) -> None:
    fixture = _fixture(policy, "exact_duplicate")
    result = engine.classify(fixture["signals"])
    assert result == "exact-duplicate"
    assert fixture["expected_bucket"] == "exact-duplicate"


def test_policy_classifies_canonical_wrapper_pair(policy: dict, engine: PolicyEngine) -> None:
    fixture = _fixture(policy, "canonical_wrapper_pair")
    result = engine.classify(fixture["signals"])
    assert result == "canonical-wrapper-pair"
    assert fixture["expected_bucket"] == "canonical-wrapper-pair"


def test_policy_classifies_adjacent_specialization(policy: dict, engine: PolicyEngine) -> None:
    fixture = _fixture(policy, "adjacent_specialization")
    result = engine.classify(fixture["signals"])
    assert result == "adjacent-specialization"
    assert fixture["expected_bucket"] == "adjacent-specialization"


def test_policy_classifies_generic_leaf_collision(policy: dict, engine: PolicyEngine) -> None:
    fixture = _fixture(policy, "generic_leaf_collision")
    result = engine.classify(fixture["signals"])
    assert result == "generic-leaf-collision"
    assert fixture["expected_bucket"] == "generic-leaf-collision"


def test_policy_routes_ambiguous_case_to_needs_human_review(
    policy: dict, engine: PolicyEngine
) -> None:
    fixture = _fixture(policy, "needs_human_review")
    result = engine.classify(fixture["signals"])
    assert result == "needs-human-review"
    assert fixture["expected_bucket"] == "needs-human-review"


# ---------------------------------------------------------------------------
# 2. Precedence — multi-match resolves to highest-priority bucket
# ---------------------------------------------------------------------------

def test_policy_precedence_picks_highest_priority_bucket(
    policy: dict, engine: PolicyEngine
) -> None:
    fixture = _fixture(policy, "precedence_multi_match")
    result = engine.classify(fixture["signals"])
    assert result == fixture["expected_bucket"]

    # Verify every declared loser would have matched on its own criteria
    for loser_name in fixture.get("expected_precedence_losers", []):
        loser_def = next(
            b for b in policy["classification_buckets"] if b["bucket"] == loser_name
        )
        required = loser_def["criteria"]["required_signals"]
        excluded = loser_def["criteria"]["excluded_signals"]
        sigs = fixture["signals"]
        loser_matches = all(sigs.get(s) for s in required) and not any(
            sigs.get(s) for s in excluded
        )
        assert loser_matches, f"Expected loser '{loser_name}' should have matched but didn't"

        winner_def = next(
            b for b in policy["classification_buckets"] if b["bucket"] == result
        )
        assert winner_def["precedence"] < loser_def["precedence"], (
            f"Winner precedence {winner_def['precedence']} should be lower than "
            f"loser precedence {loser_def['precedence']}"
        )


# ---------------------------------------------------------------------------
# 3. Mutual exclusivity — every fixture resolves to exactly one bucket
# ---------------------------------------------------------------------------

def test_policy_bucket_resolution_is_mutually_exclusive(
    policy: dict, engine: PolicyEngine
) -> None:
    primary_keys = [
        "exact_duplicate",
        "canonical_wrapper_pair",
        "adjacent_specialization",
        "generic_leaf_collision",
        "needs_human_review",
    ]
    for key in primary_keys:
        fixture = _fixture(policy, key)
        result = engine.classify(fixture["signals"])
        assert result == fixture["expected_bucket"], (
            f"Fixture '{fixture['finding_key']}' → expected '{fixture['expected_bucket']}', "
            f"got '{result}'"
        )


# ---------------------------------------------------------------------------
# 4. Severity and confidence rubric
# ---------------------------------------------------------------------------

def test_policy_assigns_severity_and_confidence_levels(
    policy: dict, engine: PolicyEngine
) -> None:
    valid_severities = {"high", "medium", "low"}
    valid_confidences = {"high", "medium", "low"}

    for bucket_def in policy["classification_buckets"]:
        name = bucket_def["bucket"]
        assert "severity" in bucket_def, f"{name} missing severity"
        assert bucket_def["severity"] in valid_severities, (
            f"{name} has invalid severity: {bucket_def['severity']}"
        )
        assert "confidence_default" in bucket_def, f"{name} missing confidence_default"
        assert bucket_def["confidence_default"] in valid_confidences, (
            f"{name} has invalid confidence_default: {bucket_def['confidence_default']}"
        )

    # Fixture expected values must match bucket defaults
    for key in ("exact_duplicate", "canonical_wrapper_pair"):
        fixture = _fixture(policy, key)
        bucket_def = next(
            b for b in policy["classification_buckets"]
            if b["bucket"] == fixture["expected_bucket"]
        )
        assert fixture["expected_severity"] == bucket_def["severity"], (
            f"Fixture {fixture['finding_key']}: expected_severity mismatch"
        )
        assert fixture["expected_confidence"] == bucket_def["confidence_default"], (
            f"Fixture {fixture['finding_key']}: expected_confidence mismatch"
        )


# ---------------------------------------------------------------------------
# 5. Carry-forward — unchanged findings stay compact
# ---------------------------------------------------------------------------

def test_policy_defines_carry_forward_behavior(
    policy: dict, engine: PolicyEngine
) -> None:
    finding = {
        "finding_key": "k1",
        "classification": "exact-duplicate",
        "severity": "high",
        "confidence": "high",
        "escalation_state": "candidate",
        "canonical_names": ["foo", "foo"],
        "paths": ["a/foo", "b/foo"],
        "suppressed": False,
    }
    # Identical prior and current → unchanged
    rule = engine.compute_carry_forward(finding, finding)
    assert rule == "unchanged"

    carry_rule = policy["carry_forward_rules"]["unchanged"]
    assert carry_rule["action"] == "compact_carry_forward"
    assert carry_rule["surface_as_new"] is False


# ---------------------------------------------------------------------------
# 6. Carry-forward — changed-but-unresolved findings surface as changed
# ---------------------------------------------------------------------------

def test_policy_handles_changed_but_unresolved_finding(
    policy: dict, engine: PolicyEngine
) -> None:
    prior = {
        "finding_key": "k1",
        "severity": "medium",
        "confidence": "medium",
        "escalation_state": "no-escalation",
        "canonical_names": ["foo", "bar"],
        "paths": ["a/foo", "b/bar"],
        "suppressed": False,
    }
    current = {
        "finding_key": "k1",
        "severity": "high",
        "confidence": "high",
        "escalation_state": "candidate",
        "canonical_names": ["foo", "bar"],
        "paths": ["a/foo", "b/bar"],
        "suppressed": False,
    }
    rule = engine.compute_carry_forward(prior, current)
    assert rule == "changed"

    carry_rule = policy["carry_forward_rules"]["changed"]
    assert carry_rule["surface_as_changed"] is True
    assert carry_rule["include_in_section"] == "changed"


# ---------------------------------------------------------------------------
# 7. Escalation thresholds
# ---------------------------------------------------------------------------

def test_policy_defines_issue_escalation_threshold(
    policy: dict, engine: PolicyEngine
) -> None:
    assert engine.compute_escalation("high", "high") == "candidate"
    assert engine.compute_escalation("high", "medium") == "no-escalation"
    assert engine.compute_escalation("medium", "high") == "no-escalation"
    assert engine.compute_escalation("low", "low") == "no-escalation"

    escalation = policy["escalation"]
    assert set(escalation["states"]) == {"no-escalation", "candidate"}


# ---------------------------------------------------------------------------
# 8. Escalation idempotence — same inputs always produce same output
# ---------------------------------------------------------------------------

def test_policy_escalation_is_idempotent(policy: dict, engine: PolicyEngine) -> None:
    # high/high is always candidate across repeated calls
    assert engine.compute_escalation("high", "high") == "candidate"
    assert engine.compute_escalation("high", "high") == "candidate"

    # medium/high is always no-escalation
    assert engine.compute_escalation("medium", "high") == "no-escalation"
    assert engine.compute_escalation("medium", "high") == "no-escalation"


# ---------------------------------------------------------------------------
# 9. Weekly summary sections contract
# ---------------------------------------------------------------------------

def test_policy_weekly_summary_sections_are_minimum_contract(policy: dict) -> None:
    required = {
        "new",
        "changed",
        "unresolved_high_confidence",
        "suppressed_carry_forward",
        "operational_errors",
    }
    actual = {s["section_id"] for s in policy["weekly_summary"]["sections"]}
    assert required.issubset(actual), f"Missing summary sections: {required - actual}"


# ---------------------------------------------------------------------------
# 10. Schema validation — malformed policy fails fast
# ---------------------------------------------------------------------------

def test_policy_rejects_invalid_policy_schema() -> None:
    # Case A: missing required top-level keys
    with pytest.raises(PolicyValidationError, match="missing required top-level keys"):
        validate_policy({"version": "1.0"})

    # Case B: empty classification_buckets list
    with pytest.raises(PolicyValidationError, match="non-empty"):
        validate_policy(
            {
                "version": "1.0",
                "finding_schema": {},
                "classification_buckets": [],
                "severity_rubric": {},
                "confidence_rubric": {},
                "carry_forward_rules": {},
                "escalation": {},
                "weekly_summary": {},
                "fixtures": {},
                "fallback_bucket": "needs-human-review",
            }
        )

    # Case C: missing one of the required named buckets
    with pytest.raises(PolicyValidationError, match="missing required buckets"):
        validate_policy(
            {
                "version": "1.0",
                "finding_schema": {},
                "classification_buckets": [
                    {"bucket": "exact-duplicate", "precedence": 1}
                ],
                "severity_rubric": {},
                "confidence_rubric": {},
                "carry_forward_rules": {},
                "escalation": {},
                "weekly_summary": {},
                "fixtures": {},
                "fallback_bucket": "needs-human-review",
            }
        )
