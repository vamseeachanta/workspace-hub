"""Audit an explicit catalog snapshot without reading or copying source payloads.

This is a derived observation, never a catalog, rights decision or readiness
certificate. Basis: docs/architecture/agent-data-handling-contract.md, sections
Existing authorities and discovery, Original retention, rights and publication,
and Descriptor v1 and qualification. See corpus-readiness.md for the input
contract, format taxonomy, counting definitions and worked example.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

# Schema revision is a local serialization convention, not a numerical limit.
SCHEMA_VERSION = 1
# Observation labels only; no extractor support is implied. Taxonomy basis:
# docs/document-intelligence/corpus-readiness.md, Sources and scope.
FORMAT_FAMILIES = frozenset({
    "text", "markdown", "html", "code", "json", "csv", "spreadsheet",
    "pdf", "scanned_document", "word", "presentation", "email", "image",
    "cad", "solver_input", "solver_output", "database", "geospatial",
    "archive", "media", "other",
})
# Existing processing vocabulary is preserved verbatim per the data contract.
PROCESSING_STATES = frozenset({
    "gap", "indexed", "summarized", "extracted", "promoted", "superseded",
    "unreachable",
})
# Route vocabulary comes from the ingestion-wave contract; see documentation.
ROUTES = frozenset({
    "public_llm_wiki", "private_sidecar", "metadata_only", "excluded_no_ingest",
})
PRIVACY_STATES = frozenset({"public", "restricted", "unknown"})
EVIDENCE_FIELDS = frozenset({"method_ref", "fidelity_ref", "citation_ref", "rights_ref"})
IDENTITY_FIELDS = frozenset({"owner_repo", "source_id", "dataset_id"})
ROW_FIELDS = IDENTITY_FIELDS | {
    "format_family", "route", "privacy", "processing_status", "evidence",
}


class SnapshotError(ValueError):
    """Invalid snapshot; messages intentionally exclude source values and paths."""


def _mapping(value: Any, fields: set | frozenset, location: str) -> dict:
    if not isinstance(value, dict) or set(value) != fields:
        raise SnapshotError(f"{location}: invalid field set")
    return value


def _choice(value: Any, choices: set | frozenset, location: str) -> None:
    if not isinstance(value, str) or value not in choices:
        raise SnapshotError(f"{location}: invalid choice")


def _identity(value: Any, location: str) -> None:
    if not isinstance(value, str) or not value or value != value.strip():
        raise SnapshotError(f"{location}: expected nonempty unpadded identity")


def _unique_object(pairs: list[tuple[str, Any]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise SnapshotError("JSON: duplicate key")
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise SnapshotError("JSON: nonfinite value")


def load_snapshot(path: Path) -> dict:
    """Read only the explicit snapshot; never follow any evidence reference."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"),
                          object_pairs_hook=_unique_object,
                          parse_constant=_reject_constant)
    except SnapshotError:
        raise
    except (OSError, ValueError, RecursionError) as exc:
        raise SnapshotError("snapshot could not be read as strict UTF-8 JSON") from exc
    _validate(data)
    return data


def _validate(data: Any) -> None:
    _mapping(data, {"schema_version", "format_families", "sources"}, "snapshot")
    if type(data["schema_version"]) is not int or data["schema_version"] != SCHEMA_VERSION:
        raise SnapshotError("snapshot: unsupported schema version")
    families = data["format_families"]
    if not isinstance(families, list) or not families:
        raise SnapshotError("format_families: expected nonempty list")
    for family in families:
        _choice(family, FORMAT_FAMILIES, "format_families")
    if len(families) != len(set(families)):
        raise SnapshotError("format_families: duplicate family")
    if not isinstance(data["sources"], list):
        raise SnapshotError("sources: expected list")
    seen = set()
    for index, row in enumerate(data["sources"]):
        location = f"sources[{index}]"
        _mapping(row, ROW_FIELDS, location)
        for field in sorted(IDENTITY_FIELDS):
            _identity(row[field], f"{location}.{field}")
        identity = tuple(row[field] for field in sorted(IDENTITY_FIELDS))
        if identity in seen:
            raise SnapshotError(f"{location}: duplicate identity")
        seen.add(identity)
        for field, choices in (
            ("format_family", set(families)), ("route", ROUTES),
            ("privacy", PRIVACY_STATES), ("processing_status", PROCESSING_STATES),
        ):
            _choice(row[field], choices, f"{location}.{field}")
        evidence = _mapping(row["evidence"], EVIDENCE_FIELDS, f"{location}.evidence")
        for field in sorted(EVIDENCE_FIELDS):
            value = evidence[field]
            if value is not None and not isinstance(value, str):
                raise SnapshotError(f"{location}.evidence.{field}: expected string or null")


def audit_snapshot(data: dict) -> dict:
    """Return aggregate evidence counts; source metadata never enters the output.

    Evidence completeness means presence of references only. Neither evidence
    integrity nor permissions, freshness, extraction accuracy, source coverage or
    computational qualification is established by this audit.
    """
    _validate(data)
    formats = {}
    for family in sorted(data["format_families"]):
        formats[family] = {
            "record_count": 0,
            "evidence_complete_count": 0,
            "incomplete_count": 0,
            "route_conflict_count": 0,
            "processing_counts": dict.fromkeys(sorted(PROCESSING_STATES), 0),
            "route_counts": dict.fromkeys(sorted(ROUTES), 0),
            "missing_evidence_counts": dict.fromkeys(sorted(EVIDENCE_FIELDS), 0),
        }
    for row in data["sources"]:
        counts = formats[row["format_family"]]
        counts["record_count"] += 1
        counts["processing_counts"][row["processing_status"]] += 1
        counts["route_counts"][row["route"]] += 1
        missing = [field for field in sorted(EVIDENCE_FIELDS)
                   if not (row["evidence"][field] or "").strip()]
        for field in missing:
            counts["missing_evidence_counts"][field] += 1
        conflict = row["route"] == "public_llm_wiki" and row["privacy"] != "public"
        counts["route_conflict_count"] += int(conflict)
        complete = (
            not missing and not conflict
            and row["route"] in {"public_llm_wiki", "private_sidecar"}
            and row["processing_status"] in {"extracted", "promoted"}
        )
        counts["evidence_complete_count"] += int(complete)
        counts["incomplete_count"] += int(not complete)
    # Integer counting identities, not fitted equations or acceptance thresholds:
    # total = sum of per-format counts; incomplete = total - complete.
    # Independent hand-count oracle is in test_corpus_readiness.test_worked_example.
    report = {
        "schema_version": SCHEMA_VERSION,
        "qualification": "NOT_EVALUATED",
        "formats": formats,
        "declared_format_count": len(formats),
        "unobserved_format_count": sum(c["record_count"] == 0 for c in formats.values()),
        "formats_with_complete_evidence": sum(
            c["evidence_complete_count"] > 0 for c in formats.values()
        ),
    }
    for key in ("record_count", "evidence_complete_count", "incomplete_count",
                "route_conflict_count"):
        report[key] = sum(c[key] for c in formats.values())
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("snapshot", type=Path, help="explicit JSON catalog observation")
    args = parser.parse_args(argv)
    try:
        report = audit_snapshot(load_snapshot(args.snapshot))
    except (SnapshotError, RecursionError) as exc:
        # Recursion errors are generic; do not include Python object representations.
        message = str(exc) if isinstance(exc, SnapshotError) else "snapshot nesting is invalid"
        print(f"ERROR: {message}", file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
