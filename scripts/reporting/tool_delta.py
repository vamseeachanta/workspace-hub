"""Compare caller-supplied normalized tool states without collecting evidence.

Contract revision ``1.0`` is defined here and by the literal examples in
``tests/reporting/test_tool_delta.py``. Inputs are lists of dictionaries with
exactly ``role``, ``tool`` and ``state`` string fields. Identities are exact,
case-sensitive (role, tool) pairs, with printable, nonempty, trimmed text.
States are ``installed``, ``usable``, ``failed`` and ``missing_evidence``.
Callers must normalize evidence into these states before comparison; this module
does not authenticate evidence, read files, run probes or infer freshness.

``compare_tools(current, previous=None)`` returns a versioned dictionary with
``baseline`` (``missing`` or ``available``) and sorted ``records``. Each output
record contains the identity, previous/current states (null for absence), change,
severity and a stable reason code. Every identity in either run is included,
including unchanged records. Missing prior data produces ``NO_BASELINE`` even
when current evidence is usable; an empty prior list is an available baseline.

Classification rules, in precedence order:
* Missing baseline -> no_baseline / NO_BASELINE.
* Absent identity -> added / TOOL_ADDED or removed / TOOL_REMOVED.
* Current missing evidence -> unknown / EVIDENCE_MISSING, including repeated gaps.
* Previous missing evidence -> unknown / EVIDENCE_RESTORED, never improvement.
* Equal observed states -> unchanged / STATE_UNCHANGED.
* Observed failure -> regressed / TOOL_FAILED.
* Failure to usability -> recovered / TOOL_RECOVERED.
* Installation to usability -> improved / TOOL_PROMOTED.
* Usability to installation -> regressed / USABILITY_LOST.
* Failure to installation -> unknown / RECOVERY_UNCONFIRMED.

Severity is error for any current failed check, warning for removal, evidence
loss, usability loss or unconfirmed recovery, and info for other observed states.
A missing baseline has unknown severity unless the current check has failed.
Membership changes alone imply neither recovery nor regression. Removing a failed
tool does not prove recovery; installation alone does not prove usability.

``render_json`` and ``render_markdown`` serialize a comparison result, returning
text with a final newline. JSON keys and identity rows have stable ordering;
there are no timestamps, generated identifiers or environment-dependent values.
Markdown cells escape HTML and Markdown punctuation. Persistence and publication
are the caller's responsibility; inputs and caller files remain untouched.
"""

from __future__ import annotations

import html
import json
import string
from typing import Any


STATES = frozenset({"installed", "usable", "failed", "missing_evidence"})
FIELDS = frozenset({"role", "tool", "state"})


def _index(records: Any, source: str) -> dict[tuple[str, str], str]:
    """Validate a complete run before comparison; never echo rejected values."""
    if not isinstance(records, list):
        raise ValueError(f"{source}: expected a list")
    indexed = {}
    for record in records:
        if not isinstance(record, dict):
            raise ValueError(f"{source}: expected a record")
        if record.keys() != FIELDS:
            raise ValueError(f"{source}: expected role, tool and state")
        for field in ("role", "tool"):
            value = record[field]
            if (
                not isinstance(value, str)
                or not value
                or value.strip() != value
                or not value.isprintable()
            ):
                raise ValueError(f"{source}: invalid {field}")
        state = record["state"]
        if not isinstance(state, str) or state not in STATES:
            raise ValueError(f"{source}: invalid state")
        identity = (record["role"], record["tool"])
        if identity in indexed:
            raise ValueError(f"{source}: duplicate role/tool identity")
        indexed[identity] = state
    return indexed


def _classify(before: str | None, after: str | None, baseline: bool) -> tuple[str, str, str]:
    """Return change, stable reason code and severity for validated states."""
    observed_severity = "error" if after == "failed" else "info"
    if not baseline:
        return "no_baseline", "NO_BASELINE", "error" if after == "failed" else "unknown"
    if after is None:
        return "removed", "TOOL_REMOVED", "warning"
    if before is None:
        severity = "warning" if after == "missing_evidence" else observed_severity
        return "added", "TOOL_ADDED", severity
    if after == "missing_evidence":
        return "unknown", "EVIDENCE_MISSING", "warning"
    if before == "missing_evidence":
        return "unknown", "EVIDENCE_RESTORED", observed_severity
    if before == after:
        return "unchanged", "STATE_UNCHANGED", observed_severity
    if after == "failed":
        return "regressed", "TOOL_FAILED", "error"
    if after == "usable":
        if before == "failed":
            return "recovered", "TOOL_RECOVERED", "info"
        return "improved", "TOOL_PROMOTED", "info"
    if before == "usable":
        return "regressed", "USABILITY_LOST", "warning"
    return "unknown", "RECOVERY_UNCONFIRMED", "warning"


def compare_tools(current: list[dict], previous: list[dict] | None = None) -> dict:
    """Return the deterministic union of two runs; None means no prior run.

    Raise ValueError for malformed records or duplicate identities in either
    run. Validation completes before constructing any output. Neither input is
    mutated, sorted in place or retained in the returned result.
    """
    after = _index(current, "current")
    baseline = previous is not None
    before = _index(previous, "previous") if baseline else {}
    rows = []
    for role, tool in sorted(before.keys() | after.keys()):
        old = before.get((role, tool))
        new = after.get((role, tool))
        change, reason, severity = _classify(old, new, baseline)
        rows.append({
            "role": role,
            "tool": tool,
            "previous": old,
            "current": new,
            "change": change,
            "reason_code": reason,
            "severity": severity,
        })
    return {
        "schema_version": "1.0",
        "baseline": "available" if baseline else "missing",
        "records": rows,
    }


def render_json(result: dict) -> str:
    """Serialize compare_tools output, using the literal example's indentation."""
    # Two-space layout is specified by test_literal_json_and_markdown_examples.
    return json.dumps(result, sort_keys=True, indent=2, ensure_ascii=False, allow_nan=False) + "\n"


def _cell(value: str | None) -> str:
    if value is None:
        return "absent"
    # Escape punctuation in the original text so generated HTML entities remain
    # intact. This also prevents automatic links from interpreting URL text.
    return "".join(
        html.escape(char, quote=True) if char in "&<>\"'"
        else "\\" + char if char in string.punctuation else char
        for char in value
    )


def render_markdown(result: dict) -> str:
    """Render compare_tools output as a table of escaped literal text."""
    lines = ["# Tool delta", "", f"Baseline: {result['baseline']}.", ""]
    if result["baseline"] == "missing":
        lines.extend(["No baseline; no improvement can be inferred.", ""])
    if not result["records"]:
        lines.append("No tool records.")
    else:
        lines.extend([
            "| Role | Tool | Previous | Current | Change | Severity | Reason |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ])
        fields = ("role", "tool", "previous", "current", "change", "severity", "reason_code")
        for row in result["records"]:
            lines.append("| " + " | ".join(_cell(row[field]) for field in fields) + " |")
    return "\n".join(lines) + "\n"
