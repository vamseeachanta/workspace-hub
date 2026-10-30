"""Evaluate a delivery evidence snapshot without changing its source registers.

Basis: docs/gtm/delivery-readiness.md, version 1. Engineering qualification,
source rights, freshness and actual artifact bytes remain NOT_EVALUATED.
"""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path
from typing import Any

# Local vocabulary and JSON version: delivery-readiness.md, Contract v1.
STAGES = ("geometry", "case", "results", "report")
TERMINAL = {"won", "lost", "declined", "withdrawn"}
TOKEN = re.compile(r"[a-z][a-z0-9_-]*")
LOCATOR = re.compile(r"[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)*")
# Digest syntax: agent-data-handling-contract.md, stable projection contract.
DIGEST = re.compile(r"[0-9a-f]{64}")


class SnapshotError(ValueError):
    """Invalid snapshot; diagnostics identify fields without echoing values."""


def _record(value: Any, keys: set[str], field: str) -> dict:
    if not isinstance(value, dict) or set(value) != keys:
        raise SnapshotError(f"{field}: incorrect fields")
    return value


def _rows(value: Any, field: str, *, allow_empty: bool = False) -> list:
    if not isinstance(value, list) or (not value and not allow_empty):
        raise SnapshotError(f"{field}: expected list")
    return value


def _text(value: Any, pattern: re.Pattern, field: str, *, nullable: bool = False) -> None:
    if value is None and nullable:
        return
    if not isinstance(value, str) or not pattern.fullmatch(value):
        raise SnapshotError(f"{field}: invalid text")


def _locator(value: Any, field: str) -> None:
    _text(value, LOCATOR, field, nullable=True)
    if value is not None and any(part in {".", ".."} for part in value.split("/")):
        raise SnapshotError(f"{field}: relative locator required")


def _unique(value: str, seen: set[str], field: str) -> None:
    if value in seen:
        raise SnapshotError(f"{field}: duplicate record")
    seen.add(value)


def validate(snapshot: Any) -> dict:
    """Validate the complete v1 structure; do not mutate or resolve locators."""
    data = _record(snapshot, {"schema_version", "capabilities", "artifacts", "pursuits"}, "snapshot")
    if type(data["schema_version"]) is not int or data["schema_version"] != 1:
        raise SnapshotError("schema_version: expected version 1")
    seen: set[str] = set()
    for index, raw in enumerate(_rows(data["capabilities"], "capabilities")):
        field = f"capabilities[{index}]"
        row = _record(raw, {"id", "workflow_ref", "criteria_ref", "inputs"}, field)
        _text(row["id"], TOKEN, field + ".id")
        _unique(row["id"], seen, field)
        for key in ("workflow_ref", "criteria_ref"):
            _locator(row[key], field + "." + key)
        inputs: set[str] = set()
        for offset, raw_input in enumerate(_rows(row["inputs"], field + ".inputs")):
            input_field = f"{field}.inputs[{offset}]"
            item = _record(raw_input, {"id", "state", "evidence_ref", "acquisition_ref"}, input_field)
            _text(item["id"], TOKEN, input_field + ".id")
            _unique(item["id"], inputs, input_field)
            if item["state"] not in ("available", "missing", "unknown"):
                raise SnapshotError(input_field + ".state: invalid state")
            for key in ("evidence_ref", "acquisition_ref"):
                _locator(item[key], input_field + "." + key)
    seen = set()
    for index, raw in enumerate(_rows(data["artifacts"], "artifacts", allow_empty=True)):
        field = f"artifacts[{index}]"
        row = _record(raw, {"stage", "ref", "revision", "sha256", "upstream_sha256"}, field)
        if row["stage"] not in STAGES:
            raise SnapshotError(field + ".stage: invalid stage")
        _unique(row["stage"], seen, field)
        _locator(row["ref"], field + ".ref")
        _text(row["revision"], LOCATOR, field + ".revision", nullable=True)
        for key in ("sha256", "upstream_sha256"):
            _text(row[key], DIGEST, field + "." + key, nullable=True)
        if row["stage"] == "geometry" and row["upstream_sha256"] is not None:
            raise SnapshotError(field + ".upstream_sha256: geometry has no upstream stage")
    seen = set()
    for index, raw in enumerate(_rows(data["pursuits"], "pursuits")):
        field = f"pursuits[{index}]"
        row = _record(raw, {"id", "state", "evidence_ref", "next_action_ref"}, field)
        _text(row["id"], TOKEN, field + ".id")
        _unique(row["id"], seen, field)
        if row["state"] not in (*TERMINAL, "active"):
            raise SnapshotError(field + ".state: invalid state")
        for key in ("evidence_ref", "next_action_ref"):
            _locator(row[key], field + "." + key)
    return data


def _status(findings: list[dict]) -> str:
    """Contract v1: known gaps dominate uncertainty; neither is completeness."""
    if any(item["status"] == "GAPS" for item in findings):
        return "GAPS"
    return "NOT_EVALUATED" if findings else "RECORDED"


