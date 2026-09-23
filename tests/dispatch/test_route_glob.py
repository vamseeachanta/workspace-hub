#!/usr/bin/env python3
"""TDD tests for scripts/dispatch/route.py `match_rule` glob/prefix domain matching.

Context (workspace-hub#2878 kanban reorg, Phase 0): subdomain splits create new
`domain:` values (e.g. `hydro` -> `hydro-diffraction`/`hydro-mooring`,
`solver` -> `solver-orcaflex`). The routing rules exact-match the parent domain
(`{repo: digitalmodel, domain: hydro}` -> licensed-win-1), so a split domain
silently falls through to the `dev-primary` catch-all and LOSES its licensed-
Windows routing. User decision (2026-05-30): make the matcher support a glob so
`domain: hydro*` covers the parent and all its subdomains with ONE rule.

These tests pin:
  * exact match unchanged (backward compat) — `solver` matches `solver`, NOT
    `solver-orcaflex` (so existing rules don't suddenly broaden)
  * glob match — `hydro*` matches `hydro`, `hydro-diffraction`, `hydro-mooring`
  * glob does not over-match — `hydro*` does not match `subsea`
  * a domain rule (exact OR glob) never matches a card with domain=None;
    the catch-all {} still does
  * first-match-wins preserved; repo+glob compose

Hermetic: `match_rule` is pure (no IO); import route.py via importlib and call it
with explicit args.

Run: uv run --with pyyaml pytest tests/dispatch/test_route_glob.py
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
ROUTE_PY = REPO_ROOT / "scripts" / "dispatch" / "route.py"


def _import_route():
    spec = importlib.util.spec_from_file_location("dispatch_route", ROUTE_PY)
    assert spec and spec.loader, f"cannot load spec for {ROUTE_PY}"
    mod = importlib.util.module_from_spec(spec)
    sys.modules["dispatch_route"] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture()
def route():
    return _import_route()


# Rule set mirroring routing-rules.yaml after the glob migration: the licensed
# domains use a glob, then the catch-all.
LICENSED = {"machine": "licensed-win-1"}
DEFAULT = {"machine": "dev-primary"}


def _rules():
    return [
        {"match": {"repo": "vamseeachanta/digitalmodel", "domain": "hydro*"},
         "assign": LICENSED, "reason": "hydro family -> licensed"},
        {"match": {"repo": "vamseeachanta/digitalmodel", "domain": "solver"},
         "assign": LICENSED, "reason": "solver exact -> licensed"},
        {"match": {}, "assign": DEFAULT, "reason": "catch-all"},
    ]


def _assign(route, *, repo, domain, labels=None):
    return route.match_rule(_rules(), repo=repo, domain=domain,
                            gh_labels=labels or []).get("assign")


def test_exact_match_unchanged_solver(route):
    assert _assign(route, repo="vamseeachanta/digitalmodel", domain="solver") == LICENSED


def test_exact_rule_does_not_broaden(route):
    # `solver` is an EXACT rule -> `solver-orcaflex` must NOT match it; it falls
    # to the catch-all. (Guards against accidentally globbing every rule.)
    assert _assign(route, repo="vamseeachanta/digitalmodel",
                   domain="solver-orcaflex") == DEFAULT


@pytest.mark.parametrize("domain", ["hydro", "hydro-diffraction", "hydro-mooring",
                                    "hydro-vessel-motions"])
def test_glob_matches_parent_and_subdomains(route, domain):
    assert _assign(route, repo="vamseeachanta/digitalmodel", domain=domain) == LICENSED


def test_glob_does_not_over_match(route):
    assert _assign(route, repo="vamseeachanta/digitalmodel", domain="subsea") == DEFAULT


def test_glob_respects_repo_scope(route):
    # hydro* rule is repo-scoped; same domain in another repo hits the catch-all.
    assert _assign(route, repo="vamseeachanta/otherrepo", domain="hydro-diffraction") == DEFAULT


def test_none_domain_never_matches_domain_rule(route):
    # A card with no domain must not match an exact OR glob domain rule.
    assert _assign(route, repo="vamseeachanta/digitalmodel", domain=None) == DEFAULT


def test_first_match_wins_preserved(route):
    # Put a glob catch-ish rule before a specific one; first wins.
    rules = [
        {"match": {"domain": "hydro*"}, "assign": {"machine": "A"}},
        {"match": {"domain": "hydro-diffraction"}, "assign": {"machine": "B"}},
    ]
    got = route.match_rule(rules, repo="r", domain="hydro-diffraction", gh_labels=[])
    assert got["assign"] == {"machine": "A"}, "first matching rule must win"


def test_question_mark_and_charclass_globs(route):
    rules = [{"match": {"domain": "subsea-?isers"}, "assign": {"machine": "Q"}},
             {"match": {"domain": "codes-[ab]*"}, "assign": {"machine": "C"}},
             {"match": {}, "assign": DEFAULT}]
    assert route.match_rule(rules, repo="r", domain="subsea-risers", gh_labels=[])["assign"] == {"machine": "Q"}
    assert route.match_rule(rules, repo="r", domain="codes-api", gh_labels=[])["assign"] == {"machine": "C"}
    assert route.match_rule(rules, repo="r", domain="codes-zzz", gh_labels=[])["assign"] == DEFAULT


# ── domain_family: precise parent-or-(parent-)child (not a greedy prefix) ─────

def _family_rules():
    return [
        {"match": {"domain_family": "hydro"}, "assign": LICENSED},
        {"match": {}, "assign": DEFAULT},
    ]


@pytest.mark.parametrize("domain", ["hydro", "hydro-diffraction", "hydro-mooring"])
def test_domain_family_matches_parent_and_children(route, domain):
    got = route.match_rule(_family_rules(), repo="r", domain=domain, gh_labels=[])
    assert got["assign"] == LICENSED


@pytest.mark.parametrize("domain", ["hydrocarbon", "hydrostatic", "hydrology", "hydro2", "subsea"])
def test_domain_family_does_not_over_match_prefix(route, domain):
    # the bare-glob bug: `hydro*` matched these; `domain_family: hydro` must NOT.
    got = route.match_rule(_family_rules(), repo="r", domain=domain, gh_labels=[])
    assert got["assign"] == DEFAULT, f"{domain} must NOT match the hydro family"


def test_domain_family_none_domain_does_not_match(route):
    got = route.match_rule(_family_rules(), repo="r", domain=None, gh_labels=[])
    assert got["assign"] == DEFAULT


# ── Integration: the REAL routing-rules.yaml must route the #2878 splits ──────

@pytest.mark.parametrize("domain", ["hydro", "hydro-diffraction", "hydro-mooring",
                                    "solver", "solver-orcaflex"])
def test_live_rules_route_digitalmodel_splits_to_licensed(route, domain):
    """Pin the shipped routing-rules.yaml: the licensed digitalmodel domains and
    their subdomain splits must resolve to a machine that can ACTUALLY RUN the
    work, not to the dev-primary catch-all. Guards the #2878 reorg from silently
    dropping licensed routing.

    deckhand#579: this test used to assert the literal `licensed-win-1`, and so
    it **protected the defect** — the destination host provably could not obtain
    an OrcaFlex licence (DLLError 25, no Sentinel LDK runtime), yet the suite
    stayed green because the test pinned the NAME rather than the CAPABILITY.

    Asserting the property instead of the identity also means the eventual #579
    migration needs no edit here: when a different host earns a dated
    `licence_verified` attestation and the rules move to it, this still passes —
    and if the rules ever move to a host WITHOUT one, this fails, which is the
    whole point.
    """
    cfg = route.load_rules()
    rules = cfg.get("rules", [])
    got = route.match_rule(rules, repo="vamseeachanta/digitalmodel",
                           domain=domain, gh_labels=[])
    target = got.get("assign", {}).get("machine")
    assert target and target != "dev-primary", (
        f"domain {domain!r} fell through to the catch-all, got {got}")

    spec = cfg.get("machines", {}).get(target, {})

    # Capability is LICENCE **and** CAPACITY. This test asserted only the first
    # until 2026-07-31, so it was satisfied by repointing batch work to a
    # workstation — trading a licence failure for a capacity failure. Owner:
    # "that host is not powerful enough."
    assert spec.get("capacity") == "heavy", (
        f"domain {domain!r} routes to {target!r} with capacity="
        f"{spec.get('capacity')!r}; these are batch-scale workloads and need the "
        f"heavy node. See tests/dispatch/test_route_capacity.py."
    )

    # The licence must be attested OR the block must be openly named. Routing to
    # a host with a pending prerequisite is legitimate; hiding that it is pending
    # is not.
    attested = isinstance(spec.get("licence_verified"), dict)
    assert attested or spec.get("blocked_on"), (
        f"domain {domain!r} routes to {target!r}, whose licence is neither "
        f"attested nor openly blocked — licence_verified="
        f"{spec.get('licence_verified')!r}, blocked_on absent (deckhand#579)."
    )


@pytest.mark.parametrize("domain", ["hydrocarbon", "hydrostatic", "solverless", "subsea"])
def test_live_rules_do_not_overmatch_prefix(route, domain):
    """The shipped rules must NOT pin unrelated hydro*/solver* prefixes to ANY
    licensed box (the domain_family fix for the adversarial-review over-match).

    Also name-independent (deckhand#579): checking against the set of licensed
    machines rather than one literal means a second licensed host cannot be
    added later and quietly become a legal over-match target.
    """
    cfg = route.load_rules()
    licensed = {
        name for name, spec in cfg.get("machines", {}).items()
        if set(spec.get("capabilities") or []) & {"orcaflex", "orcawave", "aqwa"}
    }
    assert licensed, "no licensed machines in the roster — this check would be vacuous"

    got = route.match_rule(cfg.get("rules", []), repo="vamseeachanta/digitalmodel",
                           domain=domain, gh_labels=[])
    assert got.get("assign", {}).get("machine") not in licensed, (
        f"domain {domain!r} must NOT route to a licensed box, got {got}")
