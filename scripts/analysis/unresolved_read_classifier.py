"""Classify supplied unresolved-read observations offline (issues/2185).

Input is a JSON array of rows. Each row has exactly ``provider`` and ``target``
(nonblank opaque strings), plus optional ``evidence``. No paths are resolved,
normalized or probed. Duplicate rows represent separate reads, each counted once.

Evidence is an optional object with only the following keys. Missing keys and
JSON null mean unknown, never false. Boolean fields accept only JSON booleans:

* alias_resolves: false establishes ALIAS_GAP (alias-gap).
* registry_entry_present: false establishes MISSING_REGISTRY_ENTRY
  (missing-registry-entry).
* target_accessible: false establishes INACCESSIBLE_TARGET (inaccessible-target).
* provenance_complete: false establishes PROVENANCE_GAP (provenance-gap).
* publication_matches: false establishes PUBLICATION_DRIFT (publication-drift).
* target_state: "stale" or "deleted" establishes STALE_DELETED_TARGET
  (stale-deleted-target); "present" rules out that cause; "unknown" is unknown.
* suppression_policy_matches: true AND a nonblank string suppression_basis
  establish SUPPRESSION_ELIGIBLE (suppression-eligible). These are caller-supplied
  attestations of a documented exception, not authenticated authorization.

Evidence precedence: invalid/unsupported evidence or a deleted target asserted
accessible yields UNKNOWN_NEEDS_REVIEW (unknown-needs-review). Multiple established
causes, including eligibility together with a diagnostic cause, also yield unknown:
no cause silently outranks another. Otherwise a unique established cause wins;
unobserved independent dimensions do not invalidate it. No established cause yields
unknown, even when every supplied observation is healthy. An incomplete suppression
claim does not establish eligibility and cannot erase an independent diagnosis.
Null evidence is equivalent to missing evidence. Malformed row envelopes raise
ValueError; malformed evidence remains a reviewable unknown row.

Output has ``rows`` sorted by provider, target, bucket and reason_code, and sparse
``bucket_counts`` by provider then bucket. Codes and bucket spellings above are
stable. CLI reads stdin and writes canonical JSON plus a newline to stdout; invalid
input returns a nonzero exit status and a fixed diagnostic on stderr without
echoing input. Duplicate JSON keys and nonfinite numbers are rejected. This module
never applies suppressions, writes files or reads live evidence. Integration with
repository probes, gates and publication consumers remains separate work.
"""

from __future__ import annotations

import json
import math
import sys
from collections.abc import Mapping


# Taxonomy and boolean polarity are specified by issues/2185 and the schema above.
_DIAGNOSTICS = {
    "alias_resolves": ("alias-gap", "ALIAS_GAP"),
    "registry_entry_present": ("missing-registry-entry", "MISSING_REGISTRY_ENTRY"),
    "target_accessible": ("inaccessible-target", "INACCESSIBLE_TARGET"),
    "provenance_complete": ("provenance-gap", "PROVENANCE_GAP"),
    "publication_matches": ("publication-drift", "PUBLICATION_DRIFT"),
}
_BOOLEAN_FIELDS = {*_DIAGNOSTICS, "suppression_policy_matches"}
_EVIDENCE_FIELDS = _BOOLEAN_FIELDS | {"target_state", "suppression_basis"}
_UNKNOWN = ("unknown-needs-review", "UNKNOWN_NEEDS_REVIEW")


def _classify_evidence(evidence: object) -> tuple[str, str]:
    if evidence is None:
        return _UNKNOWN
    if not isinstance(evidence, Mapping) or set(evidence) - _EVIDENCE_FIELDS:
        return _UNKNOWN
    for field in _BOOLEAN_FIELDS:
        value = evidence.get(field)
        if value is not None and type(value) is not bool:
            return _UNKNOWN
    state = evidence.get("target_state")
    if state not in (None, "unknown", "present", "stale", "deleted"):
        return _UNKNOWN
    basis = evidence.get("suppression_basis")
    if basis is not None and not isinstance(basis, str):
        return _UNKNOWN
    if state == "deleted" and evidence.get("target_accessible") is True:
        return _UNKNOWN

    candidates = [reason for field, reason in _DIAGNOSTICS.items()
                  if evidence.get(field) is False]
    if state in ("stale", "deleted"):
        candidates.append(("stale-deleted-target", "STALE_DELETED_TARGET"))
    if evidence.get("suppression_policy_matches") is True and basis and basis.strip():
        candidates.append(("suppression-eligible", "SUPPRESSION_ELIGIBLE"))
    # One independently established cause is required; ambiguity stays visible.
    if len(candidates) == 1:
        return candidates[0]
    return _UNKNOWN


def classify_read(row: Mapping) -> dict[str, str]:
    """Return one classification without mutating or probing the supplied row."""
    if not isinstance(row, Mapping) or set(row) - {"provider", "target", "evidence"}:
        raise ValueError("Invalid read row")
    for field in ("provider", "target"):
        if not isinstance(row.get(field), str) or not row[field].strip():
            raise ValueError("Invalid read row")
    bucket, reason_code = _classify_evidence(row.get("evidence"))
    return {"provider": row["provider"], "target": row["target"],
            "bucket": bucket, "reason_code": reason_code}


def classify_rows(rows: list) -> dict:
    """Classify a JSON-style array, preserving multiplicity and sorting output."""
    if not isinstance(rows, list):
        raise ValueError("Expected a list of read rows")
    results = [classify_read(row) for row in rows]
    results.sort(key=lambda row: (row["provider"], row["target"],
                                  row["bucket"], row["reason_code"]))
    counts: dict[str, dict[str, int]] = {}
    for result in results:
        buckets = counts.setdefault(result["provider"], {})
        bucket = result["bucket"]
        # Each input row contributes one observation (issues/2185 count contract).
        buckets[bucket] = buckets.get(bucket, 0) + 1
    return {"rows": results, "bucket_counts": {
        provider: dict(sorted(buckets.items()))
        for provider, buckets in sorted(counts.items())
    }}


def _unique_object(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON key")
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise ValueError("Nonfinite JSON number")


def _finite_float(value: str) -> float:
    number = float(value)
    if not math.isfinite(number):
        raise ValueError("Nonfinite JSON number")
    return number


def main() -> int:
    """Run the offline stdin/stdout interface; never echo malformed input."""
    try:
        rows = json.load(sys.stdin, object_pairs_hook=_unique_object,
                         parse_constant=_reject_constant, parse_float=_finite_float)
        result = classify_rows(rows)
        output = json.dumps(result, sort_keys=True, ensure_ascii=True, allow_nan=False)
    except (ValueError, RecursionError):
        print("Invalid input: expected a JSON array of read rows.", file=sys.stderr)
        return 1
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
