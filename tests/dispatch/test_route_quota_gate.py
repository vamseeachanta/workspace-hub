#!/usr/bin/env python3
"""TDD tests for scripts/dispatch/route.py codex weekly-quota dispatch gate (#3030).

Contracts pinned (per docs/plans/2026-06-10-issue-3030-codex-quota-dispatch-gate.md,
adversarial-review-revised):

- resolve_provider returns (provider, provider_explicit, source),
  source in {"ai", "rule", "lane", "default"}.
- lane_quota_demotion suspends ONLY the lane-derived codex choice, strictly
  below 10% remaining; ai:/rule codex and any claude routing are never altered;
  unknown quota (None) fails open.
- codex_weekly_remaining: window-validity guard — a snapshot may drive demotion
  only when source == "app-server-live" OR resets_at_epoch > now; cross-reset
  stale fallback, subprocess failure, and malformed JSON all return None.
- No environment variable alters gate behavior; the only override is the
  explicit --codex-remaining CLI value passed as the `override` argument.
- propose() consults the quota helper at most once per run; demoted proposals
  carry quota_demoted=True and keep provider_explicit=False (no sticky ai:
  labels); pool accounting follows the demoted provider.

Hermetic: import route.py via importlib; subprocess and card iteration are
monkeypatched — no live quota calls, no kanban board reads.

Run: uv run --with pyyaml pytest tests/dispatch/test_route_quota_gate.py
"""
from __future__ import annotations

import importlib.util
import json
import subprocess as real_subprocess
import sys
import time
import types
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
ROUTE_PY = REPO_ROOT / "scripts" / "dispatch" / "route.py"


def _import_route():
    spec = importlib.util.spec_from_file_location("dispatch_route_quota", ROUTE_PY)
    assert spec and spec.loader, f"cannot load spec for {ROUTE_PY}"
    mod = importlib.util.module_from_spec(spec)
    sys.modules["dispatch_route_quota"] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture()
def route():
    return _import_route()


DEFAULTS = {"machine": "dev-primary", "provider": "claude"}


# --- resolve_provider source paths -----------------------------------------

def test_resolve_provider_exposes_source(route):
    assert route.resolve_provider(["ai:claude"], {}, DEFAULTS) == ("claude", True, "ai")
    assert route.resolve_provider([], {"provider": "codex"}, DEFAULTS) == ("codex", True, "rule")
    assert route.resolve_provider(["lane:codex"], {}, DEFAULTS) == ("codex", False, "lane")
    assert route.resolve_provider([], {}, DEFAULTS) == ("claude", False, "default")


# --- pure gate decision ------------------------------------------------------

def test_gate_demotes_lane_codex_strictly_below_10(route):
    assert route.lane_quota_demotion("codex", "lane", 9.9, DEFAULTS) == ("claude", True)
    assert route.lane_quota_demotion("codex", "lane", 10.0, DEFAULTS) == ("codex", False)


def test_gate_never_touches_ai_rule_or_claude(route):
    assert route.lane_quota_demotion("codex", "ai", 2, DEFAULTS) == ("codex", False)
    assert route.lane_quota_demotion("codex", "rule", 2, DEFAULTS) == ("codex", False)
    assert route.lane_quota_demotion("claude", "lane", 2, DEFAULTS) == ("claude", False)


def test_gate_fails_open_on_unknown_quota(route):
    assert route.lane_quota_demotion("codex", "lane", None, DEFAULTS) == ("codex", False)


# --- quota helper: window validity + fail-open -------------------------------

def _fake_run(payload=None, *, raise_exc=None, stdout=None, returncode=0):
    def run(cmd, **kw):
        # pin the subprocess contract (codex code-review MINOR): exact command
        # and an explicit timeout, or these fakes mask integration drift
        assert cmd[0].endswith("query-codex-usage.sh") and cmd[1:] == ["--json"], cmd
        assert "timeout" in kw and kw["timeout"] > 0
        if raise_exc:
            raise raise_exc
        r = types.SimpleNamespace()
        r.stdout = stdout if stdout is not None else json.dumps(payload)
        r.returncode = returncode
        return r
    return run


def test_helper_accepts_app_server_live(route, monkeypatch):
    monkeypatch.setattr(route.subprocess, "run",
                        _fake_run({"pct_remaining": 9, "source": "app-server-live"}))
    assert route.codex_weekly_remaining() == 9.0


def test_helper_accepts_fallback_with_future_reset(route, monkeypatch):
    monkeypatch.setattr(route.subprocess, "run", _fake_run({
        "pct_remaining": 9, "source": "local-session-rate-limits",
        "resets_at_epoch": time.time() + 3600}))
    assert route.codex_weekly_remaining() == 9.0


def test_helper_rejects_cross_reset_stale_fallback(route, monkeypatch, capsys):
    monkeypatch.setattr(route.subprocess, "run", _fake_run({
        "pct_remaining": 9, "source": "local-session-rate-limits",
        "resets_at_epoch": time.time() - 60}))
    assert route.codex_weekly_remaining() is None
    assert "local-session-rate-limits" in capsys.readouterr().err


