"""Convert dark-intelligence archive.yaml → calc-report.yaml (WRK-1247).

Transforms the auto-extracted archive format into the calculation-report
schema expected by scripts/reporting/generate-calc-report.py.

Usage:
    uv run --no-project python scripts/data/doc_intelligence/archive_to_calc_report.py <archive.yaml> [--output <path>]
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Any

import yaml


def excel_formula_to_latex(formula: str) -> str:
    """Convert an Excel formula string to approximate LaTeX notation."""
    if not formula:
        return ""

    # Strip leading =
    expr = formula.lstrip("=").strip()
    if not expr:
        return ""

    # SQRT(x) → \sqrt{x}
    expr = re.sub(r"SQRT\(([^)]+)\)", r"\\sqrt{\1}", expr, flags=re.IGNORECASE)

    # SUM(x) → \sum x
    expr = re.sub(r"SUM\(([^)]+)\)", r"\\sum{\1}", expr, flags=re.IGNORECASE)

    # ABS(x) → |x|
    expr = re.sub(r"ABS\(([^)]+)\)", r"|\1|", expr, flags=re.IGNORECASE)

    # x^n → x^{n}
    expr = re.sub(r"\^(\d+)", r"^{\1}", expr)
    expr = re.sub(r"\^([A-Za-z]\w*)", r"^{\1}", expr)

    # PI() → \pi
    expr = re.sub(r"PI\(\)", r"\\pi", expr, flags=re.IGNORECASE)

    # a*b → a \cdot b (but not inside function args)
    expr = expr.replace("*", " \\cdot ")

    # Simple a/b → \frac{a}{b} only for simple cases
    # For complex expressions, leave as /
    simple_div = re.match(r"^([^/]+)/([^/]+)$", expr)
    if simple_div and "(" not in expr:
        expr = f"\\frac{{{simple_div.group(1).strip()}}}{{{simple_div.group(2).strip()}}}"

    return expr


def _title_from_subcategory(subcategory: str) -> str:
    """Convert kebab-case subcategory to title case."""
    return subcategory.replace("-", " ").title()


def _doc_id_from_subcategory(subcategory: str) -> str:
    """Generate a doc_id from the subcategory."""
    # Take first meaningful segment, uppercase
    parts = subcategory.split("-")
    prefix = "".join(p[:4].upper() for p in parts[:3] if p)
    return f"XLSX-{prefix}"


def convert_archive_to_calc_report(archive: dict, max_equations: int = 100) -> dict:
    """Convert a dark-intelligence archive dict to calc-report schema dict.

    Args:
        archive: Dark-intelligence archive dict.
        max_equations: Cap equations in the report (large files may have 600K+).
    """
    subcategory = archive.get("subcategory", "unknown")
    category = archive.get("category", "unknown")
    extracted_date = archive.get("extracted_date", "2026-01-01")

    # ── Metadata ──────────────────────────────────────────────────────
    metadata = {
        "title": _title_from_subcategory(subcategory),
        "doc_id": _doc_id_from_subcategory(subcategory),
        "revision": 1,
        "date": extracted_date,
        "author": "XLSX Auto-Extraction (WRK-1247)",
        "status": "draft",
    }

    # ── Inputs ────────────────────────────────────────────────────────
    raw_inputs = archive.get("inputs", [])
    if raw_inputs:
        inputs = [
            {
                "name": inp.get("name", "unknown"),
                "symbol": inp.get("symbol", inp.get("name", "x")),
                "value": inp.get("test_value", 0),
                "unit": inp.get("unit", ""),
            }
            for inp in raw_inputs
        ]
    else:
        inputs = [
            {
                "name": "No inputs extracted",
                "symbol": "-",
                "value": 0,
                "unit": "-",
            }
        ]

    # ── Methodology ───────────────────────────────────────────────────
    raw_equations = archive.get("equations", [])
    if raw_equations:
        # Cap equations for report readability (large files may have 600K+)
        capped = raw_equations[:max_equations]
        equations = []
        for i, eq in enumerate(capped, 1):
            excel_formula = eq.get("excel_formula", "")
            latex = eq.get("latex", "") or excel_formula_to_latex(excel_formula)
            equations.append({
                "id": f"eq{i}",
                "name": eq.get("name", f"Equation {i}"),
                "latex": latex if latex else f"\\text{{{eq.get('name', 'N/A')}}}",
                "description": eq.get("description", f"Excel: {excel_formula}"),
            })
    else:
        equations = [
            {
                "id": "eq1",
                "name": "No equations extracted",
                "latex": "\\text{No formulas found in source spreadsheet}",
                "description": "Source file contained no formula cells",
            }
        ]

    # Derive standard from references or category
    refs = archive.get("references", [])
    standard = refs[0] if refs else f"Excel calculation ({category})"

    methodology = {
        "description": archive.get("source_description",
                                    f"Engineering calculation from Excel ({category})"),
        "standard": standard,
        "equations": equations,
    }

    # ── Outputs ───────────────────────────────────────────────────────
    raw_outputs = archive.get("outputs", [])
    outputs = []
    for out in raw_outputs:
        val = out.get("test_expected")
        # Skip Excel error values
        if isinstance(val, str) and val.startswith("#"):
            continue
        outputs.append({
            "name": out.get("name", "unknown"),
            "symbol": out.get("symbol", out.get("name", "y")),
            "value": val if val is not None else 0,
            "unit": out.get("unit", ""),
        })
    if not outputs:
        outputs = [
            {
                "name": "No outputs extracted",
                "symbol": "-",
                "value": 0,
                "unit": "-",
                "notes": "No valid output cells with cached values found",
            }
        ]

    # ── Assumptions & References ──────────────────────────────────────
    assumptions = archive.get("assumptions", [])
    if not assumptions:
        assumptions = ["Auto-extracted from Excel — assumptions not captured"]

    references = archive.get("references", [])
    if not references:
        references = [f"Source spreadsheet: {subcategory}"]

    return {
        "metadata": metadata,
        "inputs": inputs,
        "methodology": methodology,
        "outputs": outputs,
        "assumptions": assumptions,
        "references": references,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Convert archive.yaml to calc-report.yaml"
    )
    parser.add_argument("input", help="Path to archive.yaml")
    parser.add_argument("--output", help="Output path (default: sibling calc-report.yaml)")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: {input_path} not found", file=sys.stderr)
        sys.exit(1)

    # Warn on very large files (>50MB) — YAML loading will be slow
    size_mb = input_path.stat().st_size / (1024 * 1024)
    if size_mb > 50:
        print(f"WARNING: Large archive ({size_mb:.0f} MB) — loading may take time",
              file=sys.stderr)

    with open(input_path) as f:
        archive = yaml.safe_load(f)

    result = convert_archive_to_calc_report(archive)

    output_path = args.output or str(input_path.parent / "calc-report.yaml")
    with open(output_path, "w") as f:
        yaml.dump(result, f, default_flow_style=False, sort_keys=False,
                  allow_unicode=True)

    print(f"Generated: {output_path}")


if __name__ == "__main__":
    main()
