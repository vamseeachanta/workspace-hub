#!/usr/bin/env python3
"""
WRK-1363: Classify riser-eng-job literature by digitalmodel domain.

Scans PDF/DOC/DOCX files in the riser-eng-job archive, classifies each
by filename pattern matching into digitalmodel domain categories, and
writes a domain-index.yaml.

Usage:
    python classify-riser-eng-job.py [--source DIR] [--output FILE] [--dry-run]
"""

import argparse
import os
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML required. Install: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

# Document type codes found in riser-eng-job naming conventions
DOC_TYPE_MAP = {
    "RPT": "report",
    "TNE": "technical_note",
    "DGA": "drawing_ga",
    "DDL": "drawing_detail",
    "DFG": "drawing_forging",
    "DTS": "data_sheet",
    "CTR": "calculation",
    "MTO": "material_takeoff",
    "CSH": "correspondence",
    "PRG": "programme",
    "RQI": "requisition",
    "NDF": "notification",
    "DCN": "design_change",
    "AUD": "audit",
    "PAF": "project_action",
    "INV": "invoice",
    "PRP": "proposal",
}

# Keyword-to-domain mapping (case-insensitive patterns)
DOMAIN_KEYWORDS = {
    "risers": [
        r"\briser\b", r"\bslhr\b", r"\bslor\b", r"\bfsr\b",
        r"\bspool\b", r"\bjumper\b", r"\bgooseneck\b",
        r"\briser.system\b", r"\bcontainment.riser\b",
    ],
    "riser_analysis": [
        r"\banalysis\b", r"\bresponse\b", r"\bstorm\b",
        r"\bglobal.analysis\b", r"\bconfiguration\b",
        r"\boperability\b", r"\bdesign.report\b",
    ],
    "viv": [
        r"\bviv\b", r"\bvortex\b",
    ],
    "structural": [
        r"\bfea\b", r"\bfinite.element\b", r"\bstress\b",
        r"\bbuckling\b", r"\bfatigue\b", r"\bpile\b",
        r"\bfoundation\b", r"\bballast\b", r"\bweld\b",
    ],
    "fatigue": [
        r"\bfatigue\b",
    ],
    "mooring": [
        r"\bmooring\b", r"\banchor\b",
    ],
    "fem": [
        r"\bfea\b", r"\bfinite.element\b", r"\bansys\b",
        r"\bnastran\b",
    ],
    "catenary": [
        r"\bcatenary\b", r"\blazy.wave\b",
    ],
    "connections": [
        r"\bconnect\b", r"\bflange\b", r"\bjoint\b",
        r"\bflexible.joint\b",
    ],
    "installation": [
        r"\binstall\b", r"\blay\b", r"\bpullover\b",
        r"\bhandling\b",
    ],
    "metocean": [
        r"\bmetocean\b", r"\bcurrent\b", r"\bwave\b",
        r"\bstorm\b", r"\benvironment\b",
    ],
    "pipe": [
        r"\bpipe\b", r"\bline.pipe\b", r"\btubular\b",
    ],
    "subsea": [
        r"\bsubsea\b", r"\bseabed\b", r"\bunderwater\b",
        r"\bumbilical\b",
    ],
}

# Project-level domain assignments (all files in project get these)
PROJECT_DOMAINS = {
    "2100-blk31-slor-design": ["risers", "riser_analysis", "structural"],
    "3824-containment-riser": ["risers", "riser_analysis"],
    "3836-hp1-riser": ["risers", "riser_analysis"],
    "3837-cdp2-fsr": ["risers", "riser_analysis"],
}

LITERATURE_EXTENSIONS = {".pdf", ".doc", ".docx"}


def classify_file(filepath: str, project: str) -> dict:
    """Classify a single file by filename pattern matching."""
    basename = os.path.basename(filepath).lower()
    name_no_ext = os.path.splitext(basename)[0]

    # Start with project-level domains
    domains = set(PROJECT_DOMAINS.get(project, ["risers"]))

    # Extract document type code
    doc_type = "unknown"
    for code, dtype in DOC_TYPE_MAP.items():
        if f"-{code.lower()}-" in basename or f"-{code.lower()}." in basename:
            doc_type = dtype
            break

    # Match keywords against filename
    for domain, patterns in DOMAIN_KEYWORDS.items():
        for pattern in patterns:
            if re.search(pattern, name_no_ext, re.IGNORECASE):
                domains.add(domain)
                break

    return {
        "path": filepath,
        "project": project,
        "doc_type": doc_type,
        "domains": sorted(domains),
    }

