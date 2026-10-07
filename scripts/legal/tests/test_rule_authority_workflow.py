from __future__ import annotations

import re
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


def test_automatic_rule_authority_workflows_are_retired():
    for name in ("legal-rule-authority-gate.yml", "legal-rule-authority-reusable.yml"):
        assert not (ROOT / ".github/workflows" / name).exists()


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
    assert rules["workflows"]["parameters"]["workflows"]
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
