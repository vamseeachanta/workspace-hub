#!/usr/bin/env python3
"""Read-only portability guidance comparison; standard library only.

Input shapes, reason codes and exit codes are defined in
docs/guides/portability-guidance-health.md. No provider or network access occurs.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys


_TOKEN = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*", re.ASCII)
_LOCATOR = re.compile(r"[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)*", re.ASCII)
_MODEL_FIELDS = {"shape", "schema_version"}

# Messages deliberately contain no evidence values, filesystem paths or errors.
_DIAGNOSTICS = {
    "GUIDANCE_CURRENT": "Guidance declares support for the supplied audit model.",
    "GUIDANCE_REVIEW_REQUIRED": "Review guidance at the canonical locator for the changed audit model.",
    "CANONICAL_LOCATOR_INVALID": "Supply a canonical repository-relative guidance locator.",
}
for _source in ("AUDIT", "GUIDANCE"):
    _DIAGNOSTICS.update({
        f"{_source}_MISSING": "Supply the missing evidence; consult the canonical locator.",
        f"{_source}_UNREADABLE": "Make the evidence readable; consult the canonical locator.",
        f"{_source}_DOCUMENT_INVALID": "Supply a valid JSON object; consult the canonical locator.",
        f"{_source}_MODEL_MISSING": "Declare explicit model evidence; consult the canonical locator.",
        f"{_source}_MODEL_INVALID": "Correct the model declaration; consult the canonical locator.",
    })
# Preserve the more specific remediation after populating generic source errors.
_DIAGNOSTICS["GUIDANCE_MISSING"] = (
    "Create guidance at the canonical locator and declare support."
)


def _valid_locator(locator: object) -> bool:
    return (
        isinstance(locator, str)
        and _LOCATOR.fullmatch(locator) is not None
        and all(part not in {".", ".."} for part in locator.split("/"))
    )


def _report(reason: str, locator: str | None) -> dict:
    status = {
        "GUIDANCE_CURRENT": "current",
        "GUIDANCE_MISSING": "missing_guidance",
        "GUIDANCE_REVIEW_REQUIRED": "incompatible_model",
    }.get(reason, "unknown_evidence")
    return {
        "status": status,
        "reason_code": reason,
        "canonical_locator": locator,
        "diagnostic": _DIAGNOSTICS[reason],
    }


def _model_error(document: object, key: str, source: str) -> str | None:
    if not isinstance(document, dict):
        return f"{source}_DOCUMENT_INVALID"
    if key not in document:
        return f"{source}_MODEL_MISSING"
    model = document[key]
    if (
        not isinstance(model, dict)
        or set(model) != _MODEL_FIELDS
        or not all(
            isinstance(value, str) and _TOKEN.fullmatch(value) is not None
            for value in model.values()
        )
    ):
        return f"{source}_MODEL_INVALID"
    return None


def build_report(audit: object, guidance: object, canonical_locator: str) -> dict:
    """Compare supplied objects without mutation; None denotes absent evidence.

    Validate the locator, then guidance, then audit. A current result means only
    exact declared model compatibility, not a review of guidance prose or rights.
    """
    if not _valid_locator(canonical_locator):
        return _report("CANONICAL_LOCATOR_INVALID", None)
    for document, key, source in (
        (guidance, "supported_audit_model", "GUIDANCE"),
        (audit, "audit_model", "AUDIT"),
    ):
        reason = (
            f"{source}_MISSING" if document is None
            else _model_error(document, key, source)
        )
        if reason:
            return _report(reason, canonical_locator)
    reason = (
        "GUIDANCE_CURRENT"
        if audit["audit_model"] == guidance["supported_audit_model"]
        else "GUIDANCE_REVIEW_REQUIRED"
    )
    return _report(reason, canonical_locator)


def _unique_object(pairs: list[tuple]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON key")
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise ValueError("Non-finite JSON constant")


def _read_document(path: Path, source: str) -> tuple[dict | None, str | None]:
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return None, f"{source}_MISSING"
    except UnicodeError:
        return None, f"{source}_DOCUMENT_INVALID"
    except (OSError, ValueError):
        return None, f"{source}_UNREADABLE"
    try:
        document = json.loads(
            text, object_pairs_hook=_unique_object, parse_constant=_reject_constant,
        )
    except (ValueError, RecursionError):
        return None, f"{source}_DOCUMENT_INVALID"
    if not isinstance(document, dict):
        return None, f"{source}_DOCUMENT_INVALID"
    return document, None


def report_files(audit_path: Path, guidance_path: Path, canonical_locator: str) -> dict:
    """Read only the explicitly supplied files; never resolve the locator."""
    if not _valid_locator(canonical_locator):
        return _report("CANONICAL_LOCATOR_INVALID", None)
    guidance, reason = _read_document(guidance_path, "GUIDANCE")
    if reason:
        return _report(reason, canonical_locator)
    # Match build_report's guidance-first precedence even when the audit is absent.
    reason = _model_error(guidance, "supported_audit_model", "GUIDANCE")
    if reason:
        return _report(reason, canonical_locator)
    audit, reason = _read_document(audit_path, "AUDIT")
    if reason:
        return _report(reason, canonical_locator)
    return build_report(audit, guidance, canonical_locator)


class _ValueFreeParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        # Exit code follows the documented CLI usage-error contract.
        self.exit(2, "ARGUMENTS_INVALID: Supply audit, guidance and canonical locator arguments.\n")


def main(argv: list[str] | None = None) -> int:
    parser = _ValueFreeParser(
        prog="portability_guidance_health", allow_abbrev=False,
        description="Compare explicit audit and portability guidance models offline.",
    )
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--guidance", type=Path, required=True)
    parser.add_argument("--canonical-locator", required=True)
    args = parser.parse_args(argv)
    result = report_files(args.audit, args.guidance, args.canonical_locator)
    print(json.dumps(result, sort_keys=True))
    # Exit codes follow docs/guides/portability-guidance-health.md.
    return 0 if result["status"] == "current" else 1


if __name__ == "__main__":
    sys.exit(main())
