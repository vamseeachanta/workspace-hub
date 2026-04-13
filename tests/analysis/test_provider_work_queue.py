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
            }
            for provider in ("claude", "codex", "gemini")
        },
    }

    md = module.render_markdown(queue)
    assert "Execution-ready" in md
    assert "status:plan-approved" in md