def apply_llm_overrides(results: list, source_dir: str) -> list:
    """Read LLM classifications from llm-classifications dir and apply them."""
    import hashlib
    import json
    
    llm_dir = Path(source_dir) / "llm-classifications"
    if not llm_dir.is_dir():
        return results
        
    for r in results:
        if r["doc_type"] == "unknown" and r["path"].lower().endswith(".pdf"):
            sha = hashlib.sha256(r["path"].encode('utf-8')).hexdigest()
            llm_file = llm_dir / f"{sha}.json"
            if llm_file.exists():
                try:
                    with open(llm_file, 'r') as jf:
                        llm_data = json.load(jf)
                        if "doc_type" in llm_data and llm_data["doc_type"] != "unknown":
                            r["doc_type"] = llm_data["doc_type"]
                        if "domains" in llm_data and isinstance(llm_data["domains"], list):
                            valid_domains = [d for d in llm_data["domains"] if isinstance(d, str)]
                            r["domains"] = sorted(list(set(r["domains"] + valid_domains)))
                except Exception:
                    pass
    return results

def scan_and_classify(source_dir: str) -> list:
    """Scan source directory and classify all literature files."""
    results = []
    source = Path(source_dir)

    for project_dir in sorted(source.iterdir()):
        if not project_dir.is_dir():
            continue
        project = project_dir.name

        for root, _dirs, files in os.walk(project_dir):
            for fname in files:
                ext = os.path.splitext(fname)[1].lower()
                if ext not in LITERATURE_EXTENSIONS:
                    continue
                fpath = os.path.join(root, fname)
                result = classify_file(fpath, project)
                results.append(result)

    return results


def build_domain_index(results: list) -> dict:
    """Build domain index from classification results."""
    domain_files = defaultdict(list)
    doc_type_counts = defaultdict(int)

    for r in results:
        for domain in r["domains"]:
            domain_files[domain].append({
                "path": r["path"],
                "project": r["project"],
                "doc_type": r["doc_type"],
            })
        doc_type_counts[r["doc_type"]] += 1

    # Build summary
    index = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "wrk_id": "WRK-1363",
        "source": str(Path(results[0]["path"]).parent) if results else "",
        "total_files": len(results),
        "doc_type_distribution": dict(sorted(
            doc_type_counts.items(), key=lambda x: -x[1]
        )),
        "domains": {},
    }

    for domain in sorted(domain_files.keys()):
        files = domain_files[domain]
        index["domains"][domain] = {
            "count": len(files),
            "files": [f["path"] for f in files],
        }

    return index


def main():
    parser = argparse.ArgumentParser(description="Classify riser-eng-job literature")
    parser.add_argument(
        "--source",
        default="/mnt/ace/digitalmodel/docs/domain/subsea-risers/riser-eng-job",
        help="Source directory",
    )
    parser.add_argument(
        "--output",
        default="/mnt/ace/digitalmodel/docs/domain/subsea-risers/riser-eng-job/domain-index.yaml",
        help="Output index file",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print stats only")
    parser.add_argument("--summary-only", action="store_true", help="Write summary without file lists")
    args = parser.parse_args()

    if not os.path.isdir(args.source):
        print(f"ERROR: Source directory not found: {args.source}", file=sys.stderr)
        sys.exit(1)

    print(f"Scanning {args.source}...")
    results = scan_and_classify(args.source)
    results = apply_llm_overrides(results, args.source)
    print(f"Classified {len(results)} literature files")

    if not results:
        print("No files found.", file=sys.stderr)
        sys.exit(1)

    index = build_domain_index(results)

    # Print summary
    print(f"\nDomain distribution:")
    for domain, info in sorted(index["domains"].items(), key=lambda x: -x[1]["count"]):
        print(f"  {domain}: {info['count']} files")

    print(f"\nDocument type distribution:")
    for dtype, count in index["doc_type_distribution"].items():
        print(f"  {dtype}: {count}")

    if args.dry_run:
        print("\n[dry-run] No output written.")
        return

    if args.summary_only:
        # Strip file lists for smaller output
        for domain in index["domains"]:
            index["domains"][domain] = {"count": index["domains"][domain]["count"]}

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, "w") as f:
        yaml.dump(index, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

    print(f"\nIndex written to: {args.output}")


if __name__ == "__main__":
    main()
