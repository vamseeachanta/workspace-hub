"""Render a review view from explicit synthetic JSON inputs; perform no probes.

Registry input is a mapping from synthetic role keys to records containing
``task_classes``, ``auth_expectations``, ``required_clis`` and ``verification_refs``.
Each field is a list of nonblank strings. Only required_clis may be empty.
Additional inventory fields are ignored. This projection does not enforce or
migrate the workstation registry schema.

Evidence input is a mapping from those same role keys to summary records with
exactly ``status`` and ``verification_refs``. Status uses the evidence-bundle
check vocabulary (pass, warn, fail, error, skip), plus unverified for absent
qualification. References must be nonempty. Summaries are validated here for
shape and coverage only; their authenticity, freshness and source validation
remain the caller's responsibility. A summary does not establish readiness.
Missing summaries or incomplete reference coverage stay unverified.

Rows and set-valued fields are sorted, with duplicate field values collapsed.
No runtime timestamp, environment lookup, registry discovery or tool execution
is used. HTML renders references as escaped text, never executable links.

Example invocation (all inputs must be synthetic):
    python scripts/reporting/readiness_matrix_view.py \
        --registry synthetic-registry.json --evidence synthetic-evidence.json \
        --output matrix.json --format json

Run again with --format html and a distinct explicit output for the HTML view.
Outputs are exclusively created: existing files, symlinks and hardlinks are
never replaced. Validation finishes before opening an output. CLI exit codes
follow argparse's usage-error convention and conventional success/failure.
"""

from __future__ import annotations

import argparse
import json
from collections.abc import Mapping
from html import escape
from pathlib import Path
from typing import Any

REQUIREMENT_FIELDS = (
    "task_classes",
    "auth_expectations",
    "required_clis",
    "verification_refs",
)
STATUSES = frozenset({"pass", "warn", "fail", "error", "skip", "unverified"})
COLUMNS = (
    ("role", "Role"),
    ("task_classes", "Required task classes"),
    ("auth_expectations", "Authentication expectations"),
    ("required_clis", "Required CLIs"),
    ("verification_refs", "Required verification references"),
    ("evidence_status", "Evidence status"),
    ("evidence_refs", "Evidence references"),
)


def _text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _strings(value: Any, *, allow_empty: bool = False) -> list[str]:
    if (
        not isinstance(value, list)
        or (not value and not allow_empty)
        or not all(_text(item) for item in value)
    ):
        raise ValueError("invalid string list")
    return sorted(set(value))


def build_rows(registry: Mapping, evidence: Mapping) -> list[dict[str, Any]]:
    """Validate explicit records and project one row per synthetic role.

    Evidence status is a reported check outcome, never a readiness verdict.
    Requiring reference coverage prevents an unrelated summary from qualifying
    the role. Input objects are not modified; no input paths are dereferenced.
    """
    if not isinstance(registry, Mapping) or not isinstance(evidence, Mapping):
        raise ValueError("inputs must be mappings")
    if not all(_text(role) for role in registry):
        raise ValueError("invalid role key")
    if not set(evidence).issubset(registry):
        raise ValueError("unknown evidence role")
    rows = []
    for role in sorted(registry):
        record = registry[role]
        if not isinstance(record, Mapping):
            raise ValueError("invalid role record")
        if not set(REQUIREMENT_FIELDS).issubset(record):
            raise ValueError("missing required field")
        row = {"role": role}
        for field in REQUIREMENT_FIELDS:
            row[field] = _strings(record[field], allow_empty=field == "required_clis")
        status = "unverified"
        references = []
        if role in evidence:
            summary = evidence[role]
            if not isinstance(summary, Mapping) or set(summary) != {
                "status", "verification_refs"
            }:
                raise ValueError("invalid evidence summary")
            reported = summary["status"]
            if not isinstance(reported, str) or reported not in STATUSES:
                raise ValueError("invalid evidence status")
            references = _strings(summary["verification_refs"])
            if set(row["verification_refs"]).issubset(references):
                status = reported
        row["evidence_status"] = status
        row["evidence_refs"] = references
        rows.append(row)
    return rows


def render_json(registry: Mapping, evidence: Mapping) -> str:
    """Return deterministic UTF-8-compatible JSON with sorted object keys."""
    return json.dumps(
        {"rows": build_rows(registry, evidence)},
        sort_keys=True,
        ensure_ascii=False,
        allow_nan=False,
    ) + "\n"


def render_html(registry: Mapping, evidence: Mapping) -> str:
    """Return a complete deterministic HTML view with escaped text cells."""
    rows = build_rows(registry, evidence)
    header = "".join(f"<th>{escape(label, quote=True)}</th>" for _, label in COLUMNS)
    body = []
    for row in rows:
        cells = []
        for field, _ in COLUMNS:
            value = row[field]
            text = ", ".join(value) if isinstance(value, list) else value
            cells.append(f"<td>{escape(text, quote=True)}</td>")
        body.append("<tr>" + "".join(cells) + "</tr>")
    return (
        '<!doctype html>\n<html lang="en"><head><meta charset="utf-8">'
        "<title>Synthetic readiness review</title></head><body>\n"
        "<h1>Synthetic readiness review</h1>\n"
        "<p>Evidence status is a reported observation. Registry membership and "
        "summary validation do not establish readiness.</p>\n"
        f"<table><thead><tr>{header}</tr></thead><tbody>\n"
        + "\n".join(body)
        + "\n</tbody></table>\n</body></html>\n"
    )


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def _invalid_constant(value):
    raise ValueError("nonfinite JSON constant")


def _read_json(path: Path) -> Any:
    return json.loads(
        path.read_text(encoding="utf-8"),
        object_pairs_hook=_unique_object,
        parse_constant=_invalid_constant,
    )


class _PrivateParser(argparse.ArgumentParser):
    def error(self, message):
        self.exit(2, "invalid command arguments\n")


def main(argv: list[str] | None = None) -> int:
    """Read only explicit input files and exclusively create one output file."""
    parser = _PrivateParser(description=__doc__)
    parser.add_argument("--registry", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--format", choices=("json", "html"), default="json")
    args = parser.parse_args(argv)
    try:
        registry = _read_json(args.registry)
        evidence = _read_json(args.evidence)
        renderer = render_json if args.format == "json" else render_html
        content = renderer(registry, evidence)
        with args.output.open("x", encoding="utf-8", newline="\n") as output:
            output.write(content)
    except (OSError, ValueError, RecursionError):
        # Diagnostics deliberately omit input values, references and paths.
        print("view generation failed")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
