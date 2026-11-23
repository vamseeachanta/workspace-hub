#!/usr/bin/env python3
# ABOUTME: Incremental domain reclassification audit for the 1M document index
# ABOUTME: Samples records, applies improved heuristics, shows before/after for review

"""
Usage:
    python reclassify-audit.py --batch-size 10 [--offset 0] [--source dde_project]
                               [--domain marine] [--dry-run] [--apply]
                               [--fix-nulls] [--report]

Modes:
    --report         Show current domain distribution and quality metrics
    --fix-nulls      Reclassify only domain=null records (144 SNAME ship plans)
    --batch-size N   Sample N records for audit (default 10)
    --offset N       Skip first N records in the filtered set
    --source S       Filter to a specific source type
    --domain D       Filter to a specific current domain
    --apply          Write changes back to index.jsonl (without this, dry-run)
    --out PATH       Write reclassified batch to a separate JSONL for review
"""

import argparse
import json
import logging
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

SCRIPT_DIR = Path(__file__).resolve().parent
HUB_ROOT = SCRIPT_DIR.parents[2]
INDEX_PATH = HUB_ROOT / "data" / "document-index" / "index.jsonl"
SUMMARIES_DIR = HUB_ROOT / "data" / "document-index" / "summaries"

VALID_DOMAINS = [
    "structural", "cathodic-protection", "pipeline", "marine",
    "installation", "energy-economics", "portfolio", "materials",
    "regulatory", "cad", "workspace-spec", "naval-architecture",
    "project-management", "other",
]

# Enhanced keyword scoring with weights (keyword, weight)
DOMAIN_KEYWORDS_V2 = {
    "naval-architecture": [
        ("ship plan", 5), ("hull form", 5), ("naval architect", 5),
        ("sname", 4), ("ship design", 4), ("vessel design", 4),
        ("hydrostatics", 3), ("ship stability", 4), ("displacement", 2),
        ("waterline", 3), ("draught", 2), ("freeboard", 3),
        ("propeller", 3), ("rudder", 3), ("seakeeping", 4),
        ("resistance and propulsion", 4), ("ship motion", 3),
        ("classification society", 3), ("abs rule", 3), ("dnv ship", 3),
        ("lloyd's register", 3), ("bureau veritas", 2),
        ("tonnage", 2), ("deadweight", 3), ("lines plan", 4),
        ("general arrangement", 2), ("midship section", 4),
        ("body plan", 3), ("ssr", 2), ("ship-plans", 5),
    ],
    "marine": [
        ("mooring", 4), ("calm buoy", 4), ("hydrodynamic", 3),
        ("orcaflex", 4), ("orcawave", 4), ("rao", 3), ("fpso", 4),
        ("semi-submersible", 4), ("spar", 2), ("tlp", 3),
        ("offshore platform", 3), ("wave load", 3), ("viv", 3),
        ("riser", 2), ("diffraction", 3), ("dnv-os-e301", 4),
        ("api rp 2sk", 4), ("anchor", 2),
        ("wave kinematics", 4), ("wave statistics", 4), ("wave force", 3),
        ("ocean wave", 3), ("offshore technology", 2), ("otc", 2),
        ("vibration", 2), ("deep water", 2), ("deepwater", 2),
        ("wellhead", 2), ("production riser", 4), ("drilling riser", 4),
        ("wave height", 3), ("wave period", 3), ("sea state", 3),
        ("significant wave", 4), ("current profile", 3),
    ],
    "structural": [
        ("fatigue", 3), ("s-n curve", 4), ("stress concentration", 3),
        ("jacket", 3), ("topside", 3), ("iso 19902", 4),
        ("api rp 2a", 4), ("eurocode", 3), ("weld", 2),
        ("scf", 3), ("tubular joint", 4), ("in-place analysis", 3),
        ("ansys", 3), ("fea", 3), ("finite element", 3),
    ],
    "cathodic-protection": [
        ("cathodic", 5), ("anode", 4), ("cp design", 5),
        ("dnv-rp-b401", 5), ("dnv-rp-f103", 5), ("corrosion", 2),
        ("sacrificial", 3), ("impressed current", 4),
    ],
    "pipeline": [
        ("pipeline", 3), ("dnv-st-f101", 4), ("api rp 1111", 4),
        ("flowline", 4), ("buckle", 2), ("on-bottom stability", 4),
        ("dnv-rp-f109", 4), ("subsea", 2), ("pig", 2),
        ("dnv-rp-f105", 4), ("span", 2), ("free span", 4),
    ],
    "installation": [
        ("installation", 2), ("j-lay", 4), ("s-lay", 4), ("reel-lay", 4),
        ("umbilical", 3), ("weather window", 3), ("tensioner", 3),
        ("heavy lift", 3), ("crane", 2),
    ],
    "energy-economics": [
        ("bsee", 4), ("eia", 3), ("production forecast", 4),
        ("decline curve", 4), ("npv", 2), ("economics", 2),
        ("field development", 3), ("reservoir", 2),
    ],
    "portfolio": [
        ("portfolio", 3), ("stock market", 3), ("yfinance", 5), ("sharpe", 4),
        ("value at risk", 4), ("option pricing", 4), ("covered call", 4),
        ("financial analysis", 3), ("dividend", 3), ("equity", 2),
    ],
    "materials": [
        ("astm", 3), ("composite", 3), ("laminate", 3), ("aluminium", 2),
        ("material spec", 3), ("tensile", 2), ("charpy", 3),
        ("hardness", 2), ("metallurgy", 3),
    ],
    "regulatory": [
        ("imo", 3), ("uscg", 3), ("regulation", 2), ("compliance", 2),
        ("convention", 2), ("marpol", 4), ("solas", 4),
    ],
    "cad": [
        ("autocad", 4), ("solidworks", 4), ("3d model", 3),
    ],
    "project-management": [
        ("schedule", 2), ("milestone", 3), ("gantt", 4),
        ("project plan", 3), ("deliverable", 2),
    ],
}

