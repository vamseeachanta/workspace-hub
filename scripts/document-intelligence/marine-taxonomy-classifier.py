#!/usr/bin/env python3
"""Marine sub-domain taxonomy classifier.

Classifies marine-domain documents into 7+ sub-categories using
keyword-based analysis of title, notes, and file paths.

Usage:
    uv run python scripts/document-intelligence/marine-taxonomy-classifier.py
    uv run python scripts/document-intelligence/marine-taxonomy-classifier.py --ledger data/document-index/standards-transfer-ledger.yaml

Issue: #1622
"""

import argparse
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

import yaml


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_LEDGER = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "document-index"
    / "standards-transfer-ledger.yaml"
)

REPORT_OUTPUT = (
    Path(__file__).resolve().parents[2]
    / "docs"
    / "document-intelligence"
    / "marine-taxonomy-report.md"
)

TAGS_OUTPUT = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "document-index"
    / "marine-subdomain-tags.yaml"
)


# ---------------------------------------------------------------------------
# Taxonomy definition — 7+ sub-domains with keyword lists
# ---------------------------------------------------------------------------

MARINE_TAXONOMY: Dict[str, List[str]] = {
    "hydrodynamics": [
        "hydrodynamic", "wave diffraction", "radiation", "rao",
        "response amplitude", "wave load", "wave force", "added mass",
        "damping", "diffraction", "green function", "panel method",
        "potential flow", "strip theory", "cfd", "computational fluid",
        "sloshing", "wave-body", "orcawave", "wamit", "aqwa",
        "sea state", "wave spectrum", "jonswap", "pierson-moskowitz",
        "wave period", "wave height", "significant wave",
    ],
    "mooring": [
        "mooring", "stationkeeping", "station keeping", "anchor",
        "chain", "wire rope", "polyester", "taut leg", "catenary",
        "spread mooring", "turret", "swivel", "fairlead", "bollard",
        "hawser", "position mooring", "dynamic positioning", "dp system",
        "thruster", "mooring line", "pretension", "offset",
    ],
    "structural": [
        "fatigue", "s-n curve", "stress concentration", "scf",
        "tubular joint", "weld", "fracture", "crack", "structural integrity",
        "finite element", "fea", "buckling", "yield", "ultimate strength",
        "collapse", "accidental load", "impact", "dent", "corrosion",
        "thickness", "structural design", "steel structure",
    ],
    "subsea": [
        "subsea", "submarine", "underwater", "seabed", "pipeline",
        "riser", "flowline", "umbilical", "manifold", "jumper",
        "spool", "wellhead", "christmas tree", "bop", "blowout",
        "flexible pipe", "rigid pipe", "j-tube", "pull-in", "lay",
        "vortex-induced", "viv", "touchdown", "cathodic protection subsea",
    ],
    "naval_architecture": [
        "stability", "intact stability", "damage stability", "inclining",
        "hydrostatic", "displacement", "draft", "trim", "heel",
        "metacentric", "gm", "gz curve", "freeboard", "tonnage",
        "hull form", "naval architecture", "ship design", "vessel design",
        "compartment", "flooding", "watertight", "subdivision",
        "general arrangement", "lines plan",
    ],
    "marine_operations": [
        "installation", "heavy lift", "crane", "lifting",
        "tow", "towing", "float-over", "loadout", "grillage",
        "seafastening", "transport", "weather window", "operability",
        "marine operation", "offshore operation", "vessel operation",
        "hook-up", "commissioning", "decommissioning", "removal",
        "diving", "rov", "remotely operated",
    ],
    "environmental": [
        "environmental", "metocean", "wind load", "current load",
        "ice load", "seismic", "earthquake", "tsunami", "typhoon",
        "hurricane", "cyclone", "wind speed", "wind profile",
        "ocean current", "tidal", "surge", "climate", "api rp 2met",
        "environmental condition", "environmental data", "hindcast",
        "wave climate", "extreme value",
    ],
    "geotechnical": [
        "geotechnical", "soil", "foundation", "pile", "suction caisson",
        "anchor pile", "driven pile", "drag anchor", "mud mat",
        "bearing capacity", "settlement", "consolidation", "clay",
        "sand", "seabed survey", "cone penetration", "cpt",
        "shear strength", "lateral capacity",
    ],
}


# ---------------------------------------------------------------------------
# Classification functions
# ---------------------------------------------------------------------------


