#!/usr/bin/env python3
"""TDD tests for R9 — separating the provider choice from the budget bypass.

deckhand#584 slice 3. Owner decision 2026-07-30.

## The defect

`route.py` exempted `ai:`- and rule-sourced codex from the 10% weekly quota gate:
only a `lane:`-derived choice was demotable. So an `ai:codex` label chose the
provider AND silently opted the issue out of the spend guard — one label making
two decisions, the second invisible at the point of labelling.

Those intents genuinely differ. *"Codex does this work better"* is a judgement
about a task. *"Spend into a suspended pool"* is a judgement about the month.

## After

`ai:` and rule choose the provider; **neither bypasses the gate**. A separate
`quota:override` label carries the spend decision, explicitly and visibly.

Rule-sourced codex is demotable too, decided rather than inherited: a capability
rule choosing codex is MACHINE-decided, so it has even less claim on a budget
guard than a human's deliberate `ai:` label.

## Why now

Zero `ai:` labels exist today, so the exemption has never fired and this change
costs nothing. The moment slice 4 creates those labels, changing this would mean
changing the meaning of labels already in use.

Hermetic: pure functions, explicit args, no network.

Run: uv run --with pyyaml pytest tests/dispatch/test_route_quota_decoupling.py
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
ROUTE_PY = REPO_ROOT / "scripts" / "dispatch" / "route.py"


def _load():
    spec = importlib.util.spec_from_file_location("route", ROUTE_PY)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["route"] = mod
    spec.loader.exec_module(mod)
    return mod


R = _load()

DEFAULTS = {"provider": "claude"}
BELOW = 5.0   # strictly below QUOTA_GATE_PCT (10)
ABOVE = 40.0


# --------------------------------------------------------------------------
# the R9 change: ai: and rule no longer bypass the gate
# --------------------------------------------------------------------------


@pytest.mark.parametrize("source", ["lane", "ai", "rule", "default"])
def test_codex_is_demoted_below_threshold_regardless_of_source(source):
    """The budget guard applies to everyone.

    Previously only `source == "lane"` was demotable, so an `ai:codex` label was
    a silent spend-guard bypass.
    """
    provider, demoted = R.quota_demotion("codex", source, BELOW, DEFAULTS, labels=[])
    assert demoted is True
    assert provider == "claude"


@pytest.mark.parametrize("source", ["lane", "ai", "rule"])
def test_codex_is_not_demoted_above_threshold(source):
    provider, demoted = R.quota_demotion("codex", source, ABOVE, DEFAULTS, labels=[])
    assert demoted is False
    assert provider == "codex"


# --------------------------------------------------------------------------
# quota:override carries the SPEND decision, separately
# --------------------------------------------------------------------------


@pytest.mark.parametrize("source", ["lane", "ai", "rule"])
def test_quota_override_bypasses_the_gate_for_any_source(source):
    provider, demoted = R.quota_demotion(
        "codex", source, BELOW, DEFAULTS, labels=["quota:override"]
    )
    assert demoted is False
    assert provider == "codex"


def test_quota_override_alone_does_not_choose_a_provider():
    """It is a SPEND decision, not a routing one. A non-codex provider is untouched."""
    provider, demoted = R.quota_demotion(
        "claude", "lane", BELOW, DEFAULTS, labels=["quota:override"]
    )
    assert provider == "claude"
    assert demoted is False


def test_ai_label_without_override_is_demoted():
    """The exact case R9 exists for: quality choice, no spend decision."""
    provider, demoted = R.quota_demotion(
        "codex", "ai", BELOW, DEFAULTS, labels=["ai:codex"]
    )
    assert demoted is True, "an ai: label must not silently bypass the budget guard"
    assert provider == "claude"


def test_ai_label_with_override_is_not_demoted():
    """Both decisions made, both visible."""
    provider, demoted = R.quota_demotion(
        "codex", "ai", BELOW, DEFAULTS, labels=["ai:codex", "quota:override"]
    )
    assert demoted is False
    assert provider == "codex"


# --------------------------------------------------------------------------
# preserved behaviour — these must not regress
# --------------------------------------------------------------------------


def test_unknown_quota_still_fails_open():
    """`None` means the quota source was unreachable.

    The gate is an optimisation on top of routing (#3030); an unreachable quota
    source must never strand heavy work. Fail OPEN here is deliberate and is the
    opposite of the write gate's fail-closed — different failure costs.
    """
    provider, demoted = R.quota_demotion("codex", "ai", None, DEFAULTS, labels=[])
    assert demoted is False
    assert provider == "codex"


@pytest.mark.parametrize("provider", ["claude", "agy", "hermes"])
def test_non_codex_providers_are_never_demoted(provider):
    """The gate is codex-quota specific."""
    got, demoted = R.quota_demotion(provider, "lane", BELOW, DEFAULTS, labels=[])
    assert got == provider
    assert demoted is False


def test_threshold_is_strictly_below_not_at():
    """Preserves the documented `< QUOTA_GATE_PCT` boundary."""
    at_gate = float(R.QUOTA_GATE_PCT)
    _, demoted_at = R.quota_demotion("codex", "lane", at_gate, DEFAULTS, labels=[])
    _, demoted_below = R.quota_demotion("codex", "lane", at_gate - 0.01, DEFAULTS, labels=[])
    assert demoted_at is False
    assert demoted_below is True


# --------------------------------------------------------------------------
# the call site must lose its DUPLICATE guard
# --------------------------------------------------------------------------


def test_call_site_does_not_re_restrict_to_lane_source():
    """`propose()` had its own `provider_source == "lane"` condition.

    Changing only the function would leave the exemption fully intact at the
    call site — the fix would look done and do nothing. This is the same
    declared-but-unwired shape as an uncalled safety gate.
    """
    import inspect

    # Scan EXECUTABLE lines only. The call site documents the removed guard to
    # explain why relaxing the function alone was insufficient, and a raw
    # substring scan would flag that explanation as the defect. (Fourth time
    # this session a guard has matched its own documentation — strip comments.)
    code = "\n".join(
        line.split("#", 1)[0]
        for line in inspect.getsource(R.propose).splitlines()
        if not line.strip().startswith("#")
    )
    assert 'provider_source == "lane"' not in code, (
        "call site still restricts demotion to lane-sourced providers"
    )


def test_demotion_is_reported_so_it_is_never_silent():
    """A routing decision the operator cannot see is how the original defect hid."""
    import inspect

    assert "quota_demoted" in inspect.getsource(R.propose)
    assert "quota" in inspect.getsource(R.print_summary).lower()
