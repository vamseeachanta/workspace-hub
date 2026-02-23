#!/usr/bin/env python3
# ABOUTME: Phase D — Generate per-repo data-source YAML specs from enhancement plan (WRK-309)
# ABOUTME: Legal-gated; sanitizes paths before writing to specs/data-sources/<repo>.yaml

"""
Usage:
    python phase-d-data-sources.py [--config config.yaml] [--repo REPO] [--skip-legal]
"""

import argparse
import json
import logging
import re
import subprocess
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

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
LEGAL_SCAN = HUB_ROOT / "scripts" / "legal" / "legal-sanity-scan.sh"

TIER_1_REPOS = ["digitalmodel", "worldenergydata", "assethold"]
TIER_2_REPOS = ["doris", "OGManufacturing", "saipem", "rock-oil-field", "acma-projects"]


def load_config(config_path: Path) -> Dict[str, Any]:
    """Load pipeline configuration from YAML."""
    with open(config_path) as f:
        return yaml.safe_load(f)


def load_enhancement_plan(plan_path: Path) -> Dict[str, Any]:
    """Load enhancement plan from Phase C. Fail if absent."""
    if not plan_path.exists():
        logger.error("Enhancement plan not found: %s", plan_path)
        logger.error("Run phase-c-classify.py first.")
        sys.exit(1)
    with open(plan_path) as f:
        return yaml.safe_load(f) or {}


def load_deny_list() -> List[str]:
    """Load legal deny-list patterns from workspace root."""
    deny_path = HUB_ROOT / ".legal-deny-list.yaml"
    if not deny_path.exists():
        return []
    with open(deny_path) as f:
        data = yaml.safe_load(f) or {}
    patterns: List[str] = []
    for entry in data.get("patterns", []):
        if isinstance(entry, dict):
            patterns.append(entry.get("pattern", ""))
        elif isinstance(entry, str):
            patterns.append(entry)
    return [p for p in patterns if p]


def load_index(index_path: Path) -> Dict[str, Dict]:
    """Load index records keyed by path."""
    records: Dict[str, Dict] = {}
    if not index_path.exists():
        return records
    with open(index_path) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    rec = json.loads(line)
                    records[rec["path"]] = rec
                except (json.JSONDecodeError, KeyError):
                    continue
    return records


def sanitize_text(text: str, deny_patterns: List[str]) -> str:
    """Remove or redact client-specific identifiers."""
    sanitized = text
    for pattern in deny_patterns:
        sanitized = re.sub(
            re.escape(pattern), "[REDACTED]", sanitized, flags=re.IGNORECASE
        )
    return sanitized


def collect_repo_items(
    plan: Dict, repo: str, domain_map: Dict, index_records: Dict,
) -> Dict[str, List]:
    """Collect standards, APIs, and gaps for a repo from the plan."""
    repo_domains = domain_map.get(repo, [])
    standards: List[Dict] = []
    apis: List[Dict] = []
    gaps: List[Dict] = []

    for domain_name, domain_data in plan.get("by_domain", {}).items():
        if domain_name not in repo_domains:
            continue
        for item in domain_data.get("items", []):
            idx_rec = index_records.get(item.get("path", ""), {})
            entry = {
                "id": item.get("doc_number", ""),
                "title": item.get("title", ""),
                "org": idx_rec.get("org", ""),
                "index_ref": idx_rec.get("content_hash", ""),
                "status": item.get("status", "reference"),
                "domain": domain_name,
                "notes": item.get("notes", ""),
            }

            status = item.get("status", "reference")
            if status == "gap":
                gaps.append(entry)
            elif status == "data_source":
                apis.append(entry)
            else:
                standards.append(entry)

    return {"standards": standards, "apis": apis, "gaps": gaps}


def write_repo_yaml(
    output_dir: Path, repo: str, items: Dict, deny_patterns: List[str],
) -> None:
    """Write a single repo data-source YAML spec."""
    for section in ("standards", "apis", "gaps"):
        for item in items.get(section, []):
            for key in ("title", "notes"):
                if key in item and item[key]:
                    item[key] = sanitize_text(item[key], deny_patterns)

    spec = {
        "repo": repo,
        "generated": datetime.now().strftime("%Y-%m-%d"),
        "standards": items["standards"],
        "apis": items["apis"],
        "gaps": items["gaps"],
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / f"{repo}.yaml"
    with open(out_path, "w") as f:
        yaml.dump(spec, f, default_flow_style=False, sort_keys=False, width=120)
    logger.info(
        "Wrote %s (%d standards, %d gaps, %d apis)",
        out_path, len(spec["standards"]), len(spec["gaps"]), len(spec["apis"]),
    )


def run_legal_scan(target: Path) -> bool:
    """Run legal-sanity-scan.sh on directory or file."""
    if not LEGAL_SCAN.exists():
        logger.warning("Legal scan script not found: %s", LEGAL_SCAN)
        return True
    try:
        result = subprocess.run(
            ["bash", str(LEGAL_SCAN), str(target)],
            capture_output=True, text=True, timeout=120,
        )
        if result.returncode != 0:
            logger.error("Legal scan FAILED:\n%s", result.stdout or result.stderr)
            return False
        logger.info("Legal scan passed")
        return True
    except (subprocess.TimeoutExpired, OSError) as exc:
        logger.error("Legal scan error: %s", exc)
        return False


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Phase D: Per-repo data-source specs (WRK-309)"
    )
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--repo", help="Process only this repo")
    parser.add_argument("--skip-legal", action="store_true", help="Skip legal scan (dev only)")
    args = parser.parse_args()

    cfg = load_config(args.config)
    plan_path = HUB_ROOT / cfg["output"]["enhancement_plan"]
    index_path = HUB_ROOT / cfg["output"]["index_path"]
    output_dir = HUB_ROOT / "specs" / "data-sources"

    plan = load_enhancement_plan(plan_path)
    deny_patterns = load_deny_list()
    domain_map = cfg.get("repo_domain_map", {})
    index_records = load_index(index_path)

    repos = TIER_1_REPOS + TIER_2_REPOS
    if args.repo:
        if args.repo not in repos and args.repo not in domain_map:
            logger.error("Unknown repo: %s", args.repo)
            return 1
        repos = [args.repo]

    written = 0
    for repo in repos:
        items = collect_repo_items(plan, repo, domain_map, index_records)
        total = sum(len(v) for v in items.values())
        if total == 0:
            logger.info("Skipping %s: no items", repo)
            continue
        write_repo_yaml(output_dir, repo, items, deny_patterns)
        written += 1

    if not args.skip_legal and written > 0:
        if not run_legal_scan(output_dir):
            logger.error("Legal scan failed. Fix violations before proceeding.")
            return 1

    logger.info("Phase D complete: %d repo specs written", written)
    return 0


if __name__ == "__main__":
    sys.exit(main())
