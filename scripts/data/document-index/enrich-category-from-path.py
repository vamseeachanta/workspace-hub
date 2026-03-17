#!/usr/bin/env python3
"""First-pass category enrichment from file paths and names.

Assigns category/subcategory to index records based on directory
structure, filename patterns, and document type codes. Designed
to be corrected later after content inspection.

Usage:
    uv run --no-project python scripts/data/document-index/enrich-category-from-path.py
    uv run --no-project python scripts/data/document-index/enrich-category-from-path.py --dry-run
"""

import argparse
import json
import re
import sys
import time
from pathlib import Path

# --- Discipline from directory path ---
DISCIPLINE_MAP = {
    "drilling": "drilling",
    "completion": "completions",
    "production": "production",
    "integrity_management": "asset-integrity",
    "interventions": "well-intervention",
    "knowledge_skills": "reference",
    "misc": "uncategorized",
}

# --- DDE project patterns ---
DDE_PROJECT_PATTERNS = [
    (r"riser", "riser-engineering"),
    (r"mooring", "mooring"),
    (r"pipeline", "pipeline"),
    (r"corrosion|cp\b|cathodic", "corrosion-protection"),
    (r"fea|fe\b|structural|ffs", "structural-analysis"),
    (r"drill", "drilling"),
    (r"tensioner", "subsea-equipment"),
    (r"simulation", "simulation"),
    (r"sewol", "naval-architecture"),
    (r"marketing", "business"),
    (r"python|support", "engineering-support"),
]

# --- Doc type codes in filenames ---
DOC_TYPE_MAP = {
    "CAL": "calculation",
    "REP": "report",
    "DWG": "drawing",
    "SPE": "specification",
    "PRC": "procedure",
    "MOM": "minutes-of-meeting",
    "LET": "correspondence",
    "MTR": "material-record",
    "PLN": "plan",
    "SCH": "schedule",
    "RFQ": "procurement",
    "INV": "invoice",
    "PO": "purchase-order",
    "DAT": "data-file",
}

# --- Standards org from path ---
STANDARDS_ORG_MAP = {
    "API": "api",
    "DNV": "dnv",
    "ISO": "iso",
    "NORSOK": "norsok",
    "ASTM": "astm",
    "ABS": "abs",
    "BV": "bureau-veritas",
    "BS": "british-standards",
    "ASME": "asme",
    "AWS": "aws",
    "IEC": "iec",
    "AMJIG": "amjig",
    "NACE": "nace",
    "IACS": "iacs",
    "IMCA": "imca",
    "OTC": "otc",
    "SPE": "spe-papers",
    "OMAE": "omae",
}

# --- Extension-based subcategory ---
EXT_SUBCATEGORY = {
    "dwg": "cad-drawing",
    "dxf": "cad-drawing",
    "stp": "cad-model",
    "step": "cad-model",
    "iges": "cad-model",
    "stl": "cad-model",
    "inp": "fea-input",
    "dat": "simulation-data",
    "csv": "tabular-data",
    "pptx": "presentation",
    "ppt": "presentation",
    "msg": "email",
    "eml": "email",
    "zip": "archive",
    "rar": "archive",
    "7z": "archive",
    "jpg": "image",
    "jpeg": "image",
    "png": "image",
    "tif": "image",
    "tiff": "image",
    "bmp": "image",
    "mp4": "video",
    "avi": "video",
    "py": "source-code",
    "m": "source-code",
    "f": "source-code",
}


