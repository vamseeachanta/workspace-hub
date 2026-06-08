"""Tests for scripts/ai/provider_route.py (#2970 / F3).

Exercises the SEED -> PRUNE -> RANK resolution contract:
  1. SEED  from policy['roles'][task_type] (fail closed on unknown).
  2. PRUNE hard machine constraints matched against attrs.
  3. RANK  scorecard reorders survivors only; never re-adds a pruned provider.

The module is loaded by file path via importlib and registered in sys.modules
before exec (mirrors tests/ai/test_dispatch_leader.py).
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "scripts" / "ai" / "provider_route.py"
spec = importlib.util.spec_from_file_location("provider_route", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules["provider_route"] = module
spec.loader.exec_module(module)

route = module.route
load_policy = module.load_policy

# The real policy YAML is the contract under test.
POLICY = load_policy()

# Scorecard fixture that ranks codex FIRST — used to prove a hard-pruned
# provider can never be re-added by the scorecard.
SCORECARD_CODEX_FIRST = {"recommended_provider_order": ["codex", "claude", "gemini"]}


def test_policy_has_expected_roles():
    roles = POLICY["roles"]
    assert roles["orchestrate"] == ["claude"]
    assert roles["plan"] == ["claude"]
    assert "codex" in roles["implement"]
    assert "recon" in roles and roles["recon"] == ["gemini"]
    assert "dispatch" in roles and roles["dispatch"] == ["hermes"]


def test_review_returns_two_plus_with_codex_and_gemini():
    result = route("review", "ace-linux-2", policy=POLICY)
    assert len(result) >= 2
    assert "codex" in result
    assert "gemini" in result


def test_heavy_authoring_prunes_codex_on_ace_linux_1_even_with_scorecard():
    # Hard constraint fires on authoring_weight=heavy → codex removed, and the
    # scorecard (which ranks codex first) must NOT be able to re-add it.
    result = route(
        "implement",
        "ace-linux-1",
        {"authoring_weight": "heavy"},
        policy=POLICY,
        scorecard=SCORECARD_CODEX_FIRST,
    )
    assert "codex" not in result
    # claude survives (no constraint against it)
    assert "claude" in result


def test_light_authoring_may_include_codex_on_ace_linux_1():
    # Constraint only fires on heavy → light leaves codex eligible.
    result = route(
        "implement",
        "ace-linux-1",
        {"authoring_weight": "light"},
        policy=POLICY,
    )
    assert "codex" in result


def test_no_attrs_does_not_fire_conditional_constraint():
    # disallow_attrs requires authoring_weight=heavy to be present-and-equal;
    # with no attrs the constraint must NOT fire.
    result = route("implement", "ace-linux-1", policy=POLICY)
    assert "codex" in result


def test_unknown_task_type_raises_value_error():
    with pytest.raises(ValueError):
        route("bogus_type", "ace-linux-1", policy=POLICY)


def test_scorecard_reorders_survivors_but_never_readds_pruned():
    # review default policy order: [codex, gemini, claude].
    # On ace-linux-1 heavy authoring would prune codex for 'implement', but
    # review has no per-provider heavy constraint — so use a hand-built policy
    # to prove the invariant precisely: prune codex, then a codex-first
    # scorecard must not bring it back, and survivors must be reordered.
    policy = {
        "roles": {"review": ["codex", "gemini", "claude"]},
        "machine_overrides": {
            "m1": {"codex": {"disallow_attrs": [], "reason": "unconditional"}}
        },
    }
    # Scorecard puts gemini AFTER claude to prove reordering actually happens.
    scorecard = {"recommended_provider_order": ["claude", "gemini"]}
    result = route("review", "m1", policy=policy, scorecard=scorecard)
    assert "codex" not in result  # pruned, never re-added
    assert result == ["claude", "gemini"]  # survivors reordered per scorecard


def test_scorecard_appends_providers_absent_from_order():
    # A survivor not in the scorecard keeps relative policy order, appended last.
    policy = {"roles": {"review": ["codex", "gemini", "claude"]}, "machine_overrides": {}}
    scorecard = {"recommended_provider_order": ["claude"]}
    result = route("review", "any-machine", policy=policy, scorecard=scorecard)
    # claude first (scorecard); codex, gemini keep their relative policy order after.
    assert result == ["claude", "codex", "gemini"]


def test_unconditional_machine_disallow_prunes_regardless_of_attrs():
    policy = {
        "roles": {"implement": ["codex", "claude"]},
        "machine_overrides": {"m1": {"codex": {"disallow_attrs": [], "reason": "x"}}},
    }
    assert route("implement", "m1", {"authoring_weight": "light"}, policy=policy) == ["claude"]
    assert route("implement", "m1", policy=policy) == ["claude"]


def test_no_scorecard_preserves_policy_order():
    result = route("review", "ace-linux-2", policy=POLICY)
    # default policy order is [codex, gemini, claude]; no scorecard => unchanged.
    assert result == ["codex", "gemini", "claude"]


# ── #2970 code-review MINOR fixes ────────────────────────────────────────────
def test_cli_fails_closed_on_empty_after_prune(capsys):
    import importlib.util as _u, sys as _s
    # unconditional disallow of all providers for a fake role on a machine
    pol = {"roles": {"only": ["codex"]},
           "machine_overrides": {"m": {"codex": {"disallow_attrs": []}}}}
    import json as _j, tempfile, os
    d = tempfile.mkdtemp(); pp = os.path.join(d, "p.yaml")
    import yaml as _y; open(pp, "w").write(_y.safe_dump(pol))
    rc = module.main(["only", "m", "--policy", pp, "--scorecard", "/nonexistent"])
    assert rc == 3                              # fail closed
    rc2 = module.main(["only", "m", "--policy", pp, "--scorecard", "/nonexistent", "--allow-empty"])
    assert rc2 == 0                             # opt-in permits empty


def test_constraint_clause_must_be_string():
    import pytest
    with pytest.raises(ValueError):
        module._constraint_matches([{"not": "a string"}], {"x": "y"})
