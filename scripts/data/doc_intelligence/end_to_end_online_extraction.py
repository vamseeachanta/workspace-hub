# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml", "beautifulsoup4", "requests"]
# ///
"""Orchestrate the full online extraction pipeline.

Steps:
  1. Crawl seed URLs → discover document URLs
  2. Create fetch queue → process queue (download documents)
  3. Extract content from each downloaded document → manifests
  4. Deduplicate manifests → merged manifest
  5. Optionally produce dark-intelligence archive YAML
"""

import argparse
import sys
from pathlib import Path
from typing import Any

import yaml

from scripts.data.doc_intelligence.crawl_and_enqueue import crawl_seed_urls
from scripts.data.doc_intelligence.deduplicate_manifests import merge_manifests
from scripts.data.doc_intelligence.fetch_queue_manager import create_queue, process_queue
from scripts.data.doc_intelligence.manifest_to_archive import manifest_to_archive
from scripts.data.doc_intelligence.orchestrator import extract_document


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _collect_fetched_files(output_dir: Path) -> list[str]:
    """Return paths to all files downloaded into output_dir (non-recursive YAML queue
    side-effects write raw files per domain sub-directory).

    Collects all non-YAML, non-.tmp files recursively under output_dir.
    """
    result: list[str] = []
    for p in output_dir.rglob("*"):
        if p.is_file() and p.suffix not in (".yaml", ".tmp"):
            result.append(str(p))
    return result


