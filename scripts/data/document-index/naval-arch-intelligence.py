#!/usr/bin/env python3
# ABOUTME: Extract intelligence from the 144 naval architecture documents
# ABOUTME: Decodes USN hull classification codes, categorizes textbooks, builds structured catalog

"""
Usage:
    python naval-arch-intelligence.py [--out catalog.yaml]
"""

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import yaml

SCRIPT_DIR = Path(__file__).resolve().parent
HUB_ROOT = SCRIPT_DIR.parents[2]
INDEX_PATH = HUB_ROOT / "data" / "document-index" / "index.jsonl"
_DEFAULT_SUMMARIES = "/mnt/remote/ace-linux-1/ace/data/document-index/summaries"
SUMMARIES_DIR = Path(os.environ.get("SUMMARIES_DIR", _DEFAULT_SUMMARIES))

# USN Hull Classification System
# Reference: https://en.wikipedia.org/wiki/Hull_classification_symbol
HULL_CODES = {
    # Capital ships
    "BB": ("Battleship", "capital"),
    "CC": ("Battlecruiser", "capital"),
    "CV": ("Aircraft Carrier", "capital"),
    "CVL": ("Light Aircraft Carrier", "capital"),
    "CVE": ("Escort Aircraft Carrier", "capital"),
    "CVS": ("Anti-Submarine Carrier", "capital"),
    "CB": ("Large Cruiser", "capital"),

    # Cruisers
    "CA": ("Heavy Cruiser", "cruiser"),
    "CL": ("Light Cruiser", "cruiser"),
    "CG": ("Guided Missile Cruiser", "cruiser"),
    "CGS": ("Coast Guard Ship", "cruiser"),

    # Destroyers
    "DD": ("Destroyer", "destroyer"),
    "DE": ("Destroyer Escort", "destroyer"),
    "DMS": ("Destroyer Minesweeper", "destroyer"),

    # Submarines
    "SS": ("Submarine", "submarine"),
    "SSG": ("Guided Missile Submarine", "submarine"),
    "SSR": ("Radar Picket Submarine", "submarine"),
    "SST": ("Training Submarine", "submarine"),

    # Amphibious
    "LSD": ("Landing Ship Dock", "amphibious"),
    "LSM": ("Landing Ship Medium", "amphibious"),
    "LST": ("Landing Ship Tank", "amphibious"),
    "APA": ("Attack Transport", "amphibious"),
    "APD": ("High-Speed Transport", "amphibious"),
    "APL": ("Barracks Ship", "amphibious"),

    # Patrol & Small Combatants
    "PC": ("Patrol Coastal", "patrol"),
    "PCE": ("Patrol Craft Escort", "patrol"),
    "PG": ("Patrol Gunboat", "patrol"),
    "PE": ("Eagle Boat", "patrol"),
    "PT": ("Patrol Torpedo Boat", "patrol"),
    "WPB": ("Patrol Boat (USCG)", "patrol"),
    "WPC": ("Patrol Cutter (USCG)", "patrol"),

    # Auxiliaries
    "AO": ("Fleet Oiler", "auxiliary"),
    "AR": ("Repair Ship", "auxiliary"),
    "ARS": ("Salvage Ship", "auxiliary"),
    "ARC": ("Cable Repair Ship", "auxiliary"),
    "ARG": ("Repair Ship (internal combustion)", "auxiliary"),
    "ACV": ("Auxiliary Aircraft Carrier", "auxiliary"),
    "ACR": ("Armored Cruiser", "auxiliary"),
    "AKS": ("General Stores Issue Ship", "auxiliary"),

    # Mine Warfare
    "AM": ("Minesweeper", "mine_warfare"),
    "MSO": ("Minesweeper Ocean", "mine_warfare"),

    # Coast Guard & Service
    "WAGL": ("Lighthouse Tender (USCG)", "coast_guard"),
    "WAL": ("Lightship (USCG)", "coast_guard"),
    "WLB": ("Buoy Tender (USCG)", "coast_guard"),
    "WLI": ("Inland Buoy Tender (USCG)", "coast_guard"),
    "WLM": ("Coastal Buoy Tender (USCG)", "coast_guard"),
    "WLR": ("River Buoy Tender (USCG)", "coast_guard"),
    "WMEC": ("Medium Endurance Cutter (USCG)", "coast_guard"),

    # Yard & Service
    "YF": ("Covered Lighter", "yard_service"),
    "YOG": ("Gasoline Barge", "yard_service"),
    "YSD": ("Seaplane Wrecking Derrick", "yard_service"),
    "YTB": ("Large Harbor Tug", "yard_service"),

    # Special
    "X": ("Experimental", "special"),
    "K": ("Corvette (RN)", "special"),
    "J": ("Minesweeper (RN)", "special"),
    "R": ("River Class (RN)", "special"),
    "C": ("Light Cruiser (RN)", "special"),
    "S": ("Submarine (RN)", "special"),
    "EC2": ("Liberty Ship (EC2-S-C1)", "merchant"),
    "MCB": ("Missile Cruiser (converted)", "special"),
}