def test_helper_fails_open_on_timeout_and_bad_json(route, monkeypatch):
    monkeypatch.setattr(route.subprocess, "run",
                        _fake_run(raise_exc=real_subprocess.TimeoutExpired("x", 10)))
    assert route.codex_weekly_remaining() is None
    monkeypatch.setattr(route.subprocess, "run", _fake_run(stdout="not json"))
    assert route.codex_weekly_remaining() is None


def test_helper_rejects_malformed_numerics_and_bad_exit(route, monkeypatch):
    # out-of-range / non-finite pct_remaining from an ACCEPTED source must
    # never demote (codex code-review MAJOR): fail open instead
    for bad in ("-1", 101, float("nan"), float("inf")):
        monkeypatch.setattr(route.subprocess, "run",
                            _fake_run({"pct_remaining": bad, "source": "app-server-live"}))
        assert route.codex_weekly_remaining() is None, f"accepted bad pct {bad!r}"
    # nonzero exit with parseable stdout must also fail open
    monkeypatch.setattr(route.subprocess, "run",
                        _fake_run({"pct_remaining": 5, "source": "app-server-live"},
                                  returncode=3))
    assert route.codex_weekly_remaining() is None


def test_env_var_cannot_alter_gate(route, monkeypatch):
    monkeypatch.setenv("DISPATCH_CODEX_REMAINING", "5")
    monkeypatch.setattr(route.subprocess, "run",
                        _fake_run({"pct_remaining": 50, "source": "app-server-live"}))
    assert route.codex_weekly_remaining() == 50.0  # env var ignored


def test_cli_override_skips_subprocess_and_is_loud(route, monkeypatch, capsys):
    def boom(*a, **k):
        raise AssertionError("subprocess must not run under --codex-remaining")
    monkeypatch.setattr(route.subprocess, "run", boom)
    assert route.codex_weekly_remaining(override=5) == 5.0
    assert "codex-remaining" in capsys.readouterr().err


# --- propose() integration: memoization, annotation, no sticky labels --------

def _fake_boards(route, monkeypatch, n_cards=2, labels=("lane:codex",)):
    board = {"repo": "vamseeachanta/workspace-hub", "domain": None}
    cards = [
        (board, {"idempotency_key": f"gh:vamseeachanta/workspace-hub#{i}",
                 "source": "github_issue", "gh_state": "open",
                 "gh_labels": list(labels), "title": f"card {i}", "priority": 0})
        for i in range(n_cards)
    ]
    monkeypatch.setattr(route, "iter_cards", lambda: iter(cards))
    monkeypatch.setattr(route, "load_rules", lambda: {
        "rules": [{"match": {}, "assign": {"machine": "dev-primary"}}],
        "defaults": DEFAULTS})


def test_propose_demotes_memoized_and_non_sticky(route, monkeypatch):
    _fake_boards(route, monkeypatch, n_cards=3)
    calls = []
    monkeypatch.setattr(route, "codex_weekly_remaining",
                        lambda override=None: calls.append(1) or 5.0)
    args = types.SimpleNamespace(repo=None, codex_remaining=None)
    proposals = route.propose(args)
    assert len(calls) == 1, "quota helper must be memoized per run"
    assert all(p["provider"] == "claude" for p in proposals)
    assert all(p["quota_demoted"] for p in proposals)
    assert all(p["provider_explicit"] is False for p in proposals)
    # no sticky ai: label from a demoted card
    assert not any(l.startswith("ai:")
                   for l in route.labels_for(proposals[0], existing=set()))


def test_propose_no_demotion_at_or_above_10(route, monkeypatch):
    _fake_boards(route, monkeypatch)
    monkeypatch.setattr(route, "codex_weekly_remaining", lambda override=None: 10.0)
    args = types.SimpleNamespace(repo=None, codex_remaining=None)
    proposals = route.propose(args)
    assert all(p["provider"] == "codex" for p in proposals)
    assert not any(p["quota_demoted"] for p in proposals)


def test_propose_skips_quota_when_no_lane_codex(route, monkeypatch):
    _fake_boards(route, monkeypatch, labels=("lane:claude",))
    def boom(override=None):
        raise AssertionError("quota must not be consulted without lane:codex cards")
    monkeypatch.setattr(route, "codex_weekly_remaining", boom)
    args = types.SimpleNamespace(repo=None, codex_remaining=None)
    proposals = route.propose(args)
    assert all(p["provider"] == "claude" for p in proposals)


def test_demoted_cards_count_against_claude_not_codex_pool(route):
    cfg = {
        "providers": {"codex": {"auto_routable": True}, "claude": {"auto_routable": True}},
        "budget_pools": {"codex_pool": {"members": ["codex"], "max_concurrent": 1}},
        "wip_caps": {"per_machine": {"dev-primary": 10},
                     "per_provider": {"claude": 1}},
    }
    def card(key, provider, demoted):
        return {"key": key, "machine": "dev-primary", "provider": provider,
                "provider_explicit": False, "quota_demoted": demoted, "priority": 0}
    out = route.apply_wip([card("a", "claude", True), card("b", "claude", True),
                           card("c", "codex", False)], cfg)
    # first demoted card takes the claude cap; second queues; codex_pool untouched
    assert [p["slot"] for p in out] == ["active-eligible", "queued", "active-eligible"]
