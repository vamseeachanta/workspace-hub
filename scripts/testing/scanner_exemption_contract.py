"""Reusable boundary probes for scanner adapters; issue #3938 (2026).

Only synthetic fixtures belong in contracts. Assertion messages name the failed
boundary and never echo source lines, paths or potential credential values.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass, replace


@dataclass(frozen=True)
class ExemptionProbe:
    context_id: str
    rule_category: str
    path: bytes
    body: bytes
    line_number: int


def assert_exemption_contract(
    allows: Callable[[ExemptionProbe], bool], allowed: ExemptionProbe, *,
    other_categories: Iterable[str], other_paths: Iterable[bytes],
    invalid_bodies: Iterable[bytes],
) -> None:
    """Require a positive control and independent negative boundary probes.

    Supply another *active* category that matches the same synthetic line, a
    disallowed but scanned path, and marker/structure-invalid bodies that still
    trigger the original rule. An adapter returns whether that finding was
    suppressed, not whether a file was clean or a scanner exited successfully.
    Test-owned inputs are the independent oracle; do not derive them from the
    production exemption registry. No third-party test dependency is needed.
    """
    categories = tuple(other_categories)
    paths = tuple(other_paths)
    bodies = tuple(invalid_bodies)
    if (
        not categories or not paths or not bodies
        or allowed.rule_category in categories or allowed.path in paths
        or allowed.body in bodies
    ):
        raise ValueError("boundary probes must be nonempty and distinct")

    def expect(probe: ExemptionProbe, outcome: bool, boundary: str) -> None:
        if allows(probe) is not outcome:
            raise AssertionError(f"exemption contract failed: {boundary}")

    expect(allowed, True, "positive-control")
    expect(replace(allowed, context_id=allowed.context_id + "-unknown"), False, "context")
    for category in categories:
        expect(replace(allowed, rule_category=category), False, "rule-category")
    for path in paths:
        expect(replace(allowed, path=path), False, "path")
    for body in bodies:
        expect(replace(allowed, body=body), False, "line-structure")
    # One-based physical lines are the scanner API convention, not a threshold.
    for line_number in (0, -1, len(allowed.body.splitlines()) + 1):
        expect(replace(allowed, line_number=line_number), False, "line-number")