# Named vessels (no standard hull code)
NAMED_VESSELS = {
    "alligator": ("USS Alligator", "Civil War submarine", "submarine", "1862"),
    "castle": ("HMS Castle", "Castle-class corvette", "patrol", "1943"),
    "marine-raven": ("USNS Marine Raven", "Transport", "auxiliary", "1945"),
    "ptboat": ("PT Boat", "Motor Torpedo Boat", "patrol", "1940s"),
    "river": ("River-class", "Frigate/Destroyer Escort", "destroyer", "1941"),
    "savannah": ("NS Savannah", "Nuclear merchant ship", "merchant", "1962"),
    "tribal": ("Tribal-class", "Destroyer", "destroyer", "1936"),
}


def parse_hull_code(filename: str) -> Optional[Dict]:
    """Parse USN hull classification from filename."""
    stem = Path(filename).stem.lower()

    # Check named vessels first
    if stem in NAMED_VESSELS:
        name, desc, category, era = NAMED_VESSELS[stem]
        return {
            "hull_code": stem,
            "hull_number": None,
            "vessel_name": name,
            "vessel_type": desc,
            "category": category,
            "era": era,
        }

    # Special case: ec2-s-c1 (Liberty Ship)
    if stem.startswith("ec2"):
        return {
            "hull_code": "EC2",
            "hull_number": stem.upper(),
            "vessel_name": "Liberty Ship (EC2-S-C1 type)",
            "vessel_type": "Merchant vessel",
            "category": "merchant",
            "era": "1941-1945",
        }

    # Special case: s26-ss131
    if "-" in stem and "ss" in stem:
        parts = stem.split("-")
        return {
            "hull_code": "SS",
            "hull_number": stem.upper(),
            "vessel_name": f"USS S-26 (SS-131)",
            "vessel_type": "Submarine",
            "category": "submarine",
            "era": "1920s",
        }

    # Try matching hull codes from longest to shortest
    for code in sorted(HULL_CODES.keys(), key=len, reverse=True):
        if stem.startswith(code.lower()):
            remainder = stem[len(code):]
            if remainder.isdigit() or remainder == "" or remainder == "color":
                hull_num = remainder if remainder.isdigit() else None
                vessel_type, category = HULL_CODES[code]
                designation = f"{code}-{hull_num}" if hull_num else code
                return {
                    "hull_code": code,
                    "hull_number": hull_num,
                    "designation": designation,
                    "vessel_type": vessel_type,
                    "category": category,
                }

    return None


