"""Unit tests for scripts/work-queue/infer-category.py — WRK-1015.

Covers all 7 categories, subcategory inference, title-first matching,
word-boundary protection for short keywords, empty-body edge cases,
and the uncategorised fallback.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path


# ---------------------------------------------------------------------------
# Module loader — needed because the filename has a hyphen
# ---------------------------------------------------------------------------

def _load_infer():
    spec = importlib.util.spec_from_file_location(
        "infer_category",
        Path(__file__).resolve().parent.parent.parent
        / "scripts/work-queue/infer-category.py",
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


infer_mod = _load_infer()
infer = infer_mod.infer


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _cat(title: str, body: str = "") -> str:
    return infer(title, body)["category"]


def _sub(title: str, body: str = "") -> str:
    return infer(title, body)["subcategory"]


# ---------------------------------------------------------------------------
# Category: harness
# ---------------------------------------------------------------------------

class TestCategoryHarness:
    def test_work_queue_category_grouping(self):
        result = infer("feat(work-queue): add category grouping", "")
        assert result["category"] == "harness"

    def test_gatepass_fix(self):
        result = infer("fix(gatepass): stage 5 skipped", "")
        assert result["category"] == "harness"

    def test_session_start_briefing(self):
        result = infer("feat(session): session-start briefing", "")
        assert result["category"] == "harness"

    def test_subcategory_work_queue(self):
        assert _sub("feat(work-queue): add category grouping") == "work-queue"

    def test_subcategory_workflow(self):
        assert _sub("fix(gatepass): stage 5 skipped") == "workflow"

    def test_subcategory_session(self):
        # "session-start" keyword → session subcategory
        assert _sub("feat(session): session-start briefing") == "session"

    def test_subcategory_skills(self):
        assert _sub("skill upkeep and curation") == "skills"


# ---------------------------------------------------------------------------
# Category: engineering
# ---------------------------------------------------------------------------

class TestCategoryEngineering:
    def test_orcaflex_pipeline_viv(self):
        result = infer("OrcaFlex pipeline VIV analysis", "")
        assert result["category"] == "engineering"
        assert result["subcategory"] == "pipeline"

    def test_cathodic_protection_dnv(self):
        result = infer("Cathodic protection module DNV RP B401", "")
        assert result["category"] == "engineering"
        assert result["subcategory"] == "cathodic-protection"

    def test_drilling_riser_parametric(self):
        result = infer("Drilling riser parametric analysis", "")
        assert result["category"] == "engineering"
        assert result["subcategory"] == "drilling"

    def test_subcategory_marine(self):
        result = infer("Mooring analysis with hydrodynamics", "")
        assert result["category"] == "engineering"
        assert result["subcategory"] == "marine"

    def test_subcategory_structural(self):
        result = infer("Plate capacity FEA with ANSYS APDL", "")
        assert result["category"] == "engineering"
        assert result["subcategory"] == "structural"

    def test_subcategory_wind(self):
        result = infer("Wind resource AEP assessment using PyWake", "")
        assert result["category"] == "engineering"
        assert result["subcategory"] == "wind"


# ---------------------------------------------------------------------------
# Category: data
# ---------------------------------------------------------------------------

class TestCategoryData:
    def test_bsee_field_economics(self):
        result = infer("BSEE field economics case study", "")
        assert result["category"] == "data"
        assert result["subcategory"] == "production"

    def test_abs_standards_acquisition(self):
        result = infer("ABS standards acquisition", "")
        assert result["category"] == "data"
        assert result["subcategory"] == "standards"

    def test_document_index(self):
        result = infer("Document index phase-e2 remap", "")
        assert result["category"] == "data"
        assert result["subcategory"] == "document-intelligence"

    def test_online_resources(self):
        result = infer("Semantic Scholar MCP server integration", "")
        assert result["category"] == "data"
        assert result["subcategory"] == "online-resources"


# ---------------------------------------------------------------------------
# Category: business
# ---------------------------------------------------------------------------

class TestCategoryBusiness:
    def test_gtm_strategy(self):
        result = infer("ACE-GTM: Go-to-Market strategy", "")
        assert result["category"] == "business"
        assert result["subcategory"] == "gtm"

    def test_stocks_52_week(self):
        result = infer("Stock analysis 52-week high", "")
        assert result["category"] == "business"
        assert result["subcategory"] == "cre-finance"

    def test_net_lease(self):
        result = infer("Net lease Walgreens New Orleans NN", "")
        assert result["category"] == "business"
        assert result["subcategory"] == "cre-finance"

    def test_website(self):
        result = infer("Update aceengineer-website portfolio page", "")
        assert result["category"] == "business"
        assert result["subcategory"] == "website"


# ---------------------------------------------------------------------------
# Category: platform
# ---------------------------------------------------------------------------

class TestCategoryPlatform:
    def test_remote_desktop_workstation(self):
        result = infer("Set up remote desktop on ace-linux-2", "")
        assert result["category"] == "platform"
        assert result["subcategory"] == "workstations"

    def test_claude_install_ai_tools(self):
        # "ace-linux-2" in the title matches the `ace-linux` workstations keyword
        # first (before `claude code` / `codex install` ai-tools keywords), so the
        # subcategory is `workstations` — this documents the rule-ordering behaviour.
        result = infer("fix(ace-linux-2): switch Claude install", "")
        assert result["category"] == "platform"
        assert result["subcategory"] == "workstations"

    def test_ai_tools_readiness(self):
        result = infer("ai-agent-readiness nightly check", "")
        assert result["category"] == "platform"
        assert result["subcategory"] == "ai-tools"

    def test_cron_setup(self):
        result = infer("setup-cron nightly sync coordinator", "")
        assert result["category"] == "platform"
        assert result["subcategory"] == "ci-cron"


# ---------------------------------------------------------------------------
# Category: maintenance
# ---------------------------------------------------------------------------

class TestCategoryMaintenance:
    def test_remove_setup_py(self):
        result = infer("Remove digitalmodel setup.py", "")
        assert result["category"] == "maintenance"
        assert result["subcategory"] == "refactor"

    def test_test_coverage_improvement(self):
        result = infer("digitalmodel test coverage improvement", "")
        assert result["category"] == "maintenance"
        assert result["subcategory"] == "testing"

    def test_cleanup_stale_files(self):
        result = infer("Delete stale egg-info and garbage files", "")
        assert result["category"] == "maintenance"
        assert result["subcategory"] == "cleanup"


# ---------------------------------------------------------------------------
# Category: personal
# ---------------------------------------------------------------------------

class TestCategoryPersonal:
    def test_email_cleanup(self):
        result = infer("Clean up email using AI", "")
        assert result["category"] == "personal"

    def test_heriberto_handyman(self):
        result = infer("Heriberto handyman fence repair", "")
        assert result["category"] == "personal"
        assert result["subcategory"] == "home"

    def test_photo_upload(self):
        result = infer("Photo upload from iPhone to archive", "")
        assert result["category"] == "personal"
        assert result["subcategory"] == "admin"


# ---------------------------------------------------------------------------
# Word-boundary: short keywords must not match as substrings
# ---------------------------------------------------------------------------

class TestWordBoundary:
    def test_feat_does_not_match_fea_keyword(self):
        # "feat" contains "fea" but should NOT trigger the engineering category
        # via the 'fea' keyword — word-boundary guard must block it.
        result = infer("feat(gtm): oil-and-gas persona", "")
        assert result["category"] == "business"

    def test_abs_keyword_not_triggered_by_absolute(self):
        # "absolute" contains "abs" but should not match the 'abs ' data keyword
        result = infer("Absolute path cleanup refactor", "")
        # Should land on maintenance (refactor), not data
        assert result["category"] == "maintenance"

    def test_fea_as_standalone_word_matches_engineering(self):
        # When "fea" appears as its own word it should still match
        result = infer("FEA buckling analysis plate", "")
        assert result["category"] == "engineering"


# ---------------------------------------------------------------------------
# Title-first: title overrides body
# ---------------------------------------------------------------------------

class TestTitleFirst:
    def test_title_wins_over_body_engineering_keywords(self):
        # Body is full of engineering keywords but title says GTM → business
        result = infer(
            "ACE-GTM strategy",
            "pipeline orcaflex mooring subsea viv free span cathodic protection",
        )
        assert result["category"] == "business"

    def test_body_fallback_when_title_blank(self):
        # Title gives no signal; body has engineering keyword
        result = infer("Evaluate new approach", "orcaflex free span analysis mooring")
        assert result["category"] == "engineering"

    def test_body_fallback_subcategory(self):
        # Title is neutral; body triggers subcategory via body fallback
        result = infer("New WRK item", "cathodic protection cp module anode review")
        assert result["category"] == "engineering"
        assert result["subcategory"] == "cathodic-protection"


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

class TestEdgeCases:
    def test_uncategorised_fallback(self):
        result = infer("Random unrecognised work item", "")
        assert result["category"] == "uncategorised"

    def test_empty_body_does_not_crash(self):
        result = infer("OrcaFlex pipeline analysis", "")
        assert isinstance(result, dict)
        assert "category" in result
        assert "subcategory" in result

    def test_both_empty_returns_uncategorised(self):
        result = infer("", "")
        assert result["category"] == "uncategorised"

    def test_scan_existing_does_not_crash(self):
        # scan_existing() should run without exception even if queue dirs have no files
        existing = infer_mod.scan_existing()
        assert isinstance(existing, dict)

    def test_returns_dict_with_required_keys(self):
        result = infer("Some title", "some body")
        assert set(result.keys()) == {"category", "subcategory"}
