"""Read-only retention plan from explicit JSON metadata; repository issue #2237.

Usage: python scripts/maintenance/transient_retention_plan.py metadata.json
       --now 2026-05-01T00:00:00Z [--dry-run]

Input is {"records": [...], "policy": {kind: rule}}. Each record supplies kind
(handoff, planning_quick, planning_research, signal), classification, promoted
(boolean), evidence_verified (boolean), and retention_evidence containing
verified (boolean) and policy_ref. Each rule supplies positive integer days,
basis (created_at or issue_closed_at), and nonempty source matching policy_ref.
The record supplies the selected timestamp, with an explicit UTC offset. An
issue_closed_at rule also requires issue_state (open or closed). Optional id and
path values are opaque output locators, never filesystem targets.

Policy basis: docs/document-intelligence/durable-vs-transient-knowledge-boundary.md,
sections 4.4, 4.8, 7.2, 8.1 and 8.4. No retention numbers are built in: callers
must supply a scoped policy and evidence, including any date-based fallback.
The supplied period expires at anchor + days; equality is eligible. Durable,
governance and promoted content is kept. Missing or unverified metadata is
unknown, which also means retain. Only explicitly transient, verified records
can be eligible; age and path never establish classification.

This planner trusts caller assertions; it does not authenticate evidence or
infer policy from repository paths. It emits reasons, expiration instants and
summary counts only. It does not inspect artifacts, apply actions, or schedule
work. Eligibility is a review candidate, not permission to change a file.
"""

import argparse
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import sys


KINDS = ("handoff", "planning_quick", "planning_research", "signal")
STATUSES = ("keep", "eligible", "unknown")


def _instant(value):
    if not isinstance(value, str):
        raise ValueError("an explicit timestamp is required")
    instant = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if instant.tzinfo is None or instant.utcoffset() is None:
        raise ValueError("a timestamp offset is required")
    return instant.astimezone(timezone.utc)


def _text(value):
    return isinstance(value, str) and bool(value.strip())


def _decision(record, policy, now):
    result = {"status": "unknown", "reason": "missing_metadata"}
    if not isinstance(record, dict):
        return result
    for key in ("id", "path", "kind"):
        if isinstance(record.get(key), str):
            result[key] = record[key]

    def finish(status, reason):
        return dict(result, status=status, reason=reason)

    classification = record.get("classification")
    if classification == "durable":
        return finish("keep", "durable_content")
    if classification == "governance":
        return finish("keep", "governance_evidence")
    if record.get("promoted") is True:
        return finish("keep", "promoted_content")
    if classification != "transient":
        return finish("unknown", "classification_unverified")
    if record.get("evidence_verified") is not True:
        return finish("unknown", "unverified_evidence")
    if record.get("promoted") is not False:
        return finish("unknown", "promotion_status_unknown")
    kind = record.get("kind")
    if kind not in KINDS:
        return finish("unknown", "unsupported_kind")
    rule = policy.get(kind)
    if not isinstance(rule, dict):
        return finish("unknown", "policy_missing")
    days, basis, source = rule.get("days"), rule.get("basis"), rule.get("source")
    # Zero is the mathematical lower bound for a positive supplied duration,
    # not a retention default. timedelta interprets days in calendar-day units.
    if (type(days) is not int or days <= 0 or not _text(source)
            or basis not in ("created_at", "issue_closed_at")):
        return finish("unknown", "policy_invalid")
    evidence = record.get("retention_evidence")
    if (not isinstance(evidence, dict) or evidence.get("verified") is not True
            or evidence.get("policy_ref") != source):
        return finish("unknown", "retention_evidence_unverified")
    if basis == "issue_closed_at":
        if record.get("issue_state") == "open":
            return finish("keep", "issue_open")
        if record.get("issue_state") != "closed":
            return finish("unknown", "issue_state_unknown")
    try:
        anchor = _instant(record.get(basis))
        expiry = anchor + timedelta(days=days)
    except (ValueError, TypeError, OverflowError):
        return finish("unknown", "retention_time_invalid")
    if anchor > now:
        return finish("unknown", "retention_anchor_in_future")
    result.update(expires_at=expiry.isoformat(), policy_ref=source, basis=basis)
    if now >= expiry:
        return finish("eligible", "retention_elapsed")
    return finish("keep", "retention_pending")


def build_plan(records, policy, *, now):
    """Calculate only; neither inputs nor the filesystem are modified.

    Invalid global inputs raise ValueError; incomplete records or per-kind rules
    yield unknown. Input order is preserved, including repeated opaque locators.
    """
    instant = _instant(now)
    if not isinstance(records, list) or not isinstance(policy, dict):
        raise ValueError("records must be an array and policy must be an object")
    decisions = [_decision(record, policy, instant) for record in records]
    counts = {status: sum(row["status"] == status for row in decisions)
              for status in STATUSES}
    return {"dry_run": True, "as_of": instant.isoformat(), "records": decisions,
            "summary": dict(total=len(decisions), **counts)}


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate metadata key")
        result[key] = value
    return result


def _reject_constant(value):
    raise ValueError("non-finite JSON value")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("metadata", type=Path, help="Explicit metadata and policy JSON")
    parser.add_argument("--now", required=True, help="Current time with UTC offset")
    parser.add_argument("--dry-run", action="store_true", help="All runs are dry runs")
    args = parser.parse_args(argv)
    try:
        payload = json.loads(args.metadata.read_text(encoding="utf-8"),
                             object_pairs_hook=_unique_object, parse_constant=_reject_constant)
        if not isinstance(payload, dict):
            raise ValueError("metadata must be an object")
        plan = build_plan(payload.get("records"), payload.get("policy"), now=args.now)
    except (OSError, ValueError, TypeError, OverflowError):
        # Input values and private locators must not leak through error messages.
        parser.error("invalid metadata or policy; supply records, policy and an offset timestamp")
    print(json.dumps(plan, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    sys.exit(main())
