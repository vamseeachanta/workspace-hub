"""Shared fixtures/helpers for source_doc_key promoter follow-up tests (#2389)."""

from __future__ import annotations

import re
from pathlib import Path

import pytest


SHA256_A = "sha256:" + "a" * 64
SHA256_B = "sha256:" + "b" * 64
SHA256_C = "sha256:" + "c" * 64

__all__ = [
    "SHA256_A",
    "SHA256_B",
    "SHA256_C",
    "_assert_content_hash_header",
    "_assert_source_doc_key_header",
    "_assert_no_path_leakage_in_doc_key_headers",
    "_curve_record",
    "_definition_record",
    "_procedure_record",
    "_requirement_record",
    "_table_record",
    "_worked_example_record",
]


# ── shared assertion helpers ──────────────────────────────────────────────


def _assert_content_hash_header(text: str) -> str:
    """Find the canonical ``# content-hash: <hex>`` line and return the hex."""
    for line in text.splitlines():
        m = re.match(r"^#\s*content-hash:\s*([0-9a-f]{64})\s*$", line)
        if m:
            return m.group(1)
    raise AssertionError(
        "no canonical '# content-hash: <64-hex>' header in output:\n"
        f"{text[:400]}"
    )


def _assert_source_doc_key_header(text: str, expected: str) -> None:
    needle = f"# source_doc_key: {expected}"
    assert needle in text, (
        f"expected header line {needle!r} missing; output head:\n{text[:400]}"
    )


def _assert_no_path_leakage_in_doc_key_headers(text: str) -> None:
    """No `# source_doc_key:` line may contain a path separator."""
    sdk_lines = [
        ln for ln in text.splitlines() if ln.startswith("# source_doc_key:")
    ]
    assert sdk_lines, (
        "expected at least one # source_doc_key header; "
        f"output head:\n{text[:400]}"
    )
    for ln in sdk_lines:
        value = ln.split(":", 1)[1].strip()
        # value is "<algo>:<hex>" — algorithm separator is ':', not '/'\\
        assert "/" not in value, value
        assert "\\" not in value, value


# ── record-builder fixtures (per-promoter shapes) ─────────────────────────


def _curve_record(
    *,
    doc_key: str | None = SHA256_A,
    caption: str = "S-N Curve for Tubular Joints in Seawater",
    figure_id: str = "Figure 4.1",
    domain: str = "naval-architecture",
    document: str = "DNV-RP-C203.pdf",
    page: int = 22,
) -> dict:
    source: dict = {"document": document, "page": page}
    if doc_key is not None:
        source["doc_key"] = doc_key
    return {
        "caption": caption,
        "figure_id": figure_id,
        "source": source,
        "domain": domain,
        "manifest": document,
    }


def _definition_record(
    *,
    doc_key: str | None = SHA256_A,
    text: str = (
        "Cathodic Protection (CP): A technique used to control corrosion "
        "by making the metal surface the cathode of an electrochemical cell."
    ),
    domain: str = "naval-architecture",
    document: str = "DNV-RP-B401.pdf",
    section: str = "1.3",
    page: int = 5,
) -> dict:
    source: dict = {"document": document, "section": section, "page": page}
    if doc_key is not None:
        source["doc_key"] = doc_key
    return {
        "text": text,
        "source": source,
        "domain": domain,
        "manifest": document,
    }


def _procedure_record(
    *,
    doc_key: str | None = SHA256_A,
    text: str = (
        "Procedure: Cathodic Protection Survey\n"
        "1. Verify reference electrode calibration\n"
        "2. Measure potential at each test point\n"
        "3. Record readings against Ag/AgCl reference"
    ),
    domain: str = "naval-architecture",
    document: str = "DNV-RP-B401.pdf",
    section: str = "8.2",
    page: int = 55,
) -> dict:
    source: dict = {"document": document, "section": section, "page": page}
    if doc_key is not None:
        source["doc_key"] = doc_key
    return {
        "text": text,
        "source": source,
        "domain": domain,
        "manifest": document,
    }


def _requirement_record(
    *,
    doc_key: str | None = SHA256_A,
    text: str = (
        "The minimum design life for cathodic protection systems shall be "
        "25 years unless otherwise specified by the operator."
    ),
    domain: str = "naval-architecture",
    document: str = "DNV-RP-B401.pdf",
    section: str = "4.1.2",
    page: int = 10,
) -> dict:
    source: dict = {"document": document, "section": section, "page": page}
    if doc_key is not None:
        source["doc_key"] = doc_key
    return {
        "text": text,
        "source": source,
        "domain": domain,
        "manifest": document,
    }


def _table_record(
    *,
    project_root: Path,
    doc_key: str | None = SHA256_A,
    csv_basename: str = "Sample-Table-0.csv",
    domain: str = "naval-architecture",
    document: str = "Sample.pdf",
    csv_body: str = "Material,Yield (MPa)\nS355,355\nS460,460\n",
) -> dict:
    """Create a table record AND lay down the upstream source CSV the
    tables promoter expects to find under
    ``{project_root}/data/doc-intelligence/tables/<csv_basename>``.
    """
    src = project_root / "data" / "doc-intelligence" / "tables" / csv_basename
    src.parent.mkdir(parents=True, exist_ok=True)
    src.write_text(csv_body, encoding="utf-8")

    source: dict = {"document": document, "page": 12}
    if doc_key is not None:
        source["doc_key"] = doc_key
    return {
        "title": "Material Properties",
        "columns": ["Material", "Yield (MPa)"],
        "row_count": 2,
        "csv_path": f"tables/{csv_basename}",
        "source": source,
        "domain": domain,
        "manifest": document,
    }


def _worked_example_record(
    *,
    doc_key: str | None = SHA256_A,
    text: str = (
        "Example 3.1: Calculate hydrostatic pressure at 100m depth.\n"
        "Given: rho = 1025 kg/m³, g = 9.81 m/s², d = 100 m\n"
        "Solution: P = 1025 × 9.81 × 100 = 1,005,525 Pa"
    ),
    domain: str = "naval-architecture",
    document: str = "DNV-RP-C205.pdf",
    section: str = "3.3",
    page: int = 18,
) -> dict:
    source: dict = {"document": document, "section": section, "page": page}
    if doc_key is not None:
        source["doc_key"] = doc_key
    return {
        "text": text,
        "source": source,
        "domain": domain,
        "manifest": document,
    }
