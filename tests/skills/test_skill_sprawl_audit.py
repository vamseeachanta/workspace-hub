"""Tests for the non-destructive skill sprawl audit (#3062, epic #3058)."""
import importlib.util
import os

_SPEC = importlib.util.spec_from_file_location(
    "skill_sprawl_audit",
    os.path.join(os.path.dirname(__file__), "..", "..", "scripts", "skills", "skill_sprawl_audit.py"),
)
ssa = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(ssa)


def _s(usage, calls, framework=False, children=0, tier="dead"):
    return {"baseline_usage_rate": usage, "calls_in_period": calls,
            "framework_usage": framework, "child_skill_count": children,
            "tier": tier, "path": "x/y"}


def test_dead_skill_is_candidate():
    skills = {"dead1": _s(0.0, 0)}
    c = ssa.select_candidates(skills)
    assert len(c) == 1 and c[0]["name"] == "dead1"


def test_hot_skill_not_candidate():
    skills = {"hot1": _s(0.5, 40, tier="hot")}
    assert ssa.select_candidates(skills) == []


def test_framework_skill_exempt():
    skills = {"fw": _s(0.0, 0, framework=True)}
    assert ssa.select_candidates(skills) == []


def test_parent_skill_exempt():
    skills = {"parent": _s(0.0, 0, children=3)}
    assert ssa.select_candidates(skills) == []


def test_threshold_boundary():
    # usage exactly at max (0.05) is NOT < 0.05 -> not a candidate
    skills = {"edge": _s(0.05, 0)}
    assert ssa.select_candidates(skills, max_usage=0.05) == []
    # just under -> candidate
    skills2 = {"edge2": _s(0.049, 0)}
    assert len(ssa.select_candidates(skills2, max_usage=0.05)) == 1


def test_calls_threshold_blocks_low_usage_but_active():
    # low usage but many calls -> not a candidate (still exercised)
    skills = {"busy": _s(0.04, 25)}
    assert ssa.select_candidates(skills, max_calls=10) == []


def test_tier_summary_counts():
    skills = {"a": _s(0, 0, tier="dead"), "b": _s(0.5, 9, tier="hot"), "c": _s(0.1, 3, tier="warm")}
    assert ssa.tier_summary(skills) == {"dead": 1, "hot": 1, "warm": 1}


def test_candidates_sorted_by_usage_then_calls():
    skills = {"a": _s(0.04, 5), "b": _s(0.0, 0), "c": _s(0.01, 2)}
    c = ssa.select_candidates(skills)
    assert [x["name"] for x in c] == ["b", "c", "a"]
