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

# Live-rule fixture mirroring routing-rules.yaml:90-92 (needs:cross-review ->
# codex, "Codex strong on adversarial cross-review") plus the catch-all.
def _rules():
    return [
        {"match": {"gh_label": "needs:cross-review"},
         "assign": {"provider": "codex"},
         "reason": "Codex strong on adversarial cross-review"},
        {"match": {}, "assign": {"machine": "dev-primary"}, "reason": "catch-all"},
    ]


def _resolve(route, labels, assign=None):
    return route.resolve_provider(labels, assign or {}, DEFAULTS)


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


# 3. Live rule fixture: needs:cross-review -> codex outranks lane:claude.
#    Existing routing intent must never be inverted by a lane label.
def test_cross_review_rule_wins_over_lane(route):
    labels = ["needs:cross-review", "lane:claude"]
    assign = route.match_rule(_rules(), repo="vamseeachanta/workspace-hub",
                              domain=None, gh_labels=labels).get("assign")
    provider, explicit = _resolve(route, labels, assign)
    assert provider == "codex"
    assert explicit is True  # rule-chosen provider stays explicit (unchanged)


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
