"""Build the structured evidence payload requested by issue #2110.

CLI: python scripts/workflow/session_close_report.py < evidence.json
Emits one compact JSON object followed by a newline; no files are written.

Input fields (all optional): timestamp (opaque string), tool_calls (total and
by_tool counts), gates (passed/failed/skipped counts), context (repository and
branch strings, issue string or integer), completion (string), next_steps
(list of strings). Missing or null evidence becomes an explicit unknown object.
Zero counts and empty strings/collections remain known. Unrecognized fields
are excluded. Counts must be nonnegative integers, excluding booleans; no total
is inferred or reconciled against partial per-tool evidence.

The existing presentation contract is declared in
scripts/workflow/build_session_review.py::_normalize_refs and render_session_html;
this payload does not claim renderer compatibility or change those declarations.
No policy thresholds are applied. Supplied gate counts are evidence, not a gate
verdict. No clock, logs, environment or repository state is consulted. Callers
remain responsible for publication eligibility of supplied strings.
"""
from __future__ import annotations

from collections.abc import Mapping
import json
import sys


def _unknown() -> dict:
    return {"state": "unknown", "reason": "not supplied"}


def _mapping(value, field: str) -> Mapping:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise ValueError(field)
    return value


def _count(value, field: str):
    if value is None:
        return _unknown()
    # Zero is the mathematical lower bound of a count, not a policy threshold.
    if type(value) is not int or value < 0:
        raise ValueError(field)
    return value


def _text(value, field: str):
    if value is None:
        return _unknown()
    if not isinstance(value, str):
        raise ValueError(field)
    return value


def build_report(mapping: Mapping) -> dict:
    """Return an independent JSON-ready snapshot; ValueError names only a field.

    Diagnostics for per-tool entries always name tool_calls.by_tool, never the
    caller-supplied key or value. Null input sections mean evidence is absent;
    the top-level input must itself be a mapping.
    """
    if not isinstance(mapping, Mapping):
        raise ValueError("input")
    tools = _mapping(mapping.get("tool_calls"), "tool_calls")
    gates = _mapping(mapping.get("gates"), "gates")
    context = _mapping(mapping.get("context"), "context")

    by_tool = tools.get("by_tool")
    if by_tool is None:
        tool_counts = _unknown()
    else:
        if not isinstance(by_tool, Mapping):
            raise ValueError("tool_calls.by_tool")
        tool_counts = {}
        for name, value in by_tool.items():
            if not isinstance(name, str) or not name:
                raise ValueError("tool_calls.by_tool")
            tool_counts[name] = _count(value, "tool_calls.by_tool")

    issue = context.get("issue")
    if issue is None:
        issue = _unknown()
    elif not isinstance(issue, str) and type(issue) is not int:
        raise ValueError("context.issue")

    next_steps = mapping.get("next_steps")
    if next_steps is None:
        next_steps = _unknown()
    elif not isinstance(next_steps, list) or any(not isinstance(step, str) for step in next_steps):
        raise ValueError("next_steps")
    else:
        next_steps = list(next_steps)

    return {
        "timestamp": _text(mapping.get("timestamp"), "timestamp"),
        "tool_calls": {
            "total": _count(tools.get("total"), "tool_calls.total"),
            "by_tool": tool_counts,
        },
        "gates": {field: _count(gates.get(field), f"gates.{field}")
                  for field in ("passed", "failed", "skipped")},
        "context": {
            "repository": _text(context.get("repository"), "context.repository"),
            "branch": _text(context.get("branch"), "context.branch"),
            "issue": issue,
        },
        "completion": _text(mapping.get("completion"), "completion"),
        "next_steps": next_steps,
    }


def _object(pairs: list[tuple]) -> dict:
    """Reject ambiguous duplicate JSON keys before evidence is lost."""
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("input")
        result[key] = value
    return result


def _nonfinite(_value: str):
    raise ValueError("input")


def main() -> int:
    """Read a single JSON mapping; emit no partial report on invalid evidence."""
    try:
        supplied = json.load(sys.stdin, object_pairs_hook=_object, parse_constant=_nonfinite)
    except (ValueError, UnicodeError, RecursionError):
        print("input", file=sys.stderr)
        return 1  # Conventional nonzero command failure; no policy threshold.
    try:
        result = build_report(supplied)
    except ValueError as error:
        print(str(error), file=sys.stderr)
        return 1
    print(json.dumps(result, sort_keys=True, separators=(",", ":"), allow_nan=False))
    return 0  # Conventional command success.


if __name__ == "__main__":
    sys.exit(main())