def evaluate(snapshot: Any) -> dict:
    """Check recorded completeness and digest links, never engineering fitness."""
    data = validate(snapshot)
    findings: list[dict] = []

    def add(scope: str, identifier: str, status: str, reason: str, action: str | None = None):
        findings.append({"scope": scope, "id": identifier, "status": status,
                         "reason": reason, "action_ref": action})

    capabilities = []
    for row in data["capabilities"]:
        start = len(findings)
        for key in ("workflow_ref", "criteria_ref"):
            if row[key] is None:
                add("capability", row["id"], "NOT_EVALUATED", key + "_absent")
        for item in row["inputs"]:
            identifier = row["id"] + "/" + item["id"]
            if item["state"] == "missing":
                add("input", identifier, "GAPS", "input_missing", item["acquisition_ref"])
            elif item["state"] == "unknown":
                add("input", identifier, "NOT_EVALUATED", "input_unknown", item["acquisition_ref"])
            elif item["evidence_ref"] is None:
                add("input", identifier, "NOT_EVALUATED", "input_evidence_absent", item["acquisition_ref"])
        capabilities.append({"id": row["id"], "status": _status(findings[start:])})

    start = len(findings)
    artifacts = {row["stage"]: row for row in data["artifacts"]}
    previous = None
    for stage in STAGES:
        artifact = artifacts.get(stage)
        if artifact is None:
            add("delivery", stage, "GAPS", "artifact_absent")
        else:
            for key in ("ref", "revision", "sha256"):
                if artifact[key] is None:
                    add("delivery", stage, "NOT_EVALUATED", key + "_absent")
            if previous is not None:
                upstream = artifacts.get(previous)
                expected = upstream["sha256"] if upstream else None
                actual = artifact["upstream_sha256"]
                if expected is None or actual is None:
                    add("delivery", stage, "NOT_EVALUATED", "upstream_digest_unknown")
                elif actual != expected:
                    add("delivery", stage, "GAPS", "upstream_digest_mismatch")
        previous = stage
    delivery = {"status": _status(findings[start:])}

    pursuits = []
    for row in data["pursuits"]:
        start = len(findings)
        if row["state"] == "active":
            add("pursuit", row["id"], "GAPS", "pursuit_open", row["next_action_ref"])
        elif row["evidence_ref"] is None:
            add("pursuit", row["id"], "NOT_EVALUATED", "outcome_evidence_absent")
        pursuits.append({"id": row["id"], "status": _status(findings[start:])})
    return {
        "schema_version": 1,
        "status": _status(findings),
        "engineering_status": "NOT_EVALUATED",
        "capabilities": capabilities,
        "delivery": delivery,
        "pursuits": pursuits,
        "findings": findings,
        "counts": {
            "capabilities": len(data["capabilities"]),
            "inputs": sum(len(row["inputs"]) for row in data["capabilities"]),
            "artifacts": len(data["artifacts"]),
            "pursuits": len(data["pursuits"]),
            "findings": len(findings),
        },
    }


def _pairs(pairs: list[tuple]) -> dict:
    result: dict = {}
    for key, value in pairs:
        if key in result:
            raise SnapshotError("snapshot: duplicate JSON field")
        result[key] = value
    return result


def _nonfinite(value: str) -> None:
    raise SnapshotError("snapshot: non-finite JSON value")


def load_snapshot(path: Path) -> dict:
    """Reject duplicate keys and non-finite JSON before structural validation."""
    try:
        text = path.read_text(encoding="utf-8")
        data = json.loads(text, object_pairs_hook=_pairs, parse_constant=_nonfinite)
    except (OSError, UnicodeError, ValueError, RecursionError) as exc:
        raise SnapshotError("snapshot: unreadable or invalid JSON") from exc
    return validate(data)


def render_html(result: dict) -> str:
    """Render an inert, escaped snapshot report, with no external resources."""
    payload = html.escape(json.dumps(result, indent=2, sort_keys=True))
    status = html.escape(result["status"])
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>Delivery evidence snapshot</title></head>
<body><h1>Delivery evidence snapshot</h1>
<h2>Summary</h2><p>Recorded completeness: {status}. Engineering: NOT_EVALUATED.</p>
<h2>Revision history</h2>
<table><tr><th>Revision</th><th>Date</th><th>Change and reason</th></tr>
<tr><td>Unissued</td><td>Not issued</td><td>Snapshot rendered for evidence review.</td></tr></table>
<h2>Evidence findings</h2><pre>{payload}</pre>
<p>References and hashes are supplied assertions. Artifact bytes, rights,
freshness and engineering suitability require independent review.</p></body></html>
"""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("snapshot", type=Path)
    parser.add_argument("--format", choices=("json", "html"), default="json")
    args = parser.parse_args(argv)
    try:
        result = evaluate(load_snapshot(args.snapshot))
    except SnapshotError as exc:
        print(str(exc), file=sys.stderr)
        return 2  # Contract v1 CLI: invalid input, no output report.
    print(render_html(result) if args.format == "html" else json.dumps(result, indent=2))
    return 0 if result["status"] == "RECORDED" else 1  # Contract v1 completeness only.


if __name__ == "__main__":
    raise SystemExit(main())
