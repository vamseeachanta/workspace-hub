"""Regress instruction routes against SHARED_SOUL.md, Authorization (#3943)."""

import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
GUIDE = ROOT / "docs/standards/implementation-authorization.md"
RUNTIMES = (
    "hermes/SOUL.runtime.md",
    "claude/SOUL.runtime.md",
    "codex/SOUL.runtime.md",
    "codex/AGENTS.runtime.md",
    "gemini/SOUL.runtime.md",
    "agy/SOUL.runtime.md",
)


@pytest.mark.parametrize("relative", ("hermes/SOUL.md", *RUNTIMES))
def test_provider_guidance_cannot_restore_separate_plan_approval(relative):
    """Shared authority applies to the entire artifact, including its delta."""
    text = (ROOT / "config/agents" / relative).read_text(encoding="utf-8")
    assert "**USER APPROVES**" not in text
    assert (
        "No separate user plan approval is required" in text
        or "No separate user approval of a plan is required before implementation" in text
    )
    assert "TDD" in text
    assert "Adversarial review" in text
    assert "consequential" in text.lower() and "explicit approval" in text.lower()
    assert "never self" in text.lower()


@pytest.mark.parametrize("relative", (
    "engineering-issue-workflow-skill.md", "AI_ECOSYSTEM_DESIGN.md",
))
def test_active_workflow_references_keep_authority_and_review_separate(relative):
    text = (ROOT / "docs/standards" / relative).read_text(encoding="utf-8")
    assert "SHARED_SOUL.md#authorization" in text
    assert "No separate user plan approval is required" in text
    for obsolete in (
        "HARD STOP — USER APPROVES PLAN",
        "HARD STOP — USER APPROVAL REQUIRED",
        "approval must come AFTER seeing the plan",
        "After user approval:",
        "The user must approve",
        "user acknowledgment",
        "brief plan, still requires approval",
        "user approval at status:plan-approved",
        "enforces `status:plan-approved` before writes",
        "only for plan-approved disjoint write surfaces",
        'OK?" is sufficient',
    ):
        assert obsolete not in text
    assert "TDD" in text and "review" in text.lower()
    assert "Consequential actions require" in text


def example_request():
    """Synthetic identities; the reference remains unverified by the CLI."""
    return {
        "schema_version": "1",
        "provider": "codex",
        "operation_kind": "edit",
        "scope": {
            "repository_id": "example-repository",
            "task_id": "example-task",
            "operation_id": "update-guidance",
            "bounded": True,
        },
        "changed_paths": ["config/agents/hermes/SOUL.md"],
        "effects": ["local-reversible", "substantial-change"],
        "authorization_reference": "originating-task-request",
    }


def assess_cli(request):
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts/governance/workflow_decision.py")],
        input=json.dumps(request), text=True, capture_output=True, check=False,
        env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"),
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def test_worked_example_input_and_answer_match_public_cli():
    """Policy derivation: substantial + task reference => verify-task-authority.

    SHARED_SOUL.md, Authorization, substantial row requires checking task scope;
    a JSON reference never authenticates it. Shared instructions are protected
    under the same section's scrutiny rule. No second approval event follows.
    The expected object is written from that rule, independently of the CLI.
    """
    text = GUIDE.read_text(encoding="utf-8")
    blocks = re.findall(r"```json\n(.*?)\n```", text, re.DOTALL)
    request, expected = map(json.loads, blocks)
    assert request == example_request()
    result = assess_cli(request)
    assert result == expected == {
        "risk_class": "substantial",
        "authorization_assessment": "unverified-reference",
        "action_boundary": "verify-task-authority",
        "metric_advice": "not-requested",
        "reuse_assessment": "not-requested",
        "reason_codes": [
            "PROTECTED_CHANGE", "TASK_AUTHORITY_REQUIRED", "UNVERIFIED_AUTHORITY",
        ],
    }


@pytest.mark.parametrize("provider", ("hermes", "claude", "codex", "gemini", "agy"))
def test_substantial_cli_route_is_provider_independent(provider):
    """Authorization table: provider identity grants no task authority."""
    request = example_request()
    request["provider"] = provider
    result = assess_cli(request)
    assert result["action_boundary"] == "verify-task-authority"
    assert result["authorization_assessment"] == "unverified-reference"
    assert "APPROVAL_REQUIRED" not in result["reason_codes"]


@pytest.mark.parametrize("effect", (
    "publication", "destruction", "access-change", "engineering-basis-change",
))
def test_task_reference_does_not_cover_consequential_effects(effect):
    """Authorization table: actual consequential effects override task advice."""
    request = example_request()
    request["effects"].append(effect)
    result = assess_cli(request)
    assert result["risk_class"] == "consequential"
    assert result["action_boundary"] == "approval-required"
    assert result["authorization_assessment"] == "unverified-reference"


def test_missing_task_reference_does_not_become_implementation_permission():
    """Authorization table: missing provenance requires context, not approval."""
    request = example_request()
    request.pop("authorization_reference")
    result = assess_cli(request)
    assert result["action_boundary"] == "needs-context"
    assert result["authorization_assessment"] == "missing"
