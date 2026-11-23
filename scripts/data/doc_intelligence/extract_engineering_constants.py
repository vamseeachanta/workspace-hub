# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml"]
# ///
"""Extract engineering constants from document manifest sections and tables.

Supports:
- Table extraction: detects parameter/value/unit column patterns
- Text extraction: finds inline patterns like "f_y = 450 MPa" or "E = 207 GPa"
- Manifest aggregation: processes all sections and deduplicates results
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

import yaml

# ---------------------------------------------------------------------------
# Type alias
# ---------------------------------------------------------------------------

Constant = dict[str, Any]  # {name, value, unit, source}

# ---------------------------------------------------------------------------
# Column name matching helpers
# ---------------------------------------------------------------------------

_NAME_SYNONYMS = {"parameter", "property", "name", "description", "symbol", "item"}
_VALUE_SYNONYMS = {"value", "val", "magnitude", "amount", "quantity"}
_UNIT_SYNONYMS = {"unit", "units", "uom", "dimension"}
_SOURCE_SYNONYMS = {"source", "reference", "ref", "standard", "origin"}

_DIMENSIONLESS_TOKENS = {"-", "—", "dimensionless", "none", "n/a", ""}


def _col_index(columns: list[str], synonyms: set[str]) -> int | None:
    """Return first column index whose lower-cased name is in synonyms."""
    for i, col in enumerate(columns):
        if col.strip().lower() in synonyms:
            return i
    return None


# ---------------------------------------------------------------------------
# extract_constants_from_table
# ---------------------------------------------------------------------------

def extract_constants_from_table(table: dict) -> list[Constant]:
    """Extract constants from a table dict with 'columns' and 'rows' keys.

    Detects name, value, unit, and source columns by synonym matching.
    Rows where the value cell is not numeric are silently skipped.

    Returns list of {name, value, unit, source} dicts.
    """
    columns: list[str] = table.get("columns") or []
    rows: list[list[str]] = table.get("rows") or []

    if not columns or not rows:
        return []

    name_idx = _col_index(columns, _NAME_SYNONYMS)
    value_idx = _col_index(columns, _VALUE_SYNONYMS)
    unit_idx = _col_index(columns, _UNIT_SYNONYMS)
    source_idx = _col_index(columns, _SOURCE_SYNONYMS)

    # Value column is mandatory for extraction
    if value_idx is None:
        return []

    constants: list[Constant] = []
    for row in rows:
        if len(row) <= value_idx:
            continue

        raw_value = row[value_idx].strip()
        try:
            numeric_value = float(raw_value)
        except ValueError:
            continue

        name = row[name_idx].strip() if (name_idx is not None and len(row) > name_idx) else None
        raw_unit = row[unit_idx].strip() if (unit_idx is not None and len(row) > unit_idx) else None
        unit = None if raw_unit is None or raw_unit.lower() in _DIMENSIONLESS_TOKENS else raw_unit
        source = row[source_idx].strip() if (source_idx is not None and len(row) > source_idx) else None

        constants.append(
            {"name": name, "value": numeric_value, "unit": unit, "source": source}
        )

    return constants


# ---------------------------------------------------------------------------
# extract_constants_from_text
# ---------------------------------------------------------------------------

# Matches patterns like:
#   f_y = 450 MPa
#   E_s = 200 GPa
#   SF = 2.0
#   K_IC = 1.5e2 MPa·m^0.5   (unit may contain non-space chars up to next whitespace token)
#
# Group 1: symbol (word chars + underscores + optional subscript letters)
# Group 2: numeric value (integer, decimal, scientific notation)
# Group 3: unit token (optional — one word after number, allowing special chars)

_INLINE_PATTERN = re.compile(
    r"""
    (?<![=<>!])             # not preceded by another comparison operator
    \b
    ([\w][\w./]*            # symbol start: word char
      (?:_[\w]+)?)          # optional _subscript
    \s*=\s*
    (                       # numeric value
      [+-]?
      (?:\d+\.?\d*|\.\d+)   # digits with optional decimal
      (?:[eE][+-]?\d+)?     # optional exponent
    )
    \s*
    (                       # optional unit — non-space, non-comma tokens
      [A-Za-z°µΩ]
      [\w°µΩ·/^.\-]*
    )?
    """,
    re.VERBOSE,
)

# Symbols that look like constants but are likely conjunctions/assignments in prose
_SYMBOL_BLOCKLIST = {"a", "i", "n", "t", "x", "y", "z", "or", "if", "in", "is"}


def extract_constants_from_text(text: str) -> list[Constant]:
    """Find inline constants in free text using pattern `symbol = number [unit]`.

    Returns list of {name, value, unit, source} dicts (source always None).
    """
    if not text:
        return []

    constants: list[Constant] = []
    seen: set[tuple[str, float]] = set()

    for match in _INLINE_PATTERN.finditer(text):
        symbol = match.group(1).strip()
        if symbol.lower() in _SYMBOL_BLOCKLIST:
            continue

        try:
            value = float(match.group(2))
        except ValueError:
            continue

        raw_unit = match.group(3)
        unit = (
            None
            if raw_unit is None or raw_unit.strip().lower() in _DIMENSIONLESS_TOKENS
            else raw_unit.strip()
        )

        key = (symbol, value)
        if key in seen:
            continue
        seen.add(key)

        constants.append({"name": symbol, "value": value, "unit": unit, "source": None})

    return constants


# ---------------------------------------------------------------------------
# extract_all_constants
# ---------------------------------------------------------------------------

def extract_all_constants(manifest: dict) -> list[Constant]:
    """Process all sections in a manifest dict, extracting and deduplicating constants.

    Manifest structure expected::

        {
            "sections": [
                {
                    "heading": "...",
                    "text": "...",
                    "tables": [{"columns": [...], "rows": [[...], ...]}, ...]
                },
                ...
            ]
        }

    Returns deduplicated list of constant dicts.
    """
    sections = manifest.get("sections") or []
    all_constants: list[Constant] = []
    seen: set[tuple[str | None, float]] = set()

    def _add(c: Constant) -> None:
        key = (c["name"], c["value"])
        if key not in seen:
            seen.add(key)
            all_constants.append(c)

    for section in sections:
        text = section.get("text") or ""
        for c in extract_constants_from_text(text):
            _add(c)

        for table in section.get("tables") or []:
            for c in extract_constants_from_table(table):
                _add(c)

    return all_constants


# ---------------------------------------------------------------------------
# CLI main
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Extract engineering constants from a manifest YAML file."
    )
    parser.add_argument("--input", required=True, help="Path to manifest YAML")
    parser.add_argument("--output", default=None, help="Optional output YAML path")
    args = parser.parse_args(argv)

    manifest_path = Path(args.input)
    if not manifest_path.exists():
        print(f"ERROR: input file not found: {manifest_path}", file=sys.stderr)
        sys.exit(1)

    with manifest_path.open() as fh:
        manifest = yaml.safe_load(fh) or {}

    constants = extract_all_constants(manifest)

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with out_path.open("w") as fh:
            yaml.dump({"constants": constants}, fh, default_flow_style=False, allow_unicode=True)
        print(f"Wrote {len(constants)} constants to {out_path}")
    else:
        yaml.dump({"constants": constants}, sys.stdout, default_flow_style=False, allow_unicode=True)


if __name__ == "__main__":
    main()
