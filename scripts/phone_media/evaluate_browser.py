"""Evaluate supplied trial records without accessing media, services or networks.

This validates self-reported observations, not their truth or authenticity.
See docs/runbooks/family-photo-browser.html for sources and trial procedures.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Local acceptance procedure, not a vendor performance threshold:
# issue #3588 requires private family browsing, search and archive evaluation.
# Feature basis: Immich Features / Libraries, Searching, Supported Formats,
# Facial Recognition, Duplicates Utility and Partner Sharing; PhotoPrism
# Features, Library and Advanced Settings; Tailscale Serve. Living documents
# retrieved 2026-10-22; full URLs and qualification are in the runbook.
# Restore/resource checks are conservative local prerequisites, not claims
# that either product provides backup or fits a particular device.
REQUIREMENTS = (
    "heic_preview",
    "exif_timeline",
    "face_search",
    "duplicate_review",
    "family_access",
    "originals_read_only",
    "tailnet_only",
    "restore_verified",
    "resource_fit",
)
PRODUCTS = {"immich", "photoprism"}
STATUSES = {"PASS", "FAIL", "NOT_EVALUATED"}
KINDS = {"observed", "documentation"}


def _require(condition: bool) -> None:
    if not condition:
        raise ValueError("Invalid assessment")


def _object(value: object, fields: set[str]) -> dict:
    _require(isinstance(value, dict) and set(value) == fields)
    return value


def _nonempty(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _unique_object(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        _require(key not in result)
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise ValueError("Non-finite JSON constant")


def load_assessment(text: str) -> dict:
    """Parse JSON without silently overwriting duplicate keys or accepting NaN."""
    return json.loads(text, object_pairs_hook=_unique_object,
                      parse_constant=_reject_constant)


def evaluate(data: object) -> dict:
    """Return deterministic decisions; documentation cannot establish a PASS.

    Hand-derived decision rule: FAIL takes precedence over unknowns. Otherwise
    every required observation and the installed version must be present for
    READY_FOR_REVIEW. This is an unweighted conjunction, with no fit estimates
    or numerical acceptance thresholds. References are opaque private record
    locators and are deliberately omitted from the public-safe output.
    """
    candidates = _object(data, {"candidates"})["candidates"]
    _require(isinstance(candidates, dict) and bool(candidates))
    _require(set(candidates) <= PRODUCTS)
    report = {"candidates": {}, "eligible_candidates": []}
    for product in sorted(candidates):
        candidate = _object(candidates[product], {"version", "checks"})
        version = candidate["version"]
        _require(version is None or isinstance(version, str))
        checks = candidate["checks"]
        _require(isinstance(checks, dict) and set(checks) <= set(REQUIREMENTS))
        results = {}
        for name in REQUIREMENTS:
            if name not in checks:
                results[name] = "NOT_EVALUATED"
                continue
            record = _object(checks[name], {"status", "kind", "reference"})
            _require(isinstance(record["status"], str) and record["status"] in STATUSES)
            _require(isinstance(record["kind"], str) and record["kind"] in KINDS)
            _require(_nonempty(record["reference"]))
            status = record["status"]
            if status == "PASS" and record["kind"] != "observed":
                status = "NOT_EVALUATED"
            results[name] = status
        if "FAIL" in results.values():
            decision = "BLOCKED"
        elif "NOT_EVALUATED" in results.values() or not _nonempty(version):
            decision = "NOT_EVALUATED"
        else:
            decision = "READY_FOR_REVIEW"
            report["eligible_candidates"].append(product)
        report["candidates"][product] = {
            "checks": results,
            "version_recorded": _nonempty(version),
            "decision": decision,
        }
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("assessment", type=Path, help="Trial assessment JSON file")
    args = parser.parse_args(argv)
    try:
        report = evaluate(load_assessment(args.assessment.read_text(encoding="utf-8")))
    except (OSError, UnicodeError, ValueError, RecursionError):
        # Do not echo input, record locators, exception values or private paths.
        print("Invalid assessment; check the documented input schema.", file=sys.stderr)
        return 2  # CLI usage/validation error convention; not a measured value.
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["eligible_candidates"] else 1  # Boolean CLI decision.


if __name__ == "__main__":
    sys.exit(main())