def _manifest_to_dict(manifest) -> dict:
    """Convert a DocumentManifest dataclass/object to a plain dict."""
    if isinstance(manifest, dict):
        return manifest
    if hasattr(manifest, "model_dump"):
        return manifest.model_dump()
    if hasattr(manifest, "__dict__"):
        return manifest.__dict__
    return {}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def run_pipeline(config: dict, fetcher=None) -> dict:
    """Run the full online extraction pipeline.

    Args:
        config: Pipeline configuration dict. Required keys:
            - seed_urls: list[str]
            - allowed_domains: list[str]  (empty = allow all)
            - output_dir: str
            - domain: str
            - deduplicate: bool
            - archive: bool
            - batch_size: int
          Optional keys:
            - category: str  (needed when archive=True)
            - subcategory: str  (needed when archive=True)
        fetcher: Optional UrlFetcher-compatible object for testing (no real calls).

    Returns:
        Report dict with keys:
            urls_found, fetched, extracted, deduplicated, errors
    """
    errors: list[str] = []
    output_dir = Path(config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------ #
    # Step 1: Crawl seed URLs
    # ------------------------------------------------------------------ #
    seed_urls: list[str] = config.get("seed_urls") or []
    allowed_domains: list[str] = config.get("allowed_domains") or []

    try:
        doc_urls = crawl_seed_urls(seed_urls, allowed_domains=allowed_domains, fetcher=fetcher)
    except Exception as exc:
        errors.append(f"crawl_seed_urls failed: {exc}")
        doc_urls = []

    urls_found = len(doc_urls)

    # ------------------------------------------------------------------ #
    # Step 2: Create + process fetch queue
    # ------------------------------------------------------------------ #
    if doc_urls:
        queue_path = output_dir / "fetch.queue.yaml"
        try:
            create_queue(doc_urls, queue_path)
        except Exception as exc:
            errors.append(f"create_queue failed: {exc}")

        try:
            process_queue(
                queue_path=queue_path,
                output_dir=output_dir / "fetched",
                batch_size=config.get("batch_size", 10),
                fetcher=fetcher,
            )
        except Exception as exc:
            errors.append(f"process_queue failed: {exc}")

    # ------------------------------------------------------------------ #
    # Step 3: Collect fetched files and extract content
    # ------------------------------------------------------------------ #
    fetched_files = _collect_fetched_files(output_dir / "fetched")
    fetched_count = len(fetched_files)

    manifests_dir = output_dir / "manifests"
    manifests_dir.mkdir(parents=True, exist_ok=True)
    manifest_dicts: list[dict] = []

    domain = config.get("domain", "")
    for filepath in fetched_files:
        try:
            manifest = extract_document(filepath, domain=domain)
            manifest_dicts.append(_manifest_to_dict(manifest))
        except Exception as exc:
            errors.append(f"extract_document failed for {filepath}: {exc}")

    extracted_count = len(manifest_dicts)

    # ------------------------------------------------------------------ #
    # Step 4: Deduplicate manifests
    # ------------------------------------------------------------------ #
    if config.get("deduplicate", True) and manifest_dicts:
        try:
            merged = merge_manifests(manifest_dicts)
        except Exception as exc:
            errors.append(f"merge_manifests failed: {exc}")
            merged = merge_manifests([])
    else:
        merged = merge_manifests(manifest_dicts)

    deduped_sections = len(merged.get("sections") or [])

    # ------------------------------------------------------------------ #
    # Step 5: Optionally produce dark-intelligence archive
    # ------------------------------------------------------------------ #
    if config.get("archive", False):
        category = config.get("category", "")
        subcategory = config.get("subcategory", "")
        try:
            archive = manifest_to_archive(merged, category=category, subcategory=subcategory)
            archive_path = output_dir / "archive.yaml"
            archive_path.write_text(
                yaml.dump(archive, default_flow_style=False, sort_keys=False)
            )
        except Exception as exc:
            errors.append(f"manifest_to_archive failed: {exc}")

    return {
        "urls_found": urls_found,
        "fetched": fetched_count,
        "extracted": extracted_count,
        "deduplicated": deduped_sections,
        "errors": errors,
    }


def create_pipeline_config(seed_file: str, output_dir: str, **kwargs) -> dict:
    """Build a pipeline config dict from a seed file path and output directory.

    Args:
        seed_file: Path to a plain-text file with one URL per line.
        output_dir: Directory where pipeline outputs are written.
        **kwargs: Optional overrides for any config key
                  (domain, category, subcategory, allowed_domains,
                   deduplicate, archive, batch_size).

    Returns:
        Config dict suitable for run_pipeline().
    """
    seeds_path = Path(seed_file)
    seed_urls = [
        line.strip()
        for line in seeds_path.read_text().splitlines()
        if line.strip()
    ]

    config: dict[str, Any] = {
        "seed_urls": seed_urls,
        "allowed_domains": [],
        "output_dir": output_dir,
        "domain": "",
        "category": "",
        "subcategory": "",
        "deduplicate": True,
        "archive": False,
        "batch_size": 10,
    }
    config.update(kwargs)
    return config


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the full online document extraction pipeline."
    )
    parser.add_argument(
        "--seeds",
        metavar="FILE",
        required=True,
        help="File with seed URLs, one per line",
    )
    parser.add_argument(
        "--output-dir",
        metavar="DIR",
        required=True,
        help="Directory for pipeline outputs",
    )
    parser.add_argument(
        "--domain",
        metavar="DOMAIN",
        default="",
        help="Extraction domain label (e.g. engineering-standards)",
    )
    parser.add_argument(
        "--category",
        metavar="CAT",
        default="",
        help="Archive category (used with --archive)",
    )
    parser.add_argument(
        "--subcategory",
        metavar="SUB",
        default="",
        help="Archive subcategory (used with --archive)",
    )
    parser.add_argument(
        "--allowed-domains",
        metavar="DOMAINS",
        default="",
        help="Comma-separated domain allowlist (empty = allow all)",
    )
    parser.add_argument(
        "--archive",
        action="store_true",
        help="Also produce dark-intelligence YAML archive",
    )
    parser.add_argument(
        "--report",
        metavar="FILE",
        default=None,
        help="Save pipeline report to YAML file",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=10,
        help="Fetch queue batch size (default: 10)",
    )
    return parser


def main() -> None:
    """CLI entry point."""
    parser = _build_parser()
    args = parser.parse_args()

    allowed_domains = (
        [d.strip() for d in args.allowed_domains.split(",") if d.strip()]
        if args.allowed_domains
        else []
    )

    config = create_pipeline_config(
        args.seeds,
        args.output_dir,
        domain=args.domain,
        category=args.category,
        subcategory=args.subcategory,
        allowed_domains=allowed_domains,
        archive=args.archive,
        batch_size=args.batch_size,
    )

    report = run_pipeline(config)

    print(
        f"Pipeline complete: urls_found={report['urls_found']} "
        f"fetched={report['fetched']} extracted={report['extracted']} "
        f"deduplicated={report['deduplicated']} errors={len(report['errors'])}"
    )
    if report["errors"]:
        for err in report["errors"]:
            print(f"  ERROR: {err}", file=sys.stderr)

    if args.report:
        report_path = Path(args.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(
            yaml.dump(report, default_flow_style=False, sort_keys=False)
        )
        print(f"Report written to {args.report}")


if __name__ == "__main__":
    main()
