"""Module-importable entry point for URL-based document extraction.

The CLI script lives at scripts/data/doc-intelligence/extract-url.py.
This module provides the same main() for testability and imports.
"""

import argparse
import sys
import tempfile
from pathlib import Path

from scripts.data.doc_intelligence.fetcher import UrlFetcher
from scripts.data.doc_intelligence.parsers.html import HtmlParser
from scripts.data.doc_intelligence.parsers.pdf import PdfParser
from scripts.data.doc_intelligence.schema import write_manifest
from scripts.data.doc_intelligence.utils import generate_doc_ref_from_url


def _default_output(url: str, domain: str) -> Path:
    """Generate default output path under data/doc-intelligence/manifests/."""
    repo_root = Path(__file__).resolve().parents[3]
    doc_ref = generate_doc_ref_from_url(url)
    return (
        repo_root
        / "data"
        / "doc-intelligence"
        / "manifests"
        / domain
        / f"{doc_ref}.manifest.yaml"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Extract structure from URLs (HTML or PDF)"
    )
    parser.add_argument("--url", required=True, help="URL to fetch and extract")
    parser.add_argument("--output", help="Output manifest YAML path")
    parser.add_argument(
        "--domain", default="general", help="Domain label (default: general)"
    )
    parser.add_argument("--doc-ref", help="Override document reference ID")
    parser.add_argument(
        "--dry-run", action="store_true", help="Parse but do not write manifest"
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Print detailed extraction info"
    )
    parser.add_argument(
        "--no-cache", action="store_true", help="Bypass fetch cache"
    )
    args = parser.parse_args(argv)

    # Fetch
    fetcher = UrlFetcher()
    result = fetcher.fetch(args.url, no_cache=args.no_cache)

    if result is None:
        print(f"Error: blocked by robots.txt: {args.url}", file=sys.stderr)
        return 2

    if result.status_code != 200:
        print(
            f"Error: fetch failed (HTTP {result.status_code}): {args.url}",
            file=sys.stderr,
        )
        return 1

    # Route by content type
    is_pdf = (
        result.content_type == "application/pdf"
        or args.url.lower().endswith(".pdf")
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        if is_pdf:
            tmp_file = Path(tmpdir) / "download.pdf"
            tmp_file.write_bytes(result.content_bytes)
            manifest = PdfParser().parse(str(tmp_file), domain=args.domain)
        else:
            tmp_file = Path(tmpdir) / "download.html"
            tmp_file.write_bytes(result.content_bytes)
            manifest = HtmlParser().parse(
                str(tmp_file), domain=args.domain, source_url=args.url
            )

    # Set extract-url tool identifier
    manifest.tool = "extract-url/1.0.0"

    # Set doc_ref
    title = None
    if manifest.sections:
        first_heading = next(
            (s for s in manifest.sections if s.level > 0), None
        )
        if first_heading:
            title = first_heading.text
    manifest.doc_ref = args.doc_ref or generate_doc_ref_from_url(args.url, title)

    # Check extraction quality
    if manifest.errors and not manifest.sections and not manifest.tables:
        for err in manifest.errors:
            print(f"  Warning: {err}", file=sys.stderr)
        return 3

    # Output
    stats = manifest.extraction_stats
    print(
        f"Extracted: {stats.get('sections', 0)} sections, "
        f"{stats.get('tables', 0)} tables, "
        f"{stats.get('figure_refs', 0)} figure refs"
    )
    if args.verbose:
        print(f"  Format: {manifest.metadata.format}")
        print(f"  Domain: {manifest.domain}")
        print(f"  Doc ref: {manifest.doc_ref}")
        print(f"  Cached: {result.cached}")

    if not args.dry_run:
        output = args.output or str(_default_output(args.url, args.domain))
        write_manifest(manifest, Path(output))
        print(f"Manifest: {output}")

    return 0
