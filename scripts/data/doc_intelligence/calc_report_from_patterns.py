"""Generate calc-report YAML from detected patterns.

Conforms to config/reporting/calculation-report-schema.yaml.
Lists unique patterns as equations (not per-cell).
"""

from __future__ import annotations

from datetime import date


def _pattern_to_latex(canonical: str) -> str:
    """Convert canonical Excel formula to approximate LaTeX."""
    latex = canonical.lstrip("=")
    latex = latex.replace("*", r" \times ")
    latex = latex.replace("SQRT(", r"\sqrt{").replace(")", "}")
    latex = latex.replace("PI()", r"\pi")
    latex = latex.replace("^", "^")
    return latex


def generate_calc_report_yaml(
    stem: str,
    patterns: dict[str, list[dict]],
    classification: dict,
    formulas: dict,
    domain: str,
    stats: dict,
) -> dict:
    """Generate a calc-report dict from pattern analysis.

    Args:
        stem: Workbook stem name.
        patterns: Canonical formula → list of cells.
        classification: Dict with inputs, outputs, chain.
        formulas: Original formulas dict.
        domain: Engineering domain string.
        stats: Compression statistics dict.

    Returns:
        Dict conforming to calculation-report-schema.yaml.
    """
    # Metadata
    metadata = {
        "title": f"Calculation Report: {stem}",
        "doc_id": f"XLSX-POC-V2-{stem}",
        "revision": 1,
        "date": str(date.today()),
        "author": "xlsx-poc-v2 pipeline",
        "status": "draft",
    }

    # Inputs from classification
    inputs = []
    for ref in classification.get("inputs", [])[:20]:
        inputs.append({
            "name": ref,
            "symbol": ref.lower(),
            "value": "from workbook",
            "unit": "-",
        })

    # Methodology with equations from unique patterns
    equations = []
    for idx, (canonical, cells) in enumerate(patterns.items()):
        equations.append({
            "id": f"EQ-{idx + 1:03d}",
            "name": f"Pattern {idx + 1} ({len(cells)} cells)",
            "latex": _pattern_to_latex(canonical),
            "description": (
                f"Excel: {canonical} — "
                f"applied to {len(cells)} cells in "
                f"{cells[0]['sheet'] if cells else 'unknown'}"
            ),
        })

    methodology = {
        "description": (
            f"Auto-extracted from {stem} workbook. "
            f"Pattern compression: {stats.get('compression_ratio', 0)}x "
            f"({stats.get('total_cells', 0)} cells → "
            f"{stats.get('unique_patterns', 0)} patterns)."
        ),
        "standard": "Workbook-derived calculations",
        "equations": equations,
    }

    # Outputs from classification
    outputs = []
    for ref in classification.get("outputs", [])[:20]:
        outputs.append({
            "name": ref,
            "symbol": ref.lower(),
            "value": "computed",
            "unit": "-",
        })

    assumptions = [
        "All formulas extracted from cached Excel workbook values.",
        f"Domain: {domain}.",
        f"Compression ratio: {stats.get('compression_ratio', 0)}x.",
    ]

    references = [
        f"Source workbook: {stem}",
        "Extraction pipeline: xlsx-poc-v2",
    ]

    return {
        "metadata": metadata,
        "inputs": inputs,
        "methodology": methodology,
        "outputs": outputs,
        "assumptions": assumptions,
        "references": references,
    }
