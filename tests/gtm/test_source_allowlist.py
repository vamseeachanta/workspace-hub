"""Q9 allowlist composition + dead-source scraper removal for the GTM scanner.

ABOUTME: Covers #1707 (#2348 plan v3) — asserts the post-Q9 source allowlist
contains exactly the four remaining live/fixture sources and that the three
dead-source scrape functions have been removed from module scope.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "gtm" / "job-market-scanner.py"
SPEC = importlib.util.spec_from_file_location(
    "job_market_scanner_allowlist", SCRIPT_PATH
)
module = importlib.util.module_from_spec(SPEC)
sys.modules["job_market_scanner_allowlist"] = module
assert SPEC and SPEC.loader
SPEC.loader.exec_module(module)


EXPECTED_ALLOWLIST = {"indeed", "linkedin", "career_page", "example-board"}
REMOVED_SOURCES = {"google", "google_direct", "rigzone"}
REMOVED_SCRAPERS = ("scrape_google_jobs", "scrape_google_direct", "scrape_rigzone")


def test_allowlist_contains_exactly_3_live_sources():
    assert module.SOURCE_ALLOWLIST == EXPECTED_ALLOWLIST


def test_rate_limits_exclude_removed_sources():
    for src in REMOVED_SOURCES:
        assert src not in module.SOURCE_RATE_LIMITS, (
            f"{src} must be removed from SOURCE_RATE_LIMITS per Q9"
        )


def test_allowed_domains_exclude_removed_sources():
    for src in REMOVED_SOURCES:
        assert src not in module.SOURCE_ALLOWED_DOMAINS, (
            f"{src} must be removed from SOURCE_ALLOWED_DOMAINS per Q9"
        )


def test_dead_source_scrapers_removed():
    for name in REMOVED_SCRAPERS:
        assert not hasattr(module, name), (
            f"{name} must be deleted per Q9; still present at module scope"
        )


def test_live_scraper_functions_retained():
    for name in ("scrape_indeed", "scrape_linkedin_search"):
        assert hasattr(module, name), f"{name} must be retained"


def test_indeed_query_has_no_rigzone_residue():
    source = SCRIPT_PATH.read_text()
    assert "site:rigzone.com" not in source, (
        "Indeed/Google query must not reference rigzone after Q9 removal"
    )
