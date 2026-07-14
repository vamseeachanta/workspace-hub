from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


def test_reusable_workflow_is_secret_owner_and_caller_is_pinned():
    reusable = (ROOT / ".github/workflows/legal-rule-authority-reusable.yml").read_text(
        encoding="utf-8"
    )
    caller = (ROOT / ".github/workflows/legal-rule-authority-gate.yml").read_text(
        encoding="utf-8"
    )
    assert "environment: legal-rule-authority" in reusable
    assert "LEGAL_SCAN_AUTH_CURRENT" in reusable
    assert "pull_request_target" not in reusable + caller
    assert re.search(
        r"uses: vamseeachanta/workspace-hub/.github/workflows/legal-rule-authority-reusable.yml@[0-9a-f]{40}",
        caller,
    )
    assert "secrets: inherit" not in caller
    assert "ref: ${{ inputs.tool_sha }}" in reusable
    assert "audit-tree" in reusable and "verify" in reusable


def test_fork_path_is_constant_and_precedes_private_scan():
    reusable = (ROOT / ".github/workflows/legal-rule-authority-reusable.yml").read_text(
        encoding="utf-8"
    )
    fork = reusable.index("owner review required")
    private = reusable.index("environment: legal-rule-authority")
    assert fork < private
    assert "if: inputs.is_fork" in reusable


def test_public_config_contains_no_pattern_or_locator_fields():
    for relative in (
        "config/legal-rule-registry.json",
        "config/legal-rule-authority-policy.json",
    ):
        text = (ROOT / relative).read_text(encoding="utf-8")
        assert not any(
            token in text
            for token in (
                "pattern_b64",
                "source_path",
                "private_map",
                "license_endpoint",
            )
        )
