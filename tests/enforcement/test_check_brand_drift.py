"""Tests for the brand-token drift guard (workspace-hub#3402).

Verifies: hex normalisation, :root parsing, the declare-brand-then-must-match rule
(with non-brand pages exempt), and that the real docs/reports tree is consistent.
"""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GUARD = ROOT / "scripts" / "enforcement" / "check-brand-token-drift.py"


def _load():
    spec = importlib.util.spec_from_file_location("brand_drift_guard", GUARD)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


G = _load()
CANON = {"fg": "#1a2230", "brand": "#5b3fd6", "card": "#ffffff"}


def test_norm_expands_and_lowercases():
    assert G.norm("#FFF") == "#ffffff"
    assert G.norm("#5b3FD6") == "#5b3fd6"


def test_root_tokens_parses_first_root():
    toks = G.root_tokens(":root{--fg:#1a2230;--brand:#5b3fd6;--card:#fff}")
    assert toks == {"fg": "#1a2230", "brand": "#5b3fd6", "card": "#ffffff"}


def test_matching_brand_page_has_no_violation():
    pages = {"ok.html": {"brand": "#5b3fd6", "fg": "#1a2230", "ok": "#1f9d55"}}
    assert G.find_violations(CANON, pages) == []


def test_drifted_brand_page_is_flagged():
    pages = {"bad.html": {"brand": "#7000ff", "fg": "#1a2230"}}
    v = G.find_violations(CANON, pages)
    assert v and v[0][0] == "bad.html" and v[0][1] == "brand"


def test_non_brand_page_is_exempt():
    # a dark scorecard with its own scheme and NO --brand is not checked
    pages = {"dark.html": {"bg": "#0f1117", "fg": "#e6edf3"}}
    assert G.find_violations(CANON, pages) == []


def test_real_reports_tree_is_consistent():
    assert G.main() == 0
