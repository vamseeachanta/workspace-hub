"""Dual-slot and coverage-state policy."""

from __future__ import annotations

from .codec import AuthorityError


STATES = {"scanned", "queried-no-access", "provider-follow-up", "unknown-residual"}
REQUIRED_SURFACES = {
    "actions",
    "caches",
    "commit-comments",
    "discussions",
    "forks",
    "issues",
    "lfs",
    "packages",
    "pages",
    "pull-requests",
    "releases",
    "wiki",
}


def select_slot(current, pending, head_oid):
    if (
        pending
        and pending.get("slot") == "pending"
        and pending.get("expected_head_oid") == head_oid
    ):
        return pending
    if current.get("slot") != "current":
        raise AuthorityError("integrity")
    return current


def classify_coverage(surfaces):
    if set(surfaces) != REQUIRED_SURFACES or any(
        state not in STATES for state in surfaces.values()
    ):
        raise AuthorityError("integrity")
    return (
        "complete"
        if all(state == "scanned" for state in surfaces.values())
        else "residual"
    )
