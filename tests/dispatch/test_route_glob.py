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


# ── Integration: the REAL routing-rules.yaml must route the #2878 splits ──────

@pytest.mark.parametrize("domain", ["hydro", "hydro-diffraction", "hydro-mooring",
                                    "solver", "solver-orcaflex"])
def test_live_rules_route_digitalmodel_splits_to_licensed(route, domain):
    """Pin the shipped routing-rules.yaml: the licensed digitalmodel domains and
    their subdomain splits must resolve to licensed-win-1, not the dev-primary
    catch-all. Guards the #2878 reorg from silently dropping licensed routing."""
    cfg = route.load_rules()
    rules = cfg.get("rules", [])
    got = route.match_rule(rules, repo="vamseeachanta/digitalmodel",
                           domain=domain, gh_labels=[])
    assert got.get("assign", {}).get("machine") == "licensed-win-1", (
        f"domain {domain!r} must route to licensed-win-1, got {got}")
