"""Synthetic demotion boundaries for issue #3625; no usage data is read.

Policy sources: scripts/skills/skill-usage-report.py::MIN_COVERAGE_DAYS
and apply_invocation_demotion's one-tier, zero-observation contract.
The oracle below is literal and never calls classification code.
"""

from __future__ import annotations

from copy import deepcopy
import importlib.util
from itertools import permutations
from pathlib import Path

import pytest


REPORT_PATH = (
    Path(__file__).resolve().parents[2] / "scripts/skills/skill-usage-report.py"
)
# Hand-written destinations: one move per original tier, including the terminal tier.
ONE_STEP = {"hot": "warm", "warm": "cold", "cold": "dead", "dead": "dead"}
# Synthetic counts: zero means absent; one is the smallest positive observation.
# Offsets are adjacent whole days around MIN_COVERAGE_DAYS, not new policy limits.
COVERAGE_CASES = [
    pytest.param(-1, False, id="below"),
    pytest.param(0, True, id="at"),
    pytest.param(1, True, id="above"),
]


@pytest.fixture
def report():
    spec = importlib.util.spec_from_file_location("usage_demotion_boundaries", REPORT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _entry(name, tier):
    # References are held at synthetic zero: this function consumes existing tiers.
    return {"skill": name, "tier": tier, "reference_count": 0}


@pytest.mark.parametrize("original_tier", ONE_STEP)
@pytest.mark.parametrize("offset,covered", COVERAGE_CASES)
@pytest.mark.parametrize("observed", [0, 1], ids=["unused", "used"])
@pytest.mark.parametrize("present", [False, True], ids=["missing", "recorded"])
@pytest.mark.parametrize("custom_minimum", [False, True], ids=["default", "override"])
def test_coverage_boundary_uses_one_step_oracle(
    report, original_tier, offset, covered, observed, present, custom_minimum
):
    # The override is one synthetic day above the declared minimum. Its "below"
    # case is the default boundary, so ignoring the override is observable.
    minimum = report.MIN_COVERAGE_DAYS + int(custom_minimum)
    entry = _entry("synthetic-target", original_tier)
    tiers = {tier: [] for tier in ONE_STEP}
    tiers[original_tier].append(entry)
    observation = {"session_count": observed, "coverage_days": minimum + offset}
    invocations = {entry["skill"]: observation} if present else {}
    observations_before = deepcopy(invocations)

    expected_tier = (
        ONE_STEP[original_tier] if present and covered and observed == 0 else original_tier
    )
    changed = expected_tier != original_tier
    expected_entry = {**entry, "tier": expected_tier}
    if changed:
        expected_entry["demoted_by_invocation_signal"] = True
    expected = {tier: [] for tier in ONE_STEP}
    expected[expected_tier].append(expected_entry)

    kwargs = {"min_coverage": minimum} if custom_minimum else {}
    count = report.apply_invocation_demotion(tiers, invocations, **kwargs)

    # One input entry permits exactly one demotion, or zero if unchanged.
    assert count == int(changed)
    assert tiers == expected
    assert invocations == observations_before


@pytest.mark.parametrize("original_tier", ONE_STEP)
@pytest.mark.parametrize("unrelated_record", [False, True], ids=["empty", "unrelated"])
def test_missing_observation_does_not_retire(report, original_tier, unrelated_record):
    tiers = {tier: [] for tier in ONE_STEP}
    tiers[original_tier].append(_entry("synthetic-missing", original_tier))
    before = deepcopy(tiers)
    invocations = (
        {
            "synthetic-unrelated": {
                "session_count": 0,
                "coverage_days": report.MIN_COVERAGE_DAYS,
            }
        }
        if unrelated_record
        else {}
    )
    observations_before = deepcopy(invocations)

    assert report.apply_invocation_demotion(tiers, invocations) == 0
    assert tiers == before
    assert invocations == observations_before


@pytest.mark.parametrize("tier_order", list(permutations(ONE_STEP)))
@pytest.mark.parametrize("reverse_entries", [False, True], ids=["forward", "reverse"])
def test_reordered_tiers_keep_same_classification(report, tier_order, reverse_entries):
    tiers = {tier: [] for tier in tier_order}
    invocations = {}
    expected = {tier: [] for tier in ONE_STEP}
    for original_tier in ONE_STEP:
        for kind in ("unused", "used", "missing"):
            entry = _entry(f"synthetic-{original_tier}-{kind}", original_tier)
            tiers[original_tier].append(entry)
            if kind != "missing":
                invocations[entry["skill"]] = {
                    "session_count": 0 if kind == "unused" else 1,
                    "coverage_days": report.MIN_COVERAGE_DAYS,
                }
            destination = ONE_STEP[original_tier] if kind == "unused" else original_tier
            expected_entry = {**entry, "tier": destination}
            if destination != original_tier:
                expected_entry["demoted_by_invocation_signal"] = True
            expected[destination].append(expected_entry)
    if reverse_entries:
        for entries in tiers.values():
            entries.reverse()
        invocations = dict(reversed(list(invocations.items())))
    observations_before = deepcopy(invocations)

    # Hand count: unused hot, warm and cold move once; unused dead stays dead.
    # Used and missing entries stay put. No moved entry can move a second time.
    assert report.apply_invocation_demotion(tiers, invocations) == 3
    actual_by_tier = {
        tier: sorted(entries, key=lambda entry: entry["skill"])
        for tier, entries in tiers.items()
    }
    expected_by_tier = {
        tier: sorted(entries, key=lambda entry: entry["skill"])
        for tier, entries in expected.items()
    }
    assert actual_by_tier == expected_by_tier
    assert invocations == observations_before
