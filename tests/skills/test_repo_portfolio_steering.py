"""
Tests for the repo-portfolio-steering category-table contract.
"""
import json
import sys
import textwrap
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parents[2]
SKILL_PATH = REPO_ROOT / ".claude/skills/workspace-hub/repo-portfolio-steering/SKILL.md"
COMPUTE_PY = REPO_ROOT / "scripts/skills/repo-portfolio-steering/compute-balance.py"

# Synthetic arithmetic example from issue #2420: one harness item and three
# engineering items give total 4, harness fraction 1/4 = 0.25 and engineering
# fraction 3/4 = 0.75. Expected results are hand-calculated, not read from code.
CATEGORY_TABLE = textwrap.dedent("""\
    ## By Category
    | Category | Count |
    |----------|-------|
    | harness | 1 |
    | engineering | 3 |
""")

# -- helpers ------------------------------------------------------------------

def _load_compute():
    """Import the reader without invoking its CLI."""
    import importlib.util

    spec = importlib.util.spec_from_file_location("compute_balance", COMPUTE_PY)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _run_compute(
    args: list[float],
    tmp_path: Path,
    signals_yaml: str | None = None,
    index_text: str = CATEGORY_TABLE,
):
    """Use a temporary index compatible with --index, never the live queue."""
    mod = _load_compute()
    index_path = tmp_path / "INDEX.md"
    index_path.write_text(index_text, encoding="utf-8")
    signals_path = None
    if signals_yaml is not None:
        signals_path = tmp_path / "portfolio-signals.yaml"
        signals_path.write_text(signals_yaml)
    return mod.compute_balance(
        index_path=index_path,
        signals_path=signals_path,
        # Default threshold from the existing CLI contract (30 percent).
        harness_threshold=args[0] if args else 0.30,
    )


# -- AC-1: skill file exists --------------------------------------------------

def test_skill_file_exists():
    assert SKILL_PATH.exists(), f"SKILL.md not found at {SKILL_PATH}"
    text = SKILL_PATH.read_text()
    assert "name: repo-portfolio-steering" in text
    assert "version:" in text


# -- AC-2: balance snapshot reads INDEX.md By Category -----------------------

def test_balance_explicit_category_fixture(tmp_path):
    result = _run_compute([], tmp_path=tmp_path)
    assert result["categories"] == {"harness": 1, "engineering": 3}
    assert result["total"] == 4
    assert result["harness_pct"] == 0.25
    assert result["engineering_pct"] == 0.75
    # Budget basis: SKILL_PATH, Section 5, Recommended Harness Budget.
    assert result["harness_budget"] == "1 harness per 5 engineering (maintain)"


@pytest.mark.parametrize("heading", ["## By Category", "### By Category"])
def test_parse_category_counts_independently(tmp_path, heading):
    index_path = tmp_path / "INDEX.md"
    # The repeated synthetic rows outside the section must not affect parsing.
    index_path.write_text(
        "| outside | 1 |\n"
        + CATEGORY_TABLE.replace("## By Category", heading)
        + "## Other summary\n| outside | 3 |\n",
        encoding="utf-8",
    )
    assert _load_compute()._parse_category_counts(index_path) == {
        "harness": 1,
        "engineering": 3,
    }


def _assert_unavailable(result):
    assert result["categories"] == {}
    assert result["total"] is None
    assert result["harness_pct"] is None
    assert result["engineering_pct"] is None
    assert result["harness_status"] == "UNAVAILABLE"
    assert result["harness_budget"] is None


def test_balance_missing_category_table_is_unavailable(tmp_path):
    # Unsupported legacy headings are not a category-count source.
    legacy_index = "# Legacy index\n## Pending\n## Working\n## Done\n"
    _assert_unavailable(_run_compute([], tmp_path, index_text=legacy_index))


def test_balance_empty_input_is_unavailable(tmp_path):
    _assert_unavailable(_run_compute([], tmp_path, index_text=""))


@pytest.mark.parametrize("rows", ["", "| harness | unknown |\n| engineering | unknown |\n"])
def test_balance_table_without_counts_is_unavailable(tmp_path, rows):
    _assert_unavailable(_run_compute(
        [], tmp_path, index_text="## By Category\n| Category | Count |\n" + rows,
    ))


def test_balance_explicit_zero_counts(tmp_path):
    # Explicit zero counts give total 0 and the existing zero-fraction convention.
    result = _run_compute([], tmp_path, index_text=(
        "## By Category\n| harness | 0 |\n| engineering | 0 |\n"
    ))
    assert result["categories"] == {"harness": 0, "engineering": 0}
    assert result["total"] == 0
    assert result["harness_pct"] == 0.0
    assert result["engineering_pct"] == 0.0
    assert result["harness_status"] == "HEALTHY"
    # Budget basis: SKILL_PATH, Section 5, Recommended Harness Budget.
    assert result["harness_budget"] == "1 harness per 3 engineering (ramp up harness)"


# -- AC-3a: harness threshold default 30% ------------------------------------

def test_harness_threshold_default(tmp_path):
    result = _run_compute([0.30], tmp_path=tmp_path)
    # Synthetic 0.25 fraction is below the documented default 0.30 threshold.
    assert result["harness_status"] == "HEALTHY"
    assert result["harness_threshold"] == 0.30


# -- AC-3b: custom harness threshold ------------------------------------------

# Synthetic boundary 0.25 from issue #2420, with thresholds 0.05 below/above.
@pytest.mark.parametrize("threshold, expected", [
    (0.20, "OVER-INVESTED"),
    (0.25, "HEALTHY"),
    (0.30, "HEALTHY"),
])
def test_harness_threshold_boundary(tmp_path, monkeypatch, threshold, expected):
    mod = _load_compute()
    # Supply literal counts directly so this test cannot fail due to parsing.
    monkeypatch.setattr(mod, "_parse_category_counts", lambda _: {
        "harness": 1, "engineering": 3,
    })
    result = mod.compute_balance(tmp_path / "INDEX.md", harness_threshold=threshold)
    assert result["harness_pct"] == 0.25
    assert result["harness_threshold"] == threshold
    assert result["harness_status"] == expected


@pytest.mark.parametrize("index_text", [CATEGORY_TABLE, ""])
def test_cli_explicit_index(tmp_path, monkeypatch, capsys, index_text):
    index_path = tmp_path / "INDEX.md"
    index_path.write_text(index_text, encoding="utf-8")
    # Threshold 0.20 is below the synthetic quarter, so the CLI must override
    # its default and report OVER-INVESTED when counts are available.
    monkeypatch.setattr(sys, "argv", [
        str(COMPUTE_PY), "--index", str(index_path), "--threshold", "0.20",
    ])
    _load_compute().main()
    result = json.loads(capsys.readouterr().out)
    assert result["harness_threshold"] == 0.20
    if index_text:
        assert result["categories"] == {"harness": 1, "engineering": 3}
        assert result["total"] == 4
        assert result["harness_pct"] == 0.25
        assert result["harness_status"] == "OVER-INVESTED"
    else:
        _assert_unavailable(result)


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
