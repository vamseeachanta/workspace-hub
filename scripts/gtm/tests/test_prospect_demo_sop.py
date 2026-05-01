"""Public-safety checks for the #2346 prospect-demo SOP runbook."""
from __future__ import annotations

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
SOP_PATH = REPO_ROOT / "docs" / "gtm" / "prospect-demo-sop.md"


REQUIRED_PHRASES = [
    "No outbound outreach is performed by this SOP",
    "48-hour decision tree",
    "F1 — refuse",
    "F2 — closest canonical vessel",
    "F3 — canonical-class default",
    "F4 — one clarification email",
    "F5 — reduced scope with caveats",
    "private-log/fallback-applied.json",
    "public-safe rule",
    "logical paths only",
]

FORBIDDEN_PATTERNS = [
    r"/mnt/local-analysis",
    r"/home/[^\s)]+",
    r"[A-Za-z]:\\\\",
    r"client[-_ ]?confidential",
    r"proprietary path",
]


def test_prospect_demo_sop_exists_with_required_decision_contract() -> None:
    text = SOP_PATH.read_text(encoding="utf-8")

    missing = [phrase for phrase in REQUIRED_PHRASES if phrase not in text]

    assert missing == []


def test_prospect_demo_sop_has_48_hour_timeline_and_delivery_guardrails() -> None:
    text = SOP_PATH.read_text(encoding="utf-8")

    assert "Hour 0-4" in text
    assert "Hour 4-24" in text
    assert "Hour 24-40" in text
    assert "Hour 40-48" in text
    assert "email-first" in text
    assert "no private URL is published" in text
    assert "purge_after_utc" in text


def test_prospect_demo_sop_avoids_local_or_proprietary_path_leakage() -> None:
    text = SOP_PATH.read_text(encoding="utf-8")

    leaked = [pattern for pattern in FORBIDDEN_PATTERNS if re.search(pattern, text, flags=re.IGNORECASE)]

    assert leaked == []