def classify_document(entry: Dict) -> str:
    """Classify a single document entry into a marine sub-domain.

    Uses keyword matching against title, notes, and file paths.
    Returns the sub-domain name or 'unclassified'.
    """
    # Build a searchable text blob from all available fields
    parts = []
    parts.append(entry.get("title", ""))
    parts.append(entry.get("notes", "") or "")
    parts.append(entry.get("doc_path", "") or "")
    for p in entry.get("doc_paths", []):
        parts.append(p or "")

    text = " ".join(parts).lower()

    # Score each sub-domain by keyword hit count
    scores: Dict[str, int] = {}
    for subdomain, keywords in MARINE_TAXONOMY.items():
        score = 0
        for kw in keywords:
            if kw.lower() in text:
                score += 1
        if score > 0:
            scores[subdomain] = score

    if not scores:
        return "unclassified"

    # Return the sub-domain with the highest score
    return max(scores, key=scores.get)


def classify_batch(standards: List[Dict]) -> Dict[str, str]:
    """Classify a list of standards, returning {id: subdomain}."""
    return {entry["id"]: classify_document(entry) for entry in standards}


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------


def generate_report(standards: List[Dict], mapping: Dict[str, str]) -> str:
    """Generate a markdown report of the marine taxonomy classification."""
    lines = []
    lines.append("# Marine Sub-Domain Taxonomy Report")
    lines.append("")
    lines.append(f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    lines.append(f"Total documents classified: {len(standards)}")
    lines.append("")

    # Distribution table
    counter = Counter(mapping.values())
    lines.append("## Sub-Domain Distribution")
    lines.append("")
    lines.append("| Sub-Domain | Count | Percentage |")
    lines.append("|---|---|---|")
    for subdomain, count in counter.most_common():
        pct = count / len(mapping) * 100 if mapping else 0
        lines.append(f"| {subdomain} | {count} | {pct:.1f}% |")
    lines.append("")

    # Sample files per category
    lines.append("## Sample Files per Sub-Domain")
    lines.append("")
    by_subdomain: Dict[str, List[Dict]] = {}
    for entry in standards:
        sd = mapping.get(entry["id"], "unclassified")
        by_subdomain.setdefault(sd, []).append(entry)

    for subdomain in sorted(by_subdomain.keys()):
        entries = by_subdomain[subdomain]
        lines.append(f"### {subdomain} ({len(entries)} docs)")
        lines.append("")
        for e in entries[:5]:  # top 5 samples
            lines.append(f"- **{e['id']}**: {e.get('title', 'N/A')}")
        if len(entries) > 5:
            lines.append(f"- ... and {len(entries) - 5} more")
        lines.append("")

    # Unclassified list
    unclassified = [e for e in standards if mapping.get(e["id"]) == "unclassified"]
    if unclassified:
        lines.append("## Unclassified Documents")
        lines.append("")
        for e in unclassified:
            lines.append(f"- **{e['id']}**: {e.get('title', 'N/A')} — {(e.get('notes') or 'no notes')[:100]}")
        lines.append("")

    return "\n".join(lines)


def write_tags_yaml(
    standards: List[Dict],
    mapping: Dict[str, str],
    output_path: str,
) -> None:
    """Write the sub-domain tag assignments to a YAML file."""
    counter = Counter(mapping.values())
    data = {
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S"),
        "total": len(standards),
        "summary": dict(counter.most_common()),
        "entries": [
            {
                "id": entry["id"],
                "title": entry.get("title", ""),
                "subdomain": mapping.get(entry["id"], "unclassified"),
            }
            for entry in standards
        ],
    }
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify marine documents into sub-domains")
    parser.add_argument(
        "--ledger",
        default=str(DEFAULT_LEDGER),
        help="Path to the standards-transfer-ledger YAML",
    )
    parser.add_argument(
        "--report-output",
        default=str(REPORT_OUTPUT),
        help="Output path for markdown report",
    )
    parser.add_argument(
        "--tags-output",
        default=str(TAGS_OUTPUT),
        help="Output path for sub-domain tags YAML",
    )

    args = parser.parse_args()

    # Load ledger
    with open(args.ledger) as f:
        data = yaml.safe_load(f)

    # Filter marine domain
    marine = [s for s in data["standards"] if s.get("domain") == "marine"]
    print(f"Found {len(marine)} marine-domain standards")

    # Classify
    mapping = classify_batch(marine)

    # Distribution summary
    counter = Counter(mapping.values())
    print("\nSub-domain distribution:")
    for sd, count in counter.most_common():
        print(f"  {sd}: {count}")

    # Generate report
    report = generate_report(marine, mapping)
    Path(args.report_output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.report_output, "w") as f:
        f.write(report)
    print(f"\nReport written to {args.report_output}")

    # Write tags YAML
    write_tags_yaml(marine, mapping, args.tags_output)
    print(f"Tags written to {args.tags_output}")


if __name__ == "__main__":
    main()
