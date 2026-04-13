from __future__ import annotations

import importlib.util
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[2] / "scripts" / "ai" / "provider-autolabel.py"
spec = importlib.util.spec_from_file_location("provider_autolabel", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


def test_compute_confidence_high_for_execution_ready_codex_fix() -> None:
    issue = {
        "execution_ready": True,
        "priority_rank": 1,
        "routing_reason": "implementation/test/fix language",
        "provider_priority": "highest",
        "labels": [],
    }
    confidence, reasons = module.compute_confidence("codex", issue)
    assert confidence >= 0.9
    assert "strong-codex-language-match" in reasons


def test_compute_confidence_zero_when_agent_label_exists() -> None:
    issue = {
        "execution_ready": True,
        "priority_rank": 1,
        "routing_reason": "strategy/workflow/architecture language",
        "provider_priority": "high",
        "labels": ["agent:claude"],
    }
    confidence, reasons = module.compute_confidence("claude", issue)
    assert confidence == 0.0
    assert "agent-label-exists" in reasons


def test_collect_candidates_marks_only_high_confidence_items_eligible() -> None:
    work_queue = {
        "provider_queues": {
            "claude": {"top_issues": [{"number": 1, "title": "epic: strategy", "labels": [], "execution_ready": True, "priority_rank": 1, "routing_reason": "strategy/workflow/architecture language", "provider_priority": "high"}]},
            "codex": {"top_issues": [{"number": 2, "title": "fix: implementation", "labels": [], "execution_ready": True, "priority_rank": 1, "routing_reason": "implementation/test/fix language", "provider_priority": "highest"}]},
            "gemini": {"top_issues": [{"number": 3, "title": "audit: research", "labels": [], "execution_ready": False, "priority_rank": 2, "routing_reason": "research/triage/audit language", "provider_priority": "highest"}]},
        }
    }
    candidates = module.collect_candidates(work_queue)
    eligible_numbers = {item["number"] for item in candidates if item["eligible"]}
    assert 1 in eligible_numbers
    assert 2 in eligible_numbers
    assert 3 not in eligible_numbers
