"""Regex-based extraction of cell references from Excel formula strings.

Handles: A1, $A$1, A$1, $A1, ranges A1:B10, cross-sheet Sheet1!A1,
quoted sheet names 'Sheet Name'!A1.
"""

import re
from typing import List

# Match optional sheet prefix (quoted or unquoted), cell ref, optional range end.
CELL_REF_RE = re.compile(
    r"(?:'([^']+)'!|([A-Za-z_]\w*)!)?"  # optional sheet (quoted or plain)
    r"(\$?[A-Z]{1,3}\$?\d+)"  # cell like A1 or $A$1
    r"(?::(\$?[A-Z]{1,3}\$?\d+))?",  # optional range end
    re.IGNORECASE,
)


def _normalize_ref(sheet: str | None, cell: str) -> str:
    """Return 'Sheet!Cell' or just 'Cell'."""
    if sheet:
        return f"{sheet}!{cell}"
    return cell


def parse_formula_references(formula: str) -> List[str]:
    """Extract cell references from an Excel formula string.

    Args:
        formula: An Excel formula string (e.g. '=A1+Sheet1!B2').

    Returns:
        List of reference strings, e.g. ['A1', 'Sheet1!B2'].
        Ranges are expanded to start and end refs.
    """
    if not formula:
        return []

    refs: List[str] = []
    seen: set = set()

    for m in CELL_REF_RE.finditer(formula):
        sheet = m.group(1) or m.group(2)  # quoted or plain sheet name
        cell_start = m.group(3)
        cell_end = m.group(4)

        ref = _normalize_ref(sheet, cell_start)
        if ref not in seen:
            refs.append(ref)
            seen.add(ref)

        if cell_end:
            ref_end = _normalize_ref(sheet, cell_end)
            if ref_end not in seen:
                refs.append(ref_end)
                seen.add(ref_end)

    return refs
