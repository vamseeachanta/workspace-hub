#!/usr/bin/env python3
# ABOUTME: Phase C — LLM domain classification and enhancement plan generation (WRK-309)
# ABOUTME: Classifies indexed documents by engineering domain, maps to repos, creates enhancement-plan.yaml

"""
Usage:
    python phase-c-classify.py [--config config.yaml] [--limit N] [--dry-run]
"""

import argparse
import json
import logging
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

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

VALID_STATUSES = ["implemented", "gap", "data_source", "reference"]

# Mapping from Phase B discipline labels to Phase C domain taxonomy
PHASE_B_TO_PHASE_C = {
    "structural": "structural",
    "pipeline": "pipeline",
    "cathodic-protection": "cathodic-protection",
    "marine": "marine",
    "installation": "installation",
    "drilling": "regulatory",
    "production": "energy-economics",
    "materials": "materials",
    "regulatory": "regulatory",
    "energy-economics": "energy-economics",
    "geotechnical": "structural",
    "fire-safety": "regulatory",
    "electrical": "regulatory",
    "document-processing": "other",
    "other": "other",
}

DOMAIN_KEYWORDS = {
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


def load_config(config_path: Path) -> Dict[str, Any]:
    """Load pipeline configuration from YAML."""
    with open(config_path) as f:
        return yaml.safe_load(f)


def load_index(index_path: Path) -> List[Dict]:
    """Load all records from index.jsonl."""
    records: List[Dict] = []
    if not index_path.exists():
        logger.error("Index not found: %s", index_path)
        return records
    with open(index_path) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return records


def load_summaries(summaries_dir: Path) -> Dict[str, Dict]:
    """Load all summary JSON files keyed by path and by sha."""
    summaries: Dict[str, Dict] = {}
    if not summaries_dir.exists():
        return summaries
    count = 0
    for sfile in summaries_dir.glob("*.json"):
        try:
            with open(sfile) as f:
                s = json.load(f)
            if "path" in s:
                summaries[s["path"]] = s
            # Also index by sha so index records can look up by content_hash
            sha = s.get("sha") or sfile.stem
            if sha and sha not in summaries:
                summaries[sha] = s
            count += 1
            if count % 50000 == 0:
                logger.info("Loaded %d summaries...", count)
        except (json.JSONDecodeError, OSError):
            continue
    logger.info("Loaded %d summaries (%d index entries)", count, len(summaries))
    return summaries


def classify_heuristic(record: Dict, summary: Optional[Dict]) -> Tuple[str, str]:
    """Classify domain using keyword matching. Returns (domain, status)."""
    source = record.get("source", "")
    if source == "api_metadata":
        return "energy-economics", "data_source"
    if source == "workspace_spec":
        return "workspace-spec", "reference"
    if record.get("is_cad"):
        return "cad", "reference"

    # Use Phase B discipline label if available (fastest and most accurate path)
    if summary and summary.get("discipline"):
        phase_b_disc = summary["discipline"]
        domain = PHASE_B_TO_PHASE_C.get(phase_b_disc, "other")
        return domain, "gap"

    searchable = " ".join([
        str(record.get("path", "")),
        str(record.get("org", "") or ""),
        str(record.get("doc_number", "") or ""),
        str((summary or {}).get("title", "") or ""),
        str((summary or {}).get("summary", "") or ""),
        str((summary or {}).get("text_preview", "") or ""),
    ]).lower()

    scores: Dict[str, int] = {}
    for domain, keywords in DOMAIN_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in searchable)
        if score > 0:
            scores[domain] = score

    domain = max(scores, key=scores.get) if scores else "other"
    status = "gap"
    return domain, status


