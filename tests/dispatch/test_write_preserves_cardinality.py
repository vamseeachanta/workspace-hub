#!/usr/bin/env python3
"""A label write must never produce a contradictory scalar axis.

## What this is, and what it is not

`labels_for()` is already careful — it adds `machine:` only when the issue has
none, and `ai:` only when the issue has none ("respect manual assignment"). So
today's writer does **not** create ambiguity. This file is not a bug fix.

It is the **post-condition** that keeps it true. The read side now fails closed
(`test_label_axis_cardinality.py`), and a read guard without a matching write
guard is half a control: the resolver would refuse an issue the writer had just
created. One future `out.append(f"lane:{...}")` without the accompanying
"only if none exists" check is all it takes, and nothing would catch it — the
existing tests assert which labels are added, not what the resulting SET looks
like.

Asserting the invariant on the MERGED set is the difference between testing the
implementation and testing the property. The implementation may legitimately
change; the property may not.

## The guard is fail-closed at the mutation boundary

`assert_write_preserves_cardinality()` runs in `cmd_apply` before any
`gh issue edit`, so a violation refuses the write rather than being discovered
afterwards in a coverage report. A label written wrongly across hundreds of
issues is expensive to undo — #582's 676-issue migration is the local proof of
how far a bad label mutation travels.

Hermetic: pure functions, no gh, no network.

Run: uv run --with pyyaml pytest tests/dispatch/test_write_preserves_cardinality.py
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
ROUTE_PY = REPO_ROOT / "scripts" / "dispatch" / "route.py"


def _load():
    spec = importlib.util.spec_from_file_location("route_write", ROUTE_PY)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["route_write"] = mod
    spec.loader.exec_module(mod)
    return mod


R = _load()
SINGLE = frozenset({"status:", "machine:", "lane:", "agent:", "ai:"})


def _proposal(**kw):
    base = {"domain": "subsea", "machine": "dev-primary",
            "provider": "codex", "provider_explicit": True}
    base.update(kw)
    return base


# --------------------------------------------------------------------------
# the property: merged set stays cardinal
# --------------------------------------------------------------------------


@pytest.mark.parametrize("existing", [
    set(),
    {"machine:dev-primary"},
    {"ai:claude"},
    {"machine:licensed-win-2", "ai:claude", "domain:hydro"},
    {"dispatch:active"},
    {"domain:hydro", "domain:subsea"},          # legitimately multi
])
def test_labels_for_never_creates_a_second_scalar_value(existing):
    """The invariant, over the merged set — not over which labels were added."""
    additions = R.labels_for(_proposal(), existing=existing)
    merged = set(existing) | set(additions)
    for prefix in SINGLE:
        values = [lab for lab in merged if lab.startswith(prefix)]
        assert len(values) <= 1, (
            f"write would leave {prefix} with {sorted(values)} "
            f"(existing={sorted(existing)}, added={sorted(additions)})"
        )


def test_write_respects_an_existing_manual_assignment():
    """A human's machine: choice must survive a proposal that disagrees."""
    additions = R.labels_for(_proposal(machine="cfd-dedicated"),
                             existing={"machine:dev-primary"})
    assert not any(lab.startswith("machine:") for lab in additions), (
        "the writer must not override a manual assignment")


def test_multi_axis_may_gain_another_value():
    """`domain:` is a set — a write adding a second domain is not a violation.

    Included so the guard cannot be "fixed" later by forbidding all duplicates,
    which would silently destroy the 74 legitimately multi-domain issues.
    """
    additions = R.labels_for(_proposal(domain="riser"), existing=set())
    merged = {"domain:hydro"} | set(additions)
    assert len([lab for lab in merged if lab.startswith("domain:")]) == 2
    R.assert_write_preserves_cardinality(merged, SINGLE)  # must not raise


# --------------------------------------------------------------------------
# the assertion helper itself
# --------------------------------------------------------------------------


def test_helper_passes_a_clean_set():
    R.assert_write_preserves_cardinality(
        {"machine:dev-primary", "lane:codex", "domain:a", "domain:b"}, SINGLE)


def test_helper_raises_on_a_contradictory_set():
    with pytest.raises(R.AmbiguousAxis) as exc:
        R.assert_write_preserves_cardinality(
            {"lane:claude", "lane:codex"}, SINGLE)
    assert "claude" in str(exc.value) and "codex" in str(exc.value)


def test_helper_is_order_independent():
    """A set has no order, but the MESSAGE must still be deterministic."""
    a = str(pytest.raises(R.AmbiguousAxis, R.assert_write_preserves_cardinality,
                          {"lane:claude", "lane:codex"}, SINGLE).value)
    b = str(pytest.raises(R.AmbiguousAxis, R.assert_write_preserves_cardinality,
                          {"lane:codex", "lane:claude"}, SINGLE).value)
    assert a == b


# --------------------------------------------------------------------------
# WIRED at the mutation boundary, not merely defined
# --------------------------------------------------------------------------


def test_no_two_module_functions_share_a_name():
    """A redefinition silently wins, and its return TYPE may differ.

    Found by this file: `fetch_open_issues` was defined twice — a
    `{number -> labels}` mapping for the write path, and a `list[dict]` for the
    coverage reporter added later. Python kept the last one, so `cmd_apply`'s
    `live.get(number)` raised `AttributeError: 'list' object has no attribute
    'get'`. The write path was broken on main from the moment the coverage
    reporter landed, and nothing noticed because the only caller is
    `--apply --yes`, gated behind DISPATCH_APPLY_ENABLED.

    No linter in this repo's CI flags a module-level redefinition (ruff's F811
    is not enabled), so the collision is asserted here instead.
    """
    import ast
    tree = ast.parse(ROUTE_PY.read_text(encoding="utf-8"))
    names = [n.name for n in tree.body if isinstance(n, ast.FunctionDef)]
    dupes = sorted({n for n in names if names.count(n) > 1})
    assert not dupes, f"module-level functions defined more than once: {dupes}"


def test_cmd_apply_checks_before_writing(monkeypatch):
    """BEHAVIOURAL: a contradictory write must be refused before `gh` is reached.

    Deliberately not a source scan. The last source-scanning wiring test in this
    suite passed while the wiring was mutated away, because the identifier it
    grepped for still appeared elsewhere in the function.
    """
    def boom(*a, **k):  # noqa: ANN002, ANN003
        raise AssertionError("gh was reached with a contradictory label set")

    monkeypatch.setenv("DISPATCH_APPLY_ENABLED", "1")
    monkeypatch.setattr(R, "gh", boom, raising=False)
    monkeypatch.setattr(R, "ensure_labels", lambda *a, **k: None, raising=False)
    monkeypatch.setattr(R, "repo_has_domain_authority", lambda repo: False, raising=False)
    # a writer that has regressed into producing a second lane value
    monkeypatch.setattr(R, "labels_for",
                        lambda *a, **k: ["lane:claude", "lane:codex"], raising=False)
    # the write path's fetch returns {number -> set(labels)}, NOT a list
    monkeypatch.setattr(R, "fetch_open_issues",
                        lambda *a, **k: {1: set()}, raising=False)

    proposals = [{"repo": "owner/name", "number": 1, "machine": "m",
                  "provider": "claude", "domain": None, "provider_explicit": False}]
    with pytest.raises(R.AmbiguousAxis):
        R.cmd_apply(proposals, "owner/name", do_write=True, batch=50, pace=0.0)
