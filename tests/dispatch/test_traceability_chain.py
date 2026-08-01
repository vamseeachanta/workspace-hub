#!/usr/bin/env python3
"""Traceability chain: issue → assigned → dispatched → executed → result → published.

deckhand#584 §3. The requirement is explicit that the interesting output is the
BREAK, not the completion: *"surface where the chain breaks, not just where it
completes — a result with no capability is the interesting case."*

## What building it found

`SCHEMA.yaml:125` documents the lifecycle as **`ready | active | done`**. Only
`dispatch:ready` exists as a label, in any repo. `dispatch:active` and
`dispatch:done` were never created.

Measured 2026-07-31: **867 open issues carry `dispatch:ready`** (525
workspace-hub, 342 digitalmodel). Nothing can move them out of it, because the
next two states have no vocabulary. SCHEMA.yaml:150 says as much in passing —
*"route.py only ever moves a card to dispatch:ready"* — but reads as a note about
route.py's scope rather than a dead end for 867 issues.

So the chain breaks at its second link, and every issue in the system is parked
one step past the start.

## The distinction this reporter is built around

A stage with zero occupancy has two completely different causes:

    UNREPRESENTABLE  the label does not exist — nothing COULD be here
    EMPTY            the label exists and nobody is in it

Conflating them is the failure this whole epic keeps meeting: absence of signal
reading as success. A chain report that just prints `executed: 0` invites
"nothing has finished yet"; the truth is "finishing cannot be recorded".

So every stage carries its vocabulary status, and a stage whose label is missing
is reported as a **defect in the chain itself**, not as a count.

Hermetic: pure functions over issue dicts and a label inventory. No gh, no network.

Run: uv run --with pyyaml pytest tests/dispatch/test_traceability_chain.py
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
CHAIN_PY = REPO_ROOT / "scripts" / "dispatch" / "chain.py"


def _load():
    spec = importlib.util.spec_from_file_location("chain", CHAIN_PY)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["chain"] = mod
    spec.loader.exec_module(mod)
    return mod


C = _load()

FULL_VOCAB = {"machine:dev-primary", "dispatch:ready", "dispatch:active", "dispatch:done"}
REAL_VOCAB = {"machine:dev-primary", "dispatch:ready"}   # what actually exists today


# --------------------------------------------------------------------------
# stage assignment
# --------------------------------------------------------------------------


def test_issue_with_no_machine_is_unassigned():
    assert C.stage_of({"labels": ["domain:cfd"]}) == "unassigned"


def test_issue_with_a_machine_is_assigned():
    assert C.stage_of({"labels": ["machine:dev-primary"]}) == "assigned"


def test_dispatch_ready_is_queued():
    assert C.stage_of({"labels": ["machine:dev-primary", "dispatch:ready"]}) == "queued"


def test_furthest_stage_wins():
    """An issue carrying several markers is at its FURTHEST point, not its first.

    Reporting the earliest would make progress invisible — the chain is about how
    far work got.
    """
    labels = ["machine:dev-primary", "dispatch:ready", "dispatch:done"]
    assert C.stage_of({"labels": labels}) == "executed"


def test_closed_issue_without_markers_is_not_silently_executed():
    """Closing an issue is not evidence it ran.

    Treating `state: closed` as "executed" would fabricate the very completion
    the chain exists to verify.
    """
    got = C.stage_of({"labels": ["machine:dev-primary"], "state": "closed"})
    assert got == "assigned"


# --------------------------------------------------------------------------
# the core distinction: unrepresentable vs empty
# --------------------------------------------------------------------------


def test_a_stage_whose_label_does_not_exist_is_UNREPRESENTABLE():  # noqa: N802
    """The defect this file exists for.

    `dispatch:done` does not exist in any repo. A report saying `executed: 0`
    would read as "nothing has finished"; the truth is "finishing cannot be
    recorded".
    """
    rep = C.chain_report([{"labels": ["machine:dev-primary", "dispatch:ready"]}], REAL_VOCAB)
    assert rep["stages"]["executed"]["vocabulary"] == "MISSING"
    assert rep["stages"]["queued"]["vocabulary"] == "present"


def test_a_stage_with_vocabulary_and_nobody_in_it_is_EMPTY_not_missing():  # noqa: N802
    rep = C.chain_report([{"labels": ["machine:dev-primary"]}], FULL_VOCAB)
    assert rep["stages"]["executed"]["vocabulary"] == "present"
    assert rep["stages"]["executed"]["count"] == 0


def test_missing_vocabulary_is_reported_as_a_break_not_a_count():
    """A count of zero invites a shrug. A named break invites a fix."""
    rep = C.chain_report([{"labels": ["machine:dev-primary", "dispatch:ready"]}], REAL_VOCAB)
    breaks = rep["breaks"]
    assert any(b["stage"] == "executed" and b["kind"] == "unrepresentable" for b in breaks), breaks


def test_no_break_reported_when_the_whole_vocabulary_exists():
    rep = C.chain_report([{"labels": ["machine:dev-primary"]}], FULL_VOCAB)
    assert not [b for b in rep["breaks"] if b["kind"] == "unrepresentable"]


# --------------------------------------------------------------------------
# drop-off: where does the population actually stop
# --------------------------------------------------------------------------


def _population():
    return [
        {"labels": []},                                                    # unassigned
        {"labels": ["machine:dev-primary"]},                               # assigned
        {"labels": ["machine:dev-primary"]},                               # assigned
        {"labels": ["machine:dev-primary", "dispatch:ready"]},             # queued
        {"labels": ["machine:dev-primary", "dispatch:ready"]},             # queued
        {"labels": ["machine:dev-primary", "dispatch:ready"]},             # queued
    ]


def test_report_counts_every_issue_exactly_once():
    """A histogram that does not sum to the population is silently lossy."""
    rep = C.chain_report(_population(), REAL_VOCAB)
    assert sum(s["count"] for s in rep["stages"].values()) == len(_population())


def test_report_identifies_the_wall(_pop=None):
    """The stage where the most work is stuck AND the next step is impossible.

    That pairing is the actionable finding: a pile-up in front of a missing
    state is a different problem from a pile-up in front of a busy one.
    """
    rep = C.chain_report(_population(), REAL_VOCAB)
    assert rep["wall"] is not None
    assert rep["wall"]["stage"] == "queued"
    assert rep["wall"]["count"] == 3
    assert rep["wall"]["next_stage_vocabulary"] == "MISSING"


def test_no_wall_when_the_chain_is_traversable():
    rep = C.chain_report(_population(), FULL_VOCAB)
    assert rep["wall"] is None, "a full vocabulary means work can always move on"


# --------------------------------------------------------------------------
# guards on the guard
# --------------------------------------------------------------------------


def test_stage_order_is_declared_and_non_empty():
    assert C.STAGES and C.STAGES[0] == "unassigned"
    assert "published" in C.STAGES, "the terminal state is a published capability (#584 §4)"


def test_empty_input_does_not_fabricate_a_wall():
    """Zero issues must not read as a healthy chain OR a broken one."""
    rep = C.chain_report([], FULL_VOCAB)
    assert rep["wall"] is None
    assert sum(s["count"] for s in rep["stages"].values()) == 0
