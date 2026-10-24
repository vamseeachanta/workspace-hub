"""Check recorded agent-preflight/1 evidence without starting any probes.

The caller supplies the required capabilities and receipt lifetime. A current
receipt is evidence of a past probe, not authorization or proof of present access.
Only static reason codes are printed; recorded probe text and paths stay private.
Exit codes: 0 ready, 1 invalid input, 2 CLI usage, 3 evidence not ready.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from fractions import Fraction
from pathlib import Path

CAPABILITIES = ("python", "git", "gh")


def _instant(value: object) -> tuple[dt.datetime, Fraction]:
    # RFC 3339 (2002), section 5.6: date, time and a numeric offset or Z.
    # The producer uses .NET round-trip timestamps, including fractional seconds.
    match = re.fullmatch(
        r"(?P<whole>[0-9]{4}-[0-9]{2}-[0-9]{2}[Tt](?:[01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9])"
        r"(?:\.(?P<fraction>[0-9]+))?(?P<offset>[Zz]|[+-](?:[01][0-9]|2[0-3]):[0-5][0-9])",
        value,
    ) if isinstance(value, str) else None
    if not match:
        raise ValueError("timestamp requires an explicit offset")
    whole = dt.datetime.fromisoformat((match["whole"] + match["offset"]).upper())
    # Preserve all fractional digits instead of truncating .NET round-trip times
    # to datetime's microseconds. Only the displayed age is converted to float.
    return whole, Fraction("0." + (match["fraction"] or "0"))


def _nonempty(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def evaluate(
    receipt: object, *, as_of: str, max_age_seconds: int, required: tuple[str, ...] | list[str]
) -> dict:
    """Evaluate a subset of evidence from scripts/windows/agent-preflight.ps1.

    Age = comparison instant - probe instant. Expiry is strict, following
    docs/architecture/agent-data-handling-contract.md (valid_until > as_of).
    No default lifetime or task capability requirement is inferred.
    """
    if type(max_age_seconds) is not int or max_age_seconds <= 0:
        raise ValueError("receipt lifetime must be a positive integer")
    if not isinstance(required, (tuple, list)) or not required or any(c not in CAPABILITIES for c in required):
        raise ValueError("at least one known capability is required")
    if not isinstance(receipt, dict) or receipt.get("schema") != "agent-preflight/1":
        raise ValueError("unsupported receipt schema")
    observed, observed_fraction = _instant(receipt.get("generated_at"))
    comparison, comparison_fraction = _instant(as_of)
    whole_seconds = (comparison - observed) // dt.timedelta(seconds=1)
    age = whole_seconds + comparison_fraction - observed_fraction
    failures = []
    if age < 0:
        failures.append("RECEIPT_FROM_FUTURE")
    elif age >= max_age_seconds:
        failures.append("RECEIPT_EXPIRED")

    findings = receipt.get("findings")
    if not isinstance(findings, list) or any(
        not isinstance(f, dict) or f.get("severity") not in ("info", "warn", "error")
        or not _nonempty(f.get("id")) or not _nonempty(f.get("message")) for f in findings
    ):
        raise ValueError("invalid findings")
    if any(f["severity"] == "error" for f in findings):
        failures.append("ERROR_FINDING")

    for capability in dict.fromkeys(required):
        evidence = receipt.get(capability)
        if not isinstance(evidence, dict):
            failures.append(f"{capability.upper()}_UNVERIFIED")
            continue
        if capability == "python":
            venv = evidence.get("venv_cfg_present", False)
            if (evidence.get("selected_exists") is not True or not _nonempty(evidence.get("selected"))
                    or not _nonempty(evidence.get("version"))
                    or (venv is not None and venv is not True)):
                failures.append("PYTHON_UNVERIFIED")
            encoding = evidence.get("preferred_encoding")
            if not isinstance(encoding, str) or encoding.lower().replace("-", "") != "utf8":
                failures.append("PYTHON_ENCODING_UNVERIFIED")
        else:
            if not _nonempty(evidence.get("path")) or not _nonempty(evidence.get("version")):
                failures.append(f"{capability.upper()}_UNVERIFIED")
            # The producer's authenticated API result is authoritative here; a
            # failed stored-account status probe alone does not reject active auth.
            if capability == "gh" and evidence.get("auth_ok") is not True:
                failures.append("GH_AUTH_UNVERIFIED")

    return {
        "schema": "agent-preflight-check/1",
        "status": "not-ready" if failures else "ready",
        "age_seconds": float(age),
        "required": list(dict.fromkeys(required)),
        "failures": failures,
    }


def _unique_object(pairs: list[tuple[str, object]]) -> dict:
    # RFC 8259 (2017), section 4: reject ambiguous object names rather than pick one.
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON object name")
        result[key] = value
    return result


def _invalid_constant(_: str) -> None:
    # RFC 8259 (2017), section 6 excludes NaN and Infinity from JSON numbers.
    raise ValueError("non-finite JSON constant")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("receipt", type=Path)
    parser.add_argument("--max-age-seconds", type=int, required=True)
    parser.add_argument("--require", choices=CAPABILITIES, action="append", required=True)
    parser.add_argument("--as-of", help="comparison time with offset (default: current UTC)")
    args = parser.parse_args(argv)
    try:
        receipt = json.loads(args.receipt.read_text(encoding="utf-8-sig"),
                             object_pairs_hook=_unique_object, parse_constant=_invalid_constant)
        result = evaluate(receipt, as_of=args.as_of or dt.datetime.now(dt.UTC).isoformat(),
                          max_age_seconds=args.max_age_seconds, required=args.require)
    except (OSError, ValueError, OverflowError, RecursionError):
        print("validate-agent-preflight: invalid receipt or evaluation inputs", file=sys.stderr)
        return 1
    print(json.dumps(result))
    return 0 if result["status"] == "ready" else 3


if __name__ == "__main__":
    sys.exit(main())
