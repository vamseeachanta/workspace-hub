"""Remove issue and plan prose from public control reports (issue 3768).

Local ignored mirrors retain their source text. Public reports retain their
existing structure and issue references, using a fixed marker for prose fields.
This projection does not depend on a private identifier map or its availability.
It is not a general secret scanner: other metadata still needs its own review.
"""
from __future__ import annotations

from typing import Any

# Issue 3768, public-output disclosure contract; no engineering coefficients.
WITHHELD = "[withheld; see issue]"
PROSE_FIELDS = frozenset({"title", "body", "body_excerpt", "plan_summary", "risks", "tests"})


def public_issue_view(value: Any) -> Any:
    """Copy a report, replacing prose fields before serialization or rendering.

    Apply after classification so routing can use the original source text.
    Also apply when rendering legacy reports which may still carry that text.
    """
    if isinstance(value, dict):
        return {key: WITHHELD if key in PROSE_FIELDS else public_issue_view(item)
                for key, item in value.items()}
    if isinstance(value, list):
        return [public_issue_view(item) for item in value]
    if isinstance(value, tuple):
        return tuple(public_issue_view(item) for item in value)
    return value
