"""Extraction learner — captures patterns from processed documents to improve skills.

After each document batch, analyzes extraction results to identify:
- New regex patterns for worked example detection
- Domain-specific table structures worth codifying
- Common figure caption formats for better matching
- Parsing failures that suggest skill gaps

Writes learnings to a YAML file that can be fed back into skill improvement.

Usage:
    from scripts.data.doc_intelligence.extraction_learner import (
        capture_extraction_learnings,
    )
    learnings = capture_extraction_learnings(results_batch, domain)
"""

import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import yaml


def capture_extraction_learnings(
    results: list[dict],
    domain: str,
    output_path: Optional[Path] = None,
) -> dict:
    """Analyze a batch of deep extraction results and capture learnings.

    Args:
        results: List of result dicts from deep_extract_manifest.
        domain: Domain label for the batch.
        output_path: If provided, write learnings YAML here.

    Returns:
        Learnings dict with pattern improvements and gap analysis.
    """
    learnings = {
        "domain": domain,
        "captured_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "batch_size": len(results),
        "table_patterns": _analyze_table_patterns(results),
        "example_patterns": _analyze_example_patterns(results),
        "chart_patterns": _analyze_chart_patterns(results),
        "gaps": _identify_gaps(results),
    }

    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            yaml.dump(learnings, f, default_flow_style=False, sort_keys=False)

    return learnings


def _analyze_table_patterns(results: list[dict]) -> dict:
    """Find common table column patterns across documents."""
    column_sets: Counter = Counter()
    table_count = 0

    for r in results:
        for csv_path in r.get("tables", {}).get("csv_paths", []):
            table_count += 1

    return {
        "total_tables": table_count,
        "docs_with_tables": sum(
            1 for r in results if r.get("tables", {}).get("count", 0) > 0
        ),
    }


def _analyze_example_patterns(results: list[dict]) -> dict:
    """Analyze worked example parsing success and failure patterns."""
    total_examples = 0
    examples_with_inputs = 0
    examples_with_units = 0
    input_symbols: Counter = Counter()

    for r in results:
        for ex in r.get("worked_examples", {}).get("examples", []):
            total_examples += 1
            inputs = ex.get("inputs", [])
            if inputs:
                examples_with_inputs += 1
                for inp in inputs:
                    input_symbols[inp["symbol"]] += 1
            if ex.get("output_unit"):
                examples_with_units += 1

    return {
        "total_examples": total_examples,
        "with_inputs": examples_with_inputs,
        "with_units": examples_with_units,
        "common_symbols": dict(input_symbols.most_common(10)),
    }


def _analyze_chart_patterns(results: list[dict]) -> dict:
    """Analyze chart/figure detection patterns."""
    total_refs = 0
    refs_with_images = 0
    caption_patterns: Counter = Counter()

    for r in results:
        for chart in r.get("charts", {}).get("metadata", []):
            total_refs += 1
            if chart.get("image_file"):
                refs_with_images += 1
            caption = chart.get("caption") or ""
            # Classify caption pattern
            if re.search(r"vs\.?|versus", caption, re.IGNORECASE):
                caption_patterns["x_vs_y"] += 1
            elif re.search(r"distribution|histogram", caption, re.IGNORECASE):
                caption_patterns["distribution"] += 1
            elif re.search(r"schematic|diagram", caption, re.IGNORECASE):
                caption_patterns["schematic"] += 1
            else:
                caption_patterns["other"] += 1

    return {
        "total_figure_refs": total_refs,
        "with_extracted_images": refs_with_images,
        "caption_types": dict(caption_patterns),
    }


def _identify_gaps(results: list[dict]) -> list[dict]:
    """Identify extraction gaps worth addressing."""
    gaps = []

    # Check for documents with sections but no worked examples
    docs_with_text_no_examples = sum(
        1 for r in results
        if r.get("worked_examples", {}).get("count", 0) == 0
        and r.get("domain") not in ("general", "unknown")
    )
    if docs_with_text_no_examples > 0:
        gaps.append({
            "type": "worked_example_coverage",
            "description": (
                f"{docs_with_text_no_examples} domain documents had no parseable "
                "worked examples — may need alternate regex patterns"
            ),
            "severity": "medium",
            "suggestion": "Review section text for non-standard example formats",
        })

    # Check for figures without images
    total_refs = sum(
        r.get("charts", {}).get("count", 0) for r in results
    )
    refs_with_images = sum(
        1 for r in results
        for c in r.get("charts", {}).get("metadata", [])
        if c.get("image_file")
    )
    if total_refs > 0 and refs_with_images < total_refs * 0.5:
        gaps.append({
            "type": "image_extraction_coverage",
            "description": (
                f"Only {refs_with_images}/{total_refs} figure refs have "
                "extracted images — may need PyMuPDF for image extraction pass"
            ),
            "severity": "low",
            "suggestion": "Run deep-extract.py with --input (not --manifest) for image extraction",
        })

    return gaps
