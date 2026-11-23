#!/usr/bin/env python3
"""Evaluate docling document parsing library.

Converts sample documents to Markdown/JSON, displays structured output,
and measures conversion time.

Usage:
    uv run --extra docling python scripts/integrations/docling_evaluation.py
    uv run --extra docling python scripts/integrations/docling_evaluation.py /path/to/file.pdf

Issue: #1446
"""

import sys
import time
from pathlib import Path
from textwrap import dedent

from docling.document_converter import DocumentConverter


def create_sample_html(tmp_dir: Path) -> Path:
    """Create a sample HTML document for evaluation."""
    p = tmp_dir / "docling_eval_sample.html"
    p.write_text(
        dedent("""\
        <!DOCTYPE html>
        <html><head><title>Docling Evaluation Document</title></head>
        <body>
        <h1>Docling Evaluation</h1>
        <p>This document tests docling's ability to parse structured content.</p>

        <h2>1. Pipe Stress Analysis Summary</h2>
        <p>The following table summarizes pipe stress results for the main process loop.</p>
        <table>
          <tr><th>Node</th><th>Stress (MPa)</th><th>Allowable (MPa)</th><th>Ratio</th></tr>
          <tr><td>N100</td><td>125.3</td><td>137.9</td><td>0.91</td></tr>
          <tr><td>N200</td><td>98.7</td><td>137.9</td><td>0.72</td></tr>
          <tr><td>N300</td><td>142.1</td><td>206.8</td><td>0.69</td></tr>
        </table>

        <h2>2. Equipment List</h2>
        <ul>
          <li><strong>V-101</strong> — Separator vessel, 3.0m ID x 9.0m T/T</li>
          <li><strong>P-201A/B</strong> — Centrifugal pump, 150 kW</li>
          <li><strong>E-301</strong> — Shell &amp; tube heat exchanger, 500 m²</li>
        </ul>

        <h2>3. Conclusions</h2>
        <p>All stress ratios are within allowable limits. The design is acceptable per
        ASME B31.3.</p>
        </body></html>
        """),
        encoding="utf-8",
    )
    return p


def evaluate_document(converter: DocumentConverter, source: str) -> dict:
    """Convert a document and return evaluation metrics."""
    print(f"\n{'='*60}")
    print(f"Converting: {source}")
    print(f"{'='*60}")

    start = time.monotonic()
    result = converter.convert(source)
    elapsed = time.monotonic() - start

    md = result.document.export_to_markdown()
    doc_dict = result.document.export_to_dict()

    print(f"\n--- Markdown Output ({len(md)} chars) ---")
    print(md[:2000])
    if len(md) > 2000:
        print(f"\n... ({len(md) - 2000} more chars)")

    print(f"\n--- Structured Dict Keys ---")
    print(f"Top-level keys: {list(doc_dict.keys())}")

    # Count structural elements in dict
    texts = doc_dict.get("texts", doc_dict.get("body", []))
    if isinstance(texts, list):
        print(f"Text elements: {len(texts)}")

    tables = doc_dict.get("tables", [])
    if isinstance(tables, list):
        print(f"Tables: {len(tables)}")

    print(f"\n--- Metrics ---")
    print(f"Conversion time: {elapsed:.2f}s")
    print(f"Markdown length: {len(md)} chars")
    print(f"Markdown lines:  {md.count(chr(10))}")

    return {
        "source": source,
        "elapsed_s": round(elapsed, 2),
        "md_chars": len(md),
        "md_lines": md.count("\n"),
        "dict_keys": list(doc_dict.keys()),
    }


def main():
    import tempfile

    print("Docling Evaluation Script")
    print(f"docling version: {docling_version()}")

    converter = DocumentConverter()
    results = []

    # Evaluate user-provided file or built-in sample
    if len(sys.argv) > 1:
        for path in sys.argv[1:]:
            if Path(path).exists():
                results.append(evaluate_document(converter, path))
            else:
                print(f"WARNING: File not found: {path}")
    else:
        with tempfile.TemporaryDirectory() as tmp:
            sample = create_sample_html(Path(tmp))
            results.append(evaluate_document(converter, str(sample)))

    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    for r in results:
        print(f"  {Path(r['source']).name}: {r['elapsed_s']}s, "
              f"{r['md_chars']} chars, {r['md_lines']} lines")


def docling_version() -> str:
    try:
        from importlib.metadata import version
        return version("docling")
    except Exception:
        return "unknown"


if __name__ == "__main__":
    main()
