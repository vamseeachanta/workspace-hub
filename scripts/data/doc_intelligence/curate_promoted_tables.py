"""Curate extracted CSV tables — score quality and promote usable ones.

Scores tables on: row count, numeric content ratio, header quality,
and absence of OCR artifacts (cid: patterns). Promotes tables above
a score threshold to a separate directory for downstream use.

Usage:
    uv run --no-project python scripts/data/doc_intelligence/curate_promoted_tables.py \
        --source data/doc-intelligence/extraction-reports/naval-architecture/tables/naval-architecture \
        --output data/doc-intelligence/promoted-tables/naval-architecture \
        --min-score 0.5
"""

import csv
import os
import re
import shutil
from pathlib import Path

_CID_RE = re.compile(r"\(cid:\d+\)")
_NUMBER_RE = re.compile(r"^-?[\d,]+\.?\d*$")


def score_table(path: str) -> tuple[float, dict]:
    """Score a CSV table on quality (0.0–1.0) and return metadata."""
    rows = _read_csv_safe(path)
    meta = {
        "row_count": len(rows),
        "has_cid_artifacts": False,
        "numeric_ratio": 0.0,
        "empty_ratio": 1.0,
        "header_score": 0.0,
    }

    if len(rows) < 2:
        return 0.0, meta

    all_cells = [cell for row in rows for cell in row]
    total_cells = len(all_cells) if all_cells else 1

    # OCR artifact detection
    raw_text = " ".join(all_cells)
    meta["has_cid_artifacts"] = bool(_CID_RE.search(raw_text))

    # Numeric content ratio
    numeric_count = sum(
        1 for c in all_cells if _NUMBER_RE.match(c.strip().replace(",", ""))
    )
    meta["numeric_ratio"] = numeric_count / total_cells

    # Empty cell ratio
    empty_count = sum(1 for c in all_cells if not c.strip())
    meta["empty_ratio"] = empty_count / total_cells

    # Header score: first row has non-empty, non-numeric values
    if rows:
        header = rows[0]
        non_empty_headers = [
            h for h in header
            if h.strip() and not _NUMBER_RE.match(h.strip())
        ]
        meta["header_score"] = len(non_empty_headers) / max(len(header), 1)

    # Composite score
    score = _compute_score(meta)
    return score, meta


def _compute_score(meta: dict) -> float:
    """Weighted composite quality score."""
    if meta["has_cid_artifacts"]:
        return 0.05

    row_score = min(meta["row_count"] / 5.0, 1.0)
    content_score = 1.0 - meta["empty_ratio"]
    numeric_score = meta["numeric_ratio"]
    header_score = meta["header_score"]

    return (
        0.25 * row_score
        + 0.25 * content_score
        + 0.30 * numeric_score
        + 0.20 * header_score
    )


def _read_csv_safe(path: str) -> list[list[str]]:
    """Read CSV, handling encoding errors gracefully."""
    try:
        with open(path, newline="", encoding="utf-8", errors="replace") as f:
            return list(csv.reader(f))
    except Exception:
        return []


def curate_tables(
    source_dir: str,
    output_dir: str,
    min_score: float = 0.5,
) -> dict:
    """Score all CSVs in source_dir, promote those above min_score."""
    os.makedirs(output_dir, exist_ok=True)

    table_scores = []
    promoted = 0
    rejected = 0

    csv_files = sorted(
        f for f in os.listdir(source_dir) if f.endswith(".csv")
    )

    for filename in csv_files:
        filepath = os.path.join(source_dir, filename)
        score, meta = score_table(filepath)
        table_scores.append({
            "filename": filename,
            "score": round(score, 3),
            **meta,
        })

        if score >= min_score:
            shutil.copy2(filepath, os.path.join(output_dir, filename))
            promoted += 1
        else:
            rejected += 1

    return {
        "promoted_count": promoted,
        "rejected_count": rejected,
        "total_count": promoted + rejected,
        "table_scores": table_scores,
    }


if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Curate promoted tables")
    parser.add_argument("--source", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--min-score", type=float, default=0.5)
    args = parser.parse_args()

    report = curate_tables(args.source, args.output, args.min_score)
    print(json.dumps(report, indent=2, default=str))
