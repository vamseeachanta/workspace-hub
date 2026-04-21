"""TOS_REVIEW.md governance artifact tests — #1707 / #2348 plan v3 §B.

ABOUTME: Validates the compliance record that governs the GTM scanner:
per-source owner sign-off (Q10), REMOVED-sources appendix (Q9), LinkedIn owner
override block round-trips through the parser (Q11), and README points at the
doc so operators can find it.
"""
from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "gtm" / "job-market-scanner.py"
TOS_PATH = REPO_ROOT / "docs" / "strategy" / "gtm" / "job-market-scan" / "TOS_REVIEW.md"
README_PATH = REPO_ROOT / "docs" / "strategy" / "gtm" / "job-market-scan" / "README.md"

SPEC = importlib.util.spec_from_file_location(
    "job_market_scanner_tos", SCRIPT_PATH
)
module = importlib.util.module_from_spec(SPEC)
sys.modules["job_market_scanner_tos"] = module
assert SPEC and SPEC.loader
SPEC.loader.exec_module(module)


LIVE_SOURCES = ("linkedin", "indeed", "career_page")
REMOVED_SOURCES = ("google", "google_direct", "rigzone")
OWNER_SIGNOFF_RE = re.compile(r"Owner approved:\s+\d{4}-\d{2}-\d{2}")


def _read_tos():
    assert TOS_PATH.exists(), f"TOS_REVIEW.md missing at {TOS_PATH}"
    return TOS_PATH.read_text()


def test_tos_review_md_exists():
    assert TOS_PATH.exists()


def test_tos_review_md_has_owner_signoff_per_source():
    text = _read_tos()
    for src in LIVE_SOURCES:
        header = re.search(rf"^##\s+Source:\s+{re.escape(src)}\b", text, re.MULTILINE)
        assert header, f"Missing `## Source: {src}` section in TOS_REVIEW.md"
        tail = text[header.end():]
        next_header = re.search(r"^##\s+", tail, re.MULTILINE)
        section = tail[: next_header.start()] if next_header else tail
        assert OWNER_SIGNOFF_RE.search(section), (
            f"`Owner approved: YYYY-MM-DD` line missing in section for {src}"
        )


def test_tos_review_md_lists_removed_sources():
    text = _read_tos().lower()
    for src in REMOVED_SOURCES:
        assert src in text, f"REMOVED appendix must mention {src}"
    assert "removed" in text


def test_tos_review_md_has_cease_and_desist_runbook():
    text = _read_tos().lower()
    assert "cease" in text and "desist" in text, (
        "Cease-and-desist runbook must be present per U4"
    )


def test_linkedin_override_parser_round_trips(tmp_path, monkeypatch):
    """The override-parser must find LinkedIn when a signed block is present,
    and return an empty set when the block is absent."""
    doc = tmp_path / "TOS_REVIEW.md"
    doc.write_text(
        "# TOS Review\n\n"
        "## Source: linkedin\n"
        "Owner override: LinkedIn robots.txt disallows scraping. Owner accepts risk.\n"
        "Owner approved: 2026-04-20\n"
        "Owner: Vamsee Achanta (business owner, ACE Engineer)\n\n"
        "## Source: indeed\n"
        "Owner approved: 2026-04-20\n"
        "Owner: Vamsee Achanta\n"
    )
    monkeypatch.setattr(module, "_TOS_REVIEW_PATH", doc)
    assert module._parse_owner_overrides_from_tos_review() == {"linkedin"}

    doc.write_text(
        "# TOS Review\n\n"
        "## Source: indeed\nOwner approved: 2026-04-20\n"
        "## Source: linkedin\nOwner approved: 2026-04-20\n"
    )
    assert module._parse_owner_overrides_from_tos_review() == set()


def test_override_parser_survives_missing_file(tmp_path, monkeypatch):
    monkeypatch.setattr(module, "_TOS_REVIEW_PATH", tmp_path / "does-not-exist.md")
    assert module._parse_owner_overrides_from_tos_review() == set()


def test_readme_references_tos_review():
    assert README_PATH.exists()
    text = README_PATH.read_text()
    assert "TOS_REVIEW.md" in text, "README must reference TOS_REVIEW.md"


def test_readme_reflects_three_source_reality():
    text = README_PATH.read_text().lower()
    for src in ("linkedin", "indeed", "career"):
        assert src in text, f"README must mention {src} as a current source"
    for dead in ("rigzone", "google direct", "google_direct"):
        assert dead not in text or "removed" in text, (
            f"README should not advertise removed source {dead} without marking it REMOVED"
        )
