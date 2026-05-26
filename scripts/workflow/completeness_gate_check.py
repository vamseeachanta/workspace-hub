#!/usr/bin/env python3
"""Authoritative close-gate decision for #2798.

Pure decision function shared by the GitHub Action (``.github/workflows/
completeness-gate.yml``, which reopens a closed issue when this denies) and the
local advisory pre-flight (``scripts/enforcement/check-completeness-before-close.sh``).

Encodes the plan-review fixes:
- a computed completeness record must exist (Codex#15: prove the close is gated);
- an owner-only ``status:completeness-verified`` label must be present;
- that label must have been applied by an *authorized* actor (ruleset-restricted)
  who is NOT the closing actor — closing the agent-self-verify spoof
  (Claude#2 / Codex#20: metadata/comments alone are spoofable, a label-by-owner is not).
"""
from __future__ import annotations

from dataclasses import dataclass

VERIFIED_LABEL = "status:completeness-verified"


@dataclass
class GateDecision:
    allowed: bool
    reason: str


def evaluate_close(
    record: dict | None,
    labels: list[str],
    label_actor: str | None,
    closing_actor: str,
    authorized_appliers: set[str],
    verified_label: str = VERIFIED_LABEL,
) -> GateDecision:
    """Decide whether an issue may remain closed.

    ``record`` — the persisted computed completeness record (or ``None``).
    ``labels`` — current issue labels. ``label_actor`` — who applied the verified
    label (from the GH audit log). ``closing_actor`` — who closed the issue.
    ``authorized_appliers`` — actors permitted to apply the verified label.
    """
    if not record:
        return GateDecision(False, "no computed completeness record found for this issue")

    if verified_label not in labels:
        return GateDecision(
            False, f"required owner label {verified_label!r} is absent")

    if label_actor is None or label_actor not in authorized_appliers:
        return GateDecision(
            False,
            f"verified label applied by unauthorized actor {label_actor!r}; "
            f"must be one of {sorted(authorized_appliers)}")

    if label_actor == closing_actor:
        return GateDecision(
            False,
            f"verifier and closer are the same actor {label_actor!r} — self-verification not allowed")

    pct = record.get("completeness_pct")
    threshold = record.get("threshold")
    if pct is None or threshold is None:
        return GateDecision(False, "record missing completeness_pct/threshold")
    if pct < threshold:
        return GateDecision(False, f"completeness {pct} below threshold {threshold}")

    return GateDecision(
        True, f"completeness {pct} >= {threshold}, verified by {label_actor} (closer {closing_actor})")
