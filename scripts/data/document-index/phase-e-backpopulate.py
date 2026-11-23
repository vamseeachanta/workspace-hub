#!/usr/bin/env python3
# ABOUTME: Phase E back-populate — write domain/target_repos/status into index.jsonl (WRK-309)
# ABOUTME: Streams 945K records; uses path/org/doc_number heuristics (no summary I/O) for speed

"""
Back-populates domain, target_repos, and status fields into index.jsonl using the same
classify_heuristic logic from phase-c-classify.py, but without loading summaries.

This is required because Phase C only wrote results to enhancement-plan.yaml and never
back-populated the index. query-docs.sh needs domain/target_repos/status to be non-null.

Usage:
    uv run --no-project python scripts/data/document-index/phase-e-backpopulate.py
    uv run --no-project python scripts/data/document-index/phase-e-backpopulate.py --dry-run
    uv run --no-project python scripts/data/document-index/phase-e-backpopulate.py --limit 1000
"""

import argparse
import json
import logging
import os
import sys
import tempfile
from pathlib import Path
from typing import Dict, List, Tuple

import yaml

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

SCRIPT_DIR = Path(__file__).resolve().parent
HUB_ROOT = SCRIPT_DIR.parents[2]
DEFAULT_CONFIG = SCRIPT_DIR / "config.yaml"

VALID_DOMAINS = [
    "structural", "cathodic-protection", "pipeline", "marine",
    "installation", "energy-economics", "portfolio", "materials",
    "regulatory", "cad", "workspace-spec", "other",
]

DOMAIN_KEYWORDS: Dict[str, List[str]] = {
    "structural": [
        "fatigue", "s-n curve", "stress", "structural", "jacket",
        "topside", "iso 19902", "api rp 2a", "eurocode", "weld",
    ],
    "cathodic-protection": [
        "cathodic", "anode", "cp design", "dnv-rp-b401",
        "dnv-rp-f103", "corrosion", "sacrificial",
    ],
    "pipeline": [
        "pipeline", "dnv-st-f101", "api rp 1111", "riser",
        "flowline", "buckle", "on-bottom stability", "dnv-rp-f109",
    ],
    "marine": [
        "mooring", "calm buoy", "hydrodynamic", "wave", "orcaflex",
        "vessel", "rao", "motion",
    ],
    "installation": [
        "installation", "lay", "j-lay", "s-lay", "reel",
        "umbilical", "weather window", "tensioner",
    ],
    "energy-economics": [
        "bsee", "eia", "production forecast", "decline curve",
        "npv", "economics", "field development",
    ],
    "portfolio": [
        "portfolio", "stock", "yfinance", "sharpe", "var",
        "option", "covered call",
    ],
    "materials": [
        "composite", "laminate", "aluminium", "clt", "eurocode 9",
    ],
    "regulatory": [
        "imo", "uscg", "misle", "maib", "ntsb", "regulation",
    ],
    "cad": ["dwg", "dxf", "3d model", "autocad", "iges", "step"],
}


def load_config(config_path: Path) -> Dict:
    with open(config_path) as f:
        return yaml.safe_load(f)


def classify(record: Dict) -> Tuple[str, str]:
    """Return (domain, status) using fast heuristics only — no summary I/O."""
    source = record.get("source", "")
    if source == "api_metadata":
        return "energy-economics", "data_source"
    if source == "workspace_spec":
        return "workspace-spec", "reference"
    if record.get("is_cad"):
        return "cad", "reference"

    searchable = " ".join([
        str(record.get("path", "")),
        str(record.get("org", "") or ""),
        str(record.get("doc_number", "") or ""),
    ]).lower()

    scores: Dict[str, int] = {}
    for domain, keywords in DOMAIN_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in searchable)
        if score > 0:
            scores[domain] = score

    domain = max(scores, key=lambda k: scores[k]) if scores else "other"
    return domain, "gap"


def map_to_repos(domain: str, repo_domain_map: Dict) -> List[str]:
    return sorted(
        repo for repo, domains in repo_domain_map.items()
        if domain in domains
    )


def backpopulate_index(
    index_path: Path,
    repo_domain_map: Dict[str, List[str]],
    *,
    limit: int = 0,
    dry_run: bool = False,
    classify_fn=None,
) -> Dict[str, int]:
    """Stream index.jsonl, back-populate domain/status/target_repos for records
    that lack them. Enriched fields (content_type, summary_done) survive by
    design — the rec dict is read, mutated in place, and re-emitted (#1878).

    Returns a report dict with processed/already_populated/domain_counts.
    """
    classify_fn = classify_fn or classify
    domain_counts: Dict[str, int] = {}
    already_populated = 0
    processed = 0

    if dry_run:
        with open(index_path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if rec.get("domain") is not None:
                    already_populated += 1
                domain, _ = classify_fn(rec)
                domain_counts[domain] = domain_counts.get(domain, 0) + 1
                processed += 1
                if limit and processed >= limit:
                    break
        return {
            "processed": processed,
            "already_populated": already_populated,
            "domain_counts": domain_counts,
        }

    tmp_fd, tmp_path = tempfile.mkstemp(
        dir=index_path.parent, prefix=".backpop-", suffix=".jsonl"
    )
    try:
        with os.fdopen(tmp_fd, "w") as out_f, open(index_path) as in_f:
            for line in in_f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    continue

                if rec.get("domain") is None:
                    domain, status = classify_fn(rec)
                    repos = map_to_repos(domain, repo_domain_map)
                    rec["domain"] = domain
                    rec["status"] = status
                    rec["target_repos"] = repos
                else:
                    domain = rec["domain"]
                    if not rec.get("target_repos"):
                        rec["target_repos"] = map_to_repos(domain, repo_domain_map)

                domain_counts[domain] = domain_counts.get(domain, 0) + 1
                out_f.write(json.dumps(rec) + "\n")
                processed += 1

                if limit and processed >= limit:
                    break

        os.replace(tmp_path, index_path)
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise

    return {
        "processed": processed,
        "already_populated": already_populated,
        "domain_counts": domain_counts,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Phase E back-populate (WRK-309)")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--limit", type=int, default=0, help="Max records (0=all)")
    parser.add_argument("--dry-run", action="store_true", help="Count only, no write")
    args = parser.parse_args()

    cfg = load_config(args.config)
    index_path = HUB_ROOT / cfg["output"]["index_path"]
    repo_domain_map = cfg.get("repo_domain_map", {})

    if not index_path.exists():
        logger.error("Index not found: %s", index_path)
        return 1

    logger.info("Back-populating domain/target_repos/status in %s", index_path)

    try:
        report = backpopulate_index(
            index_path=index_path,
            repo_domain_map=repo_domain_map,
            limit=args.limit,
            dry_run=args.dry_run,
        )
    except Exception as exc:
        logger.error("Failed: %s", exc)
        return 1

    processed = report["processed"]
    domain_counts = report["domain_counts"]
    already_populated = report["already_populated"]

    if args.dry_run:
        logger.info("Dry-run complete: %d records", processed)
        logger.info("Already populated: %d", already_populated)
    else:
        logger.info("Back-population complete: %d records updated", processed)
    for d, c in sorted(domain_counts.items(), key=lambda x: -x[1]):
        logger.info("  %-25s %d", d, c)
    return 0


if __name__ == "__main__":
    sys.exit(main())
