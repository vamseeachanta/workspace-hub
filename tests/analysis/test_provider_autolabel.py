"""Research readiness regressions for issues/2253 (Refs #2253).

Predicate: a strong research match requires execution_ready is True, explicit
research/recon wording, and no mixed implementation/strategy intent unless the
title starts with scout-first, recon-first or research-first. Queue summaries
omit body, so title and work_type must suffice; body is checked when supplied.
Routing metadata and broad category wording alone do not establish intent.

Reason codes: research-not-execution-ready, research-intent-ambiguous and
mixed-implementation-not-scout-first explain a fallback to weak-heuristic-match;
research-ready and explicit-scout-first explain a retained strong match.

Independent score sums from scripts/ai/provider-autolabel.py:compute_confidence:
ready .35 + priority .15 + strong .35 + highest .10 = .95;
ready .35 + priority .15 + strong .35 + high .05 = .90;
ready .35 + priority .15 + weak .10 + highest .10 = .70;
priority .15 + weak .10 + highest .10 = .35 (no readiness);
priority .15 + strong .35 + highest .10 = .60 (other-provider control).
Existing-routing reset zero + highest .10 = .10.
The unchanged CONFIDENCE_THRESHOLD is .90; provider labels force zero.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

MODULE_PATH = Path(__file__).resolve().parents[2] / "scripts" / "ai" / "provider-autolabel.py"
spec = importlib.util.spec_from_file_location("provider_autolabel", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


@pytest.fixture(autouse=True)
def forbid_github_mutation(monkeypatch):
    def reject_mutation(*args, **kwargs):
        raise AssertionError("Pure scoring tests must not mutate GitHub")

    monkeypatch.setattr(module, "gh_issue_edit_add_label", reject_mutation)


@pytest.fixture
def ready_research_issue():
    return {
        "number": 1,
        "title": "Research: compare cache eviction approaches",
        "work_type": ["research"],
        "execution_ready": True,
        "priority_rank": 1,
        "routing_reason": "research/triage/audit language",
        "provider_priority": "highest",
        "labels": [],
    }


def research_candidate(issue):
    queue = {"provider_queues": {
        provider: {"top_issues": [issue] if provider == "agy" else []}
        for provider in module.PROVIDERS
    }}
    return module.collect_candidates(queue)[0]


def test_mixed_implementation_is_not_research_ready(ready_research_issue):
    issue = {
        **ready_research_issue,
        "title": "Research cache options, then implement the adapter and tests",
        "work_type": ["research", "implementation"],
    }
    candidate = research_candidate(issue)
    assert candidate["confidence"] == 0.70  # Independent weak-match sum above.
    assert candidate["eligible"] is False
    assert "mixed-implementation-not-scout-first" in candidate["confidence_reasons"]
    assert "strong-agy-language-match" not in candidate["confidence_reasons"]


@pytest.mark.parametrize("readiness", [False, None, "true", 1])
def test_research_keywords_without_readiness_are_ineligible(
    ready_research_issue, readiness
):
    issue = {**ready_research_issue, "execution_ready": readiness}
    candidate = research_candidate(issue)
    assert candidate["eligible"] is False
    assert "research-not-execution-ready" in candidate["confidence_reasons"]


def test_missing_readiness_is_ineligible(ready_research_issue):
    issue = ready_research_issue.copy()
    del issue["execution_ready"]
    candidate = research_candidate(issue)
    assert candidate["confidence"] == 0.35  # Independent no-readiness sum above.
    assert candidate["eligible"] is False


@pytest.mark.parametrize("title", [
    "Research: compare cache approaches",
    "RECON: map dependencies",
    "Reconnaissance: inspect available sources",
    "Audit: inspect dependency metadata",
    "Triage: investigate reported symptoms",
])
@pytest.mark.parametrize("priority, expected", [("highest", 0.95), ("high", 0.90)])
def test_explicit_ready_research_can_be_eligible(
    ready_research_issue, title, priority, expected
):
    candidate = research_candidate({
        **ready_research_issue, "title": title, "provider_priority": priority,
    })
    assert candidate["confidence"] == expected  # Independent strong sums above.
    assert candidate["eligible"] is True
    assert candidate["target_label"] == "ai:agy"
    assert "research-ready" in candidate["confidence_reasons"]
    assert "strong-agy-language-match" in candidate["confidence_reasons"]


@pytest.mark.parametrize("overrides, reason", [
    ({"work_type": ["research", "implementation"]},
     "mixed-implementation-not-scout-first"),
    ({"work_type": ["research", "strategy"]},
     "mixed-implementation-not-scout-first"),
    ({"body": "Implement an adapter after comparing approaches."},
     "mixed-implementation-not-scout-first"),
    ({"title": "Research options and add a cache", "work_type": ["research"]},
     "mixed-implementation-not-scout-first"),
    ({"title": "Research options and refactor caching", "work_type": []},
     "mixed-implementation-not-scout-first"),
    ({"title": "Research options then update the adapter"},
     "mixed-implementation-not-scout-first"),
    ({"title": "Research options then patch the parser"},
     "mixed-implementation-not-scout-first"),
    ({"title": "Research options then write a parser"},
     "mixed-implementation-not-scout-first"),
    ({"title": "Research options then create an adapter"},
     "mixed-implementation-not-scout-first"),
    ({"title": "Research options then normalize the summaries"},
     "mixed-implementation-not-scout-first"),
    ({"title": "Data-pipeline knowledge inventory", "work_type": ["research"]},
     "research-intent-ambiguous"),
    ({"title": "Update the cache", "work_type": []},
     "research-intent-ambiguous"),
    ({"title": "Researcher cache catalog", "work_type": []},
     "research-intent-ambiguous"),
    ({"title": "Research options; not scout-first, implement the adapter"},
     "mixed-implementation-not-scout-first"),
])
def test_ambiguous_or_mixed_intent_uses_weak_weight(
    ready_research_issue, overrides, reason
):
    candidate = research_candidate({**ready_research_issue, **overrides})
    assert candidate["confidence"] == 0.70  # Independent weak-match sum above.
    assert candidate["eligible"] is False
    assert reason in candidate["confidence_reasons"]
    assert "weak-heuristic-match" in candidate["confidence_reasons"]


@pytest.mark.parametrize("prefix", ["Scout-first", "recon first", "Research-first"])
def test_explicit_scout_first_allows_mixed_research(ready_research_issue, prefix):
    candidate = research_candidate({
        **ready_research_issue,
        "title": f"{prefix}: compare options before implementing the adapter",
        "work_type": ["research", "implementation"],
    })
    assert candidate["confidence"] == 0.95  # Independent strong/highest sum above.
    assert candidate["eligible"] is True
    assert "explicit-scout-first" in candidate["confidence_reasons"]


def test_scout_first_still_requires_readiness(ready_research_issue):
    candidate = research_candidate({
        **ready_research_issue,
        "title": "Scout-first: research before implementing the adapter",
        "work_type": ["research", "implementation"],
        "execution_ready": False,
    })
    assert candidate["confidence"] == 0.35  # Independent no-readiness sum above.
    assert candidate["eligible"] is False


@pytest.mark.parametrize("provider, routing_reason, readiness, priority, expected", [
    ("codex", "implementation/test/fix language", True, "highest", 0.95),
    ("claude", "strategy/workflow/architecture language", True, "high", 0.90),
    ("codex", "research/triage/audit language", True, "highest", 0.70),
    ("claude", "research/triage/audit language", True, "highest", 0.70),
    ("codex", "implementation/test/fix language", False, "highest", 0.60),
    ("gemini", "research/triage/audit language", True, "highest", 0.70),
])
def test_other_provider_scores_are_unchanged(
    ready_research_issue, provider, routing_reason, readiness, priority, expected
):
    score, reasons = module.compute_confidence(provider, {
        **ready_research_issue,
        "routing_reason": routing_reason,
        "execution_ready": readiness,
        "provider_priority": priority,
    })
    assert score == expected  # Independent sums in the module documentation.
    assert "research-ready" not in reasons


def test_existing_routing_reason_stays_ineligible(ready_research_issue):
    candidate = research_candidate({
        **ready_research_issue, "routing_reason": "existing ai label: agy",
    })
    assert candidate["confidence"] == 0.10  # Independent reset sum above.
    assert candidate["eligible"] is False
    assert "already-labeled" in candidate["confidence_reasons"]


@pytest.mark.parametrize("label", ["ai:agy", "agent:agy", "ai:gemini", "agent:gemini"])
def test_research_provider_labels_are_excluded(ready_research_issue, label):
    issue = {**ready_research_issue, "labels": [label]}
    score, reasons = module.compute_confidence("agy", issue)
    assert score == 0.0  # Existing provider-label override.
    assert "provider-label-exists" in reasons
    queue = {"provider_queues": {
        provider: {"top_issues": [issue] if provider == "agy" else []}
        for provider in module.PROVIDERS
    }}
    assert module.collect_candidates(queue) == []
    assert module.LEGACY_PROVIDER_ALIASES["gemini"] == "agy"


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


def test_compute_confidence_zero_when_ai_label_exists() -> None:
    issue = {
        "execution_ready": True,
        "priority_rank": 1,
        "routing_reason": "strategy/workflow/architecture language",
        "provider_priority": "high",
        "labels": ["ai:claude"],
    }
    confidence, reasons = module.compute_confidence("claude", issue)
    assert confidence == 0.0
    assert "provider-label-exists" in reasons


def test_compute_confidence_zero_when_legacy_agent_label_exists() -> None:
    issue = {
        "execution_ready": True,
        "priority_rank": 1,
        "routing_reason": "strategy/workflow/architecture language",
        "provider_priority": "high",
        "labels": ["agent:claude"],
    }
    confidence, reasons = module.compute_confidence("claude", issue)
    assert confidence == 0.0
    assert "provider-label-exists" in reasons


def test_collect_candidates_marks_only_high_confidence_items_eligible() -> None:
    work_queue = {
        "provider_queues": {
            "claude": {"top_issues": [{"number": 1, "title": "epic: strategy", "labels": [], "execution_ready": True, "priority_rank": 1, "routing_reason": "strategy/workflow/architecture language", "provider_priority": "high"}]},
            "codex": {"top_issues": [{"number": 2, "title": "fix: implementation", "labels": [], "execution_ready": True, "priority_rank": 1, "routing_reason": "implementation/test/fix language", "provider_priority": "highest"}]},
            "agy": {"top_issues": [{"number": 3, "title": "audit: research", "labels": [], "execution_ready": False, "priority_rank": 2, "routing_reason": "research/triage/audit language", "provider_priority": "highest"}]},
        }
    }
    candidates = module.collect_candidates(work_queue)
    assert all(item["target_label"].startswith("ai:") for item in candidates)
    eligible_numbers = {item["number"] for item in candidates if item["eligible"]}
    assert 1 in eligible_numbers
    assert 2 in eligible_numbers
    assert 3 not in eligible_numbers
