"""TDD tests for #3249 — the skill_currency matrix line item (epic #3248).

Targets build_equality_matrix.skill_currency_verdict (the verdict state machine) in isolation,
plus structural wiring, mirroring test_session_curation_freshness.py. The heavy audit (git-tree
family diff, allowlist, index dangling-check) lives in scripts/curation/audit_skill_currency.py and
emits FACTS into the dimension; the matrix maps facts→verdict, so the verdict is unit-testable here.
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


def _rep(**sc) -> dict:
    """A report carrying a skill_currency dimension built from the given fields."""
    base = {"audited_at": "2026-06-26T12:00:00+00:00", "canonical_count": 44,
            "gemini_present": True, "gemini_unexpected": 0, "gemini_expected": 0,
            "codex_present": True, "hermes_present": True, "index_dangling": 0}
    base.update(sc)
    return {"dimensions": {"skill_currency": base}}


# ── verdict precedence: DRIFTED > INDEX-STALE > EXPECTED-DIVERGENCE > CURRENT ──
def test_current_when_clean():
    assert bem.skill_currency_verdict(_rep()) == "SKILLS-CURRENT"


def test_drifted_on_unexpected():
    assert bem.skill_currency_verdict(_rep(gemini_unexpected=2)) == "SKILLS-DRIFTED"


def test_drifted_dominates_index_stale_and_expected():
    # unexpected drift is the highest-severity signal — it wins even with index stale + expected extras
    assert bem.skill_currency_verdict(
        _rep(gemini_unexpected=1, index_dangling=5, gemini_expected=9)) == "SKILLS-DRIFTED"


def test_index_stale_when_no_unexpected():
    assert bem.skill_currency_verdict(_rep(index_dangling=5)) == "SKILLS-INDEX-STALE"


def test_index_stale_dominates_expected_divergence():
    assert bem.skill_currency_verdict(
        _rep(index_dangling=5, gemini_expected=9)) == "SKILLS-INDEX-STALE"


def test_unreadable_index_not_green():
    # index unreadable (null) while the tree read fine ⇒ INDEX-STALE, never silently green
    assert bem.skill_currency_verdict(_rep(index_dangling=None)) == "SKILLS-INDEX-STALE"


def test_expected_divergence_when_only_allowlisted_extras():
    assert bem.skill_currency_verdict(_rep(gemini_expected=9)) == "EXPECTED-DIVERGENCE"


def test_unexpected_ignored_when_gemini_absent():
    # a stale gemini_unexpected count must not red the cell when the gemini surface isn't present
    assert bem.skill_currency_verdict(
        _rep(gemini_present=False, gemini_unexpected=5)) == "SKILLS-CURRENT"


# ── fail-closed: missing / garbled evidence ──
def test_missing_dimension():
    assert bem.skill_currency_verdict({"dimensions": {}}) == "MISSING-EVIDENCE"


def test_non_dict_dimension():
    for bad in ("x", 1, ["a"], None):
        assert bem.skill_currency_verdict({"dimensions": {"skill_currency": bad}}) == "MISSING-EVIDENCE"


def test_missing_audited_at():
    r = _rep()
    del r["dimensions"]["skill_currency"]["audited_at"]
    assert bem.skill_currency_verdict(r) == "MISSING-EVIDENCE"


def test_unreadable_canonical_count():
    # canonical_count absent / None / 0 ⇒ the tree couldn't be read ⇒ no evidence (fail-closed)
    for bad in (None, 0, "44", -1):
        assert bem.skill_currency_verdict(_rep(canonical_count=bad)) == "MISSING-EVIDENCE"


def test_garbled_unexpected_with_gemini_present():
    assert bem.skill_currency_verdict(_rep(gemini_unexpected="two")) == "MISSING-EVIDENCE"


# ── structural wiring ──
def test_dimension_registered():
    assert "skill_currency" in bem.BASE_DISPLAY_DIMS
    assert "skill_currency" in bem.DISPLAY_DIMS


def test_current_is_ok_verdict():
    assert "SKILLS-CURRENT" in bem.OK_VERDICTS
    # EXPECTED-DIVERGENCE already an OK/expected verdict in the engine
    assert "EXPECTED-DIVERGENCE" in bem.OK_VERDICTS


def test_group_present():
    groups = {g[0]: g for g in bem.GROUPS}
    assert "skills-currency" in groups
    assert groups["skills-currency"][2] == ["skill_currency"]


def test_severity_ordering():
    sev = bem.ROLLUP_SEVERITY
    assert sev["SKILLS-DRIFTED"] > sev["SKILLS-INDEX-STALE"] > sev["SKILLS-CURRENT"]
    assert sev["SKILLS-CURRENT"] == 0


def test_verdict_routes_through_verdict_for():
    # a fresh (non-stale) report graded via the public orchestrator returns the freshness-family verdict
    from datetime import datetime  # noqa: F401  (ensure module import side-effects ok)
    rep = _rep()
    rep.update({"machine": "dev-primary", "os": "linux", "status": "active",
                "provenance": {"checkout_sha": "abc", "dirty": False, "behind_main": 0,
                               "ahead_main": 0, "origin_ref_age_h": 1}})
    roster = {"dev-primary": {"status": "active"}}
    v = bem.verdict_for("skill_currency", "dev-primary", {"dev-primary": rep}, {}, roster, [])
    assert v == "SKILLS-CURRENT"


# ── #3256 audit refactor regression: module-level _allowed parity + audit() unchanged ──
import importlib.util as _ilu  # noqa: E402

_ASC_PATH = REPO_ROOT / "scripts" / "curation" / "audit_skill_currency.py"
_aspec = _ilu.spec_from_file_location("audit_skill_currency", _ASC_PATH)
assert _aspec is not None and _aspec.loader is not None
asc = _ilu.module_from_spec(_aspec)
sys.modules["audit_skill_currency"] = asc
_aspec.loader.exec_module(asc)


def test_allowed_module_level_prefix_vs_exact():
    # entry ending in '-' is a PREFIX; everything else is EXACT (no substring over-match)
    assert asc._allowed("source-command-a", ["source-command-"]) is True
    assert asc._allowed("memory", ["memory"]) is True
    assert asc._allowed("memory-bank", ["memory"]) is False          # exact, not substring
    assert asc._allowed("anything", []) is False


def test_audit_output_unchanged_after_refactor():
    # audit() must still return the same schema_version and key set after extracting _allowed.
    out = asc.audit("dev-primary")
    assert out["schema_version"] == 2
    expected_keys = {
        "machine", "audited_at", "canonical_count", "gemini_present", "gemini_unexpected",
        "gemini_unexpected_families", "gemini_expected", "codex_present", "hermes_present",
        "index_dangling", "index_stale", "schema_version",
    }
    assert set(out.keys()) == expected_keys