def classify_from_path(rec: dict) -> tuple[str, str]:
    """Return (category, subcategory) from path/filename."""
    path = rec.get("file_path") or rec.get("path") or ""
    ext = rec.get("ext", "").lower()
    source = rec.get("source", "")
    fname = path.rsplit("/", 1)[-1] if "/" in path else path
    fname_upper = fname.upper()
    path_lower = path.lower()

    category = "uncategorized"
    subcategory = "unknown"

    # 1. Standards sources
    if source in ("ace_standards", "og_standards"):
        category = "standards"
        for org, sub in STANDARDS_ORG_MAP.items():
            if f"/{org}/" in path or f"/{org}\\" in path:
                subcategory = sub
                break
            if path_lower.startswith(
                f"/mnt/ace/0000 o&g/0000 codes & standards/{org.lower()}"
            ):
                subcategory = sub
                break
        if subcategory == "unknown":
            subcategory = "general-standards"
        return category, subcategory

    # 2. API metadata
    if source == "api_metadata":
        return "data-source", "api-metadata"

    # 3. Workspace specs
    if source == "workspace_spec":
        return "workspace", "specification"

    # 4. ace_project with discipline path
    if source == "ace_project" and "/disciplines/" in path:
        parts = path.split("/disciplines/")[1].split("/")
        disc = parts[0] if parts else ""
        category = "project-engineering"
        subcategory = DISCIPLINE_MAP.get(disc, disc)

    # 5. ace_project root-level docs (K07 pattern)
    elif source == "ace_project" and re.search(
        r"K\d{2}[A-Z]{2}\d{5}", fname
    ):
        category = "project-engineering"
        subcategory = "project-document"

    # 6. DDE project
    elif source == "dde_project":
        category = "project-engineering"
        if "/documents/" in path:
            seg = path.split("/documents/")[1].split("/")
            proj_name = seg[0] if seg else ""
            proj_lower = proj_name.lower()
            for pattern, sub in DDE_PROJECT_PATTERNS:
                if re.search(pattern, proj_lower):
                    subcategory = sub
                    break
            else:
                if proj_name.startswith("0000 Personal"):
                    subcategory = "personal"
                elif re.match(r"\d{3,4}\s", proj_name):
                    subcategory = "numbered-project"
                else:
                    subcategory = "project-document"
        else:
            subcategory = "project-document"

    # 7. Fallback for other ace_project
    elif source == "ace_project":
        category = "project-engineering"
        subcategory = "project-document"

    # Refine subcategory with doc type code
    for code, doc_type in DOC_TYPE_MAP.items():
        if f"-{code}-" in fname_upper or f"_{code}_" in fname_upper:
            subcategory = doc_type
            break

    # Refine with extension
    if ext in EXT_SUBCATEGORY and subcategory in (
        "unknown",
        "uncategorized",
        "project-document",
    ):
        subcategory = EXT_SUBCATEGORY[ext]

    return category, subcategory


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--index",
        default="data/document-index/index.jsonl",
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    index_path = Path(args.index)
    if not index_path.exists():
        print(f"Error: {index_path} not found", file=sys.stderr)
        return 1

    t0 = time.time()
    from collections import Counter

    cat_stats = Counter()
    sub_stats = Counter()
    enriched = 0
    skipped = 0
    total = 0
    records = []

    with open(index_path) as f:
        for line in f:
            rec = json.loads(line)
            total += 1

            if rec.get("path_category") and rec.get("path_subcategory"):
                skipped += 1
                records.append(rec)
                continue

            cat, sub = classify_from_path(rec)
            rec["path_category"] = cat
            rec["path_subcategory"] = sub
            enriched += 1
            cat_stats[cat] += 1
            sub_stats[f"{cat}/{sub}"] += 1
            records.append(rec)

            if total % 200000 == 0:
                print(f"  [{total:,}] ...", flush=True)

    elapsed = time.time() - t0
    print(f"\nClassified {enriched:,} / {total:,} in {elapsed:.1f}s")
    print(f"Skipped (already classified): {skipped:,}")

    print("\n=== Categories ===")
    for k, v in cat_stats.most_common():
        print(f"  {k}: {v:,}")

    print("\n=== Top 30 Subcategories ===")
    for k, v in sub_stats.most_common(30):
        print(f"  {k}: {v:,}")

    if args.dry_run:
        print("\n[DRY RUN] No changes written.")
        return 0

    tmp = index_path.with_suffix(".jsonl.tmp")
    with open(tmp, "w") as fout:
        for rec in records:
            fout.write(json.dumps(rec, separators=(",", ":")) + "\n")

    import os

    os.rename(tmp, index_path)
    print(f"\nWritten to {index_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
