"""TDD tests for #3251 — skill_link_health matrix verdict (epic #3248).

Targets build_equality_matrix.skill_link_health_verdict: SKILL-LINKS-DRIFTED when any shared-skill
link is repairable (missing/dangling/flattened) on a real ecosystem clone, else SKILL-LINKS-OK;
fail-closed MISSING-EVIDENCE on missing/garbled facts.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "scripts" / "readiness" / "build-equality-matrix.py"

spec = importlib.util.spec_from_file_location("build_equality_matrix", MODULE_PATH)
assert spec is not None and spec.loader is not None
bem = importlib.util.module_from_spec(spec)
sys.modules["build_equality_matrix"] = bem
spec.loader.exec_module(bem)


def _rep(**slh) -> dict:
    base = {"audited_at": "2026-06-27T00:00:00+00:00", "repos_total": 14, "healthy": 42,
            "repairable": 0, "worst_state": "HEALTHY"}
    base.update(slh)
    return {"dimensions": {"skill_link_health": base}}


def test_ok_when_no_repairable():
    assert bem.skill_link_health_verdict(_rep()) == "SKILL-LINKS-OK"


def test_drifted_when_repairable():
    assert bem.skill_link_health_verdict(_rep(repairable=12, worst_state="MISSING")) == "SKILL-LINKS-DRIFTED"


def test_missing_dimension():
    assert bem.skill_link_health_verdict({"dimensions": {}}) == "MISSING-EVIDENCE"


def test_non_dict():
    for bad in ("x", 1, None, ["a"]):
        assert bem.skill_link_health_verdict({"dimensions": {"skill_link_health": bad}}) == "MISSING-EVIDENCE"


def test_missing_audited_at():
    r = _rep()
    del r["dimensions"]["skill_link_health"]["audited_at"]
    assert bem.skill_link_health_verdict(r) == "MISSING-EVIDENCE"


def test_garbled_repairable():
    for bad in (None, "12", True, 1.5):
        assert bem.skill_link_health_verdict(_rep(repairable=bad)) == "MISSING-EVIDENCE"


def test_wiring():
    assert "skill_link_health" in bem.BASE_DISPLAY_DIMS
    assert "skill_link_health" in bem.DISPLAY_DIMS
    assert "SKILL-LINKS-OK" in bem.OK_VERDICTS
    groups = {g[0]: g for g in bem.GROUPS}
    assert groups["skill-links"][2] == ["skill_link_health"]
    sev = bem.ROLLUP_SEVERITY
    assert sev["SKILL-LINKS-DRIFTED"] > sev["SKILL-LINKS-OK"] == 0
