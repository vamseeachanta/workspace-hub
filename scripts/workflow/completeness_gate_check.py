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
- **The verifier did not write the work** (rules review r5, card A): the verified label
  may be applied by any authorized reviewer, not only the owner, provided the labeler is
  not an author of the closing PR or commit. When the labeler's login is one of those
  authors (several agents can act through one login), the login cannot show who wrote
  the work, so the record must name a separate verifier (``work_by`` != ``verified_by``).
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


def body_is_fresh(label_at, last_edited_at, created_at) -> bool:
    """Whether the verified label post-dates the last BODY edit (anti-forgery).

    Compare against the issue body's edit time (``last_edited_at``, falling back to
    ``created_at`` when the body was never edited) — NOT the issue's ``updatedAt``,
    which bumps on labels/comments/**the close itself** and would make a legitimate
    close fail freshness (fix #5; the close always post-dates the verified label).
    All args are datetimes or None.
    """
    edited = last_edited_at or created_at
    return bool(label_at and edited and label_at >= edited)


def gate_applies(labels: list[str], opt_in_label: str = OPT_IN_LABEL,
                 plan_approved_label: str = PLAN_APPROVED_LABEL) -> bool:
    """Whether the completeness gate enforces on this issue at all.

    The completeness opt-in is independent of implementation authorization.
    New enrollments carry gate:completeness-v2. The historical two-label route
    remains available without retroactively enrolling the bulk-labeled backlog.
    Neither enrollment authenticates authority or grants implementation approval.
    """
    return opt_in_label in labels and (
        "gate:completeness-v2" in labels or plan_approved_label in labels)


def work_authors_from(issue_node: dict | None) -> set[str]:
    """Logins that wrote the work: the closing PR or commit author, plus merged linked PRs.

    ``issue_node`` is the GraphQL issue object with ``timelineItems`` (last CLOSED_EVENT,
    its ``closer``) and ``closedByPullRequestsReferences``. Missing data gives an empty set,
    which the separation check treats as "author unknown".
    """
    authors: set[str] = set()
    node = issue_node or {}
    for ev in ((node.get("timelineItems") or {}).get("nodes") or []):
        closer = (ev or {}).get("closer") or {}
        login = ((closer.get("author") or {}).get("login")  # PullRequest
                 or ((closer.get("author") or {}).get("user") or {}).get("login"))  # Commit
        if login:
            authors.add(login)
    for pr in ((node.get("closedByPullRequestsReferences") or {}).get("nodes") or []):
        if (pr or {}).get("state") == "MERGED":
            login = (pr.get("author") or {}).get("login")
            if login:
                authors.add(login)
    return authors


def verifier_is_separate(label_actor: str | None, work_authors: set[str] | None,
                         record: dict) -> GateDecision:
    """Whether the verified label came from someone who did not write the work."""
    authors = {a.lower() for a in (work_authors or set()) if a}
    actor = (label_actor or "").lower()
    if authors and actor and actor not in authors:
        return GateDecision(True, f"labeler {label_actor!r} is not an author of the closing PR or commit")
    work_by = str(record.get("work_by") or "").strip().lower()
    verified_by = str(record.get("verified_by") or "").strip().lower()
    if work_by and verified_by and work_by != verified_by:
        return GateDecision(True, f"record names verifier {verified_by!r} separate from author {work_by!r}")
    where = (f"labeler {label_actor!r} is an author of the closing PR or commit" if authors
             else "no closing PR or commit author was found")
    return GateDecision(
        False, f"{where}, and the record does not name a separate verifier "
               "(work_by and verified_by must both be set and differ)")


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
    work_authors: set[str] | None = None,
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
        return GateDecision(False, f"required verified label {verified_label!r} is absent")

    if label_actor is None or label_actor not in authorized_appliers:
        return GateDecision(
            False,
            f"verified label applied by unauthorized actor {label_actor!r}; "
            f"must be one of {sorted(authorized_appliers)}")

    # The reviewer who applies the label must not have written the work (r5 card A).
    separation = verifier_is_separate(label_actor, work_authors, record)
    if not separation.allowed:
        return separation

    # Verifier-versus-closer separation stays OPT-IN. The check above already keeps the
    # verifier apart from the author of the work; requiring a *different* closer as well
    # makes the gate unsatisfiable for one login that both verifies and closes. Teams that
    # want it set COMPLETENESS_REQUIRE_SEPARATE_CLOSER=1.
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