# Path-based rules (highest priority — deterministic)
PATH_RULES = [
    (r"/SNAME/ship-plans/", "naval-architecture"),
    (r"/SNAME/", "naval-architecture"),
    (r"/_standards/ASTM/", "materials"),
    (r"/_standards/BS/", "materials"),
    (r"/_standards/API/", None),  # None = needs keyword check (API covers many domains)
    (r"/_standards/DNV/", None),
]


def get_summary(sha: str) -> Optional[Dict]:
    """Load summary by content hash if available."""
    if not sha:
        return None
    sha_clean = sha.replace("sha256:", "")
    sfile = SUMMARIES_DIR / f"{sha_clean}.json"
    if sfile.exists():
        try:
            with open(sfile) as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return None


def classify_v2(record: Dict, summary: Optional[Dict] = None) -> Tuple[str, float, str]:
    """Enhanced classification returning (domain, confidence, reason).

    Priority:
    1. Path rules (deterministic)
    2. CAD extension check
    3. Weighted keyword scoring on path + summary text
    """
    path = record.get("path", "").lower()

    # 1. Path-based rules
    for pattern, domain in PATH_RULES:
        if re.search(pattern, path, re.IGNORECASE):
            if domain is not None:
                return domain, 1.0, f"path_rule:{pattern}"
            break  # None means fall through to keyword check

    # 2. CAD extension
    if record.get("is_cad"):
        # But check if it's really a naval/marine/pipeline CAD file
        # by also doing keyword scoring
        pass  # fall through — keyword may override

    # 3. Build searchable text
    parts = [
        path,
        str(record.get("org", "") or ""),
        str(record.get("doc_number", "") or ""),
    ]
    if summary:
        parts.extend([
            str(summary.get("title", "") or ""),
            str(summary.get("summary", "") or ""),
            str(summary.get("text_preview", "") or "")[:500],
            str(summary.get("discipline", "") or ""),
        ])
    searchable = " ".join(parts).lower()

    # 4. Weighted keyword scoring
    scores: Dict[str, float] = {}
    for domain, keywords in DOMAIN_KEYWORDS_V2.items():
        score = 0.0
        for kw, weight in keywords:
            if kw in searchable:
                score += weight
        if score > 0:
            scores[domain] = score

    if not scores:
        # CAD files with no keyword hits stay as CAD
        if record.get("is_cad"):
            return "cad", 0.5, "is_cad_flag"
        return "other", 0.1, "no_keywords_matched"

    # Sort by score descending
    ranked = sorted(scores.items(), key=lambda x: -x[1])
    best_domain, best_score = ranked[0]
    total_score = sum(scores.values())
    confidence = best_score / total_score if total_score > 0 else 0.0

    # CAD override: if is_cad and best engineering domain score is weak, keep as cad
    if record.get("is_cad") and best_score < 4:
        return "cad", 0.6, f"is_cad_weak_signal:{best_domain}={best_score:.0f}"

    return best_domain, confidence, f"keyword_v2:{best_domain}={best_score:.0f}"


def load_index() -> List[Dict]:
    """Load all records from index.jsonl."""
    records = []
    with open(INDEX_PATH) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return records