def categorize_textbook(filename: str) -> Dict:
    """Categorize textbook by topic area."""
    fname_lower = filename.lower()

    topics = []
    if any(k in fname_lower for k in ["hydrostatic", "stability", "gz"]):
        topics.append("hydrostatics_stability")
    if any(k in fname_lower for k in ["hydrodynamic", "hydromechanic", "resistance", "flow"]):
        topics.append("hydrodynamics")
    if any(k in fname_lower for k in ["propulsion", "propeller"]):
        topics.append("propulsion")
    if any(k in fname_lower for k in ["motion", "seakeeping", "controllability"]):
        topics.append("motions_seakeeping")
    if any(k in fname_lower for k in ["structural", "design-principle", "construction", "hull"]):
        topics.append("structures_design")
    if any(k in fname_lower for k in ["naval-architecture", "principles-of-naval", "introduction-to-naval", "ship-theory"]):
        topics.append("general_naval_architecture")
    if any(k in fname_lower for k in ["offshore", "ocean"]):
        topics.append("offshore_engineering")
    if any(k in fname_lower for k in ["drag", "fluid"]):
        topics.append("fluid_mechanics")
    if any(k in fname_lower for k in ["warship", "janes", "fighting", "submarine"]):
        topics.append("naval_reference")
    if any(k in fname_lower for k in ["solas", "mca", "rules", "regulation"]):
        topics.append("regulatory")
    if any(k in fname_lower for k in ["dnv", "abs"]):
        topics.append("classification_society")
    if any(k in fname_lower for k in ["mathematics", "engineering-math"]):
        topics.append("mathematics")
    if any(k in fname_lower for k in ["performance", "en400"]):
        topics.append("ship_performance")

    # Extract author/year if present
    author = None
    year = None
    year_match = re.search(r"(\d{4})", filename)
    if year_match:
        y = int(year_match.group(1))
        if 1800 <= y <= 2030:
            year = str(y)

    for known_author in ["Rawson", "Tupper", "Biran", "Newman", "Bertram",
                          "Chakrabarti", "Hoerner", "Comstock", "Attwood",
                          "Hughes", "Paik", "Eyres"]:
        if known_author.lower() in filename.lower():
            author = known_author
            break

    return {
        "topics": topics or ["general"],
        "author": author,
        "year": year,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="data/doc-intelligence/naval-architecture-catalog.yaml")
    args = parser.parse_args()

    # Load naval-architecture records
    na_docs = []
    with open(INDEX_PATH) as f:
        for line in f:
            r = json.loads(line)
            if r.get("domain") == "naval-architecture":
                na_docs.append(r)

    # Categorize
    ship_plans = []
    textbooks = []
    hydrostatics = []
    unclassified = []

    for doc in na_docs:
        path = doc["path"]
        filename = path.split("/")[-1]
        subdir = "unknown"
        parts = path.split("/")
        sname_idx = next((i for i, p in enumerate(parts) if p == "SNAME"), None)
        if sname_idx and sname_idx + 1 < len(parts):
            subdir = parts[sname_idx + 1]

        if subdir == "ship-plans":
            hull_info = parse_hull_code(filename)
            entry = {
                "filename": filename,
                "path": path,
                "size_mb": round(doc.get("size_mb", 0), 1),
            }
            if hull_info:
                entry.update(hull_info)
            ship_plans.append(entry)
        elif subdir == "textbooks":
            tb_info = categorize_textbook(filename)
            entry = {
                "filename": filename,
                "path": path,
                "size_mb": round(doc.get("size_mb", 0), 1),
            }
            entry.update(tb_info)
            textbooks.append(entry)
        elif subdir == "hydrostatics-stability":
            tb_info = categorize_textbook(filename)
            entry = {
                "filename": filename,
                "path": path,
                "size_mb": round(doc.get("size_mb", 0), 1),
            }
            entry.update(tb_info)
            hydrostatics.append(entry)

    # Ship plan statistics
    vessel_categories = Counter()
    hull_codes = Counter()
    for sp in ship_plans:
        cat = sp.get("category", "unknown")
        vessel_categories[cat] += 1
        hc = sp.get("hull_code", "unknown")
        hull_codes[hc] += 1

    # Textbook topic coverage
    topic_coverage = Counter()
    for tb in textbooks + hydrostatics:
        for t in tb.get("topics", []):
            topic_coverage[t] += 1

    catalog = {
        "metadata": {
            "generated": "2026-03-13",
            "total_documents": len(na_docs),
            "total_size_mb": round(sum(d.get("size_mb", 0) for d in na_docs), 1),
            "source": "SNAME collection at /mnt/ace/docs/_standards/SNAME/",
        },
        "summary": {
            "ship_plans": {
                "count": len(ship_plans),
                "size_mb": round(sum(s.get("size_mb", 0) for s in ship_plans), 1),
                "vessel_categories": dict(vessel_categories.most_common()),
                "hull_codes_represented": len(hull_codes),
            },
            "textbooks": {
                "count": len(textbooks),
                "size_mb": round(sum(t.get("size_mb", 0) for t in textbooks), 1),
            },
            "hydrostatics_references": {
                "count": len(hydrostatics),
                "size_mb": round(sum(h.get("size_mb", 0) for h in hydrostatics), 1),
            },
            "topic_coverage": dict(topic_coverage.most_common()),
        },
        "ship_plans": sorted(ship_plans, key=lambda x: (x.get("category", "z"), x.get("hull_code", "z"), x.get("hull_number", "0"))),
        "textbooks": sorted(textbooks, key=lambda x: x.get("year") or "9999"),
        "hydrostatics_references": sorted(hydrostatics, key=lambda x: x.get("year") or "9999"),
    }

    out_path = Path(args.out)
    if not out_path.is_absolute():
        out_path = HUB_ROOT / out_path
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with open(out_path, "w") as f:
        yaml.dump(catalog, f, default_flow_style=False, sort_keys=False, width=120)

    print(f"Catalog written to {out_path}")
    print()
    print(f"=== COLLECTION SUMMARY ===")
    print(f"Total: {len(na_docs)} documents, {catalog['metadata']['total_size_mb']} MB")
    print()
    print(f"--- Ship Plans ({len(ship_plans)}) ---")
    print(f"  Vessel categories:")
    for cat, count in vessel_categories.most_common():
        print(f"    {cat:20s}: {count}")
    print()
    print(f"--- Textbooks ({len(textbooks)}) ---")
    for tb in sorted(textbooks, key=lambda x: x.get("year") or "9999"):
        author = tb.get("author") or ""
        year = tb.get("year") or ""
        topics = ", ".join(tb.get("topics", []))
        print(f"  [{year}] {author:12s} {tb['filename'][:55]:55s} ({topics})")
    print()
    print(f"--- Hydrostatics & Stability ({len(hydrostatics)}) ---")
    for h in sorted(hydrostatics, key=lambda x: x.get("year") or "9999"):
        author = h.get("author") or ""
        year = h.get("year") or ""
        topics = ", ".join(h.get("topics", []))
        print(f"  [{year}] {author:12s} {h['filename'][:55]:55s} ({topics})")
    print()
    print(f"--- Topic Coverage ({len(topic_coverage)} topics) ---")
    for topic, count in topic_coverage.most_common():
        print(f"  {topic:30s}: {count} references")


if __name__ == "__main__":
    main()
