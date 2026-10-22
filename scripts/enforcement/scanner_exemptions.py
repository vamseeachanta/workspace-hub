"""Category-bound, exact-path line exemptions; contract: issue #3938 (2026).

Policies are reviewed code, never scanner-input configuration. Structural
eligibility must come from the same blob as the line being scanned. A marker
alone cannot establish eligibility. This module does not authenticate review.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass


@dataclass(frozen=True)
class ExemptionPolicy:
    """One exact category binding; no category aliases, path globs or prefixes."""

    context_id: str
    rule_category: str
    paths: frozenset[bytes]
    sentinel: bytes

    def __post_init__(self) -> None:
        object.__setattr__(self, "paths", frozenset(self.paths))
        if not self.context_id or not self.rule_category or not self.paths:
            raise ValueError("exemption binding must be nonempty")
        if not self.sentinel or any(char in self.sentinel for char in (b"\n", b"\r")):
            raise ValueError("exemption marker must be a nonempty single line")


def exemption_applies(
    policies: Iterable[ExemptionPolicy], *, context_id: str, rule_category: str,
    path: bytes, line: bytes, structure_matches: bool,
) -> bool:
    """Deny unless every binding term matches; unknown categories stay visible.

    The conjunction implements issue #3938 (2026). Physical lines exclude their
    terminators. Only horizontal whitespace may follow the comment marker.
    Callers must apply this per finding, never skip the entire line/file.
    """
    if structure_matches is not True or b"\n" in line or b"\r" in line:
        return False
    return any(
        context_id == policy.context_id
        and rule_category == policy.rule_category
        and path in policy.paths
        and line.rstrip(b" \t").endswith(b"# " + policy.sentinel)
        for policy in policies
    )