def run_report(records: List[Dict]) -> None:
    """Print domain distribution and quality metrics."""
    domain_counts = Counter()
    source_counts = Counter()
    null_count = 0
    has_summary = 0

    for r in records:
        d = r.get("domain")
        domain_counts[d or "NULL"] += 1
        source_counts[r.get("source", "?")] += 1
        if r.get("content_hash"):
            sha = r["content_hash"].replace("sha256:", "")
            if (SUMMARIES_DIR / f"{sha}.json").exists():
                has_summary += 1

    print(f"Total records: {len(records):,}")
    print(f"With summaries: {has_summary:,} ({100*has_summary/len(records):.1f}%)")
    print(f"Null domain: {domain_counts.get('NULL', 0)}")
    print()
    print("Domain distribution:")
    for d, c in domain_counts.most_common():
        print(f"  {d:25s} {c:>10,}")
    print()
    print("Source distribution:")
    for s, c in source_counts.most_common():
        print(f"  {s:25s} {c:>10,}")


def run_batch(records: List[Dict], args: argparse.Namespace) -> List[Dict]:
    """Run reclassification on a batch and return changed records."""
    # Filter
    filtered = records
    if args.source:
        filtered = [r for r in filtered if r.get("source") == args.source]
    if args.domain:
        if args.domain == "null":
            filtered = [r for r in filtered if not r.get("domain")]
        else:
            filtered = [r for r in filtered if r.get("domain") == args.domain]
    if args.fix_nulls:
        filtered = [r for r in filtered if not r.get("domain")]

    # Apply offset and batch size
    start = args.offset
    end = start + args.batch_size
    batch = filtered[start:end]

    if not batch:
        print(f"No records found (filtered={len(filtered)}, offset={start})")
        return []

    print(f"Batch: {len(batch)} records (of {len(filtered):,} filtered, offset {start})")
    print(f"{'='*100}")

    changes = []
    for i, rec in enumerate(batch):
        path = rec.get("path", "")
        old_domain = rec.get("domain") or "NULL"
        sha = (rec.get("content_hash") or "").replace("sha256:", "")

        # Load summary if available
        summary = get_summary(rec.get("content_hash", ""))

        new_domain, confidence, reason = classify_v2(rec, summary)

        changed = new_domain != old_domain
        marker = "CHANGE" if changed else "same"

        short_path = "/".join(path.split("/")[-3:])
        summary_title = ""
        if summary:
            summary_title = (summary.get("title") or "")[:60]

        print(f"\n[{i+1}/{len(batch)}] {marker}")
        print(f"  Path:       {short_path}")
        if summary_title:
            print(f"  Title:      {summary_title}")
        print(f"  Old domain: {old_domain}")
        print(f"  New domain: {new_domain} (confidence={confidence:.2f}, {reason})")

        if changed:
            rec["domain"] = new_domain
            rec["_reclass_reason"] = reason
            rec["_reclass_confidence"] = confidence
            changes.append(rec)

    print(f"\n{'='*100}")
    print(f"Total changes: {len(changes)} / {len(batch)}")
    return changes


def apply_changes(records: List[Dict], changes: List[Dict]) -> None:
    """Write updated index back to disk."""
    # Build lookup by path for changed records
    change_map = {r["path"]: r for r in changes}

    updated = 0
    with open(INDEX_PATH, "w") as f:
        for rec in records:
            if rec["path"] in change_map:
                changed = change_map[rec["path"]]
                rec["domain"] = changed["domain"]
                updated += 1
            # Strip internal fields before writing
            clean = {k: v for k, v in rec.items() if not k.startswith("_reclass")}
            f.write(json.dumps(clean) + "\n")

    print(f"Applied {updated} changes to {INDEX_PATH}")


def main():
    parser = argparse.ArgumentParser(description="Incremental domain reclassification audit")
    parser.add_argument("--batch-size", type=int, default=10)
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--source", type=str, default=None)
    parser.add_argument("--domain", type=str, default=None)
    parser.add_argument("--fix-nulls", action="store_true")
    parser.add_argument("--report", action="store_true")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--out", type=str, default=None, help="Write changes to separate JSONL")
    parser.add_argument("--dry-run", action="store_true", default=True)
    args = parser.parse_args()

    if args.apply:
        args.dry_run = False

    records = load_index()

    if args.report:
        run_report(records)
        return

    changes = run_batch(records, args)

    if args.out and changes:
        out_path = Path(args.out)
        with open(out_path, "w") as f:
            for rec in changes:
                clean = {k: v for k, v in rec.items() if not k.startswith("_reclass")}
                f.write(json.dumps(clean) + "\n")
        print(f"Wrote {len(changes)} changes to {out_path}")

    if args.apply and changes:
        confirm = input(f"Apply {len(changes)} changes to index.jsonl? [y/N] ")
        if confirm.lower() == "y":
            apply_changes(records, changes)
        else:
            print("Skipped. Use --out to save changes separately.")
    elif changes and args.dry_run:
        print("\nDry run — no changes written. Use --apply to commit changes.")


if __name__ == "__main__":
    main()
