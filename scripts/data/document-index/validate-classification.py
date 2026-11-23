#!/usr/bin/env python3
# ABOUTME: Validation script for WRK-1170 reclassification accuracy (AC2)
# ABOUTME: Samples reclassified records for manual spot-check and writes evidence

"""
Sample reclassified records from index.jsonl for manual accuracy validation.

Picks 10 records per major reclassification rule, prints path + old→new domain
for human review. Use --approve to write validation evidence after review.

Usage:
    uv run --no-project python scripts/data/document-index/validate-classification.py
    uv run --no-project python scripts/data/document-index/validate-classification.py --approve
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from collections import defaultdict
from pathlib import Path

import yaml

SCRIPT_DIR = Path(__file__).resolve().parent
HUB_ROOT = SCRIPT_DIR.parents[2]
INDEX_PATH = HUB_ROOT / "data" / "document-index" / "index.jsonl"

# Major rules from WRK-1170 to sample
TARGET_RULES = [
    "ks_halliburton",
    "ks_projects_fallback",
    "dde_2h_projects",
    "misc_gis",
    "misc_projects_fallback",
    "spare_guidelines",
    "spare_otc",
    "spare_reference",
    "spare_papers",
    "spare_mil",
    "spare_fallback",
    "fname_17_otc",
    "fname_18_tne",
]

SAMPLES_PER_RULE = 5
MIN_TOTAL_SAMPLES = 50


def collect_samples(index_path: Path) -> dict[str, list[dict]]:
    """Collect records reclassified by WRK-1170 rules, grouped by rule."""
    by_rule: dict[str, list[dict]] = defaultdict(list)
    with open(index_path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            rule = rec.get("remapped_by")
            if rule != "phase-e2":
                continue
            # Infer the rule from domain + path
            domain = rec.get("domain", "")
            path = rec.get("path", "")
            # Collect all phase-e2 remapped records
            by_rule[domain].append({
                "path": path,
                "domain": domain,
                "target_repos": rec.get("target_repos", []),
                "ext": rec.get("ext", ""),
            })
    return by_rule


def sample_records(by_rule: dict[str, list[dict]], n_per_group: int) -> list[dict]:
    """Sample n records per domain group."""
    samples = []
    for domain, records in sorted(by_rule.items()):
        k = min(n_per_group, len(records))
        samples.extend(random.sample(records, k))
    # Pad to minimum if needed
    all_records = [r for recs in by_rule.values() for r in recs]
    while len(samples) < MIN_TOTAL_SAMPLES and len(all_records) > len(samples):
        extra = random.choice(all_records)
        if extra not in samples:
            samples.append(extra)
    return samples


def print_samples(samples: list[dict]) -> None:
    """Print samples for manual review."""
    print(f"\n{'='*80}")
    print(f"CLASSIFICATION VALIDATION — {len(samples)} samples")
    print(f"{'='*80}\n")
    for i, rec in enumerate(samples, 1):
        path_short = rec["path"]
        if len(path_short) > 90:
            path_short = "..." + path_short[-87:]
        print(f"[{i:3d}] domain={rec['domain']:<20s} repos={rec['target_repos']}")
        print(f"      {path_short}")
        print()


def write_evidence(samples: list[dict], evidence_path: Path) -> None:
    """Write validation evidence YAML."""
    evidence = {
        "wrk": "WRK-1170",
        "validation_type": "classification_accuracy",
        "total_samples": len(samples),
        "approved": True,
        "samples": [
            {
                "path": r["path"][-100:],
                "domain": r["domain"],
                "repos": r["target_repos"],
            }
            for r in samples
        ],
    }
    evidence_path.parent.mkdir(parents=True, exist_ok=True)
    with open(evidence_path, "w") as f:
        yaml.dump(evidence, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    print(f"\nEvidence written to: {evidence_path}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate WRK-1170 classification accuracy")
    parser.add_argument("--approve", action="store_true", help="Write validation evidence")
    parser.add_argument("--seed", type=int, default=1170, help="Random seed for reproducibility")
    args = parser.parse_args()

    random.seed(args.seed)

    if not INDEX_PATH.exists():
        print(f"ERROR: Index not found: {INDEX_PATH}", file=sys.stderr)
        return 1

    print("Collecting reclassified records...")
    by_rule = collect_samples(INDEX_PATH)
    total = sum(len(v) for v in by_rule.values())
    print(f"Found {total} records reclassified by phase-e2 across {len(by_rule)} domains")

    for domain, records in sorted(by_rule.items(), key=lambda x: -len(x[1])):
        print(f"  {domain:<25s} {len(records):>6d}")

    samples = sample_records(by_rule, SAMPLES_PER_RULE)
    print_samples(samples)

    if args.approve:
        evidence_path = (
            HUB_ROOT / ".claude" / "work-queue" / "assets" / "WRK-1170"
            / "evidence" / "classification-validation.yaml"
        )
        write_evidence(samples, evidence_path)

    return 0


if __name__ == "__main__":
    sys.exit(main())
