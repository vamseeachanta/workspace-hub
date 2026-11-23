#!/usr/bin/env python3
# ABOUTME: Batch deep extraction for naval architecture manifests (WRK-1293)
# ABOUTME: Processes all manifests without extraction reports, writes YAML reports + CSV tables

"""
Usage:
    uv run --no-project python scripts/data/doc_intelligence/batch_deep_extract_naval.py \
        [--dry-run] [--limit N] [--manifest NAME]
"""

import argparse
import logging
import os
import sys
from pathlib import Path

import yaml

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

HUB_ROOT = Path(__file__).resolve().parents[3]
MANIFESTS_DIR = HUB_ROOT / "data/doc-intelligence/manifests/naval-architecture"
REPORTS_DIR = HUB_ROOT / "data/doc-intelligence/extraction-reports/naval-architecture"
OUTPUT_DIR = REPORTS_DIR  # tables/ and charts/ subdirs created under here

sys.path.insert(0, str(HUB_ROOT))
from scripts.data.doc_intelligence.deep_extract import (
    deep_extract_manifest,
    generate_extraction_report,
)


def load_manifest(manifest_path: Path) -> dict:
    """Load a manifest YAML and return as dict."""
    with open(manifest_path) as f:
        return yaml.safe_load(f) or {}


def get_pending_manifests(specific: str | None = None) -> list[Path]:
    """Find manifests that don't have extraction reports yet."""
    done = set()
    if REPORTS_DIR.exists():
        for f in REPORTS_DIR.iterdir():
            if f.name.endswith("-extraction-report.yaml"):
                done.add(f.name.replace("-extraction-report.yaml", ""))

    pending = []
    for f in sorted(MANIFESTS_DIR.iterdir()):
        if not f.name.endswith(".manifest.yaml"):
            continue
        name = f.name.replace(".manifest.yaml", "")
        if specific and name != specific:
            continue
        if name not in done:
            pending.append(f)
    return pending


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Batch deep extraction for naval architecture (WRK-1293)"
    )
    parser.add_argument("--dry-run", action="store_true", help="List pending only")
    parser.add_argument("--limit", type=int, default=0, help="Max manifests to process")
    parser.add_argument("--manifest", help="Process only this manifest name")
    args = parser.parse_args()

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    pending = get_pending_manifests(specific=args.manifest)
    logger.info("Pending manifests: %d", len(pending))

    if args.dry_run:
        for p in pending:
            print(f"  [PENDING] {p.stem}")
        return 0

    if args.limit:
        pending = pending[: args.limit]

    processed = 0
    errors = 0
    total_tables = 0
    total_examples = 0

    for manifest_path in pending:
        name = manifest_path.stem.replace(".manifest", "")
        logger.info("Processing: %s (%d/%d)", name, processed + 1, len(pending))

        try:
            manifest = load_manifest(manifest_path)
            if not manifest:
                logger.warning("Empty manifest: %s", name)
                errors += 1
                continue

            result = deep_extract_manifest(manifest, OUTPUT_DIR)
            report = generate_extraction_report(result, name)

            report_path = REPORTS_DIR / f"{name}-extraction-report.yaml"
            with open(report_path, "w") as f:
                yaml.dump(report, f, default_flow_style=False, allow_unicode=True)

            tables = result["tables"]["count"]
            examples = result["worked_examples"]["count"]
            total_tables += tables
            total_examples += examples

            logger.info(
                "  Done: %d tables, %d worked examples", tables, examples
            )
            processed += 1

        except Exception as e:
            logger.error("Failed %s: %s", name, e)
            errors += 1

    logger.info(
        "Batch complete: %d processed, %d errors, %d tables, %d worked examples",
        processed, errors, total_tables, total_examples,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
