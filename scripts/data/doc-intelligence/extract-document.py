#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "pyyaml",
#     "pdfplumber",
#     "python-docx",
#     "openpyxl",
# ]
# ///
"""CLI entry point for document extraction.

Usage:
    python extract-document.py --input <file> [--output <path>] [--domain <domain>]
"""

import argparse
import sys
from pathlib import Path

# Ensure repo root is on PYTHONPATH when run directly
_repo_root = str(Path(__file__).resolve().parents[3])
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)

from scripts.data.doc_intelligence.orchestrator import extract_document
from scripts.data.doc_intelligence.schema import write_manifest


def _default_output(input_path: str, domain: str) -> Path:
    """Generate default output path under data/doc-intelligence/manifests/."""
    repo_root = Path(__file__).resolve().parents[3]
    name = Path(input_path).stem
    return repo_root / "data" / "doc-intelligence" / "manifests" / domain / f"{name}.manifest.yaml"


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract structure from documents")
    parser.add_argument("--input", required=True, help="Path to input document")
    parser.add_argument("--output", help="Output manifest YAML path")
    parser.add_argument("--domain", default="general", help="Domain label (default: general)")
    parser.add_argument("--doc-ref", help="Override document reference ID")
    parser.add_argument("--dry-run", action="store_true", help="Parse but do not write manifest")
    parser.add_argument("--verbose", action="store_true", help="Print detailed extraction info")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: file not found: {args.input}", file=sys.stderr)
        return 1

    # Check for unsupported format before full extraction
    from scripts.data.doc_intelligence.parsers import get_parser as _get_parser

    if _get_parser(str(input_path)) is None:
        print(f"Error: unsupported format: {input_path.suffix}", file=sys.stderr)
        return 2

    output = None if args.dry_run else (args.output or str(_default_output(args.input, args.domain)))

    manifest = extract_document(
        str(input_path), domain=args.domain, output=output, doc_ref=args.doc_ref,
    )

    if manifest.errors:
        for err in manifest.errors:
            print(f"  Warning: {err}", file=sys.stderr)
        if not manifest.sections and not manifest.tables:
            return 3

    stats = manifest.extraction_stats
    print(f"Extracted: {stats.get('sections', 0)} sections, "
          f"{stats.get('tables', 0)} tables, "
          f"{stats.get('figure_refs', 0)} figure refs")
    if args.verbose:
        print(f"  Format: {manifest.metadata.format}")
        print(f"  Domain: {manifest.domain}")
        if manifest.doc_ref:
            print(f"  Doc ref: {manifest.doc_ref}")
        if manifest.metadata.pages:
            print(f"  Pages: {manifest.metadata.pages}")
    if output:
        print(f"Manifest: {output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
