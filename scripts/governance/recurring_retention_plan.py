#!/usr/bin/env python3
"""Plan advisory retention for an explicitly supplied weekly-review manifest.

Policy: docs/document-intelligence/durable-vs-transient-knowledge-boundary.md,
section 8.1: retain 90 days OR the latest 12 runs, whichever is longer.
Section 8.3 protects promotion dependencies; section 7.4 describes evidence.
The schedule remains advisory. Nothing here authorizes or applies archival.

Input JSON object::

    {"family": "weekly-review", "runs": [
        {"run_id": "review-example", "timestamp": "2026-07-13T12:00:00Z",
         "promotion_coverage": "complete", "pending_promotion": false,
         "promotion_evidence": []}
    ]}

``promotion_coverage=complete`` asserts that the supplied record covers both
promotion evidence and pending candidate queues. Both promotion fields must be
explicit, even when false/empty. Evidence entries are opaque nonempty references;
any entry protects the source. This planner trusts the supplied coverage claim,
does not authenticate evidence, and does not inspect queues or referenced paths.
Other fields are ignored. No production manifest adapter is claimed.

Timestamps must be timezone-aware ISO calendar timestamps with seconds. The age
boundary is inclusive: a run must be strictly older than the age window to be
an archive candidate. All runs tied at the latest-run cutoff are retained,
because the manifest cannot establish a strict older ordering between them.
Invalid identities or timestamps make ranking uncertain for the entire manifest.
Promotion gaps affect their own record. Uncertainty never recommends archival.

CLI: --manifest FILE --as-of TIMESTAMP. JSON is written only to stdout, with
stable key/decision ordering and normalized UTC timestamps. Success returns
zero; unresolved/error results return nonzero. No clock or root discovery is used.
"""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import re


POLICY_SOURCE = (
    "docs/document-intelligence/durable-vs-transient-knowledge-boundary.md"
    "#81-retention-schedule"
)
# Both constants are from the recurring-run row of the section 8.1 table above.
AGE_DAYS = 90
LATEST_RUNS = 12
FAMILY = "weekly-review"
_TIMESTAMP = re.compile(
    r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?"
    r"(?:Z|[+-]\d{2}:\d{2})", re.ASCII
)


def _timestamp(value: object) -> datetime:
    if (not isinstance(value, str) or not _TIMESTAMP.fullmatch(value)
            or value.endswith("-00:00")):
        raise ValueError("invalid_timestamp")
    # datetime accepts offsets with overflowing minute components; reject those
    # before normalization so malformed input cannot silently change its date.
    if not value.endswith("Z") and int(value[-2:]) >= 60:
        raise ValueError("invalid_timestamp")
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def _utc(value: datetime) -> str:
    return value.isoformat().replace("+00:00", "Z")


def _text(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip()) and value == value.strip()


def _result(as_of: str | None = None, *, error: str | None = None) -> dict:
    return {
        "family": FAMILY, "as_of": as_of,
        "policy": {"source": POLICY_SOURCE, "age_days": AGE_DAYS,
                   "latest_runs": LATEST_RUNS, "advisory": True},
        "status": "error" if error else "ok",
        "errors": [error] if error else [], "decisions": [],
    }


def _inspect_record(record: object, now: datetime, identifiers: Counter) -> tuple:
    row = {"run_id": None, "timestamp": None, "decision": "error", "reasons": []}
    if not isinstance(record, dict):
        row["reasons"].append("invalid_run_record")
        return row, None, False
    run_id = record.get("run_id")
    if not _text(run_id):
        row["reasons"].append("invalid_run_id")
    else:
        row["run_id"] = run_id
        if identifiers[run_id] > 1:
            row["reasons"].append("duplicate_run_id")
    try:
        timestamp = _timestamp(record.get("timestamp"))
        row["timestamp"] = _utc(timestamp)
        if timestamp > now:
            row["reasons"].append("future_timestamp")
    except (ValueError, OverflowError):
        timestamp = None
        row["reasons"].append("invalid_timestamp")
    return row, timestamp, not row["reasons"]


