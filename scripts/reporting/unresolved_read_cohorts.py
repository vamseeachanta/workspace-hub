"""Reduce synthetic or caller-supplied unresolved-read snapshots to JSON cohorts.

Scope: issue #2197, recurrence by provider and canonical target. Existing
scripts/analysis/provider_session_ecosystem_audit.py declarations load_previous_audit
and build_change_alerts compare audit snapshots; this reducer neither loads
those audits nor changes their policy numbers or severity rules.

Input is a list of complete snapshots with exactly these fields::

    {"run_id": "week-a", "generated_at": "2026-01-05T00:00:00Z",
     "observations": [{"provider": "provider-a", "canonical_target": "docs/a.md"}]}

Run identities are opaque nonempty strings; generated_at is a timezone-aware
ISO timestamp. Canonical targets and provider identities must already be
resolved upstream and are preserved exactly. Observations contain exactly the
two shown fields. Duplicate pairs within a run count once; equivalent duplicate
runs count once. Conflicting normalized contents for one run identity fail.

Runs sort by UTC instant, then run identity for timestamp ties. Consecutive runs
means the trailing streak ending at the latest supplied run, including empty
runs. A missing pair breaks its streak. Missing calendar weeks are not inferred.
total_observations counts distinct supplied runs containing the pair, rather
than raw read events. Historical cohorts remain in output with a zero streak
when absent from the latest run. First/last seen are UTC observation timestamps.

No recurrence threshold or severity policy is introduced. The arithmetic uses
the empty count zero and a unit increment per deduplicated run; independent
hand calculations are in tests/reporting/test_unresolved_read_cohorts.py.
The reducer has no I/O. Direct execution reads a JSON array from stdin and emits
a JSON array to stdout, or a JSON error to stderr with a failing exit status.
No files, issues or messages are written.
"""

from __future__ import annotations

from datetime import datetime, timezone
import json
import sys


def _text(value: object, field: str) -> str:
    if not isinstance(value, str) or not value or value.strip() != value:
        raise ValueError(f"invalid {field}")
    return value


def _shape(value: object, fields: set[str], label: str) -> dict:
    if not isinstance(value, dict) or value.keys() != fields:
        raise ValueError(f"invalid {label} fields")
    return value


def _normalize(snapshot: object) -> tuple[str, datetime, frozenset[tuple[str, str]]]:
    snapshot = _shape(snapshot, {"run_id", "generated_at", "observations"}, "snapshot")
    run_id = _text(snapshot["run_id"], "run_id")
    timestamp = _text(snapshot["generated_at"], "generated_at")
    try:
        instant = datetime.fromisoformat(timestamp)
        if instant.tzinfo is None or instant.utcoffset() is None:
            raise ValueError
        instant = instant.astimezone(timezone.utc)
    except (ValueError, OverflowError):
        raise ValueError("invalid generated_at") from None
    if not isinstance(snapshot["observations"], list):
        raise ValueError("invalid observations")
    pairs = set()
    for observation in snapshot["observations"]:
        observation = _shape(observation, {"provider", "canonical_target"}, "observation")
        pairs.add((_text(observation["provider"], "provider"),
                   _text(observation["canonical_target"], "canonical_target")))
    return run_id, instant, frozenset(pairs)


def reduce_snapshots(snapshots: list[dict]) -> list[dict]:
    """Return deterministic JSON-compatible cohorts without mutating inputs.

    Invalid shapes, naive timestamps and conflicting duplicate identities raise
    ValueError. Duplicate identity equivalence compares normalized instants and
    deduplicated observation sets, so ordering and multiplicity are immaterial.
    """
    if not isinstance(snapshots, list):
        raise ValueError("snapshots must be a list")
    by_run = {}
    for snapshot in snapshots:
        run_id, instant, pairs = _normalize(snapshot)
        content = (instant, pairs)
        if run_id in by_run and by_run[run_id] != content:
            raise ValueError("conflicting run identity")
        by_run[run_id] = content

    ordered_runs = sorted(by_run, key=lambda run_id: (by_run[run_id][0], run_id))
    cohorts = {}
    last_indices = {}
    for index, run_id in enumerate(ordered_runs):
        instant, pairs = by_run[run_id]
        seen_at = instant.isoformat()
        for pair in sorted(pairs):
            if pair not in cohorts:
                provider, target = pair
                cohorts[pair] = {
                    "provider": provider,
                    "canonical_target": target,
                    "total_observations": 0,
                    "consecutive_runs": 0,
                    "first_seen": seen_at,
                    "last_seen": seen_at,
                }
            row = cohorts[pair]
            row["total_observations"] += 1
            row["consecutive_runs"] = (
                row["consecutive_runs"] + 1 if last_indices.get(pair) == index - 1 else 1
            )
            row["last_seen"] = seen_at
            last_indices[pair] = index

    for pair, row in cohorts.items():
        if last_indices[pair] != len(ordered_runs) - 1:
            row["consecutive_runs"] = 0
    return [cohorts[pair] for pair in sorted(cohorts)]


def main() -> int:
    """Read caller-supplied JSON only; never discover or write audit records."""
    try:
        rows = reduce_snapshots(json.load(sys.stdin))
    except ValueError:
        # Never echo caller data, paths or parser excerpts in public diagnostics.
        json.dump({"error": "invalid snapshots or conflicting run identity"}, sys.stderr)
        sys.stderr.write("\n")
        return 1
    json.dump(rows, sys.stdout, ensure_ascii=False, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
