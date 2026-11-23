"""Table quality filters — watermark detection, dedup, content threshold, quality rating.

Deterministic filters applied before (or instead of) LLM quality rating.
Designed to eliminate the 41% junk rate found in WRK-1246 audit.

Usage:
    from scripts.data.doc_intelligence.table_quality import (
        classify_table_quality,
        is_watermark,
        meets_content_threshold,
        dedup_tables,
        filter_tables,
    )
"""

import hashlib
import re

# Known watermark patterns (case-insensitive)
WATERMARK_PATTERNS = [
    re.compile(r"ihs\s+licensee", re.IGNORECASE),
    re.compile(r"document\s+policy\s+management\s+group", re.IGNORECASE),
    re.compile(r"det\s+norske\s+veritas.*all\s+rights\s+reserved", re.IGNORECASE),
    re.compile(r"no\s+reproduction\s+without\s+written\s+permission", re.IGNORECASE),
    re.compile(r"copyright\s+©?\s*\d{4}.*all\s+rights\s+reserved", re.IGNORECASE),
    re.compile(r"provided\s+by\s+ihs", re.IGNORECASE),
    re.compile(r"american\s+petroleum\s+institute.*copyright", re.IGNORECASE),
]

# Minimum thresholds
MIN_DATA_ROWS = 3
MIN_NUMERIC_COLUMNS = 2


def _table_text(table: dict) -> str:
    """Flatten a table dict to a single string for pattern matching."""
    parts = []
    for col in table.get("columns", []):
        parts.append(str(col))
    for row in table.get("rows", []):
        for cell in row:
            parts.append(str(cell))
    return " ".join(parts)


def _table_hash(table: dict) -> str:
    """Content hash for dedup."""
    text = _table_text(table)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _is_numeric(value: str) -> bool:
    """Check if a string looks like a number."""
    v = value.strip().strip('"').strip("'")
    if not v:
        return False
    # Handle common numeric patterns: 1.23, -4.5, 0.150, 10000, 1.5e3
    v = v.replace(",", "")  # strip thousand separators
    try:
        float(v)
        return True
    except ValueError:
        return False


def is_watermark(table: dict) -> bool:
    """Detect if a table is a copyright/license watermark."""
    rows = table.get("rows", [])
    if not rows:
        return False

    text = _table_text(table)
    for pattern in WATERMARK_PATTERNS:
        if pattern.search(text):
            return True

    return False


def meets_content_threshold(
    table: dict,
    min_data_rows: int = MIN_DATA_ROWS,
    min_numeric_cols: int = MIN_NUMERIC_COLUMNS,
) -> bool:
    """Check if table has enough real content: ≥min_data_rows non-empty rows
    and ≥min_numeric_cols columns with numeric values."""
    rows = table.get("rows", [])

    # Count non-empty rows (at least one non-empty cell)
    data_rows = [r for r in rows if any(str(c).strip() for c in r)]
    if len(data_rows) < min_data_rows:
        return False

    # Count columns with numeric values
    if not data_rows:
        return False

    max_cols = max(len(r) for r in data_rows)
    numeric_col_count = 0

    for col_idx in range(max_cols):
        numeric_in_col = 0
        total_in_col = 0
        for row in data_rows:
            if col_idx < len(row):
                cell = str(row[col_idx]).strip()
                if cell:
                    total_in_col += 1
                    if _is_numeric(cell):
                        numeric_in_col += 1
        # Column is numeric if ≥50% of non-empty cells are numbers
        if total_in_col > 0 and numeric_in_col / total_in_col >= 0.5:
            numeric_col_count += 1

    return numeric_col_count >= min_numeric_cols


def dedup_tables(tables: list[dict]) -> list[dict]:
    """Remove duplicate tables by content hash. Keeps first occurrence."""
    seen: set[str] = set()
    result = []
    for table in tables:
        h = _table_hash(table)
        if h not in seen:
            seen.add(h)
            result.append(table)
    return result


def classify_table_quality(table: dict) -> str:
    """Classify table quality deterministically.

    Returns: "usable" | "partial" | "junk"
    - junk: watermark, empty, or below content threshold
    - usable: passes all deterministic gates
    - partial: passes threshold but borderline (few rows or sparse numerics)
    """
    rows = table.get("rows", [])

    # Empty
    if not rows:
        return "junk"

    # Watermark
    if is_watermark(table):
        return "junk"

    # Below threshold
    if not meets_content_threshold(table):
        return "junk"

    # Count data density for usable vs partial
    data_rows = [r for r in rows if any(str(c).strip() for c in r)]
    if len(data_rows) >= 5:
        return "usable"

    return "partial"


def filter_tables(tables: list[dict]) -> dict:
    """Apply full quality pipeline: dedup → watermark → threshold → classify.

    Returns:
        {
            "accepted": [{"table": dict, "quality": str, "index": int}, ...],
            "rejected": [{"table": dict, "reason": str, "index": int}, ...],
            "stats": {"total": N, "deduped": N, "watermark": N, ...},
        }
    """
    total = len(tables)

    # Step 1: Dedup
    deduped = dedup_tables(tables)
    n_deduped = total - len(deduped)

    # Step 2: Classify each
    accepted = []
    rejected = []
    watermark_count = 0
    threshold_count = 0

    for i, table in enumerate(deduped):
        if is_watermark(table):
            rejected.append({"table": table, "reason": "watermark", "index": i})
            watermark_count += 1
        elif not meets_content_threshold(table):
            rejected.append({"table": table, "reason": "below_threshold", "index": i})
            threshold_count += 1
        else:
            quality = classify_table_quality(table)
            accepted.append({"table": table, "quality": quality, "index": i})

    return {
        "accepted": accepted,
        "rejected": rejected,
        "stats": {
            "total_input": total,
            "duplicates_removed": n_deduped,
            "watermarks_removed": watermark_count,
            "below_threshold": threshold_count,
            "accepted": len(accepted),
            "usable": sum(1 for a in accepted if a["quality"] == "usable"),
            "partial": sum(1 for a in accepted if a["quality"] == "partial"),
            "quality_rate": round(len(accepted) / total * 100, 1) if total else 0,
        },
    }
