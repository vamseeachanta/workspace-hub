#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml"]
# ///
"""Retroactive quality audit of all extracted table CSVs.

Reads CSV files from deep extraction output, applies quality filters
(watermark, dedup, content threshold), and writes a YAML audit report.

Usage:
    uv run --no-project python scripts/data/doc-intelligence/rate-table-quality.py
    uv run --no-project python scripts/data/doc-intelligence/rate-table-quality.py \
        --input data/doc-intelligence/deep/tables/ \
        --output data/doc-intelligence/table-quality-audit.yaml
"""

import argparse
import csv
import glob
import io
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

_repo_root = str(Path(__file__).resolve().parents[3])
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)

from scripts.data.doc_intelligence.table_quality import (
    classify_table_quality,
    is_watermark,
    meets_content_threshold,
)


def csv_to_table_dict(csv_path: str) -> dict:
    """Read a CSV file and convert to table dict format."""
    with open(csv_path, encoding="utf-8", errors="replace") as f:
        content = f.read()

    rows = []
    columns = []
    reader = csv.reader(io.StringIO(content))
    for i, row in enumerate(reader):
        if i == 0:
            columns = row
        else:
            rows.append(row)

    return {"columns": columns, "rows": rows, "path": csv_path}


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit table extraction quality")
    parser.add_argument(
        "--input",
        default="data/doc-intelligence/deep/tables/",
        help="Directory containing extracted table CSVs",
    )
    parser.add_argument(
        "--output",
        default="data/doc-intelligence/table-quality-audit.yaml",
        help="Output YAML report path",
    )
    args = parser.parse_args()

    input_dir = Path(args.input)
    if not input_dir.exists():
        print(f"Error: {input_dir} not found", file=sys.stderr)
        return 1

    csv_files = sorted(glob.glob(str(input_dir / "**/*.csv"), recursive=True))
    print(f"Found {len(csv_files)} CSV files")

    # Audit each file
    results_by_domain = {}
    all_results = []

    for csv_path in csv_files:
        rel = os.path.relpath(csv_path, input_dir)
        domain = rel.split(os.sep)[0] if os.sep in rel else "unknown"

        table = csv_to_table_dict(csv_path)
        quality = classify_table_quality(table)
        wm = is_watermark(table)
        threshold = meets_content_threshold(table)
        n_rows = len(table["rows"])

        result = {
            "file": rel,
            "domain": domain,
            "quality": quality,
            "is_watermark": wm,
            "meets_threshold": threshold,
            "rows": n_rows,
        }
        all_results.append(result)

        if domain not in results_by_domain:
            results_by_domain[domain] = {
                "total": 0, "usable": 0, "partial": 0, "junk": 0,
                "watermark": 0, "below_threshold": 0,
            }
        d = results_by_domain[domain]
        d["total"] += 1
        d[quality] += 1
        if wm:
            d["watermark"] += 1
        if not threshold and not wm:
            d["below_threshold"] += 1

    # Build report
    total = len(all_results)
    usable = sum(1 for r in all_results if r["quality"] == "usable")
    partial = sum(1 for r in all_results if r["quality"] == "partial")
    junk = sum(1 for r in all_results if r["quality"] == "junk")

    report = {
        "audit": {
            "title": "Table Extraction Quality Audit",
            "wrk_id": "WRK-1256",
            "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "input_dir": str(input_dir),
            "total_tables": total,
        },
        "summary": {
            "usable": usable,
            "partial": partial,
            "junk": junk,
            "quality_rate": round((usable + partial) / total * 100, 1) if total else 0,
            "usable_rate": round(usable / total * 100, 1) if total else 0,
        },
        "by_domain": results_by_domain,
        "junk_tables": [r["file"] for r in all_results if r["quality"] == "junk"],
    }

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        yaml.dump(report, f, default_flow_style=False, sort_keys=False)

    print(f"\nQuality Audit Results:")
    print(f"  Total:   {total}")
    print(f"  Usable:  {usable} ({report['summary']['usable_rate']}%)")
    print(f"  Partial: {partial}")
    print(f"  Junk:    {junk}")
    print(f"  Quality rate: {report['summary']['quality_rate']}%")
    print(f"\nBy domain:")
    for domain, d in sorted(results_by_domain.items()):
        rate = round((d["usable"] + d["partial"]) / d["total"] * 100) if d["total"] else 0
        print(f"  {domain:<30} {d['total']:>4} total | {d['usable']:>4} usable | {d['watermark']:>4} wmark | {rate}%")
    print(f"\nReport: {out_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
