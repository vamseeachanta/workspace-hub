#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "pyyaml",
#     "pdfplumber",
# ]
# ///
"""Deep extraction CLI — single-pass extraction + post-processing.

Extracts tables, worked examples, and chart metadata from documents.
Operates on manifests (from extract-document.py) or directly on PDFs.

Usage:
    python deep-extract.py --input <file> [--output-dir <path>] [--domain <domain>]
    python deep-extract.py --manifest <manifest.yaml> [--output-dir <path>]
"""

import argparse
import json
import sys
from pathlib import Path

import yaml

_repo_root = str(Path(__file__).resolve().parents[3])
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)

from scripts.data.doc_intelligence.deep_extract import (
    deep_extract_manifest,
    generate_extraction_report,
)
from scripts.data.doc_intelligence.schema import manifest_to_dict
from scripts.data.doc_intelligence.orchestrator import extract_document


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Deep extraction: tables, worked examples, charts from documents"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--input", help="Path to input document (PDF, DOCX, etc.)")
    group.add_argument("--manifest", help="Path to existing manifest YAML")
    parser.add_argument("--output-dir", default="data/doc-intelligence/deep",
                        help="Output directory for extracted artifacts")
    parser.add_argument("--domain", default="general", help="Domain label")
    parser.add_argument("--report", action="store_true", help="Write extraction report YAML")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    pdf_path = None

    if args.manifest:
        manifest_path = Path(args.manifest)
        if not manifest_path.exists():
            print(f"Error: manifest not found: {args.manifest}", file=sys.stderr)
            return 1
        with open(manifest_path) as f:
            manifest_dict = yaml.safe_load(f)
    else:
        input_path = Path(args.input)
        if not input_path.exists():
            print(f"Error: file not found: {args.input}", file=sys.stderr)
            return 1
        pdf_path = input_path if input_path.suffix.lower() == ".pdf" else None
        manifest = extract_document(str(input_path), domain=args.domain)
        manifest_dict = manifest_to_dict(manifest)

    result = deep_extract_manifest(manifest_dict, output_dir, pdf_path=pdf_path)

    # Print summary
    print(f"Deep extraction: {result['doc_name']} ({result['domain']})")
    print(f"  Tables:          {result['tables']['count']} exported to CSV")
    print(f"  Worked examples: {result['worked_examples']['count']} parsed")
    print(f"  Charts:          {result['charts']['count']} metadata entries")

    if args.verbose:
        for ex in result["worked_examples"]["examples"]:
            inputs_str = ", ".join(
                f"{i['symbol']}={i['value']}" for i in ex.get("inputs", [])
            )
            print(f"    Ex {ex['number']}: {ex['title']} → {ex['expected_value']} "
                  f"[{ex.get('output_unit', '')}] ({inputs_str})")

    if args.report:
        report = generate_extraction_report(result, result["doc_name"])
        report_path = output_dir / f"{result['doc_name']}-extraction-report.yaml"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, "w") as f:
            yaml.dump(report, f, default_flow_style=False, sort_keys=False)
        print(f"  Report:          {report_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
