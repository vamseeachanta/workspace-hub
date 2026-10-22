"""Summarize self-reported personal operations evidence without service access."""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from html import escape
from pathlib import Path

# Domain criteria: initiative 3609 and its linked epics, inspected 2026-10-22.
# Travel: comparison hub's trip parameters, cost recheck and open decisions.
# Media: epic 3589's extraction, integrity, off-site copy and sync decisions.
# Workspace: private-scope epic's membership and cross-scope privacy criteria.
# These are local summary criteria, not substitutes for the epics' full acceptance.
REQUIREMENTS = {
    "travel": ("surface", "parameters", "cost_basis", "decision"),
    "media": ("surface", "extraction", "integrity", "offsite", "sync_decision"),
    "workspace": ("surface", "boundary", "membership", "isolation"),
}
EVIDENCE_KEYS = {"result", "reference", "checked_at", "valid_until"}


def instant(value):
    """Require timezone-aware timestamps; compare instants, not local dates."""
    if not isinstance(value, str) or "T" not in value:
        raise ValueError("Invalid timestamp")
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        raise ValueError("Timezone required")
    return parsed


def observation(record, as_of):
    """Apply declared freshness; no default age limit is assumed."""
    if not isinstance(record, dict) or set(record) != EVIDENCE_KEYS:
        raise ValueError("Invalid evidence fields")
    if record["result"] not in ("pass", "fail", "unknown"):
        raise ValueError("Invalid result")
    reference = record["reference"]
    if not isinstance(reference, str) or not re.fullmatch(r"evidence-[a-z]+(?:-[a-z]+)*", reference):
        raise ValueError("Opaque evidence reference required")
    checked = instant(record["checked_at"])
    expiry = instant(record["valid_until"])
    # Data-handling contract: checked_at <= as_of < valid_until.
    if checked > as_of or expiry <= as_of or expiry <= checked:
        return "unknown"
    return record["result"]


def evaluate(data, as_of):
    """Return fixed labels only; declarations do not authenticate evidence."""
    now = instant(as_of)
    if not isinstance(data, dict) or set(data) - REQUIREMENTS.keys():
        raise ValueError("Invalid domains")
    rows = []
    for domain, required in REQUIREMENTS.items():
        if domain not in data:
            rows.append({"domain": domain, "status": "NOT_EVALUATED", "gaps": ["record"]})
            continue
        record = data[domain]
        if not isinstance(record, dict) or set(record) != {"state", "checks"}:
            raise ValueError("Invalid domain fields")
        if record["state"] not in ("active", "complete"):
            raise ValueError("Invalid state")
        checks = record["checks"]
        allowed = {*required, "terminal"}
        if not isinstance(checks, dict) or set(checks) - allowed:
            raise ValueError("Invalid checks")
        results = {key: observation(value, now) for key, value in checks.items()}
        needed = (*required, "terminal") if record["state"] == "complete" else required
        gaps = [key for key in needed if results.get(key) != "pass"]
        gaps.extend(key for key, value in results.items() if value == "fail" and key not in gaps)
        if "fail" in results.values():
            status = "BLOCKED"
        elif gaps:
            status = "NOT_EVALUATED"
        else:
            status = "COMPLETE" if record["state"] == "complete" else "ACTIVE"
        rows.append({"domain": domain, "status": status, "gaps": gaps})
    return rows


def render_html(rows, as_of):
    """Generate a portable static report with no private references or links."""
    assessment = escape(instant(as_of).isoformat())
    body = "".join(
        "<tr>" + "".join(f"<td>{escape(value)}</td>" for value in (
            row["domain"], row["status"], ", ".join(row["gaps"]) or "none",
        )) + "</tr>" for row in rows
    )
    return (
        '<!doctype html><html lang="en"><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        '<title>Personal operations evidence summary</title><body>'
        '<h1>Personal operations evidence summary</h1>'
        '<p>Summary of self-reported evidence at the supplied assessment time. '
        'Service availability, membership and evidence authenticity are not established.</p>'
        f'<p>Assessment time: {assessment}. Criteria: personal-operations-evidence-v1.</p>'
        '<h2>Revision history</h2><table><tr><th>Revision</th><th>Date</th>'
        '<th>Change and reason</th></tr>'
        f'<tr><td>Initial</td><td>{assessment}</td><td>Local evidence summary for review.'
        '</td></tr></table><p>Table: report revision.</p>'
        '<h2>Results</h2><table><thead><tr><th>Domain</th><th>Declared readiness</th>'
        f'<th>Missing or non-passing criteria</th></tr></thead><tbody>{body}</tbody></table>'
        '<p>Table: readiness against the local summary criteria.</p></body></html>\n'
    )


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate key")
        result[key] = value
    return result


def reject_constant(value):
    raise ValueError("Non-finite token")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--as-of", required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        data = json.loads(args.input.read_text(encoding="utf-8"),
                          object_pairs_hook=unique_object, parse_constant=reject_constant)
        rows = evaluate(data, args.as_of)
        if args.output:
            if args.output.resolve() == args.input.resolve():
                raise ValueError("Input cannot be overwritten")
            # Exclusive creation prevents replacement of existing records or reports.
            with args.output.open("x", encoding="utf-8") as stream:
                stream.write(render_html(rows, args.as_of))
        else:
            print(json.dumps({
                "basis": "self-reported", "criteria": "personal-operations-evidence-v1",
                "as_of": instant(args.as_of).isoformat(), "domains": rows,
            }, indent=2))
    except (ValueError, OSError, TypeError, OverflowError, RecursionError):
        print("Invalid input or inaccessible file.", file=sys.stderr)
        return 2
    return 0 if all(row["status"] == "COMPLETE" for row in rows) else 1


if __name__ == "__main__":
    sys.exit(main())