def _promotion(record: dict) -> tuple[list[str], list[str], list[str]]:
    errors, gaps, protection = [], [], []
    if record.get("promotion_coverage") != "complete":
        gaps.append("promotion_coverage_unknown")
    if "pending_promotion" not in record:
        gaps.append("pending_promotion_unknown")
    elif type(record["pending_promotion"]) is not bool:
        errors.append("invalid_pending_promotion")
    elif record["pending_promotion"]:
        protection.append("pending_promotion")
    if "promotion_evidence" not in record:
        gaps.append("promotion_evidence_unknown")
    else:
        evidence = record["promotion_evidence"]
        if not isinstance(evidence, list) or not all(_text(item) for item in evidence):
            errors.append("invalid_promotion_evidence")
        elif evidence:
            protection.append("promotion_evidence")
    return errors, gaps, protection


def plan_retention(manifest: object, *, as_of: str) -> dict:
    """Return decisions without mutating inputs or accessing the filesystem."""
    try:
        now = _timestamp(as_of)
    except (ValueError, OverflowError):
        return _result(error="invalid_as_of")
    result = _result(_utc(now))
    if not isinstance(manifest, dict):
        return _result(_utc(now), error="invalid_manifest")
    if manifest.get("family") != FAMILY:
        return _result(_utc(now), error="unsupported_family")
    records = manifest.get("runs")
    if not isinstance(records, list):
        return _result(_utc(now), error="invalid_runs")

    identifiers = Counter(record["run_id"] for record in records
                          if isinstance(record, dict) and _text(record.get("run_id")))
    inspected = [_inspect_record(record, now, identifiers) for record in records]
    ranking_known = all(valid for _, _, valid in inspected)
    times = sorted((time for _, time, valid in inspected if valid), reverse=True)
    cutoff = times[min(len(times), LATEST_RUNS) - 1] if times else None

    for record, (row, timestamp, valid) in zip(records, inspected):
        if not isinstance(record, dict):
            result["decisions"].append(row)
            continue
        errors, gaps, protection = _promotion(record)
        row["reasons"].extend(errors)
        if not valid or errors:
            row["reasons"].extend(gaps)
        else:
            retained = []
            # Compare elapsed duration directly to avoid calendar rounding and
            # subtraction overflow near the beginning of the datetime range.
            if now - timestamp <= timedelta(days=AGE_DAYS):
                retained.append("within_age_window")
            if ranking_known and cutoff is not None and timestamp >= cutoff:
                retained.append("within_latest_runs")
            retained.extend(protection)
            if gaps:
                row.update(decision="unresolved", reasons=gaps + retained)
            elif retained:
                row.update(decision="keep", reasons=retained)
            elif not ranking_known:
                row.update(decision="unresolved", reasons=["ranking_unresolved"])
            else:
                row.update(decision="archive_candidate", reasons=[
                    "outside_age_window", "outside_latest_runs", "promotion_clear"])
        row["reasons"].sort()
        result["decisions"].append(row)

    result["decisions"].sort(key=lambda row: json.dumps(row, sort_keys=True))
    states = {row["decision"] for row in result["decisions"]}
    result["status"] = "error" if "error" in states else (
        "unresolved" if "unresolved" in states else "ok")
    return result


def _unique_object(pairs: list[tuple]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate_json_key")
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise ValueError("nonfinite_json_value")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--as-of", required=True)
    args = parser.parse_args(argv)
    try:
        with args.manifest.open(encoding="utf-8") as stream:
            manifest = json.load(stream, object_pairs_hook=_unique_object,
                                 parse_constant=_reject_constant)
    except (OSError, UnicodeError):
        result = _result(error="manifest_unreadable")
    except ValueError:
        result = _result(error="invalid_json")
    else:
        result = plan_retention(manifest, as_of=args.as_of)
    print(json.dumps(result, sort_keys=True, ensure_ascii=False, allow_nan=False))
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
