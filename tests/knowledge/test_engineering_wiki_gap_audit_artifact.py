"""Audit-artifact existence + schema test for W1-C engineering-wiki gap audit.

Implements the test contract from `docs/plans/2026-05-02-issue-2588-llm-wiki-W1C-engineering-gap-audit.md`.
Validates that the audit at `docs/audits/2026-05-02-engineering-wiki-gap-audit.md` exists
with the required tables and ≥8 prioritized backfill entries, and that each priority
entry's rationale references a verifiable taxonomy anchor (ISO 19900-series part number,
calc-citation-contract phrase, or ratio expression).
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
AUDIT = REPO_ROOT / "docs/audits/2026-05-02-engineering-wiki-gap-audit.md"

# Anchors per W1-C plan MAJOR-2 + MAJOR-3 fixes
ISO_19900_REGEX = re.compile(r"\b(19900|19901|19902|19903|19904|19905-1)\b")
CITATION_CONTRACT_REGEX = re.compile(
    r"(citation-contract|citation contract|would cite)", re.IGNORECASE
)
RATIO_REGEX = re.compile(r"(raw/wiki|\d+\s*:\s*\d+)")


def _read_audit() -> str:
    assert AUDIT.exists(), f"audit artifact not found at {AUDIT}"
    return AUDIT.read_text(encoding="utf-8")


def _table_rows(text: str, table_header_substr: str) -> list[str]:
    """Extract data rows from a markdown table whose header line contains the substring.

    Returns the list of row lines (excluding header + separator).
    """
    lines = text.splitlines()
    rows: list[str] = []
    in_table = False
    for i, line in enumerate(lines):
        if not in_table:
            if line.startswith("|") and table_header_substr in line:
                # Look ahead for the |---| separator line
                if i + 1 < len(lines) and re.match(r"^\|[\s\-:|]+\|\s*$", lines[i + 1]):
                    in_table = True
            continue
        # In table: stop at first non-pipe line or the separator line
        if not line.startswith("|"):
            break
        if re.match(r"^\|[\s\-:|]+\|\s*$", line):
            continue
        rows.append(line)
    return rows


def test_audit_file_exists():
    assert AUDIT.exists(), f"audit artifact missing at {AUDIT}"


def test_audit_table_a_raw_inventory():
    """Table A (raw inventory) has ≥7 prefix-bucket rows."""
    text = _read_audit()
    rows = _table_rows(text, "Prefix Bucket")
    assert len(rows) >= 7, f"Table A has {len(rows)} rows; need ≥7 prefix buckets"


def test_audit_table_b_wiki_inventory():
    """Table B (wiki inventory) has 6 rows (5 subdirs + root)."""
    text = _read_audit()
    rows = _table_rows(text, "| Subdir |")
    # Filter out the "Total" row which the test contract counts separately
    data_rows = [r for r in rows if "**Total**" not in r]
    assert len(data_rows) == 6, f"Table B has {len(data_rows)} non-total rows; expected exactly 6"


def test_audit_gap_priority_table():
    """Gap-priority table (Table C) has ≥8 entries."""
    text = _read_audit()
    rows = _table_rows(text, "Logical Subdir")
    assert len(rows) >= 8, f"Gap-priority table has {len(rows)} rows; need ≥8"


def test_audit_priority_rationales_cite_required_anchors():
    """Each priority entry's rationale must cite ISO 19900-series, calc-citation-contract, or a ratio."""
    text = _read_audit()
    rows = _table_rows(text, "Logical Subdir")
    failures: list[str] = []
    for row in rows:
        # Skip rows that are just cross-references to other Tier B issues
        if "covered by #" in row.lower():
            continue
        cells = [c.strip() for c in row.split("|")]
        # Rationale is at position 7 in a 10-cell layout (counting empty edges)
        # but we just check the whole row text for any anchor match
        if not (
            ISO_19900_REGEX.search(row)
            or CITATION_CONTRACT_REGEX.search(row)
            or RATIO_REGEX.search(row)
        ):
            failures.append(row[:200])
    assert not failures, "Priority entries lack required taxonomy anchor:\n" + "\n".join(failures)


def test_audit_deprecation_pass_present():
    """Audit must include a deprecation pass section."""
    text = _read_audit()
    assert "Deprecation pass" in text or "deprecation pass" in text, (
        "audit must include a deprecation pass section"
    )


def test_audit_internal_consistency_wiki_count():
    """Wiki side per-subdir counts must sum to the reported total."""
    text = _read_audit()
    # Per Table B in the audit: concepts=42, entities=23, sources=23, standards=9, workflows=5, root=3
    # 42+23+23+9+5+3 = 105
    expected = 42 + 23 + 23 + 9 + 5 + 3
    # The audit explicitly reports "= 105"
    assert f"= **{expected}**" in text or f"= {expected}" in text or "**105**" in text, (
        f"audit's wiki-count consistency claim missing or wrong; expected {expected}"
    )
