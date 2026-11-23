#!/usr/bin/env python3
"""TDD tests for the route.py write gate — deckhand#584 slice 2.

The defect this closes: `route.py:395` PRINTS "`--apply` for Phase B (disabled)",
but `--apply` and `--yes` are real flags and `cmd_apply()` reaches a live
`gh issue edit --add-label`. The "disabled" existed only in a help string.

That matters because the engine's capability map is known-wrong — routing-rules
claims a solver capability for a host that cannot obtain the licence (#579) — so
an accidental `--apply --yes` would dispatch work into guaranteed failure across
hundreds of issues.

The gate is an explicit environment feature flag, deliberately NOT a config file
value: config is committed and diffable, so a flag flipped in a PR could be
merged without anyone registering that it armed a mass-write path. An env var
must be set by the person running the command, at the moment they run it.

Hermetic: no gh, no network. Every write primitive is booby-trapped.

Run: uv run --with pyyaml pytest tests/dispatch/test_route_write_gate.py
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

FLAG = "DISPATCH_APPLY_ENABLED"


@pytest.fixture(autouse=True)
def _no_flag(monkeypatch):
    """Default state for every test: the flag is UNSET.

    The gate must fail closed, so the unset case is the one that matters most.
    """
    monkeypatch.delenv(FLAG, raising=False)


def _boom(*a, **k):  # noqa: ANN002, ANN003
    raise AssertionError("a write primitive was reached through a closed gate")


@pytest.fixture
def trapped(monkeypatch):
    """Booby-trap every path that can mutate a live issue."""
    monkeypatch.setattr(R, "gh", _boom, raising=False)
    monkeypatch.setattr(R, "ensure_labels", _boom, raising=False)
    monkeypatch.setattr(R, "fetch_open_issues", _boom, raising=False)
    monkeypatch.setattr(R, "fetch_issues_for_coverage", _boom, raising=False)


# --------------------------------------------------------------------------
# fail closed
# --------------------------------------------------------------------------


def test_write_is_refused_when_flag_unset(trapped):
    """`--apply --yes` without the flag must not write. This is the whole point."""
    with pytest.raises(SystemExit) as exc:
        R.assert_write_allowed()
    assert FLAG in str(exc.value), "the error must name the flag, or nobody can fix it"


def test_write_is_refused_when_flag_is_empty(monkeypatch, trapped):
    monkeypatch.setenv(FLAG, "")
    with pytest.raises(SystemExit):
        R.assert_write_allowed()


@pytest.mark.parametrize("value", ["0", "false", "no", "off", "maybe", "true-ish", " "])
def test_write_is_refused_for_any_non_affirmative_value(monkeypatch, trapped, value):
    """Fail closed on anything that is not an explicit yes.

    A gate that treats "0" or "false" as truthy — the naive `if os.environ.get(F)`
    — is worse than no gate, because it reads as protected.
    """
    monkeypatch.setenv(FLAG, value)
    with pytest.raises(SystemExit):
        R.assert_write_allowed()


# --------------------------------------------------------------------------
# open only on an explicit affirmative
# --------------------------------------------------------------------------


@pytest.mark.parametrize("value", ["1", "true", "TRUE", "yes", "on"])
def test_write_is_allowed_only_on_explicit_affirmative(monkeypatch, value):
    monkeypatch.setenv(FLAG, value)
    R.assert_write_allowed()  # must not raise


# --------------------------------------------------------------------------
# the gate is actually WIRED, not merely defined
# --------------------------------------------------------------------------


def test_cmd_apply_with_write_is_gated(monkeypatch, trapped):
    """Declared-but-unwired is the classic dead safety control.

    A gate function that exists and is never called is indistinguishable from no
    gate at all — this repo has already been bitten by that shape (#580's alarm,
    the canary denylist in the PS collector).
    """
    proposals = [{"repo": "owner/name", "number": 1, "machine": "m", "provider": "claude"}]
    with pytest.raises(SystemExit) as exc:
        R.cmd_apply(proposals, "owner/name", do_write=True, batch=50, pace=0.0)
    assert FLAG in str(exc.value)


def test_dry_run_apply_is_never_gated(monkeypatch, capsys):
    """`--apply` WITHOUT `--yes` is a preview and must keep working unflagged.

    Gating the dry run too would push people toward setting the flag habitually,
    which defeats the gate.
    """
    monkeypatch.setattr(R, "ensure_labels", lambda *a, **k: None, raising=False)
    monkeypatch.setattr(R, "repo_has_domain_authority", lambda repo: False, raising=False)
    monkeypatch.setattr(R, "labels_for", lambda *a, **k: ["machine:m"], raising=False)
    monkeypatch.setattr(R, "gh", _boom, raising=False)
    monkeypatch.setattr(R, "fetch_open_issues", _boom, raising=False)
    monkeypatch.setattr(R, "fetch_issues_for_coverage", _boom, raising=False)

    proposals = [{"repo": "owner/name", "number": 1, "machine": "m", "provider": "claude"}]
    R.cmd_apply(proposals, "owner/name", do_write=False, batch=50, pace=0.0)
    assert "#1" in capsys.readouterr().out


def test_main_apply_yes_is_gated_end_to_end(monkeypatch, trapped):
    """The real production invocation, through argument parsing."""
    monkeypatch.setattr(
        R, "propose",
        lambda args: [{"repo": "owner/name", "number": 1, "machine": "m", "provider": "claude"}],
        raising=False,
    )
    monkeypatch.setattr(
        sys, "argv", ["route.py", "--apply", "--yes", "--repo", "owner/name"]
    )
    with pytest.raises(SystemExit) as exc:
        R.main()
    assert FLAG in str(exc.value)


# --------------------------------------------------------------------------
# the help text must stop lying
# --------------------------------------------------------------------------


def test_help_text_no_longer_claims_phase_b_is_disabled():
    """The original text said "(disabled)" while the path was live.

    A comment that misstates a safety property is worse than none: it stops the
    next reader from checking. This plan's own first draft repeated that claim.
    """
    import ast

    tree = ast.parse(ROUTE_PY.read_text(encoding="utf-8"))
    docstrings = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            doc = ast.get_docstring(node, clean=False)
            if doc:
                docstrings.add(doc)

    # Scan STRING LITERALS the user can actually see, not comments: the module
    # documents the old text to explain why the gate exists, and a naive
    # substring scan would forbid the module explaining itself.
    printed = [
        n.value for n in ast.walk(tree)
        if isinstance(n, ast.Constant)
        and isinstance(n.value, str)
        and n.value not in docstrings
    ]
    offenders = [s for s in printed if "Phase B (disabled)" in s]
    assert not offenders, f"user-visible text still claims Phase B is disabled: {offenders}"


def test_help_text_names_the_flag():
    """Whoever hits the gate must be able to find out how to open it."""
    src = ROUTE_PY.read_text(encoding="utf-8")
    assert FLAG in src
