from __future__ import annotations

import importlib.util
import json
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[2] / "scripts" / "ai" / "provider-work-queue.py"
spec = importlib.util.spec_from_file_location("provider_work_queue", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


def test_suggested_provider_prefers_existing_agent_label() -> None:
    issue = {"title": "Fix tests", "body": "", "labels": [{"name": "agent:gemini"}]}
    provider, reason = module.suggested_provider(issue)
    assert provider == "gemini"
    assert "existing" in reason


def test_suggested_provider_routes_fixes_to_codex() -> None:
    issue = {"title": "fix(doc-intel): normalize summary-artifact identity", "body": "regression tests", "labels": []}
    provider, reason = module.suggested_provider(issue)
    assert provider == "codex"
    assert "implementation" in reason or "test" in reason


def test_build_queue_prefers_execution_ready_items_first() -> None:
    scorecard = {
        "current_week": "2026-W16",
        "generated_at": "2026-04-13T00:00:00Z",
        "recommended_provider_order": ["codex", "gemini", "claude"],
        "recommendations": [
            {"provider": "claude", "priority": "high", "status": "underused"},
            {"provider": "codex", "priority": "highest", "status": "underused"},
            {"provider": "gemini", "priority": "highest", "status": "underused"},
        ],
    }
    issues = [
        {
            "number": 1,
            "title": "fix: bounded cleanup",
            "body": "",
            "url": "u1",
            "updatedAt": "2026-04-13T00:00:00Z",
            "labels": [{"name": "status:plan-approved"}],
        },
        {
            "number": 2,
            "title": "fix: bounded cleanup later",
            "body": "",
            "url": "u2",
            "updatedAt": "2026-04-13T00:00:00Z",
            "labels": [],
        },
    ]

    queue = module.build_queue(scorecard, issues)
    codex_issues = queue["provider_queues"]["codex"]["top_issues"]

    assert codex_issues[0]["number"] == 1
    assert codex_issues[0]["execution_ready"] is True


def test_render_markdown_mentions_execution_ready() -> None:
    queue = {
        "generated_at": "2026-04-13T00:00:00Z",
        "current_week": "2026-W16",
        "recommended_provider_order": ["gemini", "codex", "claude"],
        "provider_queues": {
            provider: {
                "routing_priority": "highest",
                "execution_ready_count": 1,
                "total_candidates": 1,
                "top_issues": [
                    {
                        "number": 1,
                        "title": "sample",
                        "execution_ready": True,
                        "routing_reason": "reason",
                        "labels": ["status:plan-approved"],
                    }
                ],
                "full_candidates": [
                    {
                        "number": 1,
                        "title": "sample",
                        "execution_ready": True,
                        "routing_reason": "reason",
                        "labels": ["status:plan-approved"],
                    }
                ],
            }
            for provider in ("claude", "codex", "gemini")
        },
    }

    md = module.render_markdown(queue)
    assert "Execution-ready" in md
    assert "status:plan-approved" in md


def _scorecard():
    return {
        "current_week": "2026-W20",
        "generated_at": "2026-05-12T00:00:00Z",
        "recommended_provider_order": ["gemini", "codex", "claude"],
        "recommendations": [
            {"provider": "claude", "priority": "high", "status": "underused"},
            {"provider": "codex", "priority": "highest", "status": "underused"},
            {"provider": "gemini", "priority": "highest", "status": "underused"},
        ],
    }


def test_provider_work_queue_emits_full_candidates_and_top_issues() -> None:
    """Per #2665: downstream Kanban/dispatcher need non-truncated provider candidates;
    readable top_issues stays capped at 8 for the Markdown table.
    """
    fixture = (
        Path(__file__).resolve().parents[1]
        / "fixtures"
        / "ai"
        / "provider_kanban"
        / "issues.json"
    )
    issues = json.loads(fixture.read_text(encoding="utf-8"))
    # The fixture is designed so codex receives well more than 8 routed candidates.
    queue = module.build_queue(_scorecard(), issues)
    codex_bucket = queue["provider_queues"]["codex"]

    assert "full_candidates" in codex_bucket, "build_queue must emit full_candidates per provider"
    # Plan requirement: "more than 8 candidates per provider" — assert > 8 (the property
    # under test is non-truncation by top_issues[:8], not routing precision).
    assert len(codex_bucket["full_candidates"]) > 8, (
        f"full_candidates must NOT be truncated to top_issues[:8]; got {len(codex_bucket['full_candidates'])}"
    )
    assert len(codex_bucket["full_candidates"]) > len(codex_bucket["top_issues"]), (
        "full_candidates must be strictly larger than top_issues when backlog exceeds 8"
    )
    assert len(codex_bucket["top_issues"]) == 8, "top_issues stays capped at 8 for readability"
    # full_candidates must be a superset of top_issues
    top_numbers = {item["number"] for item in codex_bucket["top_issues"]}
    full_numbers = {item["number"] for item in codex_bucket["full_candidates"]}
    assert top_numbers.issubset(full_numbers)


def test_provider_work_queue_report_says_plan_approved_only() -> None:
    """Per #2665: report wording must NOT imply agent:* labels grant execution-ready.
    """
    fixture = (
        Path(__file__).resolve().parents[1]
        / "fixtures"
        / "ai"
        / "provider_kanban"
        / "issues.json"
    )
    issues = json.loads(fixture.read_text(encoding="utf-8"))
    # Add an issue with agent:codex but NO status:plan-approved
    issues = list(issues) + [
        {
            "number": 9999,
            "title": "fix(impl): bounded fix without plan approval",
            "url": "https://example.test/issues/9999",
            "state": "OPEN",
            "body": "no approval yet",
            "updatedAt": "2026-05-12T12:00:00Z",
            "labels": [{"name": "agent:codex"}, {"name": "priority:medium"}],
            "comments": [],
        }
    ]
    queue = module.build_queue(_scorecard(), issues)
    md = module.render_markdown(queue)

    # The wording must say execution-ready requires status:plan-approved
    # and must NOT include the misleading "or an explicit agent label" clause.
    assert "status:plan-approved" in md
    assert "or an explicit agent label" not in md, (
        "execution-ready wording must not imply agent:* grants approval"
    )

    # The agent:codex-only issue must classify as execution_ready=False.
    codex_items = queue["provider_queues"]["codex"]["full_candidates"]
    agent_only = next(item for item in codex_items if item["number"] == 9999)
    assert agent_only["execution_ready"] is False
