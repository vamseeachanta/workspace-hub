#!/usr/bin/env python3
"""TDD tests for `route.py --coverage` — assignment coverage reporting (deckhand#584).

Context: 1,760 open issues across three repos, of which 314 lack `machine:` and
181 lack `lane:`. An unassigned issue is not *blocked* — it is silently
not-in-flight, indistinguishable from work deliberately left unscheduled.

The reporter is READ-ONLY. It is the first step of #584 precisely because the
routing engine's capability map is known-wrong (#579 claims a solver licence a
host cannot obtain), so nothing may write a label until the picture is trusted.

Four buckets, not two. "Has a label" is not "is routable":

    missing    — no label on the axis
    ambiguous  — MULTIPLE labels on one axis; route.py resolves by FIRST label
                 (existing_label_value, route.py:68), so behaviour depends on
                 API label order. Presents as healthy; is not.
    terminal   — deliberately not scheduled; a valid end state, not a finding
    routable   — exactly one label, and it resolves

Hermetic: pure functions, explicit args, no gh and no network.

Run: uv run --with pyyaml pytest tests/dispatch/test_route_coverage.py
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

TERMINAL = ["machine:unassigned", "status:icebox"]
SKIP = ["wip", "blocked", "status:plan-review"]


# --------------------------------------------------------------------------
# the four buckets
# --------------------------------------------------------------------------


def test_no_label_on_axis_is_missing():
    assert R.classify_axis([], "machine:", terminal=TERMINAL, skip=SKIP) == "missing"
    assert R.classify_axis(["lane:claude"], "machine:", terminal=TERMINAL, skip=SKIP) == "missing"


def test_exactly_one_label_is_routable():
    assert (
        R.classify_axis(["machine:ace-linux-1"], "machine:", terminal=TERMINAL, skip=SKIP)
        == "routable"
    )


def test_multiple_labels_on_one_axis_is_ambiguous_not_routable():
    """The trap this bucket exists for.

    `existing_label_value()` returns the FIRST matching label, so an issue with
    two `lane:` labels routes by whatever order the API happens to return. A
    reporter that only asks "is a label present" calls this assigned — arguably
    a worse state than missing, because it looks healthy.
    """
    labels = ["lane:claude", "lane:codex"]
    assert R.classify_axis(labels, "lane:", terminal=TERMINAL, skip=SKIP) == "ambiguous"


def test_terminal_marker_is_not_a_finding():
    """Deliberately unscheduled is a valid end state, distinct from unnoticed."""
    assert R.classify_axis(["machine:unassigned"], "machine:", terminal=TERMINAL, skip=SKIP) == "terminal"
    assert R.classify_axis(["status:icebox"], "machine:", terminal=TERMINAL, skip=SKIP) == "terminal"


def test_terminal_wins_over_missing():
    """`status:icebox` with no machine label is terminal, not a gap."""
    assert (
        R.classify_axis(["status:icebox", "lane:claude"], "machine:", terminal=TERMINAL, skip=SKIP)
        == "terminal"
    )


def test_skip_labeled_work_is_classified_not_counted_as_a_gap():
    """An issue in plan-review is in flight, not an assignment failure.

    `skip_if_labeled: [wip, blocked, status:plan-review]` already exists in
    routing-rules.yaml; mixing those with actionable gaps inflates the number
    and buries the real ones.
    """
    assert R.classify_axis(["status:plan-review"], "machine:", terminal=TERMINAL, skip=SKIP) == "skipped"
    assert R.classify_axis(["wip"], "lane:", terminal=TERMINAL, skip=SKIP) == "skipped"


# --------------------------------------------------------------------------
# the model: inversion — absence is MEANINGFUL here
# --------------------------------------------------------------------------


def test_missing_model_label_is_never_a_gap():
    """#584 decision 1: no `model:` means "executor chooses".

    This INVERTS the rule used for machine: and lane:, where absence is the gap.
    Two axes with opposite semantics for "unlabelled" on the same issue is
    exactly what gets coded wrong once and then mislabels hundreds of issues.
    """
    report = R.coverage_report(
        [{"number": 1, "labels": ["machine:ace-linux-1", "lane:claude"]}],
        axes=("machine:", "lane:"),
        terminal=TERMINAL,
        skip=SKIP,
    )
    assert "model:" not in report["axes"]
    assert report["axes"]["machine:"]["missing"] == 0
    assert report["axes"]["lane:"]["missing"] == 0


def test_model_label_present_is_not_counted_either_way():
    report = R.coverage_report(
        [{"number": 1, "labels": ["machine:ace-linux-1", "lane:claude", "model:opus"]}],
        axes=("machine:", "lane:"),
        terminal=TERMINAL,
        skip=SKIP,
    )
    assert report["axes"]["machine:"]["routable"] == 1
    assert "model:" not in report["axes"]


# --------------------------------------------------------------------------
# aggregate report shape
# --------------------------------------------------------------------------


def _issues():
    return [
        {"number": 1, "labels": ["machine:ace-linux-1", "lane:claude"]},      # routable/routable
        {"number": 2, "labels": ["lane:claude"]},                             # machine missing
        {"number": 3, "labels": []},                                          # both missing
        {"number": 4, "labels": ["machine:ace-linux-1", "lane:claude", "lane:codex"]},  # lane ambiguous
        {"number": 5, "labels": ["status:icebox"]},                           # terminal
        {"number": 6, "labels": ["machine:ace-linux-1", "status:plan-review"]},  # skipped
    ]


def test_report_counts_every_issue_exactly_once_per_axis():
    """A bucket total that does not sum to the population is silently lossy."""
    report = R.coverage_report(_issues(), axes=("machine:", "lane:"), terminal=TERMINAL, skip=SKIP)
    for axis, counts in report["axes"].items():
        total = sum(counts[b] for b in ("missing", "ambiguous", "terminal", "skipped", "routable"))
        assert total == len(_issues()), f"{axis} buckets sum to {total}, expected {len(_issues())}"


def test_report_identifies_issues_missing_both_axes():
    """The 161 workspace-hub issues with neither are the sharpest finding."""
    report = R.coverage_report(_issues(), axes=("machine:", "lane:"), terminal=TERMINAL, skip=SKIP)
    assert report["missing_all_axes"] == [3]


def test_report_lists_issue_numbers_not_just_counts():
    """A count is not actionable; the owner needs the list to review."""
    report = R.coverage_report(_issues(), axes=("machine:", "lane:"), terminal=TERMINAL, skip=SKIP)
    assert 2 in report["axes"]["machine:"]["missing_issues"]
    assert 4 in report["axes"]["lane:"]["ambiguous_issues"]


# --------------------------------------------------------------------------
# read-only guarantee
# --------------------------------------------------------------------------


def test_coverage_never_reaches_a_write_path():
    """--coverage must be incapable of mutating a label, not merely abstain.

    route.py's `--apply` reaches a live `gh issue edit --add-label`; a reporter
    that shares that module must be provably unable to get there.
    """
    import inspect

    src = inspect.getsource(R.coverage_report) + inspect.getsource(R.classify_axis)
    for forbidden in ("--add-label", "--remove-label", "issue edit", "gh("):
        assert forbidden not in src, f"coverage path can reach a write: {forbidden!r}"


def test_classify_axis_is_pure():
    """No hidden mutation of the caller's list."""
    labels = ["lane:claude", "lane:codex"]
    before = list(labels)
    R.classify_axis(labels, "lane:", terminal=TERMINAL, skip=SKIP)
    assert labels == before
