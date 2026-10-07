#!/usr/bin/env python3
"""The `ai:` provider axis — deckhand#584 slice 4.

Owner decision 2026-07-30: **frontier default models and default effort for all
work.** So `ai:` selects the PROVIDER only; each provider then uses its own
frontier default at default effort. There is no `model:` axis and no effort axis.

## What a Codex design review found BEFORE this was built

Two defects in the code this slice would have been built on top of. Both verified
against `apply_wip()` in route.py:

**1. Unknown providers fail OPEN.**

    if providers.get(prov, {}).get("auto_routable", True) is False:

An unrecognised provider gets `True` — auto-routable — and sails past the scarce
cap. The docstring one line above says "Fail-CLOSED". So a typo (`ai:agi`), or a
label left over from a retired provider, routes as a full workhorse rather than
being refused. That is the same shape as every other defect in this subsystem:
absence of a match reads as permission.

**2. `auto_routable: false` strands the manual override it exists to permit.**

The gemini entry reads `auto_routable: false, note: "manual ai:gemini only"`. But
`apply_wip` sets `over = True` for that provider unconditionally — including when
a human explicitly wrote `ai:gemini`. The config says "manual only"; the code
means "never". Those differ, and the comment hid it.

The distinction the config was missing: **not auto-SELECTABLE** (defaults, rules
and lanes may not choose it) is not the same as **not usable** (a human may).

## Design recorded here

- `ai:` is the human/dispatch override and has the HIGHEST precedence.
- It is single-valued — now declared in `label_axes`, not just enforced at the
  write boundary as it was before.
- Unknown provider values are REFUSED with a visible reason.
- `auto_routable: false` blocks default/rule/lane selection, never an explicit
  `ai:` choice.
- Reserved axes: no routing axis may be `model:`, `effort:`, `reasoning:` or
  `tier:`. Banning one spelling invites synonyms; the denylist names the class.

Hermetic: pure functions and parsed YAML. No gh, no network.

Run: uv run --with pyyaml pytest tests/dispatch/test_ai_provider_axis.py
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
ROUTE_PY = REPO_ROOT / "scripts" / "dispatch" / "route.py"
RULES_PATH = REPO_ROOT / ".claude" / "memory" / "kanban" / "routing-rules.yaml"


def _load():
    spec = importlib.util.spec_from_file_location("route_ai", ROUTE_PY)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["route_ai"] = mod
    spec.loader.exec_module(mod)
    return mod


R = _load()


@pytest.fixture(scope="module")
def cfg() -> dict:
    return yaml.safe_load(RULES_PATH.read_text(encoding="utf-8"))


def _cards(provider, explicit, n=1):
    return [{"key": f"k{i}", "machine": "dev-primary", "provider": provider,
             "provider_explicit": explicit, "priority": 0} for i in range(n)]


# --------------------------------------------------------------------------
# provider vocabulary is closed and fails CLOSED
# --------------------------------------------------------------------------


def test_unknown_provider_is_not_silently_auto_routable():
    """The verified fail-open. A typo must not become a workhorse."""
    cfg = {"providers": {"claude": {"auto_routable": True}},
           "wip_caps": {"per_machine": {"dev-primary": 9}, "per_provider": {}},
           "budget_pools": {}}
    out = R.apply_wip(_cards("agi-typo", False), cfg)
    assert out[0]["slot"] == "queued", (
        "an unrecognised provider must never be auto-eligible — it is not in the "
        "roster, so nothing has vouched for its capacity or quota"
    )


def test_unknown_provider_is_reported_not_just_queued():
    """Queued-and-silent is how a typo survives for months."""
    cfg = {"providers": {"claude": {"auto_routable": True}},
           "wip_caps": {"per_machine": {"dev-primary": 9}, "per_provider": {}},
           "budget_pools": {}}
    out = R.apply_wip(_cards("agi-typo", False), cfg)
    assert out[0].get("wip_reason"), "a refusal must carry a reason"
    assert "unknown provider" in out[0]["wip_reason"].lower()


def test_known_provider_still_routes():
    cfg = {"providers": {"claude": {"auto_routable": True}},
           "wip_caps": {"per_machine": {"dev-primary": 9}, "per_provider": {}},
           "budget_pools": {}}
    out = R.apply_wip(_cards("claude", False), cfg)
    assert out[0]["slot"] == "active-eligible"


# --------------------------------------------------------------------------
# auto_routable blocks SELECTION, not the explicit override
# --------------------------------------------------------------------------


def test_non_auto_routable_provider_is_queued_when_not_explicit():
    """Defaults, rules and lanes must not select a scarce provider."""
    cfg = {"providers": {"agy": {"auto_routable": False}},
           "wip_caps": {"per_machine": {"dev-primary": 9}, "per_provider": {}},
           "budget_pools": {}}
    out = R.apply_wip(_cards("agy", False), cfg)
    assert out[0]["slot"] == "queued"


def test_non_auto_routable_provider_IS_eligible_when_a_human_chose_it():  # noqa: N802
    """The second verified defect.

    `auto_routable: false` with `note: "manual ai:X only"` meant the config
    intended manual use to work. The code queued it regardless, so the documented
    escape hatch did not exist. "Not auto-selectable" ≠ "not usable".
    """
    cfg = {"providers": {"agy": {"auto_routable": False}},
           "wip_caps": {"per_machine": {"dev-primary": 9}, "per_provider": {}},
           "budget_pools": {}}
    out = R.apply_wip(_cards("agy", True), cfg)
    assert out[0]["slot"] == "active-eligible", (
        "an explicit ai: override must be able to use a manual-only provider — "
        "otherwise the override the config documents does not work"
    )


def test_an_explicit_override_still_obeys_its_budget_pool():
    """Override the SELECTION, not the CAP. Scarce quota stays scarce.

    Without this, `ai:agy` would be an unbounded bypass of the very quota that
    made the provider manual-only.
    """
    cfg = {"providers": {"agy": {"auto_routable": False, "budget_pool": "google_pool"}},
           "wip_caps": {"per_machine": {"dev-primary": 9}, "per_provider": {}},
           "budget_pools": {"google_pool": {"members": ["agy"], "max_concurrent": 1}}}
    out = R.apply_wip(_cards("agy", True, n=3), cfg)
    slots = [p["slot"] for p in out]
    assert slots == ["active-eligible", "queued", "queued"], slots


# --------------------------------------------------------------------------
# the shipped roster
# --------------------------------------------------------------------------


def test_agy_has_replaced_gemini_in_the_roster(cfg):
    """workspace-hub#3573 swapped the provider; the routing config had not caught up.

    Measured 2026-07-31: `agent:gemini` carries ZERO open issues, so the swap is
    complete in the wild and only the config lagged.
    """
    providers = cfg.get("providers") or {}
    assert "agy" in providers, "agy is the cross-review provider and must be declared"
    assert "gemini" not in providers, "gemini was replaced by agy (workspace-hub#3573)"


def test_agy_is_scarce_and_pooled(cfg):
    """Google AI Pro quota. Frontier-default-for-all-work sets the MODEL, not the
    budget — an explicitly chosen provider still needs a hard cap."""
    agy = (cfg.get("providers") or {}).get("agy") or {}
    assert agy.get("auto_routable") is False, "agy must not be auto-selected from backlog"
    pool = agy.get("budget_pool")
    assert pool, "agy needs a budget pool or its scarce quota is unbounded"
    caps = ((cfg.get("budget_pools") or {}).get(pool) or {})
    assert caps.get("max_concurrent"), f"{pool} needs a max_concurrent"


def test_ai_axis_is_declared_single(cfg):
    """It was enforced only at the WRITE boundary before this slice.

    A guard applied on one side of a system and not the other is the shape that
    let the read path and write path disagree elsewhere in this file's history.
    """
    single = set((cfg.get("label_axes") or {}).get("single") or {})
    assert "ai:" in single, "ai: is single-valued and must be declared, not just write-gated"


# --------------------------------------------------------------------------
# no model / effort axis — by CLASS, not by one spelling
# --------------------------------------------------------------------------


RESERVED = ("model:", "effort:", "reasoning:", "tier:")


def test_no_reserved_axis_is_declared(cfg):
    """Owner decision: frontier defaults everywhere, so no model or effort knob.

    A denylist rather than a single ban because banning `model:` alone invites
    the same control under another spelling. Naming the CLASS is what stops the
    next synonym.
    """
    axes = cfg.get("label_axes") or {}
    declared = set(axes.get("single") or {}) | set(axes.get("multi") or {})
    bad = sorted(a for a in declared if a in RESERVED)
    assert not bad, (
        f"reserved axes declared: {bad}. Frontier defaults are the owner decision; "
        "a model/effort axis needs a new decision, not a new label."
    )


def test_no_rule_matches_a_reserved_axis(cfg):
    """The label could exist unroutingly; a RULE reading it is the real breach."""
    offenders = []
    for rule in cfg.get("rules") or []:
        label = (rule.get("match") or {}).get("gh_label") or ""
        if any(label.startswith(a) for a in RESERVED):
            offenders.append(label)
    assert not offenders, f"routing rules read a reserved axis: {offenders}"


def test_reserved_list_is_not_empty():
    """Guards the guard: an emptied RESERVED tuple would make both checks pass."""
    assert RESERVED and all(a.endswith(":") for a in RESERVED)
