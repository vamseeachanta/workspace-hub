# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml"]
# ///
"""Merge multiple DocumentManifest YAML files and deduplicate by content hash.

Usage:
    uv run --no-project python scripts/data/doc_intelligence/deduplicate_manifests.py \\
        --inputs "path/to/*.yaml" [path/to/other.yaml ...] \\
        [--output merged.yaml]

Dedup stats are printed to stderr. Merged manifest is written to --output or
emitted to stdout if --output is omitted.
"""

import argparse
import glob
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any

import yaml


# ---------------------------------------------------------------------------
# Hashing helpers
# ---------------------------------------------------------------------------


def compute_section_hash(section: dict) -> str:
    """SHA256 hash of heading+text, truncated to 16 chars."""
    heading = section.get("heading") or ""
    text = section.get("text") or ""
    raw = f"{heading}\x00{text}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def compute_table_hash(table: dict) -> str:
    """SHA256 hash of columns+rows, truncated to 16 chars."""
    columns = table.get("columns") or []
    rows = table.get("rows") or []
    raw = json.dumps({"columns": columns, "rows": rows}, sort_keys=True)
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def _compute_figure_hash(figure: dict) -> str:
    """SHA256 hash of caption+figure_id, truncated to 16 chars."""
    caption = figure.get("caption") or ""
    figure_id = figure.get("figure_id") or ""
    raw = f"{caption}\x00{figure_id}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


# ---------------------------------------------------------------------------
# Deduplication
# ---------------------------------------------------------------------------


def deduplicate_sections(sections: list[dict]) -> list[dict]:
    """Remove duplicate sections by content hash. Keep first occurrence."""
    seen: set[str] = set()
    result = []
    for section in sections:
        h = compute_section_hash(section)
        if h not in seen:
            seen.add(h)
            result.append(section)
    return result


def deduplicate_tables(tables: list[dict]) -> list[dict]:
    """Remove duplicate tables by content hash. Keep first occurrence."""
    seen: set[str] = set()
    result = []
    for table in tables:
        h = compute_table_hash(table)
        if h not in seen:
            seen.add(h)
            result.append(table)
    return result


def _deduplicate_figure_refs(figure_refs: list[dict]) -> list[dict]:
    """Remove duplicate figure refs by content hash. Keep first occurrence."""
    seen: set[str] = set()
    result = []
    for fig in figure_refs:
        h = _compute_figure_hash(fig)
        if h not in seen:
            seen.add(h)
            result.append(fig)
    return result


# ---------------------------------------------------------------------------
# Merge
# ---------------------------------------------------------------------------


def merge_manifests(manifest_dicts: list[dict]) -> dict:
    """Merge list of manifest dicts into one.

    Combines all sections, tables, figure_refs; deduplicates each.
    Metadata gets a `source_count` field. Returns merged dict.
    """
    if not manifest_dicts:
        return {
            "version": "1.0.0",
            "tool": "deduplicate_manifests",
            "domain": "",
            "metadata": {"filename": "merged", "format": "merged", "size_bytes": 0, "source_count": 0},
            "sections": [],
            "tables": [],
            "figure_refs": [],
            "extraction_stats": {},
            "errors": [],
        }

    # Use first manifest as the base for top-level fields
    base = manifest_dicts[0]

    all_sections: list[dict] = []
    all_tables: list[dict] = []
    all_figure_refs: list[dict] = []

    for m in manifest_dicts:
        all_sections.extend(m.get("sections") or [])
        all_tables.extend(m.get("tables") or [])
        all_figure_refs.extend(m.get("figure_refs") or [])

    deduped_sections = deduplicate_sections(all_sections)
    deduped_tables = deduplicate_tables(all_tables)
    deduped_figure_refs = _deduplicate_figure_refs(all_figure_refs)

    # Build merged metadata from base, adding source_count
    merged_meta: dict[str, Any] = dict(base.get("metadata") or {})
    merged_meta["source_count"] = len(manifest_dicts)

    return {
        "version": base.get("version", "1.0.0"),
        "tool": base.get("tool", "deduplicate_manifests"),
        "domain": base.get("domain", ""),
        "metadata": merged_meta,
        "sections": deduped_sections,
        "tables": deduped_tables,
        "figure_refs": deduped_figure_refs,
        "extraction_stats": {},
        "errors": [],
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _resolve_inputs(raw_inputs: list[str]) -> list[Path]:
    """Expand globs and deduplicate input file paths."""
    paths: list[Path] = []
    seen: set[Path] = set()
    for pattern in raw_inputs:
        expanded = glob.glob(pattern, recursive=True)
        if expanded:
            for p in sorted(expanded):
                path = Path(p)
                if path not in seen:
                    seen.add(path)
                    paths.append(path)
        else:
            # Treat as literal path even if it doesn't glob-match
            path = Path(pattern)
            if path not in seen:
                seen.add(path)
                paths.append(path)
    return paths


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Merge and deduplicate DocumentManifest YAML files."
    )
    parser.add_argument(
        "--inputs",
        nargs="+",
        required=True,
        help="Glob pattern(s) or explicit file paths to input YAML manifests.",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output path for merged YAML. Defaults to stdout.",
    )
    args = parser.parse_args()

    input_paths = _resolve_inputs(args.inputs)
    if not input_paths:
        print("ERROR: no input files found.", file=sys.stderr)
        sys.exit(1)

    manifest_dicts: list[dict] = []
    for path in input_paths:
        with path.open() as fh:
            manifest_dicts.append(yaml.safe_load(fh))

    # Pre-merge counts for stats
    total_sections = sum(len(m.get("sections") or []) for m in manifest_dicts)
    total_tables = sum(len(m.get("tables") or []) for m in manifest_dicts)
    total_figures = sum(len(m.get("figure_refs") or []) for m in manifest_dicts)

    merged = merge_manifests(manifest_dicts)

    # Stats
    deduped_sections = len(merged["sections"])
    deduped_tables = len(merged["tables"])
    deduped_figures = len(merged["figure_refs"])

    print(
        f"Merged {len(manifest_dicts)} manifest(s): "
        f"sections {total_sections}->{deduped_sections} "
        f"({total_sections - deduped_sections} dupes removed), "
        f"tables {total_tables}->{deduped_tables} "
        f"({total_tables - deduped_tables} dupes removed), "
        f"figure_refs {total_figures}->{deduped_figures} "
        f"({total_figures - deduped_figures} dupes removed).",
        file=sys.stderr,
    )

    output_yaml = yaml.dump(merged, default_flow_style=False, sort_keys=False)

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        tmp = out_path.with_suffix(".yaml.tmp")
        tmp.write_text(output_yaml)
        os.replace(tmp, out_path)
        print(f"Written to {out_path}", file=sys.stderr)
    else:
        sys.stdout.write(output_yaml)


if __name__ == "__main__":
    main()
