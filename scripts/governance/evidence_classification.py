"""Reference adapter for recorded classes and byte-content checks.

Contract: docs/architecture/recorded-evidence-contract.md, issue 3851 (2026).
No authentication, native qualification, readiness or authorization is performed.
Existing consumers are not enrolled by importing this opt-in reference adapter.
"""
from __future__ import annotations

from collections.abc import Callable, Mapping


def assess_content(
    payload: bytes,
    *,
    recorded_class: str,
    checks: Mapping[str, Callable[[bytes], bool | None]],
) -> dict:
    """Run named content predicates without interpreting the recorded class.

    A check returns True (PASS), False (FAIL) or None (NOT_EVALUATED).
    Expected predicate errors and other return types produce ERROR. Checks must
    be trusted, side-effect-free application code; this function is no sandbox.
    Empty or incomplete check sets cannot pass. The selected procedure remains
    caller-supplied and does not establish independent engineering acceptance.
    Expected exception text is omitted from the result. Unexpected exceptions
    abort without a verdict; callers must handle diagnostics privately.
    """
    if type(payload) is not bytes:
        raise ValueError("Immutable bytes required")
    if not isinstance(recorded_class, str) or not recorded_class.strip():
        raise ValueError("Recorded class required")
    if not isinstance(checks, Mapping):
        raise TypeError("Named callable checks required")
    selected = dict(checks)
    if any(not isinstance(name, str) or not name.strip() or not callable(check)
           for name, check in selected.items()):
        raise ValueError("Named callable checks required")

    results = {}
    for name, check in sorted(selected.items()):
        try:
            value = check(payload)
        except (ArithmeticError, AssertionError, LookupError, OSError, RuntimeError, TypeError, ValueError):
            results[name] = "ERROR"
            continue
        if value is True:
            results[name] = "PASS"
        elif value is False:
            results[name] = "FAIL"
        elif value is None:
            results[name] = "NOT_EVALUATED"
        else:
            results[name] = "ERROR"

    # Truth table: recorded-evidence-contract.md, Content assessment (2026).
    # These are logical outcomes, not numerical engineering acceptance limits.
    if any(value in {"FAIL", "ERROR"} for value in results.values()):
        status = "content_checks_failed"
    elif not results or "NOT_EVALUATED" in results.values():
        status = "content_checks_not_evaluated"
    else:
        status = "content_checks_passed"
    return {
        "recorded_class": recorded_class,
        "content_check_results": results,
        "status": status,
        "classification_independently_verified": False,
        "provenance_independently_verified": False,
        "native_qualification": False,
        "readiness_status": "NOT_EVALUATED",
        "solve_authorized": False,
        "publication_authorized": False,
    }
