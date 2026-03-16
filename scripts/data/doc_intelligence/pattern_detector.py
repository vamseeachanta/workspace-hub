"""Normalize Excel formulas to row-1 canonical form and detect patterns.

Uses openpyxl.formula.translate.Translator to shift cell references so
identical patterns across rows collapse into a single canonical key.
"""

from __future__ import annotations

import re
from collections import defaultdict

from openpyxl.formula.translate import Translator

# Extract row number from a cell reference like "C5" → 5
_ROW_RE = re.compile(r"[A-Z]+(\d+)$", re.IGNORECASE)


def _cell_row(cell_ref: str) -> int:
    """Extract row number from cell_ref like 'C5' → 5."""
    m = _ROW_RE.search(cell_ref)
    return int(m.group(1)) if m else 1


def _cell_col(cell_ref: str) -> str:
    """Extract column letters from cell_ref like 'C5' → 'C'."""
    m = re.match(r"([A-Z]+)", cell_ref, re.IGNORECASE)
    return m.group(1).upper() if m else "A"


def normalize_formula(formula: str, cell_ref: str) -> str:
    """Normalize a formula to row-1 canonical form.

    Translates all relative row references so the formula appears as if
    it lived in row 1 of the same column.  Absolute references ($A$3)
    remain unchanged.

    Args:
        formula: Excel formula string starting with '='.
        cell_ref: The cell where this formula lives (e.g. 'C5').

    Returns:
        Canonical formula string.  On translator failure, returns the
        original formula unchanged.
    """
    if not formula or not formula.startswith("="):
        return formula

    row = _cell_row(cell_ref)
    if row == 1:
        return formula

    col = _cell_col(cell_ref)
    origin = f"{col}{row}"
    target = f"{col}1"

    try:
        translated = Translator(formula, origin=origin).translate_formula(
            target
        )
        return translated
    except Exception:
        return formula


def detect_row_patterns(
    formulas: list[dict],
) -> dict[str, list[dict]]:
    """Group formulas by their canonical normalized form.

    Args:
        formulas: List of formula dicts with at least keys:
            cell_ref, sheet, formula, cached_value, references.

    Returns:
        Dict mapping canonical formula → list of original cell dicts.
    """
    patterns: dict[str, list[dict]] = defaultdict(list)

    for f in formulas:
        canonical = normalize_formula(f["formula"], f["cell_ref"])
        patterns[canonical].append(f)

    return dict(patterns)


def compute_compression_stats(
    patterns: dict[str, list[dict]],
) -> dict[str, int | float]:
    """Compute compression statistics from detected patterns.

    Returns:
        Dict with total_cells, unique_patterns, compression_ratio.
    """
    total = sum(len(cells) for cells in patterns.values())
    unique = len(patterns)

    if unique == 0:
        return {
            "total_cells": 0,
            "unique_patterns": 0,
            "compression_ratio": 0.0,
        }

    return {
        "total_cells": total,
        "unique_patterns": unique,
        "compression_ratio": round(total / unique, 1),
    }
