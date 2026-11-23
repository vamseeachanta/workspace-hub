# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml"]
# ///
"""Audit extraction statistics from manifest YAML files."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import yaml


def audit_manifest(manifest_dict: dict[str, Any]) -> dict[str, Any]:
    """Compute stats for a single manifest dict."""
    metadata = manifest_dict.get("metadata", {})
    fmt = metadata.get("format", "unknown")
    domain = manifest_dict.get("domain", "unknown")
    sections = manifest_dict.get("sections", []) or []
    tables = manifest_dict.get("tables", []) or []
    figure_refs = manifest_dict.get("figure_refs", []) or []
    errors = manifest_dict.get("errors", []) or []
    return {
        "section_count": len(sections),
        "table_count": len(tables),
        "figure_ref_count": len(figure_refs),
        "error_count": len(errors),
        "format": fmt,
        "domain": domain,
        "errors": errors,
        "filename": metadata.get("filename", ""),
    }


def audit_directory(directory: str) -> dict[str, Any]:
    """Scan directory for *.manifest.yaml files and aggregate stats."""
    path = Path(directory)
    manifest_files = sorted(path.glob("*.manifest.yaml"))

    total_manifests = 0
    total_sections = 0
    total_tables = 0
    total_figure_refs = 0
    total_errors = 0
    format_breakdown: dict[str, int] = {}
    domain_breakdown: dict[str, int] = {}
    manifests_with_errors: list[dict[str, Any]] = []

    for manifest_file in manifest_files:
        with open(manifest_file, "r", encoding="utf-8") as fh:
            manifest_dict = yaml.safe_load(fh) or {}

        stats = audit_manifest(manifest_dict)
        total_manifests += 1
        total_sections += stats["section_count"]
        total_tables += stats["table_count"]
        total_figure_refs += stats["figure_ref_count"]
        total_errors += stats["error_count"]

        fmt = stats["format"]
        format_breakdown[fmt] = format_breakdown.get(fmt, 0) + 1

        domain = stats["domain"]
        domain_breakdown[domain] = domain_breakdown.get(domain, 0) + 1

        if stats["error_count"] > 0:
            manifests_with_errors.append({
                "filename": stats["filename"] or manifest_file.name,
                "error_count": stats["error_count"],
                "errors": stats["errors"],
            })

    if total_manifests > 0:
        avg_sections = total_sections / total_manifests
        avg_tables = total_tables / total_manifests
        error_rate = len(manifests_with_errors) / total_manifests
    else:
        avg_sections = 0.0
        avg_tables = 0.0
        error_rate = 0.0

    return {
        "total_manifests": total_manifests,
        "total_sections": total_sections,
        "total_tables": total_tables,
        "total_figure_refs": total_figure_refs,
        "total_errors": total_errors,
        "format_breakdown": format_breakdown,
        "domain_breakdown": domain_breakdown,
        "avg_sections_per_doc": avg_sections,
        "avg_tables_per_doc": avg_tables,
        "error_rate": error_rate,
        "manifests_with_errors": manifests_with_errors,
    }


def format_report(report: dict[str, Any]) -> str:
    """Pretty-print the report dict as human-readable text."""
    lines = [
        "Extraction Audit Report",
        "=" * 40,
        f"total_manifests:      {report['total_manifests']}",
        f"total_sections:       {report['total_sections']}",
        f"total_tables:         {report['total_tables']}",
        f"total_figure_refs:    {report['total_figure_refs']}",
        f"total_errors:         {report['total_errors']}",
        f"avg_sections_per_doc: {report['avg_sections_per_doc']:.2f}",
        f"avg_tables_per_doc:   {report['avg_tables_per_doc']:.2f}",
        f"error_rate:           {report['error_rate']:.2%}",
        "",
        "Format breakdown:",
    ]
    for fmt, count in sorted(report["format_breakdown"].items()):
        lines.append(f"  {fmt}: {count}")

    lines.append("\nDomain breakdown:")
    for domain, count in sorted(report["domain_breakdown"].items()):
        lines.append(f"  {domain}: {count}")

    if report["manifests_with_errors"]:
        lines.append("\nManifests with errors:")
        for entry in report["manifests_with_errors"]:
            lines.append(f"  {entry['filename']} ({entry['error_count']} errors)")

    return "\n".join(lines)


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Audit extraction statistics from manifest YAML files."
    )
    parser.add_argument("--directory", required=True, help="Directory containing manifest files")
    parser.add_argument("--output", help="Output file path (optional)")
    parser.add_argument(
        "--format",
        choices=["text", "yaml"],
        default="yaml",
        help="Output format (default: yaml)",
    )
    args = parser.parse_args()

    report = audit_directory(args.directory)

    if args.format == "text":
        output_str = format_report(report)
    else:
        output_str = yaml.dump(report, default_flow_style=False, sort_keys=True)

    if args.output:
        Path(args.output).write_text(output_str, encoding="utf-8")
        print(f"Report written to {args.output}")
    else:
        print(output_str)


if __name__ == "__main__":
    main()
