#!/usr/bin/env python3
# ABOUTME: Phase E — Build master registry linking all index/summary/domain data (WRK-309)
# ABOUTME: Generates data/document-index/registry.yaml (committed, sanitized)

"""
Usage:
    python phase-e-registry.py [--config config.yaml] [--skip-legal]
"""

import argparse
import json
import logging
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


def load_config(config_path: Path) -> Dict[str, Any]:
    """Load pipeline configuration from YAML."""
    with open(config_path) as f:
        return yaml.safe_load(f)


def load_index(index_path: Path) -> List[Dict]:
    """Load all index records."""
    records: List[Dict] = []
    if not index_path.exists():
        logger.error("Index not found: %s", index_path)
        sys.exit(1)
    with open(index_path) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return records


def count_summaries(summaries_dir: Path) -> int:
    """Count summary JSON files."""
    if not summaries_dir.exists():
        return 0
    return sum(1 for f in summaries_dir.iterdir() if f.suffix == ".json")


def load_data_source_specs(specs_dir: Path) -> Dict[str, Dict]:
    """Load all per-repo data-source specs."""
    specs: Dict[str, Dict] = {}
    if not specs_dir.exists():
        return specs
    for f in specs_dir.iterdir():
        if f.suffix in (".yaml", ".yml"):
            try:
                data = yaml.safe_load(f.read_text())
                repo = data.get("repo", f.stem)
                specs[repo] = data
            except (yaml.YAMLError, OSError):
                continue
    return specs


def load_enhancement_plan(plan_path: Path) -> Dict[str, Any]:
    """Load enhancement plan for domain counts."""
    if not plan_path.exists():
        return {}
    with open(plan_path) as f:
        return yaml.safe_load(f) or {}


def build_registry(
    records: List[Dict],
    summaries_dir: Path,
    repo_specs: Dict[str, Dict],
    plan: Dict[str, Any],
) -> Dict[str, Any]:
    """Build the master registry structure."""
    by_source: Dict[str, int] = defaultdict(int)
    for rec in records:
        by_source[rec.get("source", "unknown")] += 1

    # Count domains directly from index (authoritative — back-populated by phase-e-backpopulate.py)
    _by_domain: Dict[str, int] = defaultdict(int)
    for rec in records:
        d = rec.get("domain") or "other"
        _by_domain[d] += 1
    by_domain = dict(sorted(_by_domain.items(), key=lambda x: -x[1]))

    repos_summary: Dict[str, Dict] = {}
    for repo, spec in repo_specs.items():
        standards = spec.get("standards", [])
        gaps = spec.get("gaps", [])
        implemented = [s for s in standards if s.get("status") == "implemented"]
        repos_summary[repo] = {
            "standards_count": len(standards),
            "gaps": len(gaps),
            "implemented": len(implemented),
        }

    registry = {
        "generated": datetime.now().isoformat(timespec="seconds"),
        "total_docs": len(records),
        "total_summaries": count_summaries(summaries_dir),
        "by_source": dict(by_source),
        "by_domain": by_domain,
        "repos": repos_summary,
    }
    return registry


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Phase E: Master registry (WRK-309)"
    )
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--skip-legal", action="store_true", help="Deprecated compatibility flag; ignored (scanner retired)")
    args = parser.parse_args()
    if args.skip_legal:
        logger.warning("--skip-legal is ignored; the scanner is retired")

    cfg = load_config(args.config)
    index_path = HUB_ROOT / cfg["output"]["index_path"]
    summaries_dir = HUB_ROOT / cfg["output"]["summaries_dir"]
    plan_path = HUB_ROOT / cfg["output"]["enhancement_plan"]
    registry_path = HUB_ROOT / cfg["output"]["registry_path"]
    specs_dir = HUB_ROOT / "specs" / "data-sources"

    records = load_index(index_path)
    repo_specs = load_data_source_specs(specs_dir)
    plan = load_enhancement_plan(plan_path)

    logger.info(
        "Building registry: %d records, %d repo specs",
        len(records), len(repo_specs),
    )

    registry = build_registry(records, summaries_dir, repo_specs, plan)

    registry_path.parent.mkdir(parents=True, exist_ok=True)
    with open(registry_path, "w") as f:
        yaml.dump(registry, f, default_flow_style=False, sort_keys=False, width=120)
    logger.info("Wrote registry: %s", registry_path)

    logger.info("Phase E complete: %d total documents registered", registry["total_docs"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
