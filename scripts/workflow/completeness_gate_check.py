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
  authors, only a configured shared login may name a distinct verifier in the record.
  Incomplete author evidence denies closure even for a shared login.
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


def _all_nodes(parent, field, next_page):
    """Read a connection to its end, or discard the entire author result."""
    page = parent[field]
    total = page["totalCount"]
    if type(total) is not int or total < 0:
        raise ValueError("missing connection count")
    nodes = []
    cursors = set()
    while True:
        batch = page["nodes"]
        if not isinstance(batch, list) or page["totalCount"] != total:
            raise ValueError("incomplete connection")
        nodes.extend(batch)
        info = page["pageInfo"]
        if info["hasNextPage"] is False and len(nodes) == total:
            return nodes
        cursor = info["endCursor"]
        if (info["hasNextPage"] is not True or not batch or len(nodes) >= total
                or not isinstance(cursor, str) or not cursor or cursor in cursors or next_page is None):
            raise ValueError("incomplete pagination")
        cursors.add(cursor)
        page = next_page(parent["id"], field, cursor)


def _commit_authors(commit, next_page):
    authors = _all_nodes(commit, "authors", next_page)
    if not authors:
        raise ValueError("missing commit authors")
    return {author["user"]["login"] for author in authors}


def _pr_authors(pr, next_page):
    commits = _all_nodes(pr, "commits", next_page)
    if not commits:
        raise ValueError("missing PR commits")
    authors = {pr["author"]["login"]}
    for node in commits:
        authors.update(_commit_authors(node["commit"], next_page))
    return authors


def work_authors_from(issue_node: dict | None, next_page=None) -> set[str] | None:
    """Resolve the close event and every merged closing reference as one body of evidence."""
    if issue_node is None:
        return None
    authors = set()
    try:
        events = issue_node["timelineItems"]["nodes"]
        if not isinstance(events, list) or (issue_node["closed"] and not events):
            return None
        for event in events:
            closer = event["closer"]
            if closer is None:  # A manual close can still have merged references.
                continue
            if closer["__typename"] == "PullRequest":
                authors.update(_pr_authors(closer, next_page))
            elif closer["__typename"] == "Commit":
                authors.update(_commit_authors(closer, next_page))
            else:
                return None

        for pr in _all_nodes(issue_node, "closedByPullRequestsReferences", next_page):
            if pr["state"] == "MERGED":
                authors.update(_pr_authors(pr, next_page))
            elif pr["state"] not in ("OPEN", "CLOSED"):
                return None
    except (KeyError, TypeError, ValueError):
        return None
    return authors if authors and all(_identity(a) for a in authors) else None


def _identity(value) -> str:
    return value.strip().casefold() if isinstance(value, str) else ""


def verifier_is_separate(label_actor: str | None, work_authors: set[str] | None,
                         record: dict, shared_logins: set[str] | None = None) -> GateDecision:
    """Whether the verified label came from someone who did not write the work."""
    authors = {_identity(a) for a in work_authors or ()}
    actor = _identity(label_actor)
    if not authors or "" in authors or not actor:
        return GateDecision(False, "incomplete author or labeler evidence")
    if actor not in authors:
        return GateDecision(True, f"labeler {label_actor!r} is not an author of the closing PR or commit")
    if actor not in {_identity(login) for login in shared_logins or ()}:
        return GateDecision(False, f"labeler {label_actor!r} is an author of the closing PR or commit")
    work_by = _identity(record.get("work_by"))
    verified_by = _identity(record.get("verified_by"))
    if work_by and verified_by and work_by != verified_by:
        return GateDecision(True, f"record names verifier {verified_by!r} separate from author {work_by!r}")
    return GateDecision(False, "shared login requires distinct nonempty work_by and verified_by strings")


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
    shared_logins: set[str] | None = None,
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
    separation = verifier_is_separate(label_actor, work_authors, record, shared_logins)
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
