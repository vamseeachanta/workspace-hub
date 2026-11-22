#!/usr/bin/env python3
"""I/O wrapper around the #2798 close-gate decision (hardened per code review).

Gathers issue context via ``gh`` and calls the pure, unit-tested
``completeness_gate_check.evaluate_close``. Exit 0 = close allowed; exit 1 = denied
(the GitHub Action reopens + comments; the advisory pre-flight just warns).

Hardening:
- enforces explicit completeness-v2 enrollments or the historical two-label enrollment;
  enrollment neither authenticates task authority nor grants implementation approval;
- computes ``body_verified_fresh`` = verified-label applied at/after the issue body's
  last edit, so editing the body after verification invalidates the label (Codex#1);
- binds via ``expected_issue``; threshold comes from server-side config, not the record;
- authorized appliers are COMPLETENESS_OWNERS plus COMPLETENESS_REVIEWERS (repo variables),
  and the labeler must not be an author of the closing PR or commit (rules review r5).
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from completeness_gate_check import (  # noqa: E402
    OPT_IN_LABEL, PLAN_APPROVED_LABEL, VERIFIED_LABEL,
    body_is_fresh, evaluate_close, gate_applies, work_authors_from,
)
from label_authority import gh_json, parse_iso, verified_label_event  # noqa: E402

_RECORD_RE = re.compile(r"```completeness\s*(\{.*?\})\s*```", re.DOTALL)


# Keep nested first pages bounded. Most closes need one query; only an unfinished
# connection is fetched again, using its own parent ID and cursor.
def _page_of(fields):
    return " { totalCount pageInfo { hasNextPage endCursor } nodes { " + fields + " } }"


_AUTHORS = _page_of("user { login }")
_COMMIT = "id authors(first:10)" + _AUTHORS
_COMMITS = _page_of("commit { " + _COMMIT + " }")
_PR = "id author { login } commits(first:50)" + _COMMITS
_LINKS = _page_of("state " + _PR)

_ISSUE_QUERY = """
query($owner: String!, $name: String!, $issue: Int!) {
  repository(owner: $owner, name: $name) {
    issue(number: $issue) {
      id closed lastEditedAt createdAt
      timelineItems(itemTypes:[CLOSED_EVENT], last:1) {
        nodes { ... on ClosedEvent { closer {
          __typename ... on PullRequest { %(pr)s } ... on Commit { %(commit)s }
        } } }
      }
      closedByPullRequestsReferences(first:20, includeClosedPrs:true) %(links)s
    }
  }
}
""" % {"pr": _PR, "commit": _COMMIT, "links": _LINKS}


def _graphql(query, *variables):
    try:
        response = gh_json("api", "graphql", "-f", "query=" + query, *variables) or {}
    except subprocess.CalledProcessError as error:
        print(f"[completeness-gate] GraphQL read failed: {error.stderr}", file=sys.stderr)
        return {}
    return {} if response.get("errors") else response.get("data") or {}


def _next_page(parent_id, field, cursor):
    parent_type, arguments, selection = {
        "closedByPullRequestsReferences": ("Issue", "includeClosedPrs:true,", _LINKS),
        "commits": ("PullRequest", "", _COMMITS),
        "authors": ("Commit", "", _AUTHORS),
    }[field]
    query = ("query($id: ID!, $cursor: String!) { node(id:$id) { ... on "
             + parent_type + " { " + field + "(" + arguments + "first:100, after:$cursor)"
             + selection + " } } }")
    return _graphql(query, "-f", "id=" + parent_id, "-f", "cursor=" + cursor)["node"][field]


def _configured_logins(*variables):
    return {login.strip() for variable in variables
            for login in os.environ.get(variable, "").split(",") if login.strip()}


def _parse_record(body: str) -> dict | None:
    m = _RECORD_RE.search(body or "")
    if not m:
        return None
    try:
        return json.loads(m.group(1))
    except json.JSONDecodeError:
        return None  # fail-closed: unparseable record => no record


def main() -> int:
    repo = os.environ.get("GH_REPO") or os.environ.get("REPO", "")
    issue = int(os.environ.get("ISSUE_NUMBER") or sys.argv[1])
    closing_actor = os.environ.get("CLOSING_ACTOR", "")

    data = gh_json("issue", "view", str(issue), "--repo", repo,
                   "--json", "body,labels,updatedAt") or {}
    labels = [l["name"] for l in data.get("labels", [])]

    # OPT-IN SCOPE FIRST: the gate only enforces on issues that explicitly opted in
    # (gate:completeness plus v2 enrollment or the historical label pair). Checking this BEFORE the owners config
    # means an unconfigured gate is inert for everything else — no retroactive disruption.
    if not gate_applies(labels):
        print(f"[completeness-gate] issue #{issue}: not enrolled ({OPT_IN_LABEL} plus v2 enrollment or historical label pair) "
              f"— gate not applicable, ALLOW", file=sys.stderr)
        return 0

    owners = _configured_logins("COMPLETENESS_OWNERS", "COMPLETENESS_REVIEWERS")
    if not owners:
        print(f"[completeness-gate] issue #{issue}: CONFIG ERROR — opted-in but COMPLETENESS_OWNERS "
              "repo variable is unset; set it (comma-separated logins).", file=sys.stderr)
        return 1

    record = _parse_record(data.get("body", ""))
    label_actor, label_at = verified_label_event(repo, issue, VERIFIED_LABEL)
    # Freshness anchors on the BODY edit time (lastEditedAt), NOT updatedAt — the close
    # itself bumps updatedAt past the label and would falsely fail freshness (fix #5).
    owner, name = repo.split("/", 1)
    context = _graphql(_ISSUE_QUERY, "-f", f"owner={owner}", "-f", f"name={name}", "-F", f"issue={issue}")
    issue_ts = (context.get("repository") or {}).get("issue") or {}
    body_verified_fresh = body_is_fresh(
        label_at, parse_iso(issue_ts.get("lastEditedAt")), parse_iso(issue_ts.get("createdAt")))

    require_separate = os.environ.get("COMPLETENESS_REQUIRE_SEPARATE_CLOSER", "").lower() in ("1", "true", "yes")
    decision = evaluate_close(
        record=record, labels=labels, label_actor=label_actor,
        closing_actor=closing_actor, authorized_appliers=owners,
        expected_issue=issue, body_verified_fresh=body_verified_fresh,
        require_separate_closer=require_separate,
        work_authors=work_authors_from(issue_ts, _next_page),
        shared_logins=_configured_logins("COMPLETENESS_SHARED_LOGINS"),
    )
    print(f"[completeness-gate] issue #{issue}: "
          f"{'ALLOW' if decision.allowed else 'DENY'} — {decision.reason}", file=sys.stderr)
    return 0 if decision.allowed else 1


if __name__ == "__main__":
    raise SystemExit(main())
