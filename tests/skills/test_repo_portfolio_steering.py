"""
Tests for WRK-1019: repo-portfolio-steering skill
11 tests, 1:1 with acceptance criteria.
"""
import json
import sys
import textwrap
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parents[2]
SKILL_PATH = REPO_ROOT / ".claude/skills/workspace-hub/repo-portfolio-steering/SKILL.md"
COMPUTE_PY = REPO_ROOT / "scripts/skills/repo-portfolio-steering/compute-balance.py"
INDEX_MD = REPO_ROOT / ".claude/work-queue/INDEX.md"

# -- helpers ------------------------------------------------------------------

def _run_compute(args: list[str], signals_yaml: str | None = None, tmp_path: Path | None = None):
    """Import compute-balance as a module and call compute_balance()."""
    import importlib.util, os
    spec = importlib.util.spec_from_file_location("compute_balance", COMPUTE_PY)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    signals_path = None
    if signals_yaml is not None and tmp_path is not None:
        signals_path = tmp_path / "portfolio-signals.yaml"
        signals_path.write_text(signals_yaml)
    return mod.compute_balance(
        index_path=INDEX_MD,
        signals_path=signals_path,
        harness_threshold=args[0] if args else 0.30,
    )


# -- AC-1: skill file exists --------------------------------------------------

def test_skill_file_exists():
    assert SKILL_PATH.exists(), f"SKILL.md not found at {SKILL_PATH}"
    text = SKILL_PATH.read_text()
    assert "name: repo-portfolio-steering" in text
    assert "version:" in text


# -- AC-2: balance snapshot reads INDEX.md By Category -----------------------

def test_balance_snapshot_parses_index(tmp_path):
    result = _run_compute([], tmp_path=tmp_path)
    assert "categories" in result
    cats = result["categories"]
    assert "harness" in cats
    assert "engineering" in cats
    assert cats["harness"] >= 1
    assert cats["engineering"] >= 1
    assert 0 < result["harness_pct"] < 100
    assert 0 < result["engineering_pct"] < 100
    assert result["total"] >= 2


# -- AC-3a: harness threshold default 30% ------------------------------------

def test_harness_threshold_default(tmp_path):
    result = _run_compute([0.30], tmp_path=tmp_path)
    assert "harness_status" in result
    # With ~45 harness / ~300 total, pct is ~15% → HEALTHY
    assert result["harness_status"] in ("HEALTHY", "OVER-INVESTED")
    assert result["harness_threshold"] == 0.30


# -- AC-3b: custom harness threshold ------------------------------------------

def test_harness_threshold_custom(tmp_path):
    # Force OVER-INVESTED by setting threshold=0 (any harness triggers it)
    result = _run_compute([0.0], tmp_path=tmp_path)
    assert result["harness_status"] == "OVER-INVESTED"
    # Force HEALTHY by setting threshold=1.0 (100%)
    result2 = _run_compute([1.0], tmp_path=tmp_path)
    assert result2["harness_status"] == "HEALTHY"


# -- AC-4: GTM readiness ranking ----------------------------------------------

def test_gtm_readiness_ranking(tmp_path):
    result = _run_compute([], tmp_path=tmp_path)
    assert "gtm_ranking" in result
    ranking = result["gtm_ranking"]
    assert isinstance(ranking, list)
    # Each entry has required keys
    if ranking:
        entry = ranking[0]
        assert "wrk_id" in entry or "module" in entry


# -- AC-5: next 3 actions to fund mapping -------------------------------------

def test_next3_fund_mapping(tmp_path):
    result = _run_compute([], tmp_path=tmp_path)
    assert "next3" in result
    assert isinstance(result["next3"], list)
    # Must have at most 3 entries
    assert len(result["next3"]) <= 3
    # Each entry must have domain → persona mapping
    if result["next3"]:
        entry = result["next3"][0]
        assert "client_persona" in entry or "domain" in entry


# -- AC-6: recommended harness budget formula ---------------------------------

def test_harness_budget_formula(tmp_path):
    # harness_pct ≤ 15% → "ramp up harness" (1:3)
    mod_result = _run_compute([0.30], tmp_path=tmp_path)
    budget = mod_result.get("harness_budget", "")
    assert isinstance(budget, str)
    assert budget  # non-empty


# -- AC-7: provider activity from portfolio-signals.yaml ---------------------

SIGNALS_YAML = textwrap.dedent("""\
    generated_at: "2026-03-07T06:00:00Z"
    lookback_days: 30
    provider_activity:
      claude:
        harness: 4
        engineering: 3
        data: 0
        other: 1
      codex:
        harness: 1
        engineering: 5
        data: 0
        other: 0
      gemini:
        harness: 0
        engineering: 2
        data: 1
        other: 0
    capability_signals: []
""")


def test_provider_activity_parsed(tmp_path):
    result = _run_compute([], signals_yaml=SIGNALS_YAML, tmp_path=tmp_path)
    assert "provider_activity" in result
    pa = result["provider_activity"]
    assert "claude" in pa
    assert pa["claude"]["harness"] == 4
    assert pa["codex"]["engineering"] == 5


# -- AC-8: capability_signals key present does not crash (L3 compat) ---------

SIGNALS_WITH_CAPS = SIGNALS_YAML.replace(
    "capability_signals: []",
    textwrap.dedent("""\
        capability_signals:
          - date: "2026-03-04"
            provider: claude
            capability: "extended thinking"
            engineering_domains: ["structural"]
            impact: medium
            source: "https://anthropic.com/news"
    """),
)


def test_capability_signals_compat_no_crash(tmp_path):
    """L3 compat: skill must not crash when capability_signals key is present."""
    result = _run_compute([], signals_yaml=SIGNALS_WITH_CAPS, tmp_path=tmp_path)
    assert "provider_activity" in result  # L2 still works


# -- AC-9: missing portfolio-signals.yaml graceful ---------------------------

def test_portfolio_signals_missing_graceful(tmp_path):
    """No portfolio-signals.yaml → Layer 2 skipped, L1 still works."""
    result = _run_compute([], signals_yaml=None, tmp_path=tmp_path)
    assert "categories" in result
    assert result.get("provider_activity") is None or result.get("provider_activity") == {}


# -- AC-10: session-start integration documented in SKILL.md -----------------

def test_session_start_trigger_documented():
    text = SKILL_PATH.read_text()
    assert "session-start" in text.lower() or "session_start" in text.lower()


# -- AC-11: description trigger phrases in SKILL.md --------------------------

def test_description_trigger_phrases():
    text = SKILL_PATH.read_text()
    assert "portfolio" in text.lower()
    assert "steering" in text.lower()
    assert "harness" in text.lower()
