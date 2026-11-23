"""Demo 6: compare supplied scalar response envelopes with referenced limits.

Input contract: docs/gtm/mooring-screening.md (initial revision).
Only the caller's inclusive limits are compared; no standard safety factor,
physical response equation or fatigue model is implemented. In particular,
minimum breaking load alone is not an allowable line tension.

Existing domain context: scripts/animations/mooring_math.py, max_utilisation.
Its visualisation defaults and approximations are deliberately not consumed.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

NUMERIC_FIELDS = {
    "max_tension_kn": False,
    "allowable_tension_kn": True,
    "max_offset_m": False,
    "allowable_offset_m": True,
}
REFERENCE_FIELDS = {"response_source", "tension_limit_source", "offset_limit_source"}
FIELDS = {"case_id"} | NUMERIC_FIELDS.keys() | REFERENCE_FIELDS


def _validate_case(case: object) -> None:
    if not isinstance(case, dict):
        raise TypeError("each case must be an object")
    if case.keys() - FIELDS:
        raise ValueError("case contains unknown fields")
    identity = case.get("case_id")
    if not isinstance(identity, str) or not identity.strip():
        raise ValueError("case_id must be a nonempty string")
    for field, positive in NUMERIC_FIELDS.items():
        value = case.get(field)
        if value is None:
            continue
        try:
            finite = type(value) in (int, float) and math.isfinite(value)
        except OverflowError:
            finite = False
        # Zero is the mathematical lower bound for magnitudes, not a code
        # limit: see the input-domain contract in mooring-screening.md.
        if not finite or value < 0 or (positive and value == 0):
            domain = "positive" if positive else "nonnegative"
            raise ValueError(f"{field} must be a finite {domain} number")
    for field in REFERENCE_FIELDS:
        value = case.get(field)
        if value is not None and (not isinstance(value, str) or not value.strip()):
            raise ValueError(f"{field} must be a nonempty reference string")


def _not_evaluated(reason: str) -> dict:
    return {"status": "NOT_EVALUATED", "reason": reason}


def _compare(case: dict, demand: str, limit: str, source: str) -> dict:
    required = (demand, limit, source, "response_source")
    missing = [field for field in required if case.get(field) is None]
    if missing:
        return _not_evaluated("Missing inputs: " + ", ".join(missing))
    # Inclusive comparison is defined by the caller-limit contract, not by
    # DNV/API. No rounding, tolerance or undocumented factor changes the limit.
    status = (
        "WITHIN_SUPPLIED_LIMIT"
        if case[demand] <= case[limit]
        else "EXCEEDS_SUPPLIED_LIMIT"
    )
    return {"status": status, "reason": "Compared against the referenced input limit"}


def screen_cases(cases: list[dict]) -> dict:
    """Return a reproducible record; never infer whole-system acceptance.

    Sources are caller assertions retained for review, not authenticated here.
    Missing fields/nulls leave the corresponding check NOT_EVALUATED; malformed
    values reject the whole batch before a record is returned.
    """
    if not isinstance(cases, list) or not cases:
        raise ValueError("cases must be a nonempty list")
    identities: set[str] = set()
    records = []
    for case in cases:
        _validate_case(case)
        identity = case["case_id"]
        if identity in identities:
            raise ValueError("duplicate case_id")
        identities.add(identity)
        records.append(
            {
                "inputs": dict(case),
                "checks": {
                    "tension": _compare(
                        case,
                        "max_tension_kn",
                        "allowable_tension_kn",
                        "tension_limit_source",
                    ),
                    "offset": _compare(
                        case,
                        "max_offset_m",
                        "allowable_offset_m",
                        "offset_limit_source",
                    ),
                    "fatigue": _not_evaluated(
                        "No cycle history, fatigue curve, exposure or damage criterion evaluated",
                    ),
                    "dnv_os_e301": _not_evaluated(
                        "No qualified edition, clause, condition or factor selection evaluated",
                    ),
                    "api_rp_2sk": _not_evaluated(
                        "No qualified edition, clause, condition or factor selection evaluated",
                    ),
                },
            }
        )
    return {
        "analysis": "supplied_scalar_envelope_comparison",
        "limitations": (
            "Screening of supplied inputs only; no physical response calculation, "
            "source authentication, standards compliance or design approval. "
            "No overall pass is issued."
        ),
        "cases": records,
    }


def _unique_object(pairs: list[tuple]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise ValueError("non-finite JSON constant")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="JSON object containing a cases array")
    args = parser.parse_args()
    try:
        text = args.input.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        # Do not include a local input path in error output.
        parser.exit(2, "error: unable to read input\n")
    try:
        payload = json.loads(
            text,
            object_pairs_hook=_unique_object,
            parse_constant=_reject_constant,
        )
        if not isinstance(payload, dict) or set(payload) != {"cases"}:
            raise ValueError("input must be an object containing only cases")
        record = screen_cases(payload["cases"])
    except (ValueError, TypeError, RecursionError):
        # Parser exceptions can echo input fragments; emit a fixed CLI error.
        parser.exit(2, "error: invalid JSON or screening input contract\n")
    print(json.dumps(record, indent=2, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