def classify_llm(
    summary: Dict, cfg: Dict, daily_spend: float,
) -> Tuple[str, str, float]:
    """Use LLM to classify document domain and status."""
    llm_cfg = cfg.get("llm", {})
    budget = llm_cfg.get("daily_budget_usd", 20.0)
    if daily_spend >= budget:
        return "other", "reference", 0.0

    summary_text = summary.get("summary", "") or ""
    title = summary.get("title", "") or ""
    if not summary_text and not title:
        return "other", "reference", 0.0

    try:
        import anthropic
        client = anthropic.Anthropic()
        model = llm_cfg.get("model", "claude-haiku-4-5-20251001")
        domains_str = ", ".join(VALID_DOMAINS)
        prompt = (
            f"Classify this engineering document.\n"
            f"Title: {title}\nSummary: {summary_text[:2000]}\n\n"
            f"Return ONLY JSON: "
            f'{{"domain": "<one of: {domains_str}>", '
            f'"status": "<one of: implemented, gap, data_source, reference>"}}'
        )
        message = client.messages.create(
            model=model, max_tokens=200,
            messages=[{"role": "user", "content": prompt}],
        )
        text = message.content[0].text.strip()
        cost = (message.usage.input_tokens * 0.25 + message.usage.output_tokens * 1.25) / 1_000_000

        result = json.loads(text)
        domain = result.get("domain", "other")
        status = result.get("status", "reference")
        if domain not in VALID_DOMAINS:
            domain = "other"
        if status not in VALID_STATUSES:
            status = "reference"
        return domain, status, cost
    except Exception as exc:
        logger.warning("LLM classification failed: %s", exc)
        return "other", "reference", 0.0


def map_to_repos(domain: str, repo_domain_map: Dict) -> List[str]:
    """Find repos whose domain list includes this domain."""
    return sorted(
        repo for repo, domains in repo_domain_map.items()
        if domain in domains
    )


def build_enhancement_plan(
    records: List[Dict],
    summaries: Dict[str, Dict],
    cfg: Dict,
    limit: int,
) -> Dict[str, Any]:
    """Classify all documents and build enhancement plan."""
    repo_domain_map = cfg.get("repo_domain_map", {})
    by_domain: Dict[str, Dict] = {}
    daily_spend = 0.0
    classified = 0

    for rec in records:
        if limit and classified >= limit:
            break

        path = rec.get("path", "")
        summary = summaries.get(path)
        # Fallback: look up by content_hash (SHA) when path doesn't match
        if not summary:
            sha = rec.get("content_hash", "")
            if sha:
                summary = summaries.get(sha)

        # Always use heuristic (which checks Phase B discipline first).
        # LLM re-classification skipped: Phase B already classified all docs.
        domain, status = classify_heuristic(rec, summary)

        repos = map_to_repos(domain, repo_domain_map)

        if domain not in by_domain:
            by_domain[domain] = {"count": 0, "repos": [], "items": []}

        by_domain[domain]["count"] += 1
        for r in repos:
            if r not in by_domain[domain]["repos"]:
                by_domain[domain]["repos"].append(r)

        by_domain[domain]["items"].append({
            "doc_number": rec.get("doc_number") or "",
            "title": (summary.get("title") if summary else None)
                     or Path(path).name,
            "path": path,
            "status": status,
            "notes": "",
        })

        classified += 1
        if classified % 500 == 0:
            logger.info("Classified %d, LLM spend: $%.2f", classified, daily_spend)

    plan = {
        "generated": datetime.now().isoformat(timespec="seconds"),
        "total_classified": classified,
        "by_domain": by_domain,
    }
    logger.info(
        "Classification done: %d docs, %d domains, $%.2f",
        classified, len(by_domain), daily_spend,
    )
    return plan


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Phase C: LLM domain classification (WRK-309)"
    )
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--limit", type=int, default=0, help="Max docs to classify")
    parser.add_argument("--dry-run", action="store_true", help="Classify but don't write")
    args = parser.parse_args()

    cfg = load_config(args.config)
    index_path = HUB_ROOT / cfg["output"]["index_path"]
    summaries_dir = HUB_ROOT / cfg["output"]["summaries_dir"]
    plan_path = HUB_ROOT / cfg["output"]["enhancement_plan"]

    records = load_index(index_path)
    summaries = load_summaries(summaries_dir)

    if not records:
        logger.error("No index records found. Run Phase A first.")
        return 1

    plan = build_enhancement_plan(records, summaries, cfg, args.limit)

    if args.dry_run:
        for domain, data in plan["by_domain"].items():
            logger.info("  %s: %d docs -> %s", domain, data["count"], data["repos"])
        return 0

    plan_path.parent.mkdir(parents=True, exist_ok=True)
    with open(plan_path, "w") as f:
        yaml.dump(plan, f, default_flow_style=False, sort_keys=False, width=120)
    logger.info("Enhancement plan written: %s", plan_path)
    logger.info("*** USER REVIEW REQUIRED before Phase D ***")
    return 0


if __name__ == "__main__":
    sys.exit(main())
