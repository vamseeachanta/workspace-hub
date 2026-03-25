"""Deep extraction — post-processes a manifest to extract tables, worked examples, charts.

Operates on manifest data (already extracted by parsers/pdf.py in a single pass).
This module chains the three post-processors:
1. Table exporter — manifest tables → CSV files
2. Worked example parser — section text → enhanced parsed examples
3. Chart metadata generator — figure refs → calibration metadata

Usage:
    from scripts.data.doc_intelligence.deep_extract import deep_extract_manifest
    result = deep_extract_manifest(manifest_dict, output_dir)
"""

from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from scripts.data.doc_intelligence.chart_extractor import (
    generate_chart_metadata,
)
from scripts.data.doc_intelligence.table_exporter import (
    export_tables_from_manifest,
)
from scripts.data.doc_intelligence.naval_example_parsers import (
    parse_examples_multi_format,
)
from scripts.data.doc_intelligence.worked_example_parser import (
    parse_enhanced_example,
)


def deep_extract_manifest(
    manifest_dict: dict,
    output_dir: Path,
    pdf_path: Optional[Path] = None,
) -> dict:
    """Run all post-processors on a manifest.

    Args:
        manifest_dict: Manifest as produced by manifest_to_dict.
        output_dir: Root output directory for extracted artifacts.
        pdf_path: Optional path to source PDF for image extraction.

    Returns:
        Dict with results from each post-processor.
    """
    output_dir = Path(output_dir)
    domain = manifest_dict.get("domain", "general")
    doc_name = Path(manifest_dict["metadata"]["filename"]).stem

    # 1. Table export
    tables_dir = output_dir / "tables"
    table_result = export_tables_from_manifest(manifest_dict, tables_dir)

    # 2. Worked example parsing — try multi-format first, fall back to legacy
    #    Uses sliding window to catch examples that span page boundaries.
    sections = manifest_dict.get("sections", [])
    examples = []
    seen_keys: set[tuple] = set()  # (source_book, number, page) for dedup

    def _add_example(ex: dict) -> None:
        """Add example if not already seen (deduplication by key)."""
        key = (
            ex.get("source_book", ""),
            ex.get("number", ""),
            ex.get("page", 0),
        )
        if key not in seen_keys:
            seen_keys.add(key)
            examples.append(ex)

    # Pass 1: individual sections (original behavior)
    for section in sections:
        text = section.get("text", "")
        source = section.get("source", {})
        multi = parse_examples_multi_format(text, source, domain)
        if multi:
            for ex in multi:
                _add_example(ex)
        else:
            parsed = parse_enhanced_example(text, domain=domain, source=source)
            if parsed:
                _add_example(parsed)

    # Pass 2: sliding window (concatenate adjacent sections to catch
    # examples where "Example N.N" is on one page and "Solution" on the next)
    window_size = 3
    for i in range(len(sections) - 1):
        window = sections[i : i + window_size]
        combined_text = "\n\n".join(s.get("text", "") for s in window)
        first_source = window[0].get("source", {})
        multi = parse_examples_multi_format(combined_text, first_source, domain)
        if multi:
            for ex in multi:
                _add_example(ex)
        else:
            parsed = parse_enhanced_example(
                combined_text, domain=domain, source=first_source
            )
            if parsed:
                _add_example(parsed)

    # 3. Chart metadata (image extraction only if pdf_path provided)
    figure_refs = manifest_dict.get("figure_refs", [])
    images = []
    if pdf_path:
        from scripts.data.doc_intelligence.chart_extractor import (
            extract_images_from_pdf,
        )
        charts_dir = output_dir / "charts" / domain
        images = extract_images_from_pdf(pdf_path, charts_dir)

    chart_metadata = generate_chart_metadata(
        figure_refs=figure_refs,
        images=images,
        doc_name=doc_name,
        domain=domain,
    )

    return {
        "domain": domain,
        "doc_name": doc_name,
        "tables": {
            "count": table_result["tables_exported"],
            "csv_paths": table_result["csv_paths"],
        },
        "worked_examples": {
            "count": len(examples),
            "examples": examples,
        },
        "charts": {
            "count": len(chart_metadata),
            "metadata": chart_metadata,
        },
    }


def generate_extraction_report(result: dict, doc_name: str) -> dict:
    """Generate a summary report dict for the extraction run.

    Suitable for YAML serialization as extraction-report.yaml.
    """
    return {
        "document": doc_name,
        "extracted_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "summary": {
            "tables": result["tables"]["count"],
            "worked_examples": result["worked_examples"]["count"],
            "charts": result["charts"]["count"],
        },
        "tables": {
            "csv_paths": result["tables"]["csv_paths"],
        },
        "worked_examples": [
            {
                "number": ex["number"],
                "title": ex["title"],
                "expected_value": ex["expected_value"],
                "output_unit": ex.get("output_unit", ""),
                "input_count": len(ex.get("inputs", [])),
            }
            for ex in result["worked_examples"]["examples"]
        ],
        "charts": [
            {
                "figure_id": c.get("figure_id"),
                "caption": c.get("caption"),
                "image_file": c.get("image_file"),
                "digitized": c.get("digitized", False),
            }
            for c in result["charts"]["metadata"]
        ],
    }
