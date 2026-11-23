#!/usr/bin/env python3
"""TDD tests for scripts/dispatch/route.py lane-aware provider resolution (#3029).

Context: plan-time `lane:codex`/`lane:claude` labels (workspace-hub#3028) carry
the compute-lane rule from .claude/memory/agents.md, but route.py only read
`ai:` labels. These tests pin the resolution precedence decided in the #3029
adversarial review (codex r2 MAJOR findings):

    ai: (human/dispatch override)  >  rule provider  >  lane: (plan-time
    preference)  >  defaults.provider

and the non-stickiness contract: a lane-derived provider must NEVER set
`provider_explicit`, so `labels_for()` never materializes an `ai:` label from
a lane (lane stays re-classifiable; matches the labels_for docstring "ai: only
when a rule/human chose a non-default provider").

Hermetic: import route.py via importlib; call pure functions with explicit args.

Run: uv run --with pyyaml pytest tests/dispatch/test_route_lane.py
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
ROUTE_PY = REPO_ROOT / "scripts" / "dispatch" / "route.py"


def _import_route():
    spec = importlib.util.spec_from_file_location("dispatch_route_lane", ROUTE_PY)
    assert spec and spec.loader, f"cannot load spec for {ROUTE_PY}"
    mod = importlib.util.module_from_spec(spec)
    sys.modules["dispatch_route_lane"] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture()
def route():
    return _import_route()


DEFAULTS = {"machine": "dev-primary", "provider": "claude"}

def _resolve(route, labels, assign=None):
    # #3030 extended resolve_provider to (provider, explicit, source);
    # these tests pin the first two elements (source pinned in
    # test_route_quota_gate.py).
    provider, explicit, _source = route.resolve_provider(labels, assign or {}, DEFAULTS)
    return provider, explicit


# 1. lane alone routes the provider but is NOT explicit (non-sticky).
def test_lane_codex_routes_without_explicit(route):
    provider, explicit = _resolve(route, ["lane:codex"])
    assert provider == "codex"
    assert explicit is False


# 2. ai: dispatch-time override outranks lane.
def test_ai_label_wins_over_lane(route):
    provider, explicit = _resolve(route, ["ai:claude", "lane:codex"])
    assert provider == "claude"
    assert explicit is True


# 3. A rule-chosen provider still outranks lane:. This is the #3029 protection —
#    "existing routing intent must never be inverted by lane" — and it is
#    UNCHANGED. It is now asserted against a synthetic rule rather than a live
#    one, because precedence is a property of the resolver, not of whichever
#    rules happen to ship today. Pinning it to live config made the test fail
#    when the config legitimately changed, which is what happened below.
def test_rule_chosen_provider_still_wins_over_lane(route):
    labels = ["lane:claude"]
    assign = {"provider": "codex"}          # as if some rule had chosen codex
    provider, explicit = _resolve(route, labels, assign)
    assert provider == "codex", "a rule's provider must outrank lane:"
    assert explicit is True  # rule-chosen provider stays explicit (unchanged)


# 3b. …but `needs:cross-review` is NOT such a rule, and must never become one.
#
#     It previously WAS: `{gh_label: needs:cross-review} -> {provider: codex}`.
#     The label did not exist in any repo, so the rule had never fired. Creating
#     the label on 2026-07-30 would have ARMED it and silently rerouted 21 issues
#     to codex over their author's explicit `lane:` choice.
#
#     `needs:` states a REQUIREMENT on the work ("must get a second-provider
#     review before close"), not a choice of who performs it. The review workflow
#     consumes the label; the router must not. See
#     tests/dispatch/test_cross_review_is_a_phase.py, which generalises this to
#     the whole `needs:` namespace.
def test_cross_review_label_does_not_route(route):
    labels = ["needs:cross-review", "lane:claude"]
    live_rules = route.load_rules().get("rules", [])
    assign = route.match_rule(live_rules, repo="vamseeachanta/workspace-hub",
                              domain=None, gh_labels=labels).get("assign", {})
    assert not assign.get("provider"), (
        "needs:cross-review must not choose a provider — it is a phase marker")
    provider, explicit = _resolve(route, labels, assign)
    assert provider == "claude", "the author's lane: must survive a phase label"
    assert explicit is False


# 4. No ai:/lane: labels — existing behavior bit-identical.
def test_no_lane_no_ai_uses_rule_then_default(route):
    provider, explicit = _resolve(route, [], {"provider": "codex"})
    assert (provider, explicit) == ("codex", True)
    provider, explicit = _resolve(route, [])
    assert (provider, explicit) == ("claude", False)


# 5. Unknown lane values never route (vocabulary fixed to the two workhorses).
def test_unknown_lane_value_ignored(route):
    provider, explicit = _resolve(route, ["lane:gemini"])
    assert provider == "claude"  # falls through to default
    assert explicit is False


# 6. labels_for(): a lane-resolved (non-explicit) provider emits NO ai: label.
def test_labels_for_never_materializes_lane_as_ai(route):
    p = {"provider": "codex", "provider_explicit": False,
         "domain": None, "machine": "dev-primary"}
    out = route.labels_for(p, existing=set())
    assert not any(l.startswith("ai:") for l in out), out
    # control: an explicit provider still gets its ai: label written
    p_explicit = dict(p, provider_explicit=True)
    out = route.labels_for(p_explicit, existing=set())
    assert "ai:codex" in out


# 7. apply_wip() treats a lane-resolved provider identically to a rule-resolved
#    one — capacity accounting consumes `provider`, never `provider_explicit`.
def test_apply_wip_ignores_explicitness(route):
    cfg = {
        "providers": {"codex": {"auto_routable": True}},
        "budget_pools": {"codex_pool": {"members": ["codex"], "max_concurrent": 1}},
        "wip_caps": {"per_machine": {"dev-primary": 2}, "per_provider": {}},
    }
    def card(key, explicit):
        return {"key": key, "machine": "dev-primary", "provider": "codex",
                "provider_explicit": explicit, "priority": 0}
    # lane-resolved (False) first: takes the single codex_pool slot
    lane_first = route.apply_wip([card("a", False), card("b", True)], cfg)
    # rule-resolved (True) first: same outcome shape, explicitness irrelevant
    rule_first = route.apply_wip([card("a", True), card("b", False)], cfg)
    assert [p["slot"] for p in lane_first] == ["active-eligible", "queued"]
    assert [p["slot"] for p in rule_first] == ["active-eligible", "queued"]
