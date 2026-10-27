"""Format caller-supplied read observations as a deterministic JSON inventory.

Scope: issue #2180, lineage/provenance reporting only. Normalization and final
classification remain with normalize_repo_alias and classify_read_target in
scripts/analysis/provider_session_ecosystem_audit.py. This module never calls
them, consults the registry, checks target existence or evaluates suppression.
No policy thresholds, expiry rules or eligibility decisions are introduced.

Input is an array of traces with raw_token, ordered steps and disposition.
Each step has kind, input and output; candidates and evidence are optional.
Trace evidence is also optional. Evidence has state and optional reason and
references. Labels are opaque codes; tokens and references must be relative
synthetic POSIX tokens. Null tokens, dispositions, evidence and reference lists
retain unknown observations. Missing optional fields remain missing.

The caller must supply authorized synthetic observations, with no identifying
names or raw transcript excerpts. Arbitrary metadata and prose are rejected,
not silently discarded. Relative syntax alone does not establish anonymity.
Only inventory rows and object keys are sorted. Steps, repeated observations,
candidate order, recorded cycles and unknown dispositions remain unchanged.
Cycles are reported as supplied evidence, never inferred or traversed.

CLI: read_lineage_report.py [input.json], or supply the trace array on stdin.
The inventory is emitted on stdout; errors never echo input or filesystem paths.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


_LABEL = re.compile(r"[a-z][a-z0-9_-]*\Z")
_TOKEN = re.compile(r"[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)*\Z")


def _fields(value: object, required: set[str], optional: set[str]) -> dict:
    if (not isinstance(value, dict) or not required <= value.keys()
            or value.keys() - required - optional):
        raise ValueError("invalid observation fields")
    return value


def _label(value: object, *, unknown: bool = False) -> str | None:
    if unknown and value is None:
        return None
    if not isinstance(value, str) or not _LABEL.fullmatch(value):
        raise ValueError("invalid observation label")
    return value


def _token(value: object) -> str | None:
    if value is None:
        return None
    if (not isinstance(value, str) or not _TOKEN.fullmatch(value)
            or ".." in value.split("/")):
        raise ValueError("invalid relative token")
    return value


def _tokens(value: object) -> list[str] | None:
    if value is None:
        return None
    if not isinstance(value, list) or any(item is None for item in value):
        raise ValueError("invalid token list")
    return [_token(item) for item in value]


def _evidence(value: object) -> dict | None:
    if value is None:
        return None
    evidence = _fields(value, {"state"}, {"reason", "references"})
    result = {"state": _label(evidence["state"])}
    if "reason" in evidence:
        result["reason"] = _label(evidence["reason"])
    if "references" in evidence:
        result["references"] = _tokens(evidence["references"])
    return result


def _step(value: object) -> dict:
    step = _fields(value, {"kind", "input", "output"}, {"candidates", "evidence"})
    result = {
        "kind": _label(step["kind"]),
        "input": _token(step["input"]),
        "output": _token(step["output"]),
    }
    if "candidates" in step:
        result["candidates"] = _tokens(step["candidates"])
    if "evidence" in step:
        result["evidence"] = _evidence(step["evidence"])
    return result


def _trace(value: object) -> dict:
    trace = _fields(value, {"raw_token", "steps", "disposition"}, {"evidence"})
    if not isinstance(trace["steps"], list):
        raise ValueError("invalid recorded steps")
    result = {
        "raw_token": _token(trace["raw_token"]),
        "steps": [_step(step) for step in trace["steps"]],
        "disposition": _label(trace["disposition"], unknown=True),
    }
    if "evidence" in trace:
        result["evidence"] = _evidence(trace["evidence"])
    return result


def build_inventory(traces) -> dict:
    """Copy and sort an iterable of traces without altering recorded evidence.

    Rows sort by raw token (unknown first), then their complete JSON content to
    break ties independently of input order. Duplicate rows are retained.
    The result is detached from the input, including nested lists and mappings.
    """
    if isinstance(traces, (str, bytes, dict)):
        raise ValueError("invalid trace inventory")
    try:
        rows = [_trace(trace) for trace in traces]
    except TypeError as exc:
        raise ValueError("invalid trace inventory") from exc
    rows.sort(key=lambda row: (row["raw_token"] or "", json.dumps(row, sort_keys=True)))
    return {"traces": rows}


def render_json(traces) -> str:
    """Render sorted keys with a final newline; ordered evidence stays ordered."""
    return json.dumps(build_inventory(traces), sort_keys=True, indent=2, allow_nan=False) + "\n"


def _unique_object(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate input field")
        result[key] = value
    return result


def _invalid_constant(value: str) -> None:
    raise ValueError("non-finite input")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="read_lineage_report.py", description=__doc__)
    parser.add_argument("input", nargs="?", help="JSON trace array; omit to read stdin")
    args = parser.parse_args(argv)
    try:
        raw = Path(args.input).read_text(encoding="utf-8") if args.input else sys.stdin.read()
        traces = json.loads(raw, object_pairs_hook=_unique_object, parse_constant=_invalid_constant)
        if not isinstance(traces, list):
            raise ValueError("invalid trace inventory")
        output = render_json(traces)
    except (OSError, UnicodeError, ValueError, RecursionError):
        print("invalid lineage input", file=sys.stderr)
        return 1
    sys.stdout.write(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
