#!/usr/bin/env python3
"""Tests for scripts/kanban/domain_coverage.py — the #2962 invariant guard.

The planning core (`analyze`) is pure and fully covered here; the gh shell is
tested with a fake runner. Hermetic — no live gh.

Run: uv run --with pyyaml pytest tests/test_domain_coverage.py
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
GUARD_PY = REPO_ROOT / "scripts" / "kanban" / "domain_coverage.py"


def _import():
    spec = importlib.util.spec_from_file_location("domain_coverage", GUARD_PY)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


dc = _import()


def _issue(n, *labels, title="t"):
    return {"number": n, "title": title, "labels": [{"name": x} for x in labels]}


def test_zero_label_flagged():
    r = dc.analyze([_issue(1, "bug")], canonical={"x"}, aliases=set())
    assert [i["number"] for i in r["zero"]] == [1]
    assert r["multi"] == [] and r["unknown"] == [] and r["alias"] == []


def test_multi_domain_flagged():
    r = dc.analyze([_issue(2, "domain:a", "domain:b")], canonical={"a", "b"}, aliases=set())
    assert [i["number"] for i in r["multi"]] == [2]


def test_unknown_domain_flagged_on_first_label():
    r = dc.analyze([_issue(3, "domain:ghost")], canonical={"a"}, aliases=set())
    assert r["unknown"] and r["unknown"][0]["label"] == "ghost"


def test_alias_flagged_not_unknown():
    # an alias is a KNOWN synonym pending rename — must land in alias, never unknown
    r = dc.analyze([_issue(4, "domain:hydro")], canonical={"hydrodynamics"}, aliases={"hydro"})
    assert r["alias"] and r["alias"][0]["label"] == "hydro"
    assert r["unknown"] == []


def test_exactly_one_known_domain_is_clean():
    r = dc.analyze([_issue(5, "domain:a")], canonical={"a"}, aliases=set())
    assert not any(r[k] for k in ("zero", "multi", "unknown", "alias"))


def test_taxonomy_absent_skips_drift_checks():
    # canonical/aliases None => only zero/multi enforced; unknown domain is NOT flagged
    r = dc.analyze([_issue(6, "domain:whatever")], canonical=None, aliases=None)
    assert r["unknown"] == [] and r["alias"] == []
    assert r["taxonomy_checked"] is False


def test_multi_and_unknown_compound():
    # first label unknown AND more than one domain => both flags fire
    r = dc.analyze([_issue(7, "domain:ghost", "domain:a")], canonical={"a"}, aliases=set())
    assert [i["number"] for i in r["multi"]] == [7]
    assert r["unknown"] and r["unknown"][0]["label"] == "ghost"


def test_gh_runner_parses_json():
    calls = []

    def fake(args):
        calls.append(args)
        return '[{"number": 9, "title": "z", "labels": [{"name": "domain:a"}]}]'

    issues = dc._gh("o/r", fake)
    assert issues[0]["number"] == 9
    assert calls[0][:3] == ["gh", "issue", "list"]


def test_gh_runner_handles_empty():
    assert dc._gh("o/r", lambda a: "") == []


def test_render_clean_report_has_check():
    report = {"any_taxonomy": True, "repos": {
        "o/r": dc.analyze([_issue(1, "domain:a")], {"a"}, set())}}
    md, total = dc.render(report)
    assert total == 0 and "✅" in md
