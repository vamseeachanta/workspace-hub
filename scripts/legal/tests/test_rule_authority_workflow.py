from __future__ import annotations

import re
import json
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
    assert "ref: ${{ github.job_workflow_sha }}" in reusable
    assert "inputs.tool_sha" not in reusable
    assert "audit-tree" in reusable and "verify" in reusable
    assert "inputs.head_oid" not in reusable
    assert "inputs.is_fork" not in reusable
    assert "github.event.pull_request.head.sha" in reusable
    assert "github.event_name" in reusable
    assert "github.repository" in reusable


def test_fork_path_is_constant_and_precedes_private_scan():
    caller = (ROOT / ".github/workflows/legal-rule-authority-gate.yml").read_text(
        encoding="utf-8"
    )
    assert "owner review required" in caller
    assert (
        "github.event.pull_request.head.repo.full_name != github.repository" in caller
    )
    assert "environment: legal-rule-authority" not in caller


def test_trust_boundary_paths_are_codeowned_and_preview_is_exact():
    owners = (ROOT / ".github/CODEOWNERS").read_text(encoding="utf-8")
    for path in (
        "/.github/CODEOWNERS",
        "/.github/workflows/legal-rule-authority-gate.yml",
        "/.github/workflows/legal-rule-authority-reusable.yml",
        "/scripts/legal/",
        "/schemas/legal-rule-",
        "/config/legal-rule-",
    ):
        assert path in owners
    preview = json.loads(
        (
            ROOT
            / "docs/plans/evidence/2026-07-14-issue-3522-phase-a-protection-preview.json"
        ).read_text(encoding="utf-8")
    )
    rules = {item["type"]: item for item in preview["ruleset"]["rules"]}
    assert rules["required_workflows"]["workflows"]
    assert rules["pull_request"]["parameters"]["require_code_owner_review"] is True


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
