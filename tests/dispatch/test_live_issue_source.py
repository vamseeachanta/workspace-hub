#!/usr/bin/env python3
"""Routing reads LIVE GitHub, not the kanban board mirror. workspace-hub#3736.

Owner decision 2026-07-31: **retire the mirror as a routing input.**

## Why

Two sources of truth had diverged. `propose()` iterated
`.claude/memory/kanban/boards/*.yaml`, so the routing engine never read GitHub —
while every checker built this week did. The mirror held 6 `machine:`/`lane:`
labels that had been retired and deleted from GitHub the same day, and 7 labels
created that day were absent from it.

It was structural, not decay: `load.py` runs boards → Hermes; **nothing ran
GitHub → boards**. There was no refresh path to lapse, so the gap only grew.

## The design question this forced

A board gave each card exactly ONE domain — the board it lived in. A live issue
carries however many `domain:` labels it has, and **74 open issues legitimately
carry more than one** (`domain:` is declared multi-valued in `label_axes`).

`match_rule` took a single `domain`. Feeding it "the first `domain:` label" would
reintroduce the exact defect this epic spent the day removing: resolution by
GitHub's API ordering, silent and non-deterministic.

So matching is now **any-of**: a rule matches when *any* of the issue's domains
satisfies it, and rules remain first-match-wins. That is order-independent over
the label set while keeping rule precedence explicit and reviewable.

Hermetic: pure functions, injected issue lists. No gh, no network, no boards.

Run: uv run --with pyyaml pytest tests/dispatch/test_live_issue_source.py
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
ROUTE_PY = REPO_ROOT / "scripts" / "dispatch" / "route.py"


def _load():
    spec = importlib.util.spec_from_file_location("route_live", ROUTE_PY)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["route_live"] = mod
    spec.loader.exec_module(mod)
    return mod


R = _load()

RULES = [
    {"match": {"repo": "o/dm", "domain_family": "solver"}, "assign": {"machine": "heavy"}},
    {"match": {"gh_label": "domain:cfd"}, "assign": {"machine": "cfd"}},
    {"match": {}, "assign": {"machine": "dev-primary"}},
]


# --------------------------------------------------------------------------
# multi-domain matching is ORDER-INDEPENDENT
# --------------------------------------------------------------------------


def test_a_rule_matches_when_ANY_domain_satisfies_it():  # noqa: N802
    got = R.match_rule(RULES, repo="o/dm", domain=["hydro", "solver"], gh_labels=[])
    assert got["assign"] == {"machine": "heavy"}


def test_the_same_domains_in_the_other_order_give_the_same_answer():
    """The whole point.

    Taking "the first domain: label" would make routing depend on GitHub's API
    ordering — the defect this epic removed from `status:`, `lane:` and
    `machine:` today. Reintroducing it on `domain:` would be a poor trade.
    """
    a = R.match_rule(RULES, repo="o/dm", domain=["hydro", "solver"], gh_labels=[])
    b = R.match_rule(RULES, repo="o/dm", domain=["solver", "hydro"], gh_labels=[])
    assert a == b


def test_rules_remain_first_match_wins_across_domains():
    """Rule precedence must stay explicit, not become 'whichever domain matched'."""
    rules = [
        {"match": {"domain_family": "solver"}, "assign": {"machine": "A"}},
        {"match": {"domain_family": "hydro"}, "assign": {"machine": "B"}},
        {"match": {}, "assign": {"machine": "Z"}},
    ]
    for order in (["hydro", "solver"], ["solver", "hydro"]):
        got = R.match_rule(rules, repo="r", domain=order, gh_labels=[])
        assert got["assign"] == {"machine": "A"}, f"{order} must hit the FIRST rule"


def test_a_single_domain_string_still_works():
    """Back-compat: six existing call sites pass a bare string."""
    assert R.match_rule(RULES, repo="o/dm", domain="solver",
                        gh_labels=[])["assign"] == {"machine": "heavy"}


def test_no_domain_falls_through_to_the_catch_all():
    for empty in (None, [], ()):
        got = R.match_rule(RULES, repo="o/dm", domain=empty, gh_labels=[])
        assert got["assign"] == {"machine": "dev-primary"}


def test_unrelated_domains_do_not_over_match():
    got = R.match_rule(RULES, repo="o/dm", domain=["hydrocarbon", "solverless"], gh_labels=[])
    assert got["assign"] == {"machine": "dev-primary"}


# --------------------------------------------------------------------------
# live issues -> cards
# --------------------------------------------------------------------------


def _issue(number=1, labels=None, title="t", state="OPEN"):
    return {"number": number, "title": title, "state": state,
            "labels": [{"name": n} for n in (labels or [])]}


def test_issue_becomes_a_card_with_the_shape_propose_expects():
    card = R.issue_to_card(_issue(7, ["domain:cfd", "machine:dev-primary"]), "o/r")
    assert card["idempotency_key"].endswith("#7")
    assert card["repo"] == "o/r"
    assert card["gh_state"] == "open"
    assert "domain:cfd" in card["gh_labels"]
    assert card["source_url"].endswith("/o/r/issues/7")


def test_card_carries_EVERY_domain_not_just_one():  # noqa: N802
    """The board could only express one; an issue can have several."""
    card = R.issue_to_card(_issue(1, ["domain:hydro", "domain:subsea"]), "o/r")
    assert sorted(card["domains"]) == ["hydro", "subsea"]


def test_state_is_normalised_lowercase():
    """gh returns OPEN/CLOSED; `routable_states` is declared lowercase.

    A case mismatch would silently route nothing at all — every card filtered
    out, reported as an empty backlog rather than an error.
    """
    assert R.issue_to_card(_issue(1, state="OPEN"), "o/r")["gh_state"] == "open"


def test_priority_defaults_when_no_priority_label():
    assert R.issue_to_card(_issue(1), "o/r")["priority"] == 0


def test_priority_is_read_from_the_label():
    card = R.issue_to_card(_issue(1, ["priority:high"]), "o/r")
    assert card["priority"] > 0, "priority: must affect WIP ordering"


# --------------------------------------------------------------------------
# the mirror is genuinely out of the path
# --------------------------------------------------------------------------


def test_propose_does_not_read_the_board_mirror(monkeypatch):
    """BEHAVIOURAL, not a source scan.

    Booby-traps `iter_cards` — the board reader. If `propose()` still touches it,
    this raises. A grep for "iter_cards" would pass while the call remained.
    """
    def boom(*a, **k):  # noqa: ANN002, ANN003
        raise AssertionError("propose() still reads the kanban board mirror")

    monkeypatch.setattr(R, "iter_cards", boom, raising=False)
    monkeypatch.setattr(R, "load_rules", lambda: {
        "rules": [{"match": {}, "assign": {"machine": "dev-primary"}}],
        "defaults": {"provider": "claude", "machine": "dev-primary",
                     "routable_states": ["open"], "skip_if_labeled": []},
        "machines": {}, "machine_aliases": {}, "providers": {},
        "budget_pools": {}, "wip_caps": {"per_machine": {"default": 99}, "per_provider": {}},
        "label_axes": {"single": {"lane:": "one"}, "multi": {"domain:": "many"}},
    }, raising=False)
    monkeypatch.setattr(R, "fetch_issues_for_coverage",
                        lambda repo: [_issue(1, ["domain:cfd"])], raising=False)

    class _A:
        repo = "o/r"
        json = False
    out = R.propose(_A())
    assert [str(p["number"]) for p in out] == ["1"]
