"""Deckhand audit persistence and redacted reporting helpers."""

from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any, Callable, Iterable
from uuid import uuid4


Clock = Callable[[], str]


def append_raw(
    record: dict[str, Any],
    *,
    path: str | Path,
    clock: Clock,
    decision_id: str | None = None,
) -> dict[str, Any]:
    """Append one full-fidelity audit record as a JSON line."""
    raw_path = Path(path)
    persisted = _prepare_raw_record(record, clock=clock, decision_id=decision_id)

    try:
        raw_path.parent.mkdir(parents=True, exist_ok=True)
        with raw_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(persisted, sort_keys=True, separators=(",", ":")))
            handle.write("\n")
    except OSError as exc:
        raise OSError(f"failed to append audit record to {raw_path}: {exc}") from exc

    return persisted


def redacted_summary(records: Iterable[dict[str, Any]], *, policy: dict[str, Any]) -> dict[str, Any]:
    """Return an aggregate audit summary without operator, repo, branch, URL, or error detail."""
    redact = set(_audit_policy(policy).get("redact") or [])
    redact_error_specifics = "error_specifics" in redact
    summary: dict[str, Any] = {
        "total": 0,
        "allow": 0,
        "deny": 0,
        "deny_reasons": {},
        "sensitivity_counts": {},
    }

    for record in records:
        decision = str(record.get("decision") or "").upper()
        decision_key = "allow" if decision == "ALLOW" else "deny" if decision == "DENY" else None
        sensitivity = _safe_sensitivity(record.get("scope_sensitivity") or record.get("sensitivity"))

        summary["total"] += 1
        if decision_key:
            summary[decision_key] += 1

        sensitivity_bucket = summary["sensitivity_counts"].setdefault(
            sensitivity,
            {"total": 0, "allow": 0, "deny": 0},
        )
        sensitivity_bucket["total"] += 1
        if decision_key:
            sensitivity_bucket[decision_key] += 1

        if decision == "DENY":
            reason = "redacted" if redact_error_specifics else _safe_reason(record.get("reason"))
            summary["deny_reasons"][reason] = summary["deny_reasons"].get(reason, 0) + 1

    return summary


def render_summary_html(summary: dict[str, Any]) -> str:
    """Render a small self-contained HTML audit summary."""
    deny_reason_rows = _table_rows(summary.get("deny_reasons") or {}, ("Reason", "Count"))
    sensitivity_rows = []
    for sensitivity, counts in sorted((summary.get("sensitivity_counts") or {}).items()):
        if not isinstance(counts, dict):
            continue
        sensitivity_rows.append(
            "<tr>"
            f"<td>{html.escape(str(sensitivity))}</td>"
            f"<td>{html.escape(str(counts.get('total', 0)))}</td>"
            f"<td>{html.escape(str(counts.get('allow', 0)))}</td>"
            f"<td>{html.escape(str(counts.get('deny', 0)))}</td>"
            "</tr>"
        )

    return (
        "<!doctype html>\n"
        '<html lang="en">\n'
        "<head>\n"
        '  <meta charset="utf-8">\n'
        "  <title>Deckhand Audit Summary</title>\n"
        "  <style>\n"
        "    body{font-family:system-ui,sans-serif;margin:2rem;line-height:1.4;color:#202124;background:#fff;}\n"
        "    table{border-collapse:collapse;margin:1rem 0;min-width:20rem;}\n"
        "    th,td{border:1px solid #d0d7de;padding:.4rem .6rem;text-align:left;}\n"
        "    th{background:#f6f8fa;}\n"
        "  </style>\n"
        "</head>\n"
        "<body>\n"
        "  <h1>Deckhand Audit Summary</h1>\n"
        "  <dl>\n"
        f"    <dt>Total</dt><dd>{html.escape(str(summary.get('total', 0)))}</dd>\n"
        f"    <dt>Allow</dt><dd>{html.escape(str(summary.get('allow', 0)))}</dd>\n"
        f"    <dt>Deny</dt><dd>{html.escape(str(summary.get('deny', 0)))}</dd>\n"
        "  </dl>\n"
        "  <h2>Deny Reasons</h2>\n"
        "  <table><thead><tr><th>Reason</th><th>Count</th></tr></thead><tbody>"
        f"{deny_reason_rows}"
        "</tbody></table>\n"
        "  <h2>Sensitivity Counts</h2>\n"
        "  <table><thead><tr><th>Sensitivity</th><th>Total</th><th>Allow</th><th>Deny</th></tr></thead><tbody>"
        f"{''.join(sensitivity_rows)}"
        "</tbody></table>\n"
        "</body>\n"
        "</html>"
    )


def _prepare_raw_record(
    record: dict[str, Any],
    *,
    clock: Clock,
    decision_id: str | None,
) -> dict[str, Any]:
    persisted = dict(record)
    persisted.pop("ts_placeholder", None)
    persisted["ts"] = clock()
    persisted["decision_id"] = decision_id or str(persisted.get("decision_id") or uuid4())
    return persisted


def _audit_policy(policy: dict[str, Any]) -> dict[str, Any]:
    audit = policy.get("audit") if isinstance(policy, dict) else None
    return audit if isinstance(audit, dict) else {}


def _safe_sensitivity(value: Any) -> str:
    if isinstance(value, str) and value:
        return value
    return "unknown"


def _safe_reason(value: Any) -> str:
    if isinstance(value, str) and value:
        return value
    return "unspecified"


def _table_rows(values: dict[Any, Any], headers: tuple[str, str]) -> str:
    if not values:
        return f'<tr><td colspan="{len(headers)}">None</td></tr>'
    return "".join(
        "<tr>"
        f"<td>{html.escape(str(key))}</td>"
        f"<td>{html.escape(str(value))}</td>"
        "</tr>"
        for key, value in sorted(values.items())
    )
