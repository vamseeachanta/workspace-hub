#!/usr/bin/env python3
"""Authoritative close-gate decision for #2798 (hardened per code review).

Pure decision function shared by the GitHub Action (reopens on deny) and the local
advisory pre-flight. Code-review fixes (Claude + Codex impl review, 2026-05-25):

- **Threshold from config, never the record** (Codex#2): a body-stamped record is
  agent/anyone-editable; trusting its `threshold` lets `{"pct":100,"threshold":0}`
  pass. The threshold is looked up by the record's *class* from server-side config.
- **Record bound to the issue** (Codex#3): the record must declare its `issue_number`
  and it must match the issue being closed, else it is a copied/forged record.
- **Verified label must post-date the body** (Codex#1, Claude#2): `body_verified_fresh`
  (computed by the runner from label-event time vs issue body-edit time) must hold,
  so editing the body after verification invalidates the label.
- **Unknown class fails closed** rather than defaulting a threshold.
"""
from __future__ import annotations

from dataclasses import dataclass

VERIFIED_LABEL = "status:completeness-verified"
OPT_IN_LABEL = "gate:completeness"
PLAN_APPROVED_LABEL = "status:plan-approved"
DEFAULT_THRESHOLDS = {"code": 90, "evidence": 80}


@dataclass
class GateDecision:
    allowed: bool
    reason: str


def gate_applies(labels: list[str], opt_in_label: str = OPT_IN_LABEL,
                 plan_approved_label: str = PLAN_APPROVED_LABEL) -> bool:
    """Whether the completeness gate enforces on this issue at all.

    Opt-in rollout (rollout-fix): the gate enforces ONLY for issues that explicitly
    carry the ``gate:completeness`` label AND reached ``status:plan-approved``.
    Everything else is out of scope — so an unconfigured gate and the existing
    backlog are unaffected (no retroactive disruption).
    """
    return opt_in_label in labels and plan_approved_label in labels


def evaluate_close(
    record: dict | None,
    labels: list[str],
    label_actor: str | None,
    closing_actor: str,
    authorized_appliers: set[str],
    expected_issue: int,
    body_verified_fresh: bool,
    class_thresholds: dict[str, int] | None = None,
    verified_label: str = VERIFIED_LABEL,
    require_separate_closer: bool = False,
) -> GateDecision:
    thresholds = class_thresholds or DEFAULT_THRESHOLDS

    if not record:
        return GateDecision(False, "no computed completeness record found for this issue")

    # binding: record must be for THIS issue (forged/copied records rejected)
    rec_issue = record.get("issue_number")
    if rec_issue is None or int(rec_issue) != int(expected_issue):
        return GateDecision(
            False, f"record issue_number {rec_issue!r} does not match issue #{expected_issue} (unbound/forged record)")

    # threshold comes from server-side config keyed by class — NOT from the record
    cls = record.get("cls")
    if cls not in thresholds:
        return GateDecision(False, f"unknown completeness class {cls!r} — fail-closed")
    threshold = thresholds[cls]

    if verified_label not in labels:
        return GateDecision(False, f"required owner label {verified_label!r} is absent")

    if label_actor is None or label_actor not in authorized_appliers:
        return GateDecision(
            False,
            f"verified label applied by unauthorized actor {label_actor!r}; "
            f"must be one of {sorted(authorized_appliers)}")

    # Separation-of-duties is OPT-IN (teams), not default. The authorized-appliers check
    # above already guarantees an authorized owner applied the verified label — that IS the
    # human gate. Requiring a *different* closer makes the gate unsatisfiable for a solo
    # operator (always both verifier and closer). Teams that want separation set
    # COMPLETENESS_REQUIRE_SEPARATE_CLOSER=1.
    if require_separate_closer and label_actor == closing_actor:
        return GateDecision(
            False, f"verifier and closer are the same actor {label_actor!r} and separate-closer is "
                   "required (COMPLETENESS_REQUIRE_SEPARATE_CLOSER)")

    if not body_verified_fresh:
        return GateDecision(
            False, "issue body was edited after the verified label was applied — re-verification required")

    pct = record.get("completeness_pct")
    if pct is None:
        return GateDecision(False, "record missing completeness_pct")
    if pct < threshold:
        return GateDecision(False, f"completeness {pct} below class '{cls}' threshold {threshold}")

    return GateDecision(
        True, f"completeness {pct} >= {threshold} ({cls}), verified by {label_actor} (closer {closing_actor})")
