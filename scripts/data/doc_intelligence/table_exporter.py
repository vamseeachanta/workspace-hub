"""Table exporter — converts manifest ExtractedTable dicts to CSV files.

Bridges the gap between pdfplumber extraction (in parsers/pdf.py) and the
tables promoter. Tables are already extracted during the single PDF parse pass;
this module writes them as CSV and generates JSONL records for the promoter.

Usage:
    from scripts.data.doc_intelligence.table_exporter import export_tables_from_manifest
    result = export_tables_from_manifest(manifest_dict, output_dir)
"""

import csv
import hashlib
import os
import re
from pathlib import Path
from typing import Optional


def _sanitize_filename(text: str) -> str:
    """Convert title text to a safe filename component."""
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9\s_-]", "", text)
    text = re.sub(r"\s+", "_", text)
    text = re.sub(r"_+", "_", text).strip("_")
    return text[:60] if text else ""


def _csv_content(columns: list[str], rows: list[list[str]]) -> str:
    """Render columns + rows as CSV string."""
    import io

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(columns)
    for row in rows:
        writer.writerow(row)
    return buf.getvalue()


def export_tables_to_csv(
    tables: list[dict],
    output_dir: Path,
    doc_name: str,
) -> list[Path]:
    """Write each table dict to a CSV file under output_dir.

    Returns list of written/existing file paths.
    Idempotent: skips files whose content matches.
    """
    if not tables:
        return []

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = []

    for idx, table in enumerate(tables, start=1):
        title = table.get("title")
        columns = table.get("columns", [])
        rows = table.get("rows", [])

        # Build filename: prefer sanitized title, fallback to index
        title_part = _sanitize_filename(title) if title else ""
        name = f"{doc_name}_table_{idx:03d}"
        if title_part:
            name = f"{doc_name}_{title_part}"
        csv_path = output_dir / f"{name}.csv"

        content = _csv_content(columns, rows)

        # Idempotency check
        if csv_path.exists():
            existing = csv_path.read_text(encoding="utf-8")
            if existing == content:
                paths.append(csv_path)
                continue

        # Atomic write
        tmp = csv_path.with_suffix(".csv.tmp")
        tmp.write_text(content, encoding="utf-8")
        os.replace(tmp, csv_path)
        paths.append(csv_path)

    return paths


def export_tables_from_manifest(
    manifest_dict: dict,
    output_dir: Path,
    apply_quality_filter: bool = True,
) -> dict:
    """Export all tables from a manifest dict to CSV files.

    When apply_quality_filter=True (default), tables are deduped, watermarks
    removed, and each table is quality-classified (usable/partial/junk).
    Junk tables are still exported but flagged in the result.

    Returns a summary dict with tables_exported, csv_paths, domain, quality.
    """
    from scripts.data.doc_intelligence.table_quality import (
        classify_table_quality,
        dedup_tables,
    )

    tables = manifest_dict.get("tables", [])
    domain = manifest_dict.get("domain", "general")
    doc_name = Path(manifest_dict["metadata"]["filename"]).stem

    quality_stats = {
        "total_input": len(tables),
        "duplicates_removed": 0,
        "usable": 0,
        "partial": 0,
        "junk": 0,
    }

    if apply_quality_filter:
        deduped = dedup_tables(tables)
        quality_stats["duplicates_removed"] = len(tables) - len(deduped)
        tables_to_export = deduped
    else:
        tables_to_export = tables

    # Classify each table
    table_qualities = []
    for table in tables_to_export:
        q = classify_table_quality(table)
        table_qualities.append(q)
        quality_stats[q] = quality_stats.get(q, 0) + 1

    # Export to domain-specific subdirectory
    domain_dir = Path(output_dir) / domain
    csv_paths = export_tables_to_csv(tables_to_export, domain_dir, doc_name)

    return {
        "tables_exported": len(csv_paths),
        "csv_paths": [str(p) for p in csv_paths],
        "domain": domain,
        "doc_name": doc_name,
        "quality": quality_stats,
        "table_qualities": table_qualities,
    }


def tables_to_jsonl_records(
    tables: list[dict],
    csv_paths: list[Path],
    domain: str,
    manifest_id: str,
) -> list[dict]:
    """Generate JSONL records linking tables to their CSV paths.

    These records are compatible with the tables promoter's expected input format.
    """
    records = []
    for table, csv_path in zip(tables, csv_paths):
        title = table.get("title")
        columns = table.get("columns", [])
        rows = table.get("rows", [])

        records.append({
            "title": title or f"Table from {manifest_id}",
            "columns": columns,
            "row_count": len(rows),
            "csv_path": str(csv_path),
            "domain": domain,
            "manifest": manifest_id,
            "source": table.get("source", {}),
        })

    return records
