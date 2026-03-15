#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml"]
# ///
"""Convert a DocumentManifest YAML to a dark-intelligence archive YAML.

Usage:
    uv run --no-project python manifest_to_archive.py \
        --input path/to/manifest.yaml \
        --category pipeline \
        --subcategory wall_thickness \
        [--output path/to/archive.yaml]

If --output is omitted, the archive YAML is printed to stdout.
"""

import argparse
import os
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml


# ---------------------------------------------------------------------------
# Regex patterns
# ---------------------------------------------------------------------------

# Equation reference patterns: "Eq. 5.16", "Equation (3.2)", "eq 12", "Eqn. A-1"
_EQ_REF_PATTERN = re.compile(
    r"\b(?:Eq(?:uation|n)?\.?\s*[\(\[]?)([A-Z]?\d+[\.\-]\d+|[A-Z]\-\d+|\d+)[\)\]]?",
    re.IGNORECASE,
)

# Standard reference patterns: "DNV-ST-F101", "API RP 2A", "ISO 19901-1"
_STANDARD_PATTERN = re.compile(
    r"\b(DNV-[A-Z]{2}-[A-Z0-9]+|API\s+RP\s+[\w\-]+|ISO\s+[\d\-]+(?:-\d+)?)",
    re.IGNORECASE,
)

# Formula line: symbol = expression (single line), must contain "="
# Heuristic: short lines with a variable on the left and "=" in the middle
_FORMULA_PATTERN = re.compile(
    r"^\s*([A-Za-z_]\w*(?:\s*[\+\-\*\/\(\)]?\s*)*)\s*=\s*.+",
)

# "where X is the description (unit)" patterns
_WHERE_PATTERN = re.compile(
    r"where\s+([A-Za-z_]\w*(?:\.[A-Za-z_]\w*)?)\s+is\s+(?:the\s+)?(.+?)(?:\s+\(([^\)]+)\))?\s*$",
    re.IGNORECASE | re.MULTILINE,
)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def extract_equations(text: str) -> List[Dict[str, Any]]:
    """Find equation references and associated formulas in section text.

    Args:
        text: Plain text extracted from a document section.

    Returns:
        List of dicts with keys: name, formula, standard, description.
    """
    if not text:
        return []

    lines = text.splitlines()
    results: List[Dict[str, Any]] = []
    seen_names: set = set()

    for line_idx, line in enumerate(lines):
        # Find the standard referenced on this line (if any)
        std_match = _STANDARD_PATTERN.search(line)
        standard = std_match.group(0).strip() if std_match else ""

        for eq_match in _EQ_REF_PATTERN.finditer(line):
            eq_num = eq_match.group(1)
            # Build canonical name — preserve original keyword
            raw_keyword = eq_match.group(0)
            if raw_keyword.lower().startswith("equation"):
                eq_name = f"Equation ({eq_num})"
            elif raw_keyword.lower().startswith("eqn"):
                eq_name = f"Eqn. {eq_num}"
            else:
                eq_name = f"Eq. {eq_num}"

            if eq_name in seen_names:
                continue
            seen_names.add(eq_name)

            # Look for a formula on the following lines (up to 3 lines ahead)
            formula = ""
            description = ""
            for ahead in range(1, 4):
                if line_idx + ahead >= len(lines):
                    break
                candidate = lines[line_idx + ahead].strip()
                if _FORMULA_PATTERN.match(candidate) and "=" in candidate:
                    formula = candidate
                    # Description = the line after the formula, if it exists
                    desc_idx = line_idx + ahead + 1
                    if desc_idx < len(lines):
                        desc_candidate = lines[desc_idx].strip()
                        if desc_candidate and not _EQ_REF_PATTERN.search(desc_candidate):
                            description = desc_candidate
                    break

            results.append(
                {
                    "name": eq_name,
                    "formula": formula,
                    "standard": standard,
                    "description": description,
                }
            )

    return results


def extract_inputs_outputs(
    text: str,
) -> Tuple[List[Dict[str, str]], List[Dict[str, str]]]:
    """Find 'where X is the description (unit)' patterns in section text.

    Args:
        text: Plain text extracted from a document section.

    Returns:
        Tuple of (inputs_list, outputs_list). Both are lists of dicts with
        keys: name, symbol, unit. outputs_list is always empty (cannot be
        determined from 'where' clauses alone).
    """
    if not text:
        return [], []

    inputs: List[Dict[str, str]] = []
    seen_symbols: set = set()

    for match in _WHERE_PATTERN.finditer(text):
        symbol = match.group(1).strip()
        name = match.group(2).strip().rstrip(".,;")
        unit = match.group(3).strip() if match.group(3) else ""

        if symbol in seen_symbols:
            continue
        seen_symbols.add(symbol)

        inputs.append({"name": name, "symbol": symbol, "unit": unit})

    return inputs, []


def manifest_to_archive(
    manifest_dict: Dict[str, Any],
    category: str,
    subcategory: str,
) -> Dict[str, Any]:
    """Convert a DocumentManifest dict to a dark-intelligence archive dict.

    Args:
        manifest_dict: Plain dict matching the DocumentManifest schema.
        category: Top-level domain category (e.g. "pipeline").
        subcategory: Sub-domain (e.g. "wall_thickness").

    Returns:
        Archive dict ready for YAML serialisation.
    """
    metadata = manifest_dict.get("metadata", {})
    filename = metadata.get("filename", "unknown")
    fmt = metadata.get("format", "pdf")

    # Join all section texts
    sections = manifest_dict.get("sections", [])
    full_text = "\n".join(s.get("text", "") for s in sections if s.get("text"))

    equations = extract_equations(full_text)
    inputs, outputs = extract_inputs_outputs(full_text)

    # Collect standard references from equations + raw scan
    ref_set: set = set()
    for eq in equations:
        if eq["standard"]:
            ref_set.add(eq["standard"])
    for std_match in _STANDARD_PATTERN.finditer(full_text):
        ref_set.add(std_match.group(0).strip())
    # Also include doc_ref if present
    doc_ref = manifest_dict.get("doc_ref")
    if doc_ref:
        ref_set.add(doc_ref)

    return {
        "source_type": fmt,
        "source_description": f"Extracted from {filename}",
        "extracted_date": date.today().isoformat(),
        "legal_scan_passed": False,
        "category": category,
        "subcategory": subcategory,
        "equations": equations,
        "inputs": inputs,
        "outputs": outputs,
        "worked_examples": [],
        "assumptions": [],
        "references": sorted(ref_set),
        "notes": "Auto-extracted by manifest_to_archive.py",
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Convert a DocumentManifest YAML to a dark-intelligence archive YAML."
    )
    parser.add_argument("--input", required=True, help="Path to manifest YAML file.")
    parser.add_argument("--category", required=True, help="Archive category.")
    parser.add_argument("--subcategory", required=True, help="Archive subcategory.")
    parser.add_argument(
        "--output",
        default=None,
        help="Output path for archive YAML. Defaults to stdout.",
    )
    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    manifest_dict = yaml.safe_load(input_path.read_text())
    archive = manifest_to_archive(manifest_dict, args.category, args.subcategory)
    output_yaml = yaml.dump(archive, default_flow_style=False, sort_keys=False)

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        tmp = out_path.with_suffix(".yaml.tmp")
        tmp.write_text(output_yaml)
        os.replace(tmp, out_path)
        print(f"Archive written to {out_path}", file=sys.stderr)
    else:
        print(output_yaml)


if __name__ == "__main__":
    main()
