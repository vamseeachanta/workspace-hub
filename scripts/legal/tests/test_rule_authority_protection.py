from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts" / "legal"))
from rule_authority import codec, protection  # noqa: E402


def test_live_environment_and_ruleset_readback_matches_preview():
    preview = codec.parse_canonical(
        (
            ROOT
            / "docs/plans/evidence/2026-07-14-issue-3522-phase-a-protection-preview.json"
        ).read_bytes()
    )
    environment = {
        "name": "legal-rule-authority",
        "deployment_branch_policy": {
            "protected_branches": True,
            "custom_branch_policies": False,
        },
        "protection_rules": [
            {
                "type": "required_reviewers",
                "reviewers": [{"reviewer": {"login": "vamseeachanta"}}],
            }
        ],
    }
    ruleset = {
        "name": "legal-rule-authority-main",
        "target": "branch",
        "enforcement": "active",
        "bypass_actors": [],
        "conditions": {"ref_name": {"include": ["refs/heads/main"], "exclude": []}},
        "rules": [
            {
                "type": "pull_request",
                "parameters": {
                    "required_approving_review_count": 1,
                    "require_code_owner_review": True,
                },
            },
            {
                "type": "required_status_checks",
                "parameters": {
                    "required_status_checks": [
                        {
                            "context": "Legal Rule Authority / strict-scan / authority",
                            "integration_id": "github-actions",
                        }
                    ]
                },
            },
            {
                "type": "required_workflows",
                "parameters": {
                    "workflows": [
                        {
                            "path": ".github/workflows/legal-rule-authority-gate.yml",
                            "ref": "refs/heads/main",
                            "repository": "vamseeachanta/workspace-hub",
                        }
                    ]
                },
            },
            {"type": "update", "parameters": {"allows_direct_updates": False}},
        ],
    }
    assert protection.verify_readback(preview, environment, ruleset)
    ruleset["bypass_actors"] = [{"actor_id": 1}]
    with pytest.raises(codec.AuthorityError, match="integrity"):
        protection.verify_readback(preview, environment, ruleset)
