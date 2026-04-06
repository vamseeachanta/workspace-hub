#!/usr/bin/env python3
"""Lightweight conference indexer — catalog files with metadata.

Scans /mnt/ace/docs/conferences/ and produces a JSONL index with:
- file path, name, extension, size
- collection name, year (if in path)
- PDF page count (if available)

No full text extraction — just fast cataloging for Phase A of #1608.

Usage:
    uv run python scripts/document-intelligence/index-conferences-lightweight.py
    uv run python scripts/document-intelligence/index-conferences-lightweight.py --dry-run
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

CONF_ROOT = Path("/mnt/ace/docs/conferences")
REPO_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_JSONL = REPO_ROOT / "data" / "document-index" / "conference-index.jsonl"
OUTPUT_REPORT = REPO_ROOT / "data" / "document-index" / "conference-index-report.md"
REGISTRY = REPO_ROOT / "data" / "document-index" / "conference-registry.yaml"

INDEXABLE_EXTS = {".pdf", ".html", ".htm", ".txt", ".ppt", ".pptx", ".doc", ".docx", ".xls", ".xlsx"}


def extract_year(path: Path) -> str | None:
    """Try to extract a 4-digit year from the path."""
    import re
    for part in path.parts:
        m = re.search(r'\b(19[89]\d|20[012]\d)\b', part)
        if m:
            return m.group(1)
    return None


def get_pdf_pages(filepath: Path) -> int | None:
    """Try to get page count from PDF without full parsing."""
    try:
        import subprocess
        result = subprocess.run(
            ["pdfinfo", str(filepath)],
            capture_output=True, text=True, timeout=5
        )
        for line in result.stdout.splitlines():
            if line.startswith("Pages:"):
                return int(line.split(":")[1].strip())
    except Exception:
        pass
    return None


def scan_collection(coll_path: Path, coll_name: str) -> list[dict]:
    """Scan a single collection directory."""
    records = []
    if not coll_path.is_dir():
        return records

    for root, dirs, files in os.walk(coll_path):
        for fname in sorted(files):
            fpath = Path(root) / fname
            ext = fpath.suffix.lower()
            if ext not in INDEXABLE_EXTS:
                continue

            try:
                stat = fpath.stat()
            except OSError:
                continue

            rec = {
                "collection": coll_name,
                "filename": fname,
                "path": str(fpath),
                "extension": ext,
                "size_bytes": stat.st_size,
                "year": extract_year(fpath),
                "relative_path": str(fpath.relative_to(CONF_ROOT)),
            }

            # Skip PDF page count for speed — can add later

            records.append(rec)

    return records


def main():
    parser = argparse.ArgumentParser(description="Lightweight conference indexer")
    parser.add_argument("--dry-run", action="store_true", help="Count only, don't write")
    args = parser.parse_args()

    if not CONF_ROOT.is_dir():
        print(f"Error: conference root not found: {CONF_ROOT}", file=sys.stderr)
        return 1

    collections = sorted(d.name for d in CONF_ROOT.iterdir() if d.is_dir())
    print(f"Found {len(collections)} conference collections")

    all_records = []
    stats = {}

    for coll_name in collections:
        coll_path = CONF_ROOT / coll_name
        records = scan_collection(coll_path, coll_name)
        all_records.extend(records)

        # Per-collection stats
        total_size = sum(r["size_bytes"] for r in records)
        ext_counts = {}
        for r in records:
            ext_counts[r["extension"]] = ext_counts.get(r["extension"], 0) + 1

        stats[coll_name] = {
            "files": len(records),
            "size_mb": round(total_size / (1024 * 1024), 1),
            "extensions": ext_counts,
        }
        print(f"  {coll_name}: {len(records)} files ({stats[coll_name]['size_mb']} MB)")

    print(f"\nTotal: {len(all_records)} indexable files across {len(collections)} collections")

    if args.dry_run:
        print("[DRY RUN] Would write to:")
        print(f"  {OUTPUT_JSONL}")
        print(f"  {OUTPUT_REPORT}")
        print(f"  {REGISTRY}")
        return 0

    # Write JSONL index
    OUTPUT_JSONL.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_JSONL, "w") as f:
        for rec in all_records:
            f.write(json.dumps(rec) + "\n")
    print(f"\nWrote {len(all_records)} records to {OUTPUT_JSONL}")

    # Write report
    with open(OUTPUT_REPORT, "w") as f:
        f.write("# Conference Collection Index Report\n\n")
        f.write(f"Generated: {datetime.now(timezone.utc).isoformat()}\n\n")
        f.write(f"**Total:** {len(all_records)} files across {len(collections)} collections\n\n")
        f.write("| Collection | Files | Size (MB) | PDF | PPT | DOC | Other |\n")
        f.write("|------------|-------|-----------|-----|-----|-----|-------|\n")
        for coll_name, s in sorted(stats.items(), key=lambda x: -x[1]["files"]):
            exts = s["extensions"]
            pdf = exts.get(".pdf", 0)
            ppt = exts.get(".ppt", 0) + exts.get(".pptx", 0)
            doc = exts.get(".doc", 0) + exts.get(".docx", 0)
            other = s["files"] - pdf - ppt - doc
            f.write(f"| {coll_name} | {s['files']} | {s['size_mb']} | {pdf} | {ppt} | {doc} | {other} |\n")
    print(f"Wrote report to {OUTPUT_REPORT}")

    # Write YAML registry
    import yaml
    registry = {
        "generated": datetime.now(timezone.utc).isoformat(),
        "source": str(CONF_ROOT),
        "total_files": len(all_records),
        "total_collections": len(collections),
        "collections": {},
    }
    for coll_name, s in sorted(stats.items()):
        registry["collections"][coll_name] = {
            "files": s["files"],
            "size_mb": s["size_mb"],
            "extensions": s["extensions"],
        }
    with open(REGISTRY, "w") as f:
        yaml.dump(registry, f, default_flow_style=False, sort_keys=False)
    print(f"Wrote registry to {REGISTRY}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
