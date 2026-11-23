from __future__ import annotations

import importlib.util
import json
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[2] / "scripts" / "ai" / "provider-routing-scorecard.py"
spec = importlib.util.spec_from_file_location("provider_routing_scorecard", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


def test_build_recommendation_prioritizes_codex_when_underused_and_quota_visible() -> None:
    metrics = {
        "reported_utilization_pct": 1.0,
        "quota_basis": "quota",
        "quota_source": "history.jsonl",
        "sessions": 0,
        "post_records": 0,
    }
    audit = {
        "post_records": 31413,
        "missing_repo_reads": 0,
        "python3_bash_calls": 319,
        "top_tools": [{"tool": "Bash", "count": 100}],
    }

    rec = module.build_recommendation("codex", metrics, audit)

    assert rec["priority"] == "highest"
    assert rec["status"] == "underused"
    assert any("bounded implementation" in x.lower() for x in rec["preferred_work"])


def test_build_recommendation_flags_claude_cleanup_when_missing_reads_are_high() -> None:
    metrics = {
        "reported_utilization_pct": 12.0,
        "quota_basis": "unavailable",
        "quota_source": "unavailable",
        "sessions": 1,
        "post_records": 10,
    }
    audit = {
        "post_records": 74657,
        "missing_repo_reads": 7560,
        "python3_bash_calls": 644,
        "missing_repo_read_remediation_hints": [{"rule_id": "legacy_work_queue_transition", "total_count": 318}],
    }

    rec = module.build_recommendation("claude", metrics, audit)

    assert rec["status"] == "needs_cleanup"
    assert rec["top_migration_hint"] == "legacy_work_queue_transition"
    assert any("stale-path drift" in x for x in rec["actions"])


def test_build_scorecard_orders_by_priority_then_utilization() -> None:
    utilization = {
        "generated_at": "2026-04-13T00:00:00Z",
        "current_week": "2026-W16",
        "weekly_data": {
            "2026-W16": {
                "claude": {"reported_utilization_pct": 20.0, "quota_basis": "unavailable", "quota_source": "unavailable", "sessions": 1, "post_records": 10},
                "codex": {"reported_utilization_pct": 1.0, "quota_basis": "quota", "quota_source": "history.jsonl", "sessions": 0, "post_records": 0},
                "gemini": {"reported_utilization_pct": 0.0, "quota_basis": "estimated_daily_quota", "quota_source": "estimated", "sessions": 0, "post_records": 0},
            }
        },
    }
    audit = {
        "generated_at": "2026-04-13T01:00:00Z",
        "providers": {
            "claude": {"post_records": 1000, "missing_repo_reads": 1500, "python3_bash_calls": 5},
            "codex": {"post_records": 500, "missing_repo_reads": 0, "python3_bash_calls": 1},
            "gemini": {"post_records": 100, "missing_repo_reads": 10, "python3_bash_calls": 5},
        },
    }

    scorecard = module.build_scorecard(utilization, audit)

    assert scorecard["recommended_provider_order"][0] in {"codex", "gemini"}
    assert set(scorecard["recommended_provider_order"]) == {"claude", "codex", "gemini"}
