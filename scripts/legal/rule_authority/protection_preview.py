"""Closed parsing for offline Phase A owner-transaction readback fixtures."""

from __future__ import annotations


def _fields(value: object, expected: set[str], label: str) -> dict:
    if not isinstance(value, dict) or set(value) != expected:
        raise ValueError(f"invalid {label} readback")
    return value


def expected_readback(preview: object) -> dict:
    """Extract the exact externally verifiable contract from the owner preview."""
    document = _fields(
        preview,
        {"codeowners", "cutover", "environment", "issue", "owner", "repository",
         "ruleset", "schema_id", "target_ref"},
        "owner preview",
    )
    if document["schema_id"] != "legal-rule-phase-a-owner-preview-v1":
        raise ValueError("invalid owner preview readback")
    return {name: document[name] for name in ("codeowners", "environment", "ruleset")}


def parse_readback_fixture(value: object) -> dict:
    """Normalize captured API fixtures without performing any provider request."""
    document = _fields(value, {"codeowners", "environment", "ruleset"}, "fixture")
    environment = _fields(
        document["environment"],
        {"deployment_branch_policy", "name", "prevent_self_review", "reviewers"},
        "environment",
    )
    ruleset = _fields(
        document["ruleset"],
        {"block_deletions", "block_non_fast_forward", "bypass_actors", "conditions",
         "enforcement", "name", "required_check", "required_pull_request", "target"},
        "ruleset",
    )
    check = _fields(ruleset["required_check"], {"context", "integration_id"}, "check")
    if (environment["reviewers"] != ["vamseeachanta"] or
            check != {"context": "legal-rule-authority / strict-scan",
                      "integration_id": 15368} or ruleset["bypass_actors"] != []):
        raise ValueError("readback differs from owner preview")
    return document
