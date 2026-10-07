#!/usr/bin/env python3
"""Label axes declare their cardinality, and single-valued axes fail closed.

## The defect

A GitHub label set permits states the domain forbids. Nothing stops two
`status:` labels, but an issue cannot be in two workflow states at once.

Measured across 1,761 open issues (2026-07-30): **146 issues carried 2+ labels
on one axis** — 36 on `status:` alone, of which **14 were `status:plan-approved`
AND `status:plan-review` simultaneously**. Those 14 read as *approved* to
anything checking for `plan-approved` and *pending* to anything checking for
`plan-review`. The never-self-approve gate is unenforceable against that state,
and nothing surfaced it, because both labels look deliberate.

## Why it was invisible

`existing_label_value()` (route.py:68) returns the **first** matching label. So
routing resolved silently, by whatever order the GitHub API happened to return —
non-deterministic, never reported, and indistinguishable from a correct
single-label issue at the point of use.

Silently picking one of two contradictory answers is worse than refusing: a
refusal gets fixed, a silent pick gets shipped.

## The fix, in three parts

1. **Declare** cardinality per axis in routing-rules.yaml. Today it is implicit,
   therefore unenforceable, therefore unenforced.
2. **Fail closed** at read: a single-valued axis carrying 2+ values raises rather
   than guessing. The card is excluded from routing with a stated reason.
3. **Replace, not add**, at write.

## Which axes are genuinely multi-valued

Not every ambiguity is a defect. `domain:` legitimately holds several values —
an issue really can span `pipeline` and `subsea`; 74 do. `needs:` accumulates
requirements by design. Forcing those to one value would destroy information.

That is exactly why the split has to be **declared** rather than inferred: no
scan can tell "this axis permits multiple" from "this axis was violated 74
times".

Hermetic: pure functions, explicit args, no gh and no network.

Run: uv run --with pyyaml pytest tests/dispatch/test_label_axis_cardinality.py
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
    spec = importlib.util.spec_from_file_location("route_axes", ROUTE_PY)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["route_axes"] = mod
    spec.loader.exec_module(mod)
    return mod


R = _load()
SINGLE = frozenset({"status:", "machine:", "lane:", "agent:"})


# --------------------------------------------------------------------------
# the declaration itself
# --------------------------------------------------------------------------


@pytest.fixture(scope="module")
def cfg() -> dict:
    return yaml.safe_load(RULES_PATH.read_text(encoding="utf-8"))


def test_config_declares_both_cardinalities(cfg):
    single, multi = R.load_axis_cardinality(cfg)
    assert single, "no single-valued axes declared — every check below would be vacuous"
    assert multi, "no multi-valued axes declared — domain: would be wrongly enforced"


def test_the_four_scalar_axes_are_declared_single(cfg):
    single, _ = R.load_axis_cardinality(cfg)
    for axis in ("status:", "machine:", "lane:", "agent:"):
        assert axis in single, f"{axis} is a scalar and must be declared single"


def test_domain_and_needs_are_declared_multi(cfg):
    """The axes where 2+ values is CORRECT.

    74 open issues carry multiple `domain:` labels legitimately. `needs:`
    accumulates requirements — an issue can need both a cross-review and the
    frontier tier.
    """
    _, multi = R.load_axis_cardinality(cfg)
    for axis in ("domain:", "needs:"):
        assert axis in multi, f"{axis} is genuinely multi-valued"


def test_an_axis_is_never_both(cfg):
    single, multi = R.load_axis_cardinality(cfg)
    assert not (single & multi), f"axes declared both single and multi: {single & multi}"


def test_every_declared_axis_is_a_prefix(cfg):
    """`status` and `status:` are different strings; a missing colon silently
    matches nothing and the axis goes unenforced while looking declared."""
    single, multi = R.load_axis_cardinality(cfg)
    for axis in single | multi:
        assert axis.endswith(":"), f"{axis!r} must end with ':' to match labels"


def test_each_axis_states_a_reason(cfg):
    """Declared as a mapping, not a list, so each entry carries WHY.

    A bare list invites flipping an axis on a hunch. A reason string makes the
    next person argue with a sentence instead of deleting a word.
    """
    axes = cfg.get("label_axes") or {}
    for bucket in ("single", "multi"):
        for axis, reason in (axes.get(bucket) or {}).items():
            assert isinstance(reason, str) and reason.strip(), f"{axis} has no stated reason"


# --------------------------------------------------------------------------
# fail closed — the core behaviour
# --------------------------------------------------------------------------


def test_single_axis_with_one_value_resolves():
    assert R.axis_value(["lane:claude"], "lane:", SINGLE) == "claude"


def test_single_axis_with_no_value_is_none():
    assert R.axis_value(["domain:cfd"], "lane:", SINGLE) is None


def test_single_axis_with_two_values_raises():
    """The whole point. Previously this silently returned the first label."""
    with pytest.raises(R.AmbiguousAxis) as exc:
        R.axis_value(["lane:claude", "lane:codex"], "lane:", SINGLE)
    msg = str(exc.value)
    assert "lane:" in msg
    assert "claude" in msg and "codex" in msg, (
        "the error must name BOTH values — an operator cannot fix what it does not print"
    )


def test_raised_values_are_sorted_for_a_stable_message():
    """Same conflict must produce the same text regardless of label order,
    or the error is as API-order-dependent as the bug it replaces."""
    a = str(pytest.raises(R.AmbiguousAxis, R.axis_value,
                          ["lane:claude", "lane:codex"], "lane:", SINGLE).value)
    b = str(pytest.raises(R.AmbiguousAxis, R.axis_value,
                          ["lane:codex", "lane:claude"], "lane:", SINGLE).value)
    assert a == b


def test_multi_axis_with_many_values_does_not_raise():
    """`domain:` is a set by design — enforcing it would destroy real information."""
    got = R.axis_value(["domain:pipeline", "domain:subsea"], "domain:", SINGLE)
    assert got == "pipeline"  # first, and that is FINE for a multi axis


def test_undeclared_axis_is_not_enforced():
    """Fail-open for the undeclared case is deliberate and bounded.

    A new axis must not break routing on the day it is invented. The
    compensating control is that undeclared axes are REPORTED (below), so this
    cannot become a silent hole — 'absence of signal reads as success' is the
    failure mode being avoided.
    """
    got = R.axis_value(["priority:high", "priority:low"], "priority:", SINGLE)
    assert got == "high"


def test_undeclared_axes_are_reported(cfg):
    """The compensating control for the fail-open above."""
    single, multi = R.load_axis_cardinality(cfg)
    labels = ["status:working", "priority:high", "epic"]
    undeclared = R.undeclared_axes(labels, single, multi)
    assert "priority:" in undeclared
    assert "status:" not in undeclared
    assert "epic" not in undeclared, "a bare label has no axis and is not a finding"


# --------------------------------------------------------------------------
# the guard is WIRED, not merely defined
# --------------------------------------------------------------------------


def test_resolve_provider_fails_closed_on_two_lanes():
    """Declared-but-unwired is the classic dead safety control.

    A validator that exists and is never called is indistinguishable from no
    validator — this repo has been bitten by that shape repeatedly (the alarm in
    deckhand#580, the `needs:cross-review` rule whose label never existed).
    """
    with pytest.raises(R.AmbiguousAxis):
        R.resolve_provider(["lane:claude", "lane:codex"], {},
                           {"provider": "claude"}, single_axes=SINGLE)


def test_resolve_provider_still_works_on_a_clean_card():
    provider, explicit, source = R.resolve_provider(
        ["lane:codex"], {}, {"provider": "claude"}, single_axes=SINGLE)
    assert (provider, explicit, source) == ("codex", False, "lane")


def test_resolve_provider_defaults_to_no_enforcement_only_when_asked():
    """Back-compat: omitting single_axes preserves the old lenient behaviour.

    Called out explicitly because a lenient DEFAULT is how an enforced guard
    quietly becomes optional. propose() must pass the loaded set — asserted next.
    """
    provider, _, _ = R.resolve_provider(["lane:claude", "lane:codex"], {},
                                        {"provider": "claude"})
    assert provider == "claude"  # first label, old behaviour, no raise


def test_propose_excludes_an_ambiguous_card(monkeypatch, capsys):
    """BEHAVIOURAL proof that the guard is wired into production.

    An earlier version of this test scanned `propose()`'s source for the string
    "single_axes" and passed while the wiring was mutated away — the identifier
    still appeared elsewhere in the function. That is the same weak shape as a
    read-only test that inspects the wrong helper: it asserts the code *mentions*
    the guard, not that the guard *runs*.

    Mutation-checked: deleting the `classify_card_axes` call in propose() fails
    this test.
    """
    cfg = {
        "label_axes": {"single": {"lane:": "one provider"}, "multi": {"domain:": "spans"}},
        "rules": [{"match": {}, "assign": {"machine": "dev-primary"}}],
        "defaults": {"provider": "claude", "machine": "dev-primary",
                     "routable_states": ["open"], "skip_if_labeled": []},
        "machine_aliases": {}, "providers": {}, "budget_pools": {},
        "wip_caps": {"per_machine": {"default": 99}, "per_provider": {}},
    }
    board = {"domain": None, "repo": "owner/name"}
    cards = [
        ({"number": 1, "source": "github_issue", "gh_state": "open",
          "gh_labels": ["lane:claude", "lane:codex"], "repo": "owner/name",
          "idempotency_key": "owner/name#1", "title": "ambiguous"}),
        ({"number": 2, "source": "github_issue", "gh_state": "open",
          "gh_labels": ["lane:codex"], "repo": "owner/name",
          "idempotency_key": "owner/name#2", "title": "clean"}),
    ]
    monkeypatch.setattr(R, "load_rules", lambda: cfg)
    # Live-issue source since workspace-hub#3736 — patching iter_cards would now
    # be a no-op that also let this test reach the network.
    monkeypatch.setattr(R, "fetch_issues_for_coverage", lambda repo: [
        {"number": 1, "state": "OPEN", "title": "ambiguous",
         "labels": [{"name": "lane:claude"}, {"name": "lane:codex"}]},
        {"number": 2, "state": "OPEN", "title": "clean",
         "labels": [{"name": "lane:codex"}]},
    ])

    class _Args:
        repo = None
        json = False
    proposals = R.propose(_Args())

    numbers = {str(p.get("number")) for p in proposals}
    assert "1" not in numbers, "the contradictory card must NOT be routed"
    assert "2" in numbers, "the clean card must still route — one bad card is not a run abort"
    assert "REFUSED" in capsys.readouterr().err, "a refusal must be reported, not silent"


def test_an_ambiguous_card_is_excluded_with_a_reason_not_crashed():
    """One bad card must not take down the whole run.

    Fail-closed means 'do not route THIS card', not 'abort routing'. A crash
    would pressure an operator into disabling the check entirely.
    """
    card = {"labels": ["lane:claude", "lane:codex"], "number": 1,
            "repo": "owner/name"}
    out = R.classify_card_axes(card, SINGLE)
    assert out["routable"] is False
    assert "lane:" in out["reason"]
    assert "claude" in out["reason"] and "codex" in out["reason"]


def test_a_clean_card_classifies_routable():
    card = {"labels": ["lane:codex", "domain:cfd", "domain:subsea"], "number": 2,
            "repo": "owner/name"}
    out = R.classify_card_axes(card, SINGLE)
    assert out["routable"] is True, "multi-valued domain: must not block routing"
    assert out["reason"] is None
