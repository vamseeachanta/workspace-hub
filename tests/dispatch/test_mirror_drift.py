#!/usr/bin/env python3
"""The kanban board mirror must agree with live GitHub about routing labels.

workspace-hub#3736.

## Why this exists

There are two sources of truth for routing, and they diverged:

    route.py --coverage, check-label-vocabulary.py  ->  live GitHub
    route.py propose(), dispatch.py                 ->  board mirror

`propose()` iterates `.claude/memory/kanban/boards/*.yaml`, so the **routing
engine** never reads GitHub. Measured 2026-07-31: the mirror held **37**
references to `machine:` labels that had been retired and deleted from GitHub
that morning, while every live-GitHub checker reported clean.

The dashboards were green and the dispatcher was wrong.

## The structural part

There is **no GitHub → board refresh path**. `.claude/memory/kanban/scripts/load.py`
runs boards → Hermes; nothing runs the other direction. So the drift is not a
lapsed cron that can be re-run — it grows monotonically, and every label
correction made against GitHub widens it.

That is why detection is worth having before a fix is chosen: whichever way the
mirror question is settled (refresh it, gate it, or retire it as a routing
input), *knowing when it disagrees* is correct.

## What is asserted

`mirror_drift()` compares the routing labels the mirror uses against the labels
that actually exist, and separates the two directions — they have different
causes and different fixes:

    retired   in the mirror, absent from GitHub  -> routes to a machine that is gone
    unknown   on GitHub, absent from the mirror  -> mirror has not caught up

Hermetic: pure set comparison, explicit inputs. No gh, no filesystem, no network.

Run: uv run --with pyyaml pytest tests/dispatch/test_mirror_drift.py
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
CHECK_PY = REPO_ROOT / "scripts" / "enforcement" / "check-label-vocabulary.py"


def _load():
    spec = importlib.util.spec_from_file_location("check_vocab", CHECK_PY)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["check_vocab"] = mod
    spec.loader.exec_module(mod)
    return mod


C = _load()


# --------------------------------------------------------------------------
# the two directions are separated
# --------------------------------------------------------------------------


def test_label_in_mirror_but_not_on_github_is_RETIRED():  # noqa: N802
    """The dangerous direction: the engine routes to something that is gone.

    This is the real 2026-07-31 shape — the mirror still held `machine:ace-win-1`
    after it was deleted, while GitHub had moved to `machine:licensed-win-1`. So
    BOTH directions fire at once: one retired, one not yet mirrored. An earlier
    draft of this test asserted `unknown == []`, which was simply wrong about its
    own fixture.
    """
    d = C.mirror_drift(mirror={"machine:ace-win-1"}, live={"machine:licensed-win-1"})
    assert d["retired"] == ["machine:ace-win-1"]
    assert d["unknown"] == ["machine:licensed-win-1"]


def test_label_on_github_but_not_in_mirror_is_UNKNOWN():  # noqa: N802
    """The lagging direction: real work the engine cannot see yet."""
    d = C.mirror_drift(mirror=set(), live={"machine:licensed-win-1"})
    assert d["unknown"] == ["machine:licensed-win-1"]
    assert d["retired"] == []


def test_agreement_is_no_drift():
    d = C.mirror_drift(mirror={"machine:dev-primary"}, live={"machine:dev-primary"})
    assert d["retired"] == [] and d["unknown"] == []


def test_only_ROUTING_axes_are_compared():  # noqa: N802
    """A `domain:` or `cat:` label differing is not a routing defect.

    Comparing every axis would bury the finding that matters under taxonomy
    churn — the mirror legitimately lags on labels the router never reads.
    """
    d = C.mirror_drift(mirror={"domain:cfd", "epic"}, live={"domain:subsea"})
    assert d["retired"] == [] and d["unknown"] == []


def test_output_is_sorted_for_a_stable_diff():
    """An unsorted report churns in CI and trains people to ignore it."""
    d = C.mirror_drift(mirror={"machine:z", "machine:a"}, live=set())
    assert d["retired"] == ["machine:a", "machine:z"]


# --------------------------------------------------------------------------
# extraction from board documents
# --------------------------------------------------------------------------


def test_extracts_routing_labels_from_board_cards():
    boards = [{"cards": [{"gh_labels": ["machine:dev-primary", "domain:cfd", "epic"]}]}]
    assert C.mirror_routing_labels(boards) == {"machine:dev-primary"}


def test_extraction_survives_a_board_with_no_cards():
    """A malformed or empty board must not crash the check — it must contribute
    nothing, so one bad file cannot mask drift in the others by aborting."""
    assert C.mirror_routing_labels([{}, {"cards": None}, {"cards": []}]) == set()


def test_extraction_covers_every_declared_routing_axis():
    boards = [{"cards": [{"gh_labels": ["lane:codex", "ai:claude", "machine:multi"]}]}]
    got = C.mirror_routing_labels(boards)
    assert got == {"lane:codex", "ai:claude", "machine:multi"}


# --------------------------------------------------------------------------
# guards on the guard
# --------------------------------------------------------------------------


def test_routing_axes_constant_is_not_empty():
    """An emptied ROUTING_AXES would make every comparison above vacuously pass."""
    assert C.ROUTING_AXES and all(a.endswith(":") for a in C.ROUTING_AXES)


def test_empty_inputs_do_not_fabricate_drift():
    d = C.mirror_drift(mirror=set(), live=set())
    assert d["retired"] == [] and d["unknown"] == []


@pytest.mark.parametrize("bad", [None, set()])
def test_missing_live_set_is_not_read_as_everything_retired(bad):
    """If the live query failed, EVERY mirror label would look retired.

    That would turn an API failure into a fleet-wide false alarm, and the
    resulting noise is how a real drift report gets ignored. The caller must
    distinguish 'no labels' from 'could not ask' — asserted here so the shape
    cannot regress silently.
    """
    d = C.mirror_drift(mirror={"machine:dev-primary"}, live=bad or set())
    assert d["live_was_empty"] is True, (
        "an empty live set must be flagged, not silently treated as authoritative"
    )
