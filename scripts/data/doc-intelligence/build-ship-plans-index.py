#!/usr/bin/env python3
"""Build an index of ship plan PDFs with metadata.

Reads manifests for ship plan PDFs (drawing-heavy, minimal text) and produces
a structured YAML index with vessel classification, page count, and source path.

Usage:
    uv run --no-project --with pyyaml python scripts/data/doc-intelligence/build-ship-plans-index.py
"""

import re
import sys
import yaml
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
MANIFEST_DIR = REPO_ROOT / "data" / "doc-intelligence" / "manifests" / "naval-architecture"
SNAME_PLANS = Path("/mnt/ace/docs/_standards/SNAME/ship-plans")
OUTPUT = REPO_ROOT / "data" / "doc-intelligence" / "ship-plans-index.yaml"

# Hull classification codes (US Navy standard designations)
HULL_CODES = {
    "ac": "Collier", "acr": "Large Cruiser", "acv": "Auxiliary Aircraft Carrier",
    "aks": "General Stores Issue Ship", "am": "Minesweeper", "ao": "Fleet Oiler",
    "ap": "Transport", "apa": "Attack Transport", "apd": "High-Speed Transport",
    "apl": "Barracks Ship", "ar": "Repair Ship", "arc": "Cable Repair Ship",
    "arg": "Internal Combustion Engine Repair Ship", "ars": "Salvage Ship",
    "bb": "Battleship", "c": "Cruiser", "ca": "Heavy Cruiser",
    "castle": "Castle-class Corvette", "cc": "Battle Cruiser",
    "cg": "Guided Missile Cruiser", "cgs": "Coast Guard Ship",
    "cl": "Light Cruiser", "cv": "Aircraft Carrier",
    "cve": "Escort Aircraft Carrier", "cvl": "Light Aircraft Carrier",
    "cvs": "Anti-Submarine Warfare Carrier",
    "dd": "Destroyer", "de": "Destroyer Escort", "dms": "High-Speed Minesweeper",
    "ec": "Liberty Ship", "hmb": "Harbor Minesweeper",
    "j": "Minesweeping Trawler", "k": "Corvette",
    "lsd": "Landing Ship Dock", "lsm": "Landing Ship Medium",
    "lst": "Landing Ship Tank", "mcb": "Minesweeper Coastal",
    "mso": "Minesweeper Ocean", "pc": "Submarine Chaser",
    "pce": "Patrol Craft Escort", "pe": "Eagle Boat",
    "pg": "Patrol Gunboat", "r": "Destroyer Tender",
    "river": "River-class Frigate", "s": "Submarine (pre-SS)",
    "savannah": "NS Savannah (Nuclear Merchant Ship)",
    "ss": "Submarine", "ssg": "Guided Missile Submarine",
    "ssr": "Radar Picket Submarine", "sst": "Target/Training Submarine",
    "tribal": "Tribal-class Destroyer",
    "wagl": "USCG Lighthouse Tender", "wal": "USCG Cutter",
    "wlb": "USCG Buoy Tender (Seagoing)", "wli": "USCG Buoy Tender (Inland)",
    "wlm": "USCG Buoy Tender (Coastal)", "wlr": "USCG Buoy Tender (River)",
    "wmec": "USCG Medium Endurance Cutter",
    "wpb": "USCG Patrol Boat", "wpc": "USCG Patrol Craft",
    "x": "Submersible Craft", "yf": "Covered Lighter",
    "yog": "Gasoline Barge", "ysd": "Seaplane Wrecking Derrick",
    "ytb": "Large Harbor Tug",
    "alligator": "USS Alligator (First US Navy Submarine)",
    "ptboat": "PT Boat (Motor Torpedo Boat)",
    "marine-raven": "USNS Marine Raven (Transport)",
}


def _classify_hull(stem: str) -> dict:
    """Extract hull code, hull number, and vessel type from filename stem."""
    # Try matching code + number (e.g. bb34, ss298, cv60color)
    m = re.match(r"^([a-z]+?)(\d+)?(?:color)?$", stem)
    if not m:
        return {"hull_code": stem, "hull_number": None, "vessel_type": "Unknown"}
    code = m.group(1)
    number = m.group(2)

    # Match against hull codes (try longest prefix first)
    vessel_type = "Unknown"
    matched_code = code
    for prefix_len in range(len(code), 0, -1):
        prefix = code[:prefix_len]
        if prefix in HULL_CODES:
            vessel_type = HULL_CODES[prefix]
            matched_code = prefix
            break

    # Special cases for full-name entries
    if stem in HULL_CODES:
        vessel_type = HULL_CODES[stem]
        matched_code = stem
        number = None

    return {
        "hull_code": matched_code,
        "hull_number": int(number) if number else None,
        "vessel_type": vessel_type,
    }


def main() -> int:
    entries = []

    for pdf in sorted(SNAME_PLANS.glob("*.pdf")):
        stem = pdf.stem
        manifest_path = MANIFEST_DIR / f"{stem}.manifest.yaml"

        meta = {"pages": None, "sections": 0, "tables": 0, "figure_refs": 0}
        if manifest_path.exists():
            with open(manifest_path) as f:
                manifest = yaml.safe_load(f)
            if manifest:
                md = manifest.get("metadata", {})
                meta["pages"] = md.get("pages")
                stats = manifest.get("extraction_stats", {})
                meta["sections"] = stats.get("sections", 0)
                meta["tables"] = stats.get("tables", 0)
                meta["figure_refs"] = stats.get("figure_refs", 0)

        hull = _classify_hull(stem)
        entry = {
            "filename": pdf.name,
            "stem": stem,
            **hull,
            "pages": meta["pages"],
            "has_text": meta["sections"] > 0 or meta["tables"] > 0,
            "sections": meta["sections"],
            "tables": meta["tables"],
            "figure_refs": meta["figure_refs"],
            "source_path": str(pdf),
            "drawing_extraction_status": "pending",
        }
        entries.append(entry)

    # Sort by hull code then number
    entries.sort(key=lambda e: (e["hull_code"], e["hull_number"] or 0))

    # Summary stats
    total = len(entries)
    with_text = sum(1 for e in entries if e["has_text"])
    drawing_only = total - with_text
    vessel_types = sorted(set(e["vessel_type"] for e in entries))

    index = {
        "version": "1.0.0",
        "description": "Ship plan PDF index with vessel classification metadata",
        "source": "/mnt/ace/docs/_standards/SNAME/ship-plans/",
        "summary": {
            "total_plans": total,
            "with_extractable_text": with_text,
            "drawing_only": drawing_only,
            "vessel_types_count": len(vessel_types),
            "vessel_types": vessel_types,
        },
        "plans": entries,
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT, "w") as f:
        yaml.dump(index, f, default_flow_style=False, sort_keys=False, width=120)

    print(f"Ship plans index: {OUTPUT}")
    print(f"  Total: {total} | With text: {with_text} | Drawing-only: {drawing_only}")
    print(f"  Vessel types: {len(vessel_types)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
