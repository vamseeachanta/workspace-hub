"""Pure raw-versus-canonical unresolved-read arithmetic over caller data.

No logs, configuration, or history files are read or written. Observations carry
``run_id``, ``provider``, ``raw_unresolved``, and ``canonical_unresolved``. Counts
are nonnegative integers; repeated keys are summed as disjoint count fragments.
Callers are responsible for supplying comparable raw and canonical populations.

``delta = raw - canonical`` counts eliminated unresolved reads. Percent reduction
is ``delta / raw * 100``, rounded to one decimal with ties to even, or ``None``
when raw is zero. A negative delta is retained and flagged as canonical exceeding
raw; no historical noise classification or calibration is inferred.

Budgets, when supplied, are provider-specific inclusive maxima for canonical
counts, applied independently to each run. Missing budgets remain unconfigured.
Returned history preserves existing record order and metadata, then appends the
new batch sorted by run and provider. Overlapping history keys are rejected;
reruns must use a new run identifier. History records are prior returned records
with optional caller metadata. Persistence and chronological run ordering belong
to the caller; sorting opaque identifiers does not infer chronology.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from copy import deepcopy
from fractions import Fraction
from typing import Any


def _key(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a nonempty string")
    return value


def _count(value: object, field: str) -> int:
    # Zero is the counting identity; booleans are not read counts.
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{field} must be a nonnegative integer")
    return value


def _identity(item: Mapping[str, Any]) -> tuple[str, str]:
    return _key(item.get("run_id"), "run_id"), _key(item.get("provider"), "provider")


def build_baseline(
    observations: Iterable[Mapping[str, Any]],
    *,
    budgets: Mapping[str, int] | None = None,
    history: Iterable[Mapping[str, Any]] = (),
) -> list[dict[str, Any]]:
    """Return an independent history with validated, deterministic new records.

    Invalid counts, identifiers, budgets, duplicate prior keys, and attempted
    history overwrites raise ``ValueError`` without modifying caller data.
    No default budget is supplied, including for providers absent in the batch.
    """
    limits = {
        _key(provider, "budget provider"): _count(limit, "budget")
        for provider, limit in (budgets.items() if budgets is not None else ())
    }
    result: list[dict[str, Any]] = []
    prior_keys: set[tuple[str, str]] = set()
    for item in history:
        key = _identity(item)
        if key in prior_keys:
            raise ValueError("duplicate history key")
        prior_keys.add(key)
        result.append(deepcopy(dict(item)))

    counts: dict[tuple[str, str], tuple[int, int]] = {}
    for item in observations:
        key = _identity(item)
        if key in prior_keys:
            raise ValueError("run and provider already in history")
        raw = _count(item.get("raw_unresolved"), "raw_unresolved")
        canonical = _count(item.get("canonical_unresolved"), "canonical_unresolved")
        # Additive identity for an unseen run/provider, without inferred counts.
        previous_raw, previous_canonical = counts.get(key, (0, 0))
        counts[key] = previous_raw + raw, previous_canonical + canonical

    for (run_id, provider), (raw, canonical) in sorted(counts.items()):
        delta = raw - canonical
        # Percent means per hundred; ten tenths per unit gives one decimal.
        # Fraction keeps the tie exact before round applies ties-to-even.
        percent = round(Fraction(delta * 100 * 10, raw)) / 10 if raw else None
        budget = limits.get(provider)
        result.append({
            "run_id": run_id,
            "provider": provider,
            "raw_unresolved": raw,
            "canonical_unresolved": canonical,
            "delta": delta,
            "percent_reduction": percent,
            "canonical_exceeds_raw": canonical > raw,
            "budget": budget,
            "budget_status": (
                "not_configured" if budget is None
                else "within" if canonical <= budget else "exceeded"
            ),
        })
    return result
