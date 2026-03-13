"""Federated index builder — reads manifests, produces content-type JSONL indexes."""

import csv
import json
import os
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

import yaml

from scripts.data.doc_intelligence.classifiers import classify_section
from scripts.data.doc_intelligence.schema import (
    DocumentManifest,
    ExtractedSection,
    ExtractedTable,
    ExtractedFigureRef,
    manifest_from_dict,
)

CONTENT_TYPES = [
    "constants", "equations", "requirements",
    "procedures", "definitions", "worked_examples",
]


@dataclass
class BuildStats:
    """Summary of a build run."""

    manifests_processed: int = 0
    manifests_skipped: int = 0
    records_by_type: Dict[str, int] = field(default_factory=dict)
    tables_written: int = 0
    curves_written: int = 0


def _sanitize_ref(ref: str) -> str:
    """Strip path separators and traversal sequences from a manifest ref."""
    return re.sub(r"[/\\]", "_", ref).replace("..", "_")


def _source_dict(source) -> dict:
    d = {"document": source.document}
    if source.section is not None:
        d["section"] = source.section
    if source.page is not None:
        d["page"] = source.page
    if source.sheet is not None:
        d["sheet"] = source.sheet
    return d


def _section_record(section: ExtractedSection, domain: str, manifest: str) -> dict:
    return {
        "text": section.text,
        "source": _source_dict(section.source),
        "domain": domain,
        "manifest": manifest,
    }


def _write_jsonl_atomic(path: Path, records: List[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".jsonl.tmp")
    with open(tmp, "w") as fh:
        for r in records:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    os.replace(tmp, path)


def _write_csv(path: Path, columns: List[str], rows: List[List[str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".csv.tmp")
    with open(tmp, "w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(columns)
        writer.writerows(rows)
    os.replace(tmp, path)


def _load_checksum_map(manifest_index_path: Path) -> Dict[str, str]:
    """Load existing manifest-index.jsonl into {manifest_path: checksum}."""
    if not manifest_index_path.exists():
        return {}
    result = {}
    with open(manifest_index_path) as fh:
        for line in fh:
            line = line.strip()
            if line:
                rec = json.loads(line)
                result[rec["manifest_path"]] = rec["checksum"]
    return result


def build_indexes(
    manifest_dir: Path,
    output_dir: Path,
    force: bool = False,
    dry_run: bool = False,
    verbose: bool = False,
) -> BuildStats:
    """Build federated content indexes from manifest YAML files.

    Args:
        manifest_dir: Directory containing *.manifest.yaml files (recursive).
        output_dir: Where to write JSONL indexes and CSV files.
        force: Rebuild all manifests, ignoring checksums.
        dry_run: Scan only, don't write any files.
        verbose: Print per-manifest details.

    Returns:
        BuildStats with counts.
    """
    manifest_dir = Path(manifest_dir)
    output_dir = Path(output_dir)
    stats = BuildStats()

    # Load existing checksum map for incremental builds
    manifest_index_path = output_dir / "manifest-index.jsonl"
    existing_checksums = {} if force else _load_checksum_map(manifest_index_path)

    # Accumulators
    content_accumulators: Dict[str, List[dict]] = {ct: [] for ct in CONTENT_TYPES}
    table_index_records: List[dict] = []
    curve_index_records: List[dict] = []
    manifest_index_records: List[dict] = []

    # Find all manifests
    manifest_files = sorted(manifest_dir.rglob("*.manifest.yaml"))

    for mf_path in manifest_files:
        rel_path = str(mf_path.relative_to(manifest_dir))
        # Determine domain from directory structure
        parts = mf_path.relative_to(manifest_dir).parts
        domain_from_path = parts[0] if len(parts) > 1 else "unknown"

        # Load manifest
        raw = yaml.safe_load(mf_path.read_text())
        manifest = manifest_from_dict(raw)
        checksum = manifest.metadata.checksum or ""

        # Track whether this manifest changed (for stats + CSV rewrites)
        changed = force or existing_checksums.get(rel_path) != checksum
        if changed:
            stats.manifests_processed += 1
            if verbose:
                print(f"Processing: {rel_path}")
        else:
            stats.manifests_skipped += 1

        manifest_ref = _sanitize_ref(manifest.doc_ref or manifest.metadata.filename)
        counts = _count_manifest(manifest)

        # Classify sections
        type_counts: Dict[str, int] = {ct: 0 for ct in CONTENT_TYPES}
        for section in manifest.sections:
            ct = classify_section(section)
            if ct is None:
                continue
            record = _section_record(section, manifest.domain, manifest_ref)
            content_accumulators[ct].append(record)
            type_counts[ct] = type_counts.get(ct, 0) + 1

        # Tables → CSV + index
        for i, table in enumerate(manifest.tables):
            csv_rel = f"tables/{manifest_ref}-table-{i}.csv"
            if not dry_run and changed:
                _write_csv(
                    output_dir / csv_rel,
                    table.columns,
                    table.rows,
                )
            if changed:
                stats.tables_written += 1
            table_index_records.append({
                "title": table.title,
                "columns": table.columns,
                "row_count": len(table.rows),
                "csv_path": csv_rel,
                "source": _source_dict(table.source),
                "domain": manifest.domain,
                "manifest": manifest_ref,
            })

        # Figure refs → curves index
        for fig_ref in manifest.figure_refs:
            curve_index_records.append({
                "caption": fig_ref.caption,
                "figure_id": fig_ref.figure_id,
                "source": _source_dict(fig_ref.source),
                "domain": manifest.domain,
                "manifest": manifest_ref,
            })
            if changed:
                stats.curves_written += 1

        # Manifest index entry
        counts.update(type_counts)
        manifest_index_records.append({
            "manifest_path": rel_path,
            "domain": manifest.domain,
            "filename": manifest.metadata.filename,
            "checksum": checksum,
            "counts": counts,
            "indexed_at": datetime.now(timezone.utc).isoformat(),
        })

    # Record counts
    for ct in CONTENT_TYPES:
        stats.records_by_type[ct] = len(content_accumulators[ct])

    if dry_run:
        return stats

    # Write all JSONL indexes atomically
    _write_jsonl_atomic(manifest_index_path, manifest_index_records)

    for ct in CONTENT_TYPES:
        _write_jsonl_atomic(output_dir / f"{ct}.jsonl", content_accumulators[ct])

    # Tables index
    (output_dir / "tables").mkdir(parents=True, exist_ok=True)
    _write_jsonl_atomic(output_dir / "tables" / "index.jsonl", table_index_records)

    # Curves index
    (output_dir / "curves").mkdir(parents=True, exist_ok=True)
    _write_jsonl_atomic(output_dir / "curves" / "index.jsonl", curve_index_records)

    return stats


def _count_manifest(manifest: DocumentManifest) -> dict:
    return {
        "sections": len(manifest.sections),
        "tables": len(manifest.tables),
        "figure_refs": len(manifest.figure_refs),
    }
